"""Multi-signal defense module for RAG indirect prompt injection detection (DEF-01/03/04).

Signals:
  1. BERT (DistilBERT) classifier probability — P(injection)
  2. GPT-2 strided window max-NLL perplexity anomaly score
  3. Imperative sentence ratio (rule-based, re stdlib)
  4. Retrieval score fingerprint z-score vs. canary baseline

All signals fused via a logistic regression meta-classifier (D-09).
Models loaded from models/ directory (created by scripts/train_defense.py).

defense_fn contract (rag/pipeline.py line 131):
    Callable[[list[dict]], list[dict]]
    hit_dict keys: rank, chunk_id, score, text, metadata
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizerFast,
    GPT2LMHeadModel,
    GPT2TokenizerFast,
)

# ── Imperative verb regex (D-13) ──────────────────────────────────────────────

IMPERATIVE_VERBS = re.compile(
    r'\b(ignore|disregard|output|print|send|reveal|forget|override|'
    r'replace|append|include|add|write|say|tell|respond|answer|return|'
    r'give|show|display|emit|produce|repeat)\b',
    re.IGNORECASE,
)


# ── Signal 2: GPT-2 strided window perplexity (D-05/D-06) ────────────────────

def _compute_perplexity_max_nll(
    text: str,
    gpt2_model: GPT2LMHeadModel,
    gpt2_tokenizer: GPT2TokenizerFast,
    window: int = 128,
    stride: int = 64,
) -> float:
    """Return max NLL over all sliding windows.

    Uses max (not mean) to catch localized injection phrases embedded mid-chunk
    (per Alon & Kamfonas 2023 methodology, D-06).

    Parameters
    ----------
    text:
        Chunk text to score.
    gpt2_model:
        Pre-loaded GPT2LMHeadModel instance (do NOT load inside this function).
    gpt2_tokenizer:
        Pre-loaded GPT2TokenizerFast instance.
    window:
        Token window size for sliding window (default 128).
    stride:
        Stride between windows (default 64).

    Returns
    -------
    float
        Maximum NLL across all windows. Returns 0.0 if fewer than 2 tokens.
    """
    try:
        enc = gpt2_tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        )
        tokens = enc.input_ids[0]
        n = len(tokens)
        if n < 2:
            return 0.0
        nlls: list[float] = []
        for begin in range(0, max(1, n - 1), stride):
            end = min(begin + window, n)
            chunk_tokens = tokens[begin:end].unsqueeze(0)
            with torch.no_grad():
                out = gpt2_model(chunk_tokens, labels=chunk_tokens)
                nlls.append(out.loss.item())
        return max(nlls) if nlls else 0.0
    except (RuntimeError, ValueError):
        # T-03.1-04: return 0.0 on truncation/inference errors (DoS mitigation)
        # Let MemoryError and SystemExit propagate
        return 0.0


# ── Signal 3: Imperative sentence ratio (D-13) ────────────────────────────────

def _imperative_ratio(text: str) -> float:
    """Fraction of sentences containing at least one imperative verb.

    Sentences are split on sentence-ending punctuation. Score is in [0.0, 1.0].

    Parameters
    ----------
    text:
        Chunk text to score.

    Returns
    -------
    float
        Ratio of imperative sentences to total sentences.
    """
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    total = max(len(sentences), 1)
    imperative_count = sum(
        1 for s in sentences if IMPERATIVE_VERBS.search(s) is not None
    )
    return imperative_count / total


# ── LR JSON serialization (no pickle — anti-pickle requirement) ───────────────

def _load_lr_from_json(path: str) -> tuple[LogisticRegression, StandardScaler]:
    """Load a trained LogisticRegression + StandardScaler from a JSON file.

    The JSON file must contain the keys: lr_coef, lr_intercept, lr_classes,
    scaler_mean, scaler_scale. Raises FileNotFoundError if path does not exist.

    Parameters
    ----------
    path:
        Path to the JSON artifact (e.g. models/lr_meta_classifier.json).

    Returns
    -------
    tuple[LogisticRegression, StandardScaler]
        Reconstructed classifier and scaler, ready for .predict_proba() and
        .transform() calls respectively.

    Raises
    ------
    FileNotFoundError
        If the JSON file does not exist at path.
    ValueError
        If the JSON does not contain the expected keys or the coef_ shape does
        not match the expected 4 features (T-03.1-03).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"LR meta-classifier not found at {path}. "
            "Run scripts/train_defense.py first."
        )
    with open(p) as f:
        data = json.load(f)

    lr = LogisticRegression()
    lr.coef_ = np.array(data["lr_coef"])
    lr.intercept_ = np.array(data["lr_intercept"])
    lr.classes_ = np.array(data["lr_classes"])

    # T-03.1-03: Validate that coef_ shape matches expected 4 features
    if lr.coef_.shape[1] != 4:
        raise ValueError(
            f"LR coef_ expected shape (*, 4) but got {lr.coef_.shape}. "
            "Artifact may be from an incompatible model version."
        )

    scaler = StandardScaler()
    scaler.mean_ = np.array(data["scaler_mean"])
    scaler.scale_ = np.array(data["scaler_scale"])

    return lr, scaler


# ── FusedDefense ──────────────────────────────────────────────────────────────

class FusedDefense:
    """4-signal ensemble defense fused via logistic regression meta-classifier.

    Implements the defense_fn contract from rag/pipeline.py line 131:
        Callable[[list[dict]], list[dict]]

    All models are loaded once at __init__ time (never per-chunk). See RESEARCH.md
    Pitfall 1 for the performance rationale.

    Parameters
    ----------
    models_dir:
        Directory containing bert_classifier/, lr_meta_classifier.json, and
        signal4_baseline.json (output of scripts/train_defense.py).
    threshold:
        Injection probability threshold for hard removal (D-12). Default 0.5.

    Raises
    ------
    FileNotFoundError
        If any required model artifact is missing in models_dir.
    """

    def __init__(self, models_dir: str = "models", threshold: float = 0.5) -> None:
        self.threshold = threshold
        self._models_dir = Path(models_dir)
        self._load_bert()
        self._load_gpt2()
        self._load_lr()
        self._load_signal4_baseline()

    # ── Model loading ─────────────────────────────────────────────────────────

    def _load_bert(self) -> None:
        """Load DistilBERT tokenizer and classifier from models_dir/bert_classifier/."""
        bert_dir = self._models_dir / "bert_classifier"
        config_path = bert_dir / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(
                f"BERT classifier not found at {bert_dir}. "
                "Run scripts/train_defense.py first."
            )
        self._bert_tokenizer: DistilBertTokenizerFast = (
            DistilBertTokenizerFast.from_pretrained(str(bert_dir))
        )
        self._bert_model: DistilBertForSequenceClassification = (
            DistilBertForSequenceClassification.from_pretrained(str(bert_dir))
        )
        self._bert_model.eval()

    def _load_gpt2(self) -> None:
        """Load GPT-2 small from HuggingFace cache (zero download if already cached)."""
        self._gpt2_tokenizer: GPT2TokenizerFast = GPT2TokenizerFast.from_pretrained(
            "gpt2"
        )
        # Suppress "Setting `pad_token_id` to `eos_token_id`" warning
        self._gpt2_tokenizer.pad_token_id = self._gpt2_tokenizer.eos_token_id
        self._gpt2_model: GPT2LMHeadModel = GPT2LMHeadModel.from_pretrained("gpt2")
        self._gpt2_model.eval()

    def _load_lr(self) -> None:
        """Load LR meta-classifier and StandardScaler from JSON artifact."""
        lr_path = str(self._models_dir / "lr_meta_classifier.json")
        self._lr, self._scaler = _load_lr_from_json(lr_path)

    def _load_signal4_baseline(self) -> None:
        """Load retrieval score baseline (mu, std) for Signal 4 z-score."""
        baseline_path = self._models_dir / "signal4_baseline.json"
        if not baseline_path.exists():
            raise FileNotFoundError(
                f"Signal 4 baseline not found at {baseline_path}. "
                "Run scripts/train_defense.py first."
            )
        with open(baseline_path) as f:
            self._s4_baseline: dict = json.load(f)

    # ── Per-signal extractors ─────────────────────────────────────────────────

    def _bert_prob(self, text: str) -> float:
        """Return P(injection) from DistilBERT classifier.

        Parameters
        ----------
        text:
            Chunk text to classify.

        Returns
        -------
        float
            Probability of injection class (index 1), in [0.0, 1.0].
        """
        inputs = self._bert_tokenizer(
            text,
            truncation=True,
            max_length=256,
            return_tensors="pt",
        )
        with torch.no_grad():
            logits = self._bert_model(**inputs).logits[0]
        probs = torch.softmax(logits, dim=-1)
        return float(probs[1].item())

    def _perplexity_z(self, text: str) -> float:
        """Return max-window NLL from GPT-2 strided window perplexity (Signal 2).

        The "z" naming reflects how it is used as a feature for the LR meta-
        classifier (raw NLL; StandardScaler normalises it before LR fit).
        """
        return _compute_perplexity_max_nll(
            text, self._gpt2_model, self._gpt2_tokenizer
        )

    def _imperative_ratio_score(self, text: str) -> float:
        """Return imperative sentence ratio (Signal 3)."""
        return _imperative_ratio(text)

    def _retrieval_z(self, score: float) -> float:
        """Return z-score of retrieval score vs. canary baseline (Signal 4)."""
        mu = self._s4_baseline.get("mu", 0.0)
        std = self._s4_baseline.get("std", 1.0)
        return (score - mu) / max(std, 1e-9)

    # ── Public API ────────────────────────────────────────────────────────────

    def score(self, chunk: dict) -> dict:
        """Return all 4 raw signal scores for a chunk.

        Parameters
        ----------
        chunk:
            hit_dict from pipeline.py with keys: rank, chunk_id, score, text,
            metadata. All keys accessed via .get() for safety (T-03.1-05).

        Returns
        -------
        dict with keys: bert_prob, perplexity_z, imperative_ratio, retrieval_z
            All values are floats.
        """
        text = chunk.get("text", "")
        retrieval_score = chunk.get("score", 0.0)
        return {
            "bert_prob": self._bert_prob(text),
            "perplexity_z": self._perplexity_z(text),
            "imperative_ratio": self._imperative_ratio_score(text),
            "retrieval_z": self._retrieval_z(retrieval_score),
        }

    def _is_injection(self, chunk: dict) -> bool:
        """Return True if chunk is classified as an injection.

        Applies LR meta-classifier to the 4-signal feature vector.
        """
        scores = self.score(chunk)
        features = np.array([[
            scores["bert_prob"],
            scores["perplexity_z"],
            scores["imperative_ratio"],
            scores["retrieval_z"],
        ]])
        features_scaled = self._scaler.transform(features)
        inject_prob = float(self._lr.predict_proba(features_scaled)[0, 1])
        return inject_prob > self.threshold

    def filter(self, chunks: list[dict]) -> list[dict]:
        """Filter injection chunks from a list of retrieved chunks.

        Implements the defense_fn contract from rag/pipeline.py line 131:
            Callable[[list[dict]], list[dict]]

        Parameters
        ----------
        chunks:
            List of hit_dicts from the retriever.

        Returns
        -------
        list[dict]
            Filtered list with injected chunks removed (hard removal per D-12).
        """
        return [c for c in chunks if not self._is_injection(c)]


# ── SingleSignalDefense ───────────────────────────────────────────────────────

class SingleSignalDefense:
    """Single-signal defense for ablation experiments (DEF-04).

    Applies only one of the 4 signals with a fixed threshold. Implements the
    same defense_fn contract as FusedDefense.

    Parameters
    ----------
    signal:
        One of 'bert', 'perplexity', 'imperative', 'fingerprint'.
    models_dir:
        Directory containing model artifacts. Only loaded if the selected
        signal requires model files.
    threshold:
        Override the signal-specific default threshold. None = use default.

    Raises
    ------
    ValueError
        If signal is not one of VALID_SIGNALS.
    FileNotFoundError
        If the signal requires model artifacts that are missing.
    """

    VALID_SIGNALS = ("bert", "perplexity", "imperative", "fingerprint")

    # Signal-specific default thresholds (from RESEARCH.md signal performance data)
    _DEFAULT_THRESHOLDS = {
        "bert": 0.5,
        "perplexity": 4.5,  # NLL threshold: T1=4.64, T2=5.33, clean=4.49
        "imperative": 0.1,  # Any imperative sentence = flagged
        "fingerprint": 2.0,  # z-score of 2.0 catches targeted poison
    }

    def __init__(
        self,
        signal: str,
        models_dir: str = "models",
        threshold: float | None = None,
    ) -> None:
        if signal not in self.VALID_SIGNALS:
            raise ValueError(
                f"signal must be one of {self.VALID_SIGNALS}, got {signal!r}"
            )
        self.signal = signal
        self._models_dir = Path(models_dir)
        self._threshold = threshold
        self._default_threshold = self._DEFAULT_THRESHOLDS[signal]
        self._init_signal()

    def _init_signal(self) -> None:
        """Conditionally load only what this signal needs."""
        if self.signal == "bert":
            bert_dir = self._models_dir / "bert_classifier"
            config_path = bert_dir / "config.json"
            if not config_path.exists():
                raise FileNotFoundError(
                    f"BERT classifier not found at {bert_dir}. "
                    "Run scripts/train_defense.py first."
                )
            self._bert_tokenizer: DistilBertTokenizerFast = (
                DistilBertTokenizerFast.from_pretrained(str(bert_dir))
            )
            self._bert_model: DistilBertForSequenceClassification = (
                DistilBertForSequenceClassification.from_pretrained(str(bert_dir))
            )
            self._bert_model.eval()

        elif self.signal == "perplexity":
            self._gpt2_tokenizer: GPT2TokenizerFast = (
                GPT2TokenizerFast.from_pretrained("gpt2")
            )
            self._gpt2_tokenizer.pad_token_id = (
                self._gpt2_tokenizer.eos_token_id
            )
            self._gpt2_model: GPT2LMHeadModel = (
                GPT2LMHeadModel.from_pretrained("gpt2")
            )
            self._gpt2_model.eval()

        elif self.signal == "imperative":
            # No model files needed — pure regex (D-13)
            pass

        elif self.signal == "fingerprint":
            baseline_path = self._models_dir / "signal4_baseline.json"
            if not baseline_path.exists():
                raise FileNotFoundError(
                    f"Signal 4 baseline not found at {baseline_path}. "
                    "Run scripts/train_defense.py first."
                )
            with open(baseline_path) as f:
                self._s4_baseline: dict = json.load(f)

    def _score_single(self, chunk: dict) -> float:
        """Return only the relevant signal score for this chunk.

        All chunk accesses use .get() with defaults (T-03.1-05).
        """
        text = chunk.get("text", "")
        retrieval_score = chunk.get("score", 0.0)

        if self.signal == "bert":
            inputs = self._bert_tokenizer(
                text,
                truncation=True,
                max_length=256,
                return_tensors="pt",
            )
            with torch.no_grad():
                logits = self._bert_model(**inputs).logits[0]
            probs = torch.softmax(logits, dim=-1)
            return float(probs[1].item())

        elif self.signal == "perplexity":
            return _compute_perplexity_max_nll(
                text, self._gpt2_model, self._gpt2_tokenizer
            )

        elif self.signal == "imperative":
            return _imperative_ratio(text)

        elif self.signal == "fingerprint":
            mu = self._s4_baseline.get("mu", 0.0)
            std = self._s4_baseline.get("std", 1.0)
            return (retrieval_score - mu) / max(std, 1e-9)

        return 0.0  # unreachable but satisfies type checker

    def filter(self, chunks: list[dict]) -> list[dict]:
        """Filter injection chunks using only the selected signal.

        Implements the defense_fn contract from rag/pipeline.py line 131:
            Callable[[list[dict]], list[dict]]

        Parameters
        ----------
        chunks:
            List of hit_dicts from the retriever.

        Returns
        -------
        list[dict]
            Filtered list with chunks scoring above threshold removed.
        """
        effective_threshold = (
            self._threshold
            if self._threshold is not None
            else self._default_threshold
        )
        return [c for c in chunks if self._score_single(c) < effective_threshold]
