"""ATK-02: Poisoning ratio sweep driver.

Generates 5 poisoned corpus files, one per ratio in {0.5%, 1%, 2%, 5%, 10%}.
Each file contains the full clean corpus plus a Tier-1 subset sized by
math.ceil(ratio * n_clean) — PoisonedRAG adversary-favoring convention.

Output filenames: data/corpus_ratio_{0005, 0010, 0020, 0050, 0100}.jsonl

Run with:
    python scripts/run_ratio_sweep.py
"""
from __future__ import annotations

import math
import sys
from dataclasses import replace as dc_replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.corpus import load_passages_from_jsonl, persist_passages
from rag.constants import TIER2_ID_START, ATK02_SWEEP_ID_START
from scripts.generate_poisoned_corpus import build_poisoned_passages

# PoisonedRAG-standard ratio sweep (5 points)
RATIOS: list[float] = [0.005, 0.01, 0.02, 0.05, 0.10]

CLEAN_PATH: str = "data/corpus_clean.jsonl"


def _tier1_only(all_poisoned):
    """Filter build_poisoned_passages() output to Tier-1 entries only,
    then extend the pool for the 10% sweep (100 docs) by cycling with
    unique IDs from the ATK02_SWEEP_ID_START reserved band (21000-21049).

    ID layout after cycling:
      cycle 0: original IDs 20000-20049 (Tier-1 range)
      cycle 1: extension IDs 21000-21049 (ATK02_SWEEP_ID_START band —
               above all existing tier ranges, no collision with
               T2 20050-20099 or T3 20100-20149)
    """
    tier1 = [p for p in all_poisoned if p.passage_id < TIER2_ID_START]
    # Replicate pool for 10% sweep (100 docs > 50 base).
    extended = []
    for cycle in range(2):  # 0, 1 — enough for 100 docs from a 50-pool
        for p in tier1:
            if cycle == 0:
                new_id = p.passage_id          # 20000-20049: original Tier-1 IDs
            else:
                # ATK02_SWEEP_ID_START + offset keeps these above all existing tiers
                offset = p.passage_id - 20000  # 0..49
                new_id = ATK02_SWEEP_ID_START + offset  # 21000-21049
            extended.append(dc_replace(p, passage_id=new_id))
    return extended


def main() -> None:
    clean = load_passages_from_jsonl(CLEAN_PATH)
    n_clean = len(clean)
    print(f"Loaded {n_clean} clean passages from {CLEAN_PATH}")

    all_tier1 = _tier1_only(build_poisoned_passages())
    print(f"Tier-1 pool: {len(all_tier1)} passages available")

    for ratio in RATIOS:
        # math.ceil = adversary-favoring rounding (PoisonedRAG convention)
        n_poison = math.ceil(ratio * n_clean)
        if n_poison > len(all_tier1):
            raise ValueError(
                f"Ratio {ratio} requires {n_poison} poisoned docs but Tier-1 pool "
                f"only has {len(all_tier1)}. Extend TIER1_OPENERS / TIER1_INJECTIONS."
            )
        subset = all_tier1[:n_poison]
        # Naming: int(0.005 * 1000) = 5 -> "0005"; int(0.10 * 1000) = 100 -> "0100"
        out_path = f"data/corpus_ratio_{int(ratio * 1000):04d}.jsonl"
        n_written = persist_passages(clean + subset, out_path)
        print(f"  {ratio*100:>5.1f}% -> {n_poison:>3d} poisoned docs -> {out_path} ({n_written} total lines)")


if __name__ == "__main__":
    main()
