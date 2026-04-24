"""Retrain LR meta-classifier using the real Signal 4 baseline (after calibration).

Run after _calibrate_signal4.py to update models/lr_meta_classifier.json
with retrieval_z features using the real mu/std baseline.
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizerFast,
    GPT2LMHeadModel,
    GPT2TokenizerFast,
)

sys.path.insert(0, str(Path(__file__).parent.parent))

import random
random.seed(42)
np.random.seed(42)

CORPUS_PATH = Path("data/corpus_poisoned.jsonl")
BERT_OUTPUT_DIR = Path("models/bert_classifier")
LR_JSON_PATH = Path("models/lr_meta_classifier.json")
SIGNAL4_JSON_PATH = Path("models/signal4_baseline.json")

from rag.constants import TIER1_ID_START, TIER2_ID_START, TIER3_ID_START, CLEAN_ID_MAX  # IN-05
from rag.defense import _imperative_ratio as imperative_ratio  # IN-01: no duplicate


def perplexity_max_nll(text, gpt2_model, gpt2_tokenizer, window=128, stride=64):
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
    except Exception:
        return 0.0


def bert_prob(text, bert_model, bert_tokenizer):
    inputs = bert_tokenizer(text, truncation=True, max_length=256, return_tensors="pt")
    with torch.no_grad():
        logits = bert_model(**inputs).logits[0]
    probs = torch.softmax(logits, dim=-1)
    return float(probs[1].item())


def main():
    # Load Signal 4 real baseline
    with open(SIGNAL4_JSON_PATH) as f:
        s4 = json.load(f)
    mu = s4["mu"]
    std = max(s4["std"], 1e-9)
    print(f"Signal 4 baseline: mu={mu:.4f}, std={std:.4f}")

    # Load data
    all_positives = []
    all_clean = []
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
            if TIER1_ID_START <= pid <= TIER2_ID_START + 49:
                all_positives.append({"text": text, "pid": pid})
            elif pid <= CLEAN_ID_MAX:
                all_clean.append({"text": text, "pid": pid})

    random.shuffle(all_clean)
    train_clean_pool = all_clean[:300]
    val_pos = all_positives[-10:]
    val_neg = train_clean_pool[:10]
    final_train_pos = all_positives[:90]
    final_train_neg = train_clean_pool[10:]

    train_items = [(t["text"], 1) for t in final_train_pos] + [(t["text"], 0) for t in final_train_neg]
    val_items = [(t["text"], 1) for t in val_pos] + [(t["text"], 0) for t in val_neg]

    # Load models
    print("Loading BERT...")
    bert_tokenizer = DistilBertTokenizerFast.from_pretrained(str(BERT_OUTPUT_DIR))
    bert_model = DistilBertForSequenceClassification.from_pretrained(str(BERT_OUTPUT_DIR))
    bert_model.eval()

    print("Loading GPT-2...")
    gpt2_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    gpt2_tokenizer.pad_token_id = gpt2_tokenizer.eos_token_id
    gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")
    gpt2_model.eval()

    def compute_features(items, default_retrieval_score=0.7):
        X_rows, y_vals = [], []
        for i, (text, label) in enumerate(items):
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(items)}...")
            bp = bert_prob(text, bert_model, bert_tokenizer)
            pz = perplexity_max_nll(text, gpt2_model, gpt2_tokenizer)
            ir = imperative_ratio(text)
            rz = (default_retrieval_score - mu) / std
            X_rows.append([bp, pz, ir, rz])
            y_vals.append(label)
        return np.array(X_rows, dtype=np.float32), np.array(y_vals, dtype=np.int32)

    print(f"Computing features for {len(train_items)} train items...")
    X_train, y_train = compute_features(train_items)
    print(f"Computing features for {len(val_items)} val items...")
    X_val, y_val = compute_features(val_items)

    # Fit scaler and LR
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    lr = LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs",
                            class_weight="balanced", random_state=42)
    lr.fit(X_train_s, y_train)

    print(f"Train acc: {lr.score(X_train_s, y_train):.3f}, Val acc: {lr.score(X_val_s, y_val):.3f}")

    val_probs = lr.predict_proba(X_val_s)[:, 1]
    best_thresh, best_f1 = 0.5, 0.0
    for thresh in np.arange(0.1, 1.0, 0.1):
        y_pred = (val_probs >= thresh).astype(int)
        if len(np.unique(y_pred)) < 2:
            continue
        f1 = f1_score(y_val, y_pred, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = float(thresh)

    print(f"Tuned threshold: {best_thresh:.2f} (F1={best_f1:.3f})")
    print(f"LR coef: {lr.coef_.tolist()}")

    data = {
        "lr_coef": lr.coef_.tolist(),
        "lr_intercept": lr.intercept_.tolist(),
        "lr_classes": lr.classes_.tolist(),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "tuned_threshold": float(best_thresh),
    }
    with open(LR_JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"LR meta-classifier updated at {LR_JSON_PATH}")


if __name__ == "__main__":
    main()
