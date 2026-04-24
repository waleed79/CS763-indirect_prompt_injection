"""One-shot Signal 4 canary baseline calibration using nq_poisoned_v4 collection.

Run after train_defense.py if Ollama was unavailable during training.
Overwrites models/signal4_baseline.json with real calibration data.
"""
import dataclasses
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.constants import TIER1_ID_START  # IN-05: single source of truth

CORPUS_PATH = Path("data/corpus_poisoned.jsonl")
QUERIES_PATH = Path("data/test_queries.json")
SIGNAL4_JSON_PATH = Path("models/signal4_baseline.json")


def main():
    from rag.config import load_config
    from rag.pipeline import RAGPipeline

    with open(QUERIES_PATH, encoding="utf-8") as f:
        queries = json.load(f)
    # Canary queries: indices 50-99 (paired=False), key is 'query'
    canary_queries = [
        q.get("query") or q.get("question", "")
        for i, q in enumerate(queries)
        if i >= 50 and q.get("paired") is False
    ]
    canary_queries = [q for q in canary_queries if q]
    print(f"Canary queries: {len(canary_queries)}")

    cfg = load_config()
    eval_cfg = dataclasses.replace(cfg, collection="nq_poisoned_v4")
    pipeline = RAGPipeline(eval_cfg)
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
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(canary_queries)} queries, {len(scores)} scores so far")

    try:
        pipeline.close()
    except Exception:
        pass

    if not scores:
        print("No scores collected. Is Ollama running and nq_poisoned_v4 collection built?")
        return

    mu = float(np.mean(scores))
    std = float(np.std(scores))
    if std < 1e-9:
        std = 0.1

    baseline = {"mu": mu, "std": std}
    SIGNAL4_JSON_PATH.write_text(json.dumps(baseline, indent=2))
    print(f"Signal 4 baseline: mu={mu:.4f}, std={std:.4f} (n={len(scores)} scores)")
    print(f"Saved to {SIGNAL4_JSON_PATH}")


if __name__ == "__main__":
    main()
