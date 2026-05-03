"""Demo script for presentation GIF recording.

Shows two queries side-by-side:
  1. Clean query  -> normal factual answer
  2. Poisoned query -> hijacked answer containing attacker payload

Usage:
    conda run -n rag-security python scripts/run_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.config import load_config
from rag.pipeline import RAGPipeline, set_global_seed

COLLECTION = "nq_poisoned_v4"
CORPUS = "data/corpus_poisoned.jsonl"
MODEL = "mistral:7b"

QUERIES = [
    ("CLEAN",    "What is the capital of France?"),
    ("POISONED", "Who wrote Hamlet?"),
]

SEP = "=" * 60


def main() -> None:
    cfg = load_config()
    import dataclasses
    cfg = dataclasses.replace(cfg, collection=COLLECTION, llm_model=MODEL)
    set_global_seed(cfg.seed)

    pipeline = RAGPipeline(cfg)
    print(f"\nBuilding RAG pipeline (collection: {COLLECTION}, model: {MODEL}) ...")
    pipeline.build(corpus_path=CORPUS)
    print("Pipeline ready.\n")

    for label, query in QUERIES:
        print(SEP)
        print(f"[{label}] Q: {query}")
        print(SEP)
        result = pipeline.query(query)
        answer = result["answer"].strip()
        print(f"A: {answer}")
        print()

    print(SEP)
    print("Demo complete.")
    print(SEP)


if __name__ == "__main__":
    main()
