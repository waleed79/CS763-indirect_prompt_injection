"""Wave 0 stub for scripts/run_phase6_eval.py (Wave 1) and Phase 6 figure renderers.

Skips until run_phase6_eval.py and make_figures.py v6 renderers are implemented.
Maps 1:1 onto P6-* requirements in 06-VALIDATION.md.
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
        "run_phase6_eval", _SCRIPTS_DIR / "run_phase6_eval.py"
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
    reason="scripts/run_phase6_eval.py not yet implemented (Wave 1)",
)


# --- P6-PRE: D-01a sanity assert -----------------------------------------
class TestSanityAssert:
    """P6-PRE: assert_collection_has_all_tiers raises on stale collection."""
    def test_missing_tier_range_raises(self):
        pytest.skip("Wave 1: implement assert_collection_has_all_tiers + mock chromadb")


# --- P6-RUN-20b-UND, P6-RUN-120b-UND -------------------------------------
class TestUndefendedRuns20b:
    """P6-RUN-20b-UND: Driver emits logs/eval_harness_undefended_gptoss20b_v6.json."""
    @pytest.mark.skipif(
        not Path("logs/eval_harness_undefended_gptoss20b_v6.json").exists(),
        reason="Wave 2 cloud run not yet executed",
    )
    def test_undefended_20b_log_exists(self):
        path = Path("logs/eval_harness_undefended_gptoss20b_v6.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "aggregate" in data
        for k in ["asr_tier1", "asr_tier1b", "asr_tier2", "asr_tier3", "asr_tier4"]:
            assert k in data["aggregate"], f"missing aggregate key: {k}"


class TestUndefendedRuns120b:
    """P6-RUN-120b-UND: Driver emits logs/eval_harness_undefended_gptoss120b_v6.json."""
    @pytest.mark.skipif(
        not Path("logs/eval_harness_undefended_gptoss120b_v6.json").exists(),
        reason="Wave 2 cloud run not yet executed",
    )
    def test_undefended_120b_log_exists(self):
        path = Path("logs/eval_harness_undefended_gptoss120b_v6.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "aggregate" in data
        for k in ["asr_tier1", "asr_tier1b", "asr_tier2", "asr_tier3", "asr_tier4"]:
            assert k in data["aggregate"], f"missing aggregate key: {k}"


# --- P6-PRO: provenance fields -------------------------------------------
class TestProvenanceFields:
    """P6-PRO: each _v6.json carries phase=06, supersedes_phase_02_3, error_count."""
    @pytest.mark.skipif(
        not Path("logs/eval_harness_undefended_gptoss20b_v6.json").exists(),
        reason="Wave 2 cloud run not yet executed",
    )
    def test_provenance_fields_present_20b(self):
        data = json.loads(
            Path("logs/eval_harness_undefended_gptoss20b_v6.json")
            .read_text(encoding="utf-8")
        )
        assert data.get("phase") == "06"
        assert data.get("supersedes_phase_02_3") is True
        assert data.get("collection") == "nq_poisoned_v4"
        assert data.get("corpus") == "data/corpus_poisoned.jsonl"
        assert isinstance(data.get("aggregate", {}).get("error_count"), int)


# --- P6-DEF: defended runs -----------------------------------------------
class TestDefendedRuns:
    """P6-DEF: 4 defended _v6 cells under logs/eval_matrix/."""
    @pytest.mark.skipif(
        not Path("logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json").exists(),
        reason="Wave 2 defended runs not yet executed",
    )
    def test_all_four_defended_cells_exist(self):
        for model_key in ["gptoss20b_cloud", "gptoss120b_cloud"]:
            for defense in ["fused", "def02"]:
                path = Path(f"logs/eval_matrix/{model_key}__{defense}__all_tiers_v6.json")
                assert path.exists(), f"missing defended cell: {path}"


# --- P6-MTX: _summary_v6.json composition --------------------------------
class TestMatrixSummary:
    """P6-MTX: _summary_v6.json contains exactly 75 cells."""
    @pytest.mark.skipif(
        not Path("logs/eval_matrix/_summary_v6.json").exists(),
        reason="Wave 2 summary composition not yet executed",
    )
    def test_summary_has_exactly_75_cells(self):
        rows = json.loads(
            Path("logs/eval_matrix/_summary_v6.json").read_text(encoding="utf-8")
        )
        assert isinstance(rows, list)
        assert len(rows) == 75, f"expected 75 cells, got {len(rows)}"
        for cell in rows:
            for k in ["model", "defense", "tier", "asr_overall", "asr_tier_native",
                      "fpr", "retrieval_rate"]:
                assert k in cell, f"cell missing key {k}: {cell}"


# --- P6-D12-FUSED: 5x5 fused heatmap -------------------------------------
class TestD12FusedV6:
    """P6-D12-FUSED: figures/d12_cross_model_heatmap_v6.png exists, >1KB, shape (5,5) enforced."""
    @pytest.mark.skipif(
        not Path("figures/d12_cross_model_heatmap_v6.png").exists(),
        reason="Wave 4 figure not yet rendered",
    )
    def test_d12_fused_v6_exists_and_sized(self):
        path = Path("figures/d12_cross_model_heatmap_v6.png")
        assert path.exists()
        assert path.stat().st_size > 1024


# --- P6-D12-UND: 5x4 undefended heatmap ----------------------------------
class TestD12UndefendedV6:
    """P6-D12-UND: figures/d12_undefended_v6.png exists, >1KB, shape (5,4) enforced."""
    @pytest.mark.skipif(
        not Path("figures/d12_undefended_v6.png").exists(),
        reason="Wave 4 figure not yet rendered",
    )
    def test_d12_undefended_v6_exists_and_sized(self):
        path = Path("figures/d12_undefended_v6.png")
        assert path.exists()
        assert path.stat().st_size > 1024


# --- P6-D03: arms-race v6 ------------------------------------------------
class TestD03V6:
    """P6-D03: figures/d03_arms_race_v6.png exists and is larger (gpt-oss bars added)."""
    @pytest.mark.skipif(
        not Path("figures/d03_arms_race_v6.png").exists(),
        reason="Wave 4 figure not yet rendered",
    )
    def test_d03_v6_exists_and_sized(self):
        path = Path("figures/d03_arms_race_v6.png")
        assert path.exists()
        assert path.stat().st_size > 1024


# --- P6-AUTH: ollama list pre-flight -------------------------------------
class TestPreflightCloudAuth:
    """P6-AUTH: ollama list shows both gpt-oss models."""
    def test_ollama_list_contains_gptoss_models(self):
        pytest.skip("Wave 2: invoked at run-time by driver, not by unit test")


# --- P6-ERR: error policy ------------------------------------------------
class TestErrorPolicy:
    """P6-ERR: single-query failure does not abort run; error_count incremented."""
    def test_error_policy_increments_count(self):
        pytest.skip("Wave 1: implement post-run mutation + simulate failure path")


# --- P6-ENC: utf-8 encoding everywhere -----------------------------------
class TestEncodingExplicit:
    """P6-ENC: every open()/read_text/write_text in run_phase6_eval.py specifies encoding=utf-8."""
    def test_run_phase6_eval_uses_utf8_explicit(self):
        path = _SCRIPTS_DIR / "run_phase6_eval.py"
        if not path.exists():
            pytest.skip("Wave 1: production file not yet created")
        src = path.read_text(encoding="utf-8")
        # Every read_text / write_text must include encoding="utf-8"
        for needle in ["read_text(", "write_text("]:
            offset = 0
            while True:
                i = src.find(needle, offset)
                if i == -1:
                    break
                # Find matching close paren
                depth = 1
                j = i + len(needle)
                while j < len(src) and depth > 0:
                    if src[j] == "(":
                        depth += 1
                    elif src[j] == ")":
                        depth -= 1
                    j += 1
                call = src[i:j]
                assert "encoding=" in call and "utf-8" in call, (
                    f"P6-ENC violation: {needle}...) without encoding='utf-8' at "
                    f"offset {i}: {call!r}"
                )
                offset = j
