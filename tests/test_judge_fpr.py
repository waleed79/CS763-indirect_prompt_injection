"""Wave 0 stubs for scripts/run_judge_fpr.py (Phase 5 Plan 02).

Skips until run_judge_fpr.py is implemented. After Plan 02 lands, all 9 tests
must pass. Covers V-01..V-09 from .planning/phases/05-*/05-VALIDATION.md.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
_MODULE_NAME = "run_judge_fpr"
_MODULE_FILE = _SCRIPTS_DIR / "run_judge_fpr.py"

try:
    _spec = importlib.util.spec_from_file_location(_MODULE_NAME, _MODULE_FILE)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    main = _mod.main
    DEFENSE_LOG_MAP = _mod.DEFENSE_LOG_MAP
    TOP_K = _mod.TOP_K
    N_CLEAN = _mod.N_CLEAN
    parse_verdict = _mod.parse_verdict
    _AVAILABLE = True
except (AttributeError, FileNotFoundError):
    # Expected when Plan 02 has not yet landed (script absent) or has not yet
    # exposed all required symbols. Fall through to the skip path silently.
    _AVAILABLE = False
    DEFENSE_LOG_MAP = {}  # placeholder so module loads cleanly during collect-only
    TOP_K = 5
    N_CLEAN = 50
except Exception:
    # WR-06: any other exception (SyntaxError, ImportError, etc.) is a real
    # bug in run_judge_fpr.py — print the traceback so it is not swallowed by
    # the misleading "not yet implemented" skip reason.
    import traceback
    traceback.print_exc()
    _AVAILABLE = False
    DEFENSE_LOG_MAP = {}
    TOP_K = 5
    N_CLEAN = 50

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason="scripts/run_judge_fpr.py not yet implemented (Phase 5 Plan 02)",
)


NEW_KEYS = ("per_chunk_fpr", "answer_preserved_fpr", "judge_fpr", "judge_model", "judge_n_calls")

# IN-01: anchor paths to the repo root so tests are not cwd-sensitive.
# tests/ is one level below the repo root, so parent.parent is the repo root.
_LOGS_DIR = Path(__file__).parent.parent / "logs"


def _load_ablation():
    return json.loads((_LOGS_DIR / "ablation_table.json").read_text())


def _load_verdicts():
    return json.loads((_LOGS_DIR / "judge_fpr_llama.json").read_text())


class TestSchemaExtension:
    def test_schema_extension(self):
        """V-08: each defense row has 5 new keys plus existing keys."""
        ablation = _load_ablation()
        for defense_key in DEFENSE_LOG_MAP:
            row = ablation[defense_key]
            for key in NEW_KEYS:
                assert key in row, f"{defense_key} missing {key}"
        # no_defense gets trivial fill per D-02
        assert "no_defense" in ablation
        for key in NEW_KEYS:
            assert key in ablation["no_defense"], f"no_defense missing {key}"

    def test_back_compat_fpr_unchanged(self, ablation_snapshot):
        """V-09: existing fpr key on every row equals pre-Plan-03 snapshot value."""
        pre = json.loads(ablation_snapshot.read_text())
        post = _load_ablation()
        for defense_key, pre_row in pre.items():
            if "fpr" in pre_row:
                assert post[defense_key]["fpr"] == pre_row["fpr"], (
                    f"fpr key on {defense_key} changed: {pre_row['fpr']} -> {post[defense_key]['fpr']}"
                )


class TestMetricBounds:
    def test_no_defense_zero(self):
        """V-01: no_defense row has all three new metrics == 0 (D-02 trivial fill)."""
        row = _load_ablation()["no_defense"]
        assert row["per_chunk_fpr"] == 0.0
        assert row["answer_preserved_fpr"] == 0.0
        assert row["judge_fpr"] == 0.0
        assert row["judge_n_calls"] == 0

    def test_m1_in_range(self):
        """V-04: 0.0 <= per_chunk_fpr <= 1.0 for all 6 defense rows."""
        ablation = _load_ablation()
        for defense_key in DEFENSE_LOG_MAP:
            m1 = ablation[defense_key]["per_chunk_fpr"]
            assert 0.0 <= m1 <= 1.0, f"{defense_key} M1={m1} out of [0,1]"

    def test_m1_numerator_bounded(self):
        """V-05: M1 numerator <= top_k * 50 = 250 (sanity bound)."""
        ablation = _load_ablation()
        denom = TOP_K * N_CLEAN
        for defense_key, log_fname in DEFENSE_LOG_MAP.items():
            log = json.loads((_LOGS_DIR / log_fname).read_text())
            clean = [r for r in log["results"] if not r.get("paired", False)]
            numerator = sum(r.get("chunks_removed", 0) for r in clean)
            assert numerator <= denom, (
                f"{defense_key} M1 numerator {numerator} > {denom} = top_k * N_clean"
            )

    def test_m2_le_m1(self):
        """V-02: M2 numerator (chunks_removed>0 AND DEGRADED) <= M1 numerator (chunks_removed>0)."""
        verdicts_doc = _load_verdicts()
        for defense_key, log_fname in DEFENSE_LOG_MAP.items():
            log = json.loads((_LOGS_DIR / log_fname).read_text())
            clean = [r for r in log["results"] if not r.get("paired", False)]
            m1_count = sum(1 for r in clean if r.get("chunks_removed", 0) > 0)
            vds = verdicts_doc["verdicts"].get(defense_key, {})
            # Map query_index -> chunks_removed via record order (paired==False subset)
            # Use the verdicts dict's intersection with chunks_removed>0 records.
            chunk_removed_indices = {str(50 + i) for i, r in enumerate(clean) if r.get("chunks_removed", 0) > 0}
            m2_count = sum(
                1 for q_idx, v in vds.items()
                if v.get("verdict") == "DEGRADED" and q_idx in chunk_removed_indices
            )
            assert m2_count <= m1_count, (
                f"{defense_key} M2 count {m2_count} > M1 count {m1_count}"
            )


class TestJudgeConsistency:
    def test_judge_n_calls_min(self):
        """V-03: judge_n_calls >= 50 for each of the 6 defense rows."""
        ablation = _load_ablation()
        for defense_key in DEFENSE_LOG_MAP:
            n_calls = ablation[defense_key]["judge_n_calls"]
            assert n_calls >= 50, f"{defense_key} judge_n_calls={n_calls} < 50"

    def test_m3_consistency(self):
        """V-07: judge_fpr * 50 == count(verdict == DEGRADED) in per-cell file."""
        ablation = _load_ablation()
        verdicts_doc = _load_verdicts()
        for defense_key in DEFENSE_LOG_MAP:
            vds = verdicts_doc["verdicts"][defense_key]
            degraded_count = sum(1 for v in vds.values() if v.get("verdict") == "DEGRADED")
            m3 = ablation[defense_key]["judge_fpr"]
            # WR-05: use the N_CLEAN constant from run_judge_fpr.py instead of a
            # hardcoded 50 so the denominator stays in sync if N_CLEAN changes.
            expected = degraded_count / N_CLEAN
            assert abs(m3 - expected) < 1e-9, (
                f"{defense_key} judge_fpr={m3} disagrees with per-cell DEGRADED count {degraded_count}/{N_CLEAN}={expected}"
            )

    def test_idempotent_with_cache(self, frozen_judge_cache, tmp_path, monkeypatch):
        """V-06: re-running main() with cached verdicts produces byte-identical ablation_table.json."""
        # Snapshot pre-state, run main with frozen cache, snapshot post-state, run again, compare.
        # IN-02: explicit utf-8 on read+write so round-trip cannot corrupt the production file.
        ablation_path = _LOGS_DIR / "ablation_table.json"
        pre = ablation_path.read_text(encoding="utf-8")
        try:
            rc1 = main(["--cache", str(frozen_judge_cache), "--delay", "0"])
            assert rc1 == 0
            post1 = ablation_path.read_text(encoding="utf-8")
            rc2 = main(["--cache", str(frozen_judge_cache), "--delay", "0"])
            assert rc2 == 0
            post2 = ablation_path.read_text(encoding="utf-8")
            assert post1 == post2, "Re-run with cache produced different ablation_table.json"
        finally:
            # Restore pre-test state
            ablation_path.write_text(pre, encoding="utf-8")
