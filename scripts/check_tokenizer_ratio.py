#!/usr/bin/env python3
"""Tokenizer ratio spot-check script (Plan 02.1-01 verification gate).

Verifies that the whitespace token/wordpiece-token ratio for the
all-MiniLM-L6-v2 embedding model stays within expected bounds (0.5 – 2.5x),
confirming that our 256-token chunk budget is reasonable.

Usage
-----
    python scripts/check_tokenizer_ratio.py

Exit codes
----------
0 — all checks passed
1 — ratio out of bounds for any sample
"""
from __future__ import annotations

import sys

SAMPLES = [
    # (label, text)
    (
        "short_sentence",
        "What is retrieval-augmented generation?",
    ),
    (
        "medium_paragraph",
        (
            "Retrieval-Augmented Generation (RAG) combines a retrieval system "
            "with a generative language model. The retriever finds relevant "
            "documents from a knowledge corpus, and the generator uses those "
            "documents as context to produce a grounded answer."
        ),
    ),
    (
        "dense_technical",
        (
            "Adversarial corpus poisoning for indirect prompt injection exploits "
            "the semantic retrieval step: a maliciously crafted document is "
            "embedded close to legitimate query embeddings, thereby hijacking "
            "the context window supplied to the language model and causing it "
            "to execute attacker-controlled instructions instead of answering "
            "the user's question."
        ),
    ),
    (
        "whitespace_heavy",
        " ".join(["token"] * 100),
    ),
]

RATIO_MIN = 0.5
RATIO_MAX = 2.5


def main() -> int:
    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("ERROR: transformers not installed in this environment.", file=sys.stderr)
        return 1

    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Loading tokenizer: {model_name} …", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print(f"Tokenizer loaded: {tokenizer.__class__.__name__}\n")

    header = f"{'Sample':<25} {'WS tokens':>10} {'WP tokens':>10} {'Ratio':>8}  {'Status'}"
    print(header)
    print("-" * len(header))

    all_ok = True
    for label, text in SAMPLES:
        ws_tokens = len(text.split())
        wp_tokens = len(tokenizer.encode(text, add_special_tokens=False))
        ratio = wp_tokens / ws_tokens if ws_tokens > 0 else float("inf")
        ok = RATIO_MIN <= ratio <= RATIO_MAX
        status = "OK" if ok else f"FAIL (expected {RATIO_MIN}-{RATIO_MAX}x)"
        print(f"{label:<25} {ws_tokens:>10} {wp_tokens:>10} {ratio:>8.2f}  {status}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print(
            "[PASS] All ratios within expected bounds -- "
            "256-token chunk budget is sound."
        )
        return 0
    else:
        print(
            "[FAIL] One or more ratios out of bounds -- "
            "review chunk_size parameter."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
