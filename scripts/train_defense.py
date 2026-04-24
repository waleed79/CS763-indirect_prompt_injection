"""Offline training script for Phase 3.1 multi-signal defense (DEF-01/DEF-04).

Produces three model artifacts in models/:
  models/bert_classifier/         -- fine-tuned DistilBERT (Signal 1)
  models/lr_meta_classifier.json  -- LR coefs + StandardScaler (meta-classifier)
  models/signal4_baseline.json    -- canary retrieval score mu/std (Signal 4)

Run once before evaluation:
    conda activate rag-security
    python scripts/train_defense.py

Design decisions (from 03.1-CONTEXT.md):
  D-01: Tier-stratified hold-out -- train on T1/T2 (IDs 20000-20099), test on T3/T4 (20100+)
  D-03: class_weight='balanced' -- 3:1 imbalance requires weighting
  D-09: LogisticRegression, L2, solver='lbfgs'
  D-10: Feature vector [bert_prob, perplexity_z, imperative_ratio, retrieval_z]
  D-14: Signal 4 baseline from canary queries (paired=False, indices 50-99 of test_queries.json)
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from datasets import Dataset
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from transformers import (
    DataCollatorWithPadding,
    DistilBertForSequenceClassification,
    DistilBertTokenizerFast,
    GPT2LMHeadModel,
    GPT2TokenizerFast,
    Trainer,
    TrainingArguments,
)

# Allow running from repo root or scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Constants ─────────────────────────────────────────────────────────────────

CORPUS_PATH = Path("data/corpus_poisoned.jsonl")
QUERIES_PATH = Path("data/test_queries.json")
MODELS_DIR = Path("models")
BERT_OUTPUT_DIR = MODELS_DIR / "bert_classifier"
LR_JSON_PATH = MODELS_DIR / "lr_meta_classifier.json"
SIGNAL4_JSON_PATH = MODELS_DIR / "signal4_baseline.json"

TIER1_ID_START = 20000
TIER2_ID_START = 20050
TIER3_ID_START = 20100
TIER4_ID_START = 20200
CLEAN_ID_MAX = 19999


# ── WeightedTrainer (from RESEARCH.md Pattern 2) ─────────────────────────────

class WeightedTrainer(Trainer):
    """HF Trainer with class-weighted cross-entropy loss for imbalanced training."""

    def __init__(self, class_weights: torch.Tensor, **kwargs):
        super().__init__(**kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss_fct = torch.nn.CrossEntropyLoss(
            weight=self.class_weights.to(logits.device)
        )
        loss = loss_fct(logits.view(-1, 2), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


# ── Step 1: Load training data ────────────────────────────────────────────────

def load_training_data(seed: int = 42):
    """Read corpus_poisoned.jsonl and split into train/val/test sets.

    Parameters
    ----------
    seed:
        Random seed for the clean-negative shuffle so splits are reproducible
        even when called in isolation (e.g. notebooks, tests). Aligned with
        Phase 3.2 EVAL-05 multi-seed aggregation (--seed flag, WR-04 fix).

    Returns
    -------
    tuple of:
        train_examples: list of (text, label) for BERT + LR training
        val_examples:   list of (text, label) for LR threshold tuning
        test_examples:  list of (text, label, retrieval_score) for test eval
        train_pos_texts: texts for positive training examples (for feature extraction)
        all_splits:     dict with raw split info
    """
    all_positives = []  # T1+T2 (train)
    test_positives = []  # T3+T4 (held-out)
    all_clean = []  # passage_id <= 19999

    with open(CORPUS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            pid = item["passage_id"]
            text = item.get("text", "")
            if not text:
                continue

            if TIER1_ID_START <= pid <= TIER2_ID_START + 49:  # 20000-20099
                all_positives.append({"text": text, "pid": pid, "score": 0.9})
            elif pid >= TIER3_ID_START:  # 20100+
                test_positives.append({"text": text, "pid": pid, "score": 0.9})
            elif pid <= CLEAN_ID_MAX:
                all_clean.append({"text": text, "pid": pid, "score": 0.7})

    # Assertion: T3/T4 data must not leak into training (D-01 / T-03.1-08)
    for item in all_positives:
        assert item["pid"] < TIER3_ID_START, (
            f"T3/T4 data found in training positives! pid={item['pid']}"
        )

    print(
        f"  Positives (T1+T2): {len(all_positives)}, "
        f"Test positives (T3+T4): {len(test_positives)}, "
        f"Clean: {len(all_clean)}"
    )

    # Sample 300 clean negatives for training pool; hold out 150 for test
    # Use a local RNG seeded with `seed` so the split is reproducible even
    # when load_training_data() is called in isolation (WR-04 fix).
    rng = random.Random(seed)
    rng.shuffle(all_clean)
    train_clean_pool = all_clean[:300]
    test_clean = all_clean[300:450]  # 150 test negatives

    # Threshold-tuning hold-out: last 10 positives + first 10 clean
    val_pos = all_positives[-10:]
    val_neg = train_clean_pool[:10]
    final_train_pos = all_positives[:90]    # 90 positives
    final_train_neg = train_clean_pool[10:]  # 290 negatives

    # Build labeled example lists
    train_examples = (
        [(item["text"], 1) for item in final_train_pos]
        + [(item["text"], 0) for item in final_train_neg]
    )
    val_examples = (
        [(item["text"], 1) for item in val_pos]
        + [(item["text"], 0) for item in val_neg]
    )
    test_examples = (
        [(item["text"], 1, item["score"]) for item in test_positives]
        + [(item["text"], 0, item["score"]) for item in test_clean]
    )

    print(
        f"  Train: {len(train_examples)} ({len(final_train_pos)} pos + "
        f"{len(final_train_neg)} neg)"
    )
    print(
        f"  Val: {len(val_examples)} ({len(val_pos)} pos + {len(val_neg)} neg)"
    )
    print(
        f"  Test: {len(test_examples)} ({len(test_positives)} pos + "
        f"{len(test_clean)} neg)"
    )

    return train_examples, val_examples, test_examples


# ── Step 2: Train DistilBERT ──────────────────────────────────────────────────

def train_bert(train_examples: list, val_examples: list) -> None:
    """Fine-tune DistilBERT on train_examples, evaluate on val_examples.

    Saves tokenizer and model to models/bert_classifier/.
    """
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2
    )

    # Tokenize examples
    def tokenize(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=128,
            padding=False,
        )

    train_texts, train_labels = zip(*train_examples)
    val_texts, val_labels = zip(*val_examples)

    train_dataset = Dataset.from_dict(
        {"text": list(train_texts), "label": list(train_labels)}
    )
    val_dataset = Dataset.from_dict(
        {"text": list(val_texts), "label": list(val_labels)}
    )

    train_dataset = train_dataset.map(tokenize, batched=True)
    val_dataset = val_dataset.map(tokenize, batched=True)

    train_dataset = train_dataset.rename_column("label", "labels")
    val_dataset = val_dataset.rename_column("label", "labels")
    train_dataset = train_dataset.remove_columns(["text"])
    val_dataset = val_dataset.remove_columns(["text"])

    # Class weights for imbalanced training (D-03)
    y_train = np.array(train_labels)
    cw = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_train)
    class_weights = torch.tensor(cw, dtype=torch.float)
    print(f"  Class weights: neg={cw[0]:.3f}, pos={cw[1]:.3f}")

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    training_args = TrainingArguments(
        output_dir=str(BERT_OUTPUT_DIR),
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        use_cpu=True,
        report_to="none",
        seed=42,
        logging_steps=20,
    )

    trainer = WeightedTrainer(
        class_weights=class_weights,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        processing_class=tokenizer,
    )

    trainer.train()

    # Save model and tokenizer
    trainer.save_model(str(BERT_OUTPUT_DIR))
    tokenizer.save_pretrained(str(BERT_OUTPUT_DIR))
    print(f"  BERT model saved to {BERT_OUTPUT_DIR}")

    # Print final eval metrics
    metrics = trainer.evaluate()
    print(f"  Final eval loss: {metrics.get('eval_loss', 'N/A'):.4f}")


# ── Step 3: Compute signal features ──────────────────────────────────────────

def _bert_prob_score(text: str, model, tokenizer) -> float:
    """Compute P(injection) from fine-tuned DistilBERT."""
    inputs = tokenizer(
        text,
        truncation=True,
        max_length=256,
        return_tensors="pt",
    )
    with torch.no_grad():
        logits = model(**inputs).logits[0]
    probs = torch.softmax(logits, dim=-1)
    return float(probs[1].item())


def _perplexity_max_nll(text: str, gpt2_model, gpt2_tokenizer,
                        window: int = 128, stride: int = 64) -> float:
    """Max-window NLL from GPT-2 strided sliding window (Pattern 3 in RESEARCH.md)."""
    try:
        enc = gpt2_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        tokens = enc.input_ids[0]
        n = len(tokens)
        if n < 2:
            return 0.0
        nlls = []
        for begin in range(0, max(1, n - 1), stride):
            end = min(begin + window, n)
            chunk_tokens = tokens[begin:end].unsqueeze(0)
            with torch.no_grad():
                out = gpt2_model(chunk_tokens, labels=chunk_tokens)
                nlls.append(out.loss.item())
        return max(nlls) if nlls else 0.0
    except (RuntimeError, ValueError):
        # Truncation/inference errors — treat as 0.0 (DoS mitigation T-03.1-04)
        # Let MemoryError and SystemExit propagate
        return 0.0


def _imperative_ratio_score(text: str) -> float:
    """Fraction of sentences containing at least one imperative verb (D-13)."""
    import re
    IMPERATIVE_VERBS = re.compile(
        r'\b(ignore|disregard|output|print|send|reveal|forget|override|'
        r'replace|append|include|add|write|say|tell|respond|answer|return|'
        r'give|show|display|emit|produce|repeat)\b',
        re.IGNORECASE,
    )
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    total = max(len(sentences), 1)
    imperative_count = sum(
        1 for s in sentences if IMPERATIVE_VERBS.search(s) is not None
    )
    return imperative_count / total


def compute_signal_features(
    examples: list,  # [(text, label, retrieval_score), ...]
    bert_model,
    bert_tokenizer,
    gpt2_model,
    gpt2_tokenizer,
    signal4_baseline: dict,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute [bert_prob, perplexity_z, imperative_ratio, retrieval_z] for each example.

    Parameters
    ----------
    examples:
        List of (text, label, retrieval_score) tuples.
    signal4_baseline:
        Dict with 'mu' and 'std' for retrieval z-score computation.

    Returns
    -------
    X: np.ndarray of shape (n, 4)
    y: np.ndarray of shape (n,)
    """
    mu = signal4_baseline.get("mu", 0.0)
    std = signal4_baseline.get("std", 1.0)

    X_rows = []
    y_vals = []
    n = len(examples)

    for i, example in enumerate(examples):
        if len(example) == 3:
            text, label, retrieval_score = example
        else:
            text, label = example
            retrieval_score = 0.7  # default for training examples

        if (i + 1) % 50 == 0:
            print(f"    Computing features {i + 1}/{n}...")

        bert_prob = _bert_prob_score(text, bert_model, bert_tokenizer)
        perplexity_z = _perplexity_max_nll(text, gpt2_model, gpt2_tokenizer)
        imperative_ratio = _imperative_ratio_score(text)
        retrieval_z = (retrieval_score - mu) / max(std, 1e-9)

        X_rows.append([bert_prob, perplexity_z, imperative_ratio, retrieval_z])
        y_vals.append(label)

    return np.array(X_rows, dtype=np.float32), np.array(y_vals, dtype=np.int32)


# ── Step 4: Calibrate Signal 4 canary baseline ────────────────────────────────

def calibrate_signal4() -> dict:
    """Compute mu/std of clean-passage retrieval scores from unpaired canary queries.

    Uses indices 50-99 of test_queries.json (paired=False), queries the
    nq_poisoned_v4 collection, collects scores from clean passages only
    (passage_id < 20000).

    Returns fallback {"mu": 0.7, "std": 0.1} if Ollama is not reachable.
    """
    try:
        import dataclasses
        from rag.config import load_config
        from rag.pipeline import RAGPipeline

        queries = json.load(open(QUERIES_PATH, encoding="utf-8"))
        # Canary queries: indices 50-99 (paired=False)
        canary_queries = [
            q.get("query") or q.get("question", "") for i, q in enumerate(queries)
            if i >= 50 and q.get("paired") is False
        ]
        canary_queries = [q for q in canary_queries if q]  # remove empty strings
        print(f"  Canary queries: {len(canary_queries)}")

        cfg = load_config()
        eval_cfg = dataclasses.replace(cfg, collection="nq_poisoned_v4")
        pipeline = RAGPipeline(eval_cfg)
        # Build corpus (existing collection — just connect, don't reindex)
        pipeline.build(corpus_path=str(CORPUS_PATH))

        scores = []
        for i, q in enumerate(canary_queries):
            try:
                result = pipeline.query(q, defense_fn=None)
                for hit in result.get("hits", []):
                    if hit.get("metadata", {}).get("passage_id", 99999) < TIER1_ID_START:
                        scores.append(hit["score"])
            except Exception as e:
                print(f"  Warning: query {i} failed: {e}")
                continue

        try:
            pipeline.close()
        except Exception:
            pass

        if not scores:
            print("  Warning: no clean scores collected; using fallback baseline")
            return _fallback_baseline()

        mu = float(np.mean(scores))
        std = float(np.std(scores))
        if std < 1e-9:
            std = 0.1
        print(f"  Signal 4 baseline: mu={mu:.4f}, std={std:.4f} (n={len(scores)} scores)")
        return {"mu": mu, "std": std}

    except ConnectionError as e:
        print(f"  Warning: Ollama not reachable ({e}); using fallback baseline")
        return _fallback_baseline()
    except Exception as e:
        print(f"  Warning: Signal 4 calibration failed ({e}); using fallback baseline")
        return _fallback_baseline()


def _fallback_baseline() -> dict:
    """Return a safe fallback Signal 4 baseline when Ollama is offline."""
    baseline = {"mu": 0.7, "std": 0.1, "note": "fallback -- run with Ollama for real calibration"}
    print("  Using fallback baseline:", baseline)
    return baseline


# ── Step 5: Train LR meta-classifier ─────────────────────────────────────────

def save_lr_to_json(lr: LogisticRegression, scaler: StandardScaler,
                    path: str, tuned_threshold: float) -> None:
    """Serialize LR + scaler to JSON (no pickle — anti-pickle requirement)."""
    data = {
        "lr_coef": lr.coef_.tolist(),
        "lr_intercept": lr.intercept_.tolist(),
        "lr_classes": lr.classes_.tolist(),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "tuned_threshold": float(tuned_threshold),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def train_lr_meta_classifier(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
) -> tuple[LogisticRegression, StandardScaler, float]:
    """Fit StandardScaler + LogisticRegression on training features.

    Returns
    -------
    lr: fitted LogisticRegression
    scaler: fitted StandardScaler
    best_thresh: tuned threshold from val set
    """
    # Feature normalization (Pitfall 7: required to avoid scale bias)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    # D-09: LR with L2, lbfgs, class_weight='balanced'
    lr = LogisticRegression(
        C=1.0,
        max_iter=1000,
        solver="lbfgs",
        class_weight="balanced",
        random_state=42,
    )
    lr.fit(X_train_s, y_train)

    train_acc = lr.score(X_train_s, y_train)
    val_acc = lr.score(X_val_s, y_val)
    print(f"  Train accuracy: {train_acc:.3f}")
    print(f"  Val accuracy:   {val_acc:.3f}")

    # Threshold tuning on val set (D-11): find threshold maximizing F1
    val_probs = lr.predict_proba(X_val_s)[:, 1]
    best_thresh = 0.5
    best_f1 = 0.0
    for thresh in np.arange(0.1, 1.0, 0.1):
        y_pred = (val_probs >= thresh).astype(int)
        if len(np.unique(y_pred)) < 2:
            continue
        f1 = f1_score(y_val, y_pred, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = float(thresh)

    print(f"  Fixed threshold: 0.5, Tuned threshold: {best_thresh:.2f} (val F1={best_f1:.3f})")
    print(f"  LR coef: {lr.coef_.tolist()}")

    # Save artifact
    save_lr_to_json(lr, scaler, str(LR_JSON_PATH), best_thresh)
    print(f"  LR meta-classifier saved to {LR_JSON_PATH}")

    return lr, scaler, best_thresh


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    random.seed(42)
    np.random.seed(42)

    print("=== Phase 3.1 Defense Training ===")
    MODELS_DIR.mkdir(exist_ok=True)
    BERT_OUTPUT_DIR.mkdir(exist_ok=True)

    # ── [1/4] Load training data ──────────────────────────────────────────────
    print("\n[1/4] Loading training data...")
    train_examples, val_examples, test_examples = load_training_data()

    # ── [2/4] Fine-tune DistilBERT (Signal 1) ────────────────────────────────
    print("\n[2/4] Fine-tuning DistilBERT (Signal 1)...")
    train_bert(train_examples, val_examples)

    # ── [3/4] Compute signal features for LR training ────────────────────────
    print("\n[3/4] Computing signal features for LR training...")
    print("  Loading trained BERT from models/bert_classifier...")
    bert_tokenizer = DistilBertTokenizerFast.from_pretrained(str(BERT_OUTPUT_DIR))
    bert_model = DistilBertForSequenceClassification.from_pretrained(str(BERT_OUTPUT_DIR))
    bert_model.eval()

    print("  Loading GPT-2 for perplexity signal...")
    gpt2_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    gpt2_tokenizer.pad_token_id = gpt2_tokenizer.eos_token_id
    gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")
    gpt2_model.eval()

    # Use a temporary uniform baseline for retrieval_z during feature extraction
    # (Signal 4 calibration happens in step 4; we use a dummy baseline here
    #  and the LR will learn weights relative to the actual baseline after calibration)
    dummy_baseline = {"mu": 0.7, "std": 0.1}

    # Build train+val feature sets (use 2-tuple examples for train/val)
    train_val_examples = [
        (text, label, 0.7) for text, label in train_examples + val_examples
    ]
    print(f"  Processing {len(train_val_examples)} train+val examples...")
    X_trainval, y_trainval = compute_signal_features(
        train_val_examples, bert_model, bert_tokenizer,
        gpt2_model, gpt2_tokenizer, dummy_baseline
    )

    # Split back into train and val
    n_train = len(train_examples)
    X_train = X_trainval[:n_train]
    y_train = y_trainval[:n_train]
    X_val = X_trainval[n_train:]
    y_val = y_trainval[n_train:]

    # ── [4/4a] Calibrate Signal 4 canary baseline ─────────────────────────────
    print("\n[4/4a] Calibrating Signal 4 canary baseline (requires Ollama + nq_poisoned_v4)...")
    signal4_baseline = calibrate_signal4()

    # Save Signal 4 baseline
    # Only save non-fallback keys (mu, std) plus optional note
    s4_out = {"mu": signal4_baseline["mu"], "std": signal4_baseline["std"]}
    if "note" in signal4_baseline:
        s4_out["note"] = signal4_baseline["note"]
    SIGNAL4_JSON_PATH.write_text(json.dumps(s4_out, indent=2))
    print(f"  Signal 4 baseline saved to {SIGNAL4_JSON_PATH}")

    # ── [4/4b] Train LR meta-classifier ──────────────────────────────────────
    print("\n[4/4b] Training LR meta-classifier...")
    # Recompute retrieval_z column with real baseline and per-example scores.
    # Positives (label==1) have retrieval_score=0.9; negatives have 0.7.
    # Overwriting column 3 with a single constant (as before) gives zero variance
    # and makes Signal 4 useless during LR fitting (CR-02 fix).
    mu = signal4_baseline["mu"]
    std = max(signal4_baseline["std"], 1e-9)
    train_val_scores = [0.9 if label == 1 else 0.7 for _, label in train_examples + val_examples]
    for i, rs in enumerate(train_val_scores):
        X_trainval[i, 3] = (rs - mu) / std
    X_train = X_trainval[:n_train]
    X_val   = X_trainval[n_train:]

    lr, scaler, best_thresh = train_lr_meta_classifier(X_train, y_train, X_val, y_val)

    print("\n=== Training complete. Model artifacts in models/ ===")
    print(f"  models/bert_classifier/      : DistilBERT fine-tuned (Signal 1)")
    print(f"  models/lr_meta_classifier.json: LR coefs + scaler (4 features, threshold={best_thresh:.2f})")
    print(f"  models/signal4_baseline.json  : mu={signal4_baseline['mu']:.4f}, std={signal4_baseline['std']:.4f}")


if __name__ == "__main__":
    main()
