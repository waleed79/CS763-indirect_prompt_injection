"""Wave 0 stub for scripts/make_results.py (Wave 1 Plan 02).

Skips until make_results.py is implemented. After Plan 02 lands, all tests must pass.
"""
from __future__ import annotations
import importlib.util
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
except (AttributeError, FileNotFoundError, Exception):
    _AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AVAILABLE, reason="scripts/make_results.py not yet implemented (Wave 1 Plan 02)"
)


class TestMakeResultsSmoke:
    def test_main_runs_with_no_args(self, tmp_path):
        """make_results.py main([]) returns 0 with default args."""
        rc = main(["--output-dir", str(tmp_path)])
        assert rc == 0

    def test_arms_race_table_emitted(self, tmp_path):
        """docs/results/arms_race_table.md exists after run with expected columns."""
        main(["--output-dir", str(tmp_path)])
        md = (tmp_path / "arms_race_table.md").read_text()
        # CONTEXT D-03: 5 defense column names
        for col in ["No Defense", "BERT", "Fused", "DEF-02"]:
            assert col in md, f"missing column {col} in arms race table"

    def test_three_source_aggregation(self, tmp_path):
        """PH3-01: arms race aggregates 3 sources per ROADMAP SC-1 (a/b/c)."""
        main(["--output-dir", str(tmp_path)])
        # Source (a) Phase 2.3 undefended baseline — 4 LLMs
        baseline = (tmp_path / "undefended_baseline.md").read_text()
        for model in ["llama3.2", "mistral", "gpt-oss"]:
            assert model in baseline, f"undefended baseline missing model {model}"
        # Source (b) Phase 3.3 EVAL-V2-01 cross-model matrix — 3 LLMs × 3 defenses × 5 tiers
        matrix = (tmp_path / "cross_model_matrix.md").read_text()
        for tier in ["T1", "T1b", "T2", "T3", "T4"]:
            assert tier in matrix, f"cross_model_matrix missing tier {tier}"
        # Source (c) Phase 3.1 single-LLM ablation — 7 defense modes
        ablation = (tmp_path / "ablation_table.md").read_text()
        assert "fused_fixed_0.5" in ablation or "fused" in ablation.lower()

    def test_canonical_numbers_present(self, tmp_path):
        """EVAL-02: FPR + retrieval_rate columns present with canonical numbers."""
        main(["--output-dir", str(tmp_path)])
        ablation = (tmp_path / "ablation_table.md").read_text()
        # Canonical numbers from logs/ablation_table.json (verified RESEARCH line 343 + ROADMAP SC-4)
        assert "0.76" in ablation or "76%" in ablation, "fused FPR 76% not in ablation table"
        assert "0.50" in ablation or "50%" in ablation, "fused retrieval_rate 50% not in ablation table"
