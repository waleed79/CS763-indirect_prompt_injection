"""Build the clean retrieval corpus from MS-MARCO passages.

Downloads the first 1000 passages from the MS-MARCO v1.1 dataset and saves
them to data/corpus_clean.jsonl in the same JSONL format as data/nq_500.jsonl.

Each line: {"passage_id": int, "query": str, "text": str}

Usage:
    python scripts/build_corpus.py

If MS-MARCO is unavailable (network error), falls back to duplicating
data/nq_500.jsonl to produce 1000 entries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running from the repo root without installing the package.
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.corpus import Passage, load_passages_from_jsonl, persist_passages

TARGET_COUNT = 1000
OUTPUT_PATH = "data/corpus_clean.jsonl"
FALLBACK_PATH = "data/nq_500.jsonl"


def build_from_msmarco(n: int = TARGET_COUNT) -> list[Passage]:
    """Load n passages from MS-MARCO v1.1 train split via HuggingFace datasets."""
    from datasets import load_dataset

    print("Downloading MS-MARCO v1.1 (train split) from HuggingFace …")
    ds = load_dataset("ms_marco", "v1.1", split="train", trust_remote_code=True)

    passages: list[Passage] = []
    for i, row in enumerate(ds):
        if len(passages) >= n:
            break
        # Each row has: query (str), passages (dict with passage_text list)
        query_text: str = row.get("query", "") or ""
        passage_texts = row.get("passages", {}).get("passage_text", [])
        for pt in passage_texts:
            if len(passages) >= n:
                break
            text = pt.strip()
            if text:
                passages.append(
                    Passage(
                        passage_id=len(passages),
                        query=query_text,
                        text=text,
                    )
                )

    print(f"  Loaded {len(passages)} passages from MS-MARCO.")
    return passages


def build_from_fallback(n: int = TARGET_COUNT) -> list[Passage]:
    """Duplicate data/nq_500.jsonl until we have n passages (fallback path)."""
    print(f"Falling back to duplicating {FALLBACK_PATH} …")
    base = load_passages_from_jsonl(FALLBACK_PATH)
    if not base:
        raise RuntimeError(f"Fallback corpus {FALLBACK_PATH} is empty or missing.")

    passages: list[Passage] = []
    idx = 0
    while len(passages) < n:
        src = base[idx % len(base)]
        passages.append(
            Passage(
                passage_id=len(passages),
                query=src.query,
                text=src.text,
            )
        )
        idx += 1

    print(f"  Built {len(passages)} passages via fallback duplication.")
    return passages


def main() -> None:
    passages: list[Passage] = []

    try:
        passages = build_from_msmarco(TARGET_COUNT)
    except Exception as exc:
        print(f"MS-MARCO download failed: {exc}")
        print("Switching to fallback …")
        passages = build_from_fallback(TARGET_COUNT)

    if len(passages) < TARGET_COUNT:
        print(
            f"WARNING: Only {len(passages)} passages available; "
            f"expected {TARGET_COUNT}. Padding via fallback …"
        )
        extra = build_from_fallback(TARGET_COUNT - len(passages))
        # Re-number extra passages to continue from where we left off
        offset = len(passages)
        extra = [
            Passage(passage_id=offset + p.passage_id, query=p.query, text=p.text)
            for p in extra
        ]
        passages.extend(extra)

    # Final trim to exactly TARGET_COUNT
    passages = passages[:TARGET_COUNT]

    out = persist_passages(passages, OUTPUT_PATH)
    print(f"\nWrote {len(passages)} passages to {out}")


if __name__ == "__main__":
    main()
