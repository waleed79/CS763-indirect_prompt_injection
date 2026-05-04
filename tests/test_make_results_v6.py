"""Wave 0 stub for Phase 6 make_results.py extensions.

Tests path resolver (_v6.json preferred), disclosure header injection,
and _v6.csv companion emission. Skips until Wave 3 edits land.
"""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
try:
    _spec = importlib.util.spec_from_file_location(
        "make_results", _SCRIPTS_DIR / "make_results.py"
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    main = _mod.main
    _AVAILABLE = True
except (AttributeError, FileNotFoundError):
    _AVAILABLE = False
except Exception:
    import traceback
    traceback.print_exc()
    _AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason="scripts/make_results.py not importable",
)

# _V6_AVAILABLE is True only when Wave 3 has added Phase 6 v6 support to make_results.py.
# Wave 3 must expose a PHASE6_DISCLOSURE constant (or _resolve_v6_path) for this flag to flip.
_V6_AVAILABLE: bool = (
    _AVAILABLE and (
        hasattr(_mod, "PHASE6_DISCLOSURE") or hasattr(_mod, "_resolve_v6_path")
    )
) if _AVAILABLE else False

# Sentinel used in per-method @pytest.mark.skipif decorators below.
_SKIP_V6 = pytest.mark.skipif(
    not _V6_AVAILABLE,
    reason="scripts/make_results.py Phase 6 v6 extensions not yet implemented (Wave 3)",
)

# Phase-6 v6 disclosure header literal — should also appear as module
# constant inside scripts/make_results.py once Wave 3 lands. Test asserts on substring.
PHASE6_DISCLOSURE_SUBSTR = "Updated 2026-05-04: Phase 6 cross-LLM gap fill"


def _stage_minimal_inputs(tmp_path: Path) -> tuple[Path, Path]:
    """Stage minimum logs/ and ablation/matrix files so main() runs end-to-end."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    # Minimal ablation
    ablation = {"no_defense": {"asr_tier1": 0.05, "asr_tier2": 0.10}}
    (logs_dir / "ablation_table.json").write_text(
        json.dumps(ablation), encoding="utf-8"
    )
    # Minimal matrix
    eval_matrix_dir = logs_dir / "eval_matrix"
    eval_matrix_dir.mkdir(exist_ok=True)
    (eval_matrix_dir / "_summary.json").write_text(
        json.dumps([{"model": "llama3.2_3b", "defense": "no_defense", "tier": "tier1",
                     "asr_overall": 0.0, "asr_tier_native": 0.0,
                     "fpr": 0.0, "retrieval_rate": 0.0}]),
        encoding="utf-8",
    )
    return logs_dir, out_dir


# --- P6-RES-PR: path resolver --------------------------------------------
class TestPathResolver:
    """P6-RES-PR: prefer _v6.json over un-versioned when present."""

    @_SKIP_V6
    def test_v6_preferred_when_present(self, tmp_path):
        logs_dir, out_dir = _stage_minimal_inputs(tmp_path)
        # Stage BOTH versioned and un-versioned for gptoss20b
        (logs_dir / "eval_harness_undefended_gptoss20b.json").write_text(
            json.dumps({
                "phase": "02.3", "llm_model": "gpt-oss:20b-cloud",
                "n_queries": 100, "aggregate": {
                    "asr_tier1": 0.0, "asr_tier2": 0.5,
                    "retrieval_rate": 0.86,
                }
            }),
            encoding="utf-8",
        )
        (logs_dir / "eval_harness_undefended_gptoss20b_v6.json").write_text(
            json.dumps({
                "phase": "06", "llm_model": "gpt-oss:20b-cloud",
                "supersedes_phase_02_3": True, "n_queries": 100,
                "collection": "nq_poisoned_v4",
                "aggregate": {
                    "asr_tier1": 0.10, "asr_tier1b": 0.20,
                    "asr_tier2": 0.30, "asr_tier3": 0.40,
                    "asr_tier4": 0.50, "retrieval_rate": 0.88,
                    "error_count": 0,
                },
            }),
            encoding="utf-8",
        )
        rc = main(["--logs-dir", str(logs_dir), "--output-dir", str(out_dir)])
        assert rc == 0
        md = (out_dir / "undefended_baseline.md").read_text(encoding="utf-8")
        # _v6 number 0.40 (asr_tier3) MUST appear; un-versioned would have shown nothing
        assert "0.40" in md, "v6 numbers not surfaced — resolver did not prefer _v6.json"

    @_SKIP_V6
    def test_v6_summary_preferred_when_present(self, tmp_path):
        logs_dir, out_dir = _stage_minimal_inputs(tmp_path)
        # Stage BOTH _summary.json and _summary_v6.json
        (logs_dir / "eval_matrix" / "_summary_v6.json").write_text(
            json.dumps([
                {"model": "gpt-oss_20b-cloud", "defense": "fused", "tier": "tier1",
                 "asr_overall": 0.99, "asr_tier_native": 0.99,
                 "fpr": 0.0, "retrieval_rate": 1.0},
            ]),
            encoding="utf-8",
        )
        rc = main(["--logs-dir", str(logs_dir), "--output-dir", str(out_dir)])
        assert rc == 0
        md = (out_dir / "cross_model_matrix.md").read_text(encoding="utf-8")
        # 0.99 only appears in _summary_v6.json — assert resolver picked it up
        assert "0.99" in md, "v6 summary not surfaced — resolver did not prefer _summary_v6.json"


# --- P6-MD: disclosure header --------------------------------------------
class TestMarkdownDisclosure:
    """P6-MD: regenerated .md files include the dated disclosure header."""

    @_SKIP_V6
    def test_undefended_baseline_disclosure_present(self, tmp_path):
        logs_dir, out_dir = _stage_minimal_inputs(tmp_path)
        rc = main(["--logs-dir", str(logs_dir), "--output-dir", str(out_dir)])
        assert rc == 0
        md = (out_dir / "undefended_baseline.md").read_text(encoding="utf-8")
        assert PHASE6_DISCLOSURE_SUBSTR in md, (
            f"missing disclosure header. md head: {md[:200]!r}"
        )

    @_SKIP_V6
    def test_arms_race_table_disclosure_present(self, tmp_path):
        logs_dir, out_dir = _stage_minimal_inputs(tmp_path)
        rc = main(["--logs-dir", str(logs_dir), "--output-dir", str(out_dir)])
        assert rc == 0
        md = (out_dir / "arms_race_table.md").read_text(encoding="utf-8")
        assert PHASE6_DISCLOSURE_SUBSTR in md, (
            f"missing disclosure header. md head: {md[:200]!r}"
        )


# --- P6-CSV: csv companions ----------------------------------------------
class TestCsvCompanions:
    """P6-CSV: undefended_baseline_v6.csv and arms_race_table_v6.csv emitted."""

    @_SKIP_V6
    def test_undefended_baseline_v6_csv_exists(self, tmp_path):
        logs_dir, out_dir = _stage_minimal_inputs(tmp_path)
        rc = main(["--logs-dir", str(logs_dir), "--output-dir", str(out_dir)])
        assert rc == 0
        csv_path = out_dir / "undefended_baseline_v6.csv"
        assert csv_path.exists(), "undefended_baseline_v6.csv missing"
        header = csv_path.read_text(encoding="utf-8").splitlines()[0]
        # Post-Phase-6 schema includes T1b/T3/T4 columns
        for col in ["asr_tier1b", "asr_tier3", "asr_tier4"]:
            assert col in header, f"missing column {col} in v6 csv header: {header!r}"

    @_SKIP_V6
    def test_arms_race_table_v6_csv_exists(self, tmp_path):
        logs_dir, out_dir = _stage_minimal_inputs(tmp_path)
        rc = main(["--logs-dir", str(logs_dir), "--output-dir", str(out_dir)])
        assert rc == 0
        csv_path = out_dir / "arms_race_table_v6.csv"
        assert csv_path.exists(), "arms_race_table_v6.csv missing"
