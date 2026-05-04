"""Phase 5 fixtures: ablation snapshot + frozen judge cache.

First conftest.py in this repo. Provides fixtures needed by
tests/test_judge_fpr.py for V-06 (idempotency) and V-09 (back-compat) tests
without mutating the real logs/ablation_table.json or burning cloud-LLM calls.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

# Mirror DEFENSE_LOG_MAP keys from scripts/run_judge_fpr.py (RESEARCH §3).
# Kept in sync manually; if Plan 02 changes the keys, update this list.
_DEFENSE_KEYS = [
    "def02",
    "bert_only",
    "perplexity_only",
    "imperative_only",
    "fingerprint_only",
    "fused_fixed_0.5",
    "fused_tuned_threshold",
]
_N_CLEAN = 50  # indices 50-99 in defense logs (paired==False)

# IN-01: anchor paths to the repo root so fixtures are not cwd-sensitive.
# tests/ is one level below the repo root, so parent.parent is the repo root.
_REPO_ROOT = Path(__file__).parent.parent


@pytest.fixture
def ablation_snapshot(tmp_path):
    """Copy of logs/ablation_table.json in tmp_path; tests can mutate freely."""
    src = _REPO_ROOT / "logs" / "ablation_table.json"
    if not src.exists():
        pytest.skip("logs/ablation_table.json not present in working tree")
    dst = tmp_path / "ablation_table.json"
    shutil.copy(src, dst)
    return dst


@pytest.fixture
def frozen_judge_cache(tmp_path):
    """Pre-populated judge cache so V-06 idempotency test makes zero cloud calls.

    Builds a minimal valid cache: each defense key maps to a dict of query
    indices (as strings) -> verdict_record. All verdicts are PRESERVED so
    downstream metrics are deterministic and the cache loader can short-circuit.
    """
    cache_path = tmp_path / "judge_fpr_llama.json.cache"
    cache = {}
    for defense_key in _DEFENSE_KEYS:
        cache[defense_key] = {
            str(50 + i): {
                "verdict": "PRESERVED",
                "ab_assignment": "off=A,on=B",
                "raw_response": "PRESERVED",
                "retry_count": 0,
            }
            for i in range(_N_CLEAN)
        }
    # IN-02: explicit utf-8 so Windows cp1252 default cannot corrupt non-ASCII content.
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return cache_path
