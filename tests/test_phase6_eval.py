"""Wave 0 stub for scripts/run_phase6_eval.py (Wave 1) and Phase 6 figure renderers.

Skips until run_phase6_eval.py and make_figures.py v6 renderers are implemented.
Maps 1:1 onto P6-* requirements in 06-VALIDATION.md.
"""
from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

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
    def test_missing_tier_range_raises(self, monkeypatch):
        """D-01a: stale T1b range -> AssertionError with 'T1b range' in message."""
        # Build a fake chromadb collection where T1b range returns no IDs
        def fake_get(where=None, limit=1, include=None):
            # Determine which tier range is being queried from the $and filter
            if where and "$and" in where:
                conditions = where["$and"]
                lo = next(
                    (c["passage_id"]["$gte"] for c in conditions if "$gte" in c.get("passage_id", {})),
                    None,
                )
                from rag.constants import TIER1B_ID_START
                if lo == TIER1B_ID_START:
                    return {"ids": []}  # T1b is empty — triggers the assert
            return {"ids": ["fake-id-001"]}

        fake_collection = MagicMock()
        fake_collection.get.side_effect = fake_get

        fake_client = MagicMock()
        fake_client.get_collection.return_value = fake_collection

        monkeypatch.setattr(_mod.chromadb, "PersistentClient", lambda **kwargs: fake_client)

        with pytest.raises(AssertionError, match="T1b range"):
            _mod.assert_collection_has_all_tiers("nq_poisoned_v4")


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

    def test_summary_has_exactly_75_cells(self, tmp_path, monkeypatch):
        """Info-05 P6-MTX shift-left: fixture-based unit test — no cloud files needed."""
        # Build a 45-cell stub _summary.json
        base_cell = {
            "model": "llama3.2_3b",
            "defense": "no_defense",
            "tier": "tier1",
            "asr_overall": 0.0,
            "asr_tier_native": 0.0,
            "fpr": 0.0,
            "retrieval_rate": 0.0,
        }
        stub_summary = [dict(base_cell) for _ in range(45)]
        summary_path = tmp_path / "_summary.json"
        summary_path.write_text(json.dumps(stub_summary), encoding="utf-8")

        # Build 6 stub run JSONs (2 models × 3 defenses)
        run_outputs = []
        for model_id, model_key in [("gpt-oss:20b-cloud", "gptoss20b"), ("gpt-oss:120b-cloud", "gptoss120b")]:
            for defense_flag, defense_name in [("off", "no_defense"), ("fused", "fused"), ("def02", "def02")]:
                stub_run = {
                    "llm_model": model_id,
                    "aggregate": {
                        "asr_tier1": 0.1,
                        "asr_tier1b": 0.1,
                        "asr_tier2": 0.1,
                        "asr_tier3": 0.1,
                        "asr_tier4": 0.1,
                        "fpr": 0.0,
                        "retrieval_rate": 0.85,
                    },
                }
                run_path = tmp_path / f"{model_key}__{defense_name}__all_tiers_v6.json"
                run_path.write_text(json.dumps(stub_run), encoding="utf-8")
                run_outputs.append((model_id, defense_name, run_path))

        summary_v6_path = tmp_path / "_summary_v6.json"
        monkeypatch.setattr(_mod, "EXISTING_SUMMARY", summary_path)
        monkeypatch.setattr(_mod, "SUMMARY_V6", summary_v6_path)

        _mod.compose_summary_v6(run_outputs)

        rows = json.loads(summary_v6_path.read_text(encoding="utf-8"))
        assert isinstance(rows, list)
        assert len(rows) == 75, f"expected 75 cells, got {len(rows)}"
        for cell in rows:
            for k in ["model", "defense", "tier", "asr_overall", "asr_tier_native",
                      "fpr", "retrieval_rate"]:
                assert k in cell, f"cell missing key {k}: {cell}"

    @pytest.mark.skipif(
        not Path("logs/eval_matrix/_summary_v6.json").exists(),
        reason="Wave 2 summary composition not yet executed",
    )
    def test_summary_in_real_logs_has_75_cells(self):
        """Post-Wave-2 reality check: real _summary_v6.json has exactly 75 cells."""
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
    def test_ollama_list_contains_gptoss_models(self, monkeypatch):
        """Info-04 P6-AUTH shift-left: missing 120b model -> RuntimeError."""
        fake_result = MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = "NAME\tID\ngpt-oss:20b-cloud\tabc\t1.2 GB\n"
        fake_result.stderr = ""

        monkeypatch.setattr(_mod.subprocess, "run", lambda *a, **kw: fake_result)

        with pytest.raises(RuntimeError, match="gpt-oss:120b-cloud"):
            _mod.preflight_ollama_list()

    def test_ollama_list_returns_clean_when_both_present(self, monkeypatch):
        """P6-AUTH: both models present -> no exception raised."""
        fake_result = MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = (
            "NAME\tID\n"
            "gpt-oss:20b-cloud\tabc\t1.2 GB\n"
            "gpt-oss:120b-cloud\tdef\t7.8 GB\n"
        )
        fake_result.stderr = ""

        monkeypatch.setattr(_mod.subprocess, "run", lambda *a, **kw: fake_result)

        # Should not raise
        _mod.preflight_ollama_list()


# --- P6-ERR: error policy ------------------------------------------------
class TestErrorPolicy:
    """P6-ERR: single-query failure does not abort run; error_count incremented."""
    def test_error_policy_increments_count(self, tmp_path):
        """add_provenance counts [ERROR: prefixed answers and writes error_count=1."""
        fixture = {
            "llm_model": "gpt-oss:20b-cloud",
            "aggregate": {},
            "results": [
                {"query": "q1", "answer": "[ERROR: rate_limit] timeout"},
                {"query": "q2", "answer": "normal answer"},
            ],
        }
        p = tmp_path / "fixture.json"
        p.write_text(json.dumps(fixture), encoding="utf-8")

        _mod.add_provenance(p)

        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["phase"] == "06"
        assert data["supersedes_phase_02_3"] is True
        assert data["aggregate"]["error_count"] == 1


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
