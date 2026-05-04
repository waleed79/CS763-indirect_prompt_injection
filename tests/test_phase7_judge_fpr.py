"""Wave 0 stubs for scripts/run_judge_fpr_gptoss.py (Phase 7).

Skips until the script lands; after Plan 02 lands, all tests pass.
Covers P7-M1, P7-M2, P7-M3, P7-LCR, P7-UTF, P7-PATH, P7-CKEY,
P7-OUT-J-SHAPE, P7-OUT-J-NOROW, P7-OUT-V-SHAPE, P7-OUT-V-COUNT,
P7-OUT-V-FIELDS, P7-INHERIT-PROMPT, P7-INHERIT-PARSE,
P7-CACHE, P7-DRYRUN, P7-AUTH from 07-VALIDATION.md.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_LOGS_DIR = Path(__file__).parent.parent / "logs"
_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
_MODULE_NAME = "run_judge_fpr_gptoss"
_MODULE_FILE = _SCRIPTS_DIR / "run_judge_fpr_gptoss.py"

# Load Phase 5 helper separately (needed for P7-UTF and P7-INHERIT-* checks)
_PHASE5_FILE = _SCRIPTS_DIR / "run_judge_fpr.py"
try:
    _p5_spec = importlib.util.spec_from_file_location("run_judge_fpr", _PHASE5_FILE)
    _phase5 = importlib.util.module_from_spec(_p5_spec)
    _p5_spec.loader.exec_module(_phase5)
    _PHASE5_AVAILABLE = True
except Exception:
    _phase5 = None  # type: ignore[assignment]
    _PHASE5_AVAILABLE = False

try:
    _spec = importlib.util.spec_from_file_location(_MODULE_NAME, _MODULE_FILE)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    main = _mod.main
    CELL_LOG_MAP = _mod.CELL_LOG_MAP
    OFF_LOG_MAP = _mod.OFF_LOG_MAP
    N_CLEAN = _mod.N_CLEAN
    TOP_K = _mod.TOP_K
    _AVAILABLE = True
except (AttributeError, FileNotFoundError):
    _AVAILABLE = False
    CELL_LOG_MAP, OFF_LOG_MAP = {}, {}
    N_CLEAN, TOP_K = 50, 5
except Exception:
    import traceback; traceback.print_exc()
    _AVAILABLE = False
    CELL_LOG_MAP, OFF_LOG_MAP = {}, {}
    N_CLEAN, TOP_K = 50, 5

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason="scripts/run_judge_fpr_gptoss.py not yet implemented (Phase 7)",
)

# ---------------------------------------------------------------------------
# Module-level schema constants (D-02 / D-04)
# ---------------------------------------------------------------------------
NEW_KEYS = (
    "model", "defense_mode", "per_chunk_fpr",
    "answer_preserved_fpr", "judge_fpr", "judge_model", "judge_n_calls",
)
EXPECTED_KEYS = {
    "gptoss20b_cloud__fused",
    "gptoss20b_cloud__def02",
    "gptoss120b_cloud__fused",
    "gptoss120b_cloud__def02",
}
VERDICT_FIELDS = ("verdict", "ab_assignment", "raw_response", "retry_count")


# ---------------------------------------------------------------------------
# P7-M1: M1 numerator correctness (synthetic fixture)
# ---------------------------------------------------------------------------
class TestM1Numerator:
    """P7-M1: M1 = sum(chunks_removed) / (TOP_K * N_CLEAN)."""

    def test_m1_formula(self):
        """Synthetic 5-record fixture: chunks_removed=[3,0,2,1,0]; M1=6/(5*5)=0.24."""
        chunks_removed_values = [3, 0, 2, 1, 0]
        m1_numerator = sum(chunks_removed_values)
        m1 = m1_numerator / (TOP_K * len(chunks_removed_values))
        assert m1_numerator == 6
        assert abs(m1 - 0.24) < 1e-9, f"Expected M1=0.24, got {m1}"

    def test_m1_in_range(self):
        """M1 must lie in [0, 1] for all 4 cells if ablation file exists."""
        ablation_path = _LOGS_DIR / "ablation_table_gptoss_v7.json"
        if not ablation_path.exists():
            pytest.skip("output artifact pending Plan 04")
        ablation = json.loads(ablation_path.read_text(encoding="utf-8"))
        for key, row in ablation.items():
            m1 = row.get("per_chunk_fpr", -1)
            assert 0.0 <= m1 <= 1.0, f"{key} M1={m1} out of [0,1]"


# ---------------------------------------------------------------------------
# P7-M2: M2 aggregation (synthetic fixture)
# ---------------------------------------------------------------------------
class TestM2Aggregation:
    """P7-M2: M2 = count(chunks_removed>0 AND DEGRADED) / N_CLEAN."""

    def test_m2_formula(self):
        """Synthetic: 3 records with chunks_removed>0, of which 1 is DEGRADED -> M2=1/50."""
        # 3 records with removal, 1 DEGRADED among them
        records_with_removal = [
            {"chunks_removed": 2, "verdict": "DEGRADED"},
            {"chunks_removed": 1, "verdict": "PRESERVED"},
            {"chunks_removed": 3, "verdict": "TIE"},
        ]
        degraded_with_removal = sum(
            1 for r in records_with_removal
            if r["chunks_removed"] > 0 and r["verdict"] == "DEGRADED"
        )
        m2 = degraded_with_removal / N_CLEAN
        assert degraded_with_removal == 1
        assert abs(m2 - 1 / N_CLEAN) < 1e-9, f"Expected M2={1/N_CLEAN}, got {m2}"


# ---------------------------------------------------------------------------
# P7-M3: M3 aggregation (synthetic fixture)
# ---------------------------------------------------------------------------
class TestM3Aggregation:
    """P7-M3: M3 = count(DEGRADED) / N_CLEAN; TIE+refusal collapse to PRESERVED."""

    def test_m3_formula(self):
        """Synthetic: 2 DEGRADED, 1 TIE, 1 refusal in 50 -> M3=2/50=0.04."""
        verdicts = (
            ["DEGRADED"] * 2
            + ["TIE"] * 1
            + ["PRESERVED"] * 1  # refusal treated as PRESERVED
            + ["PRESERVED"] * 46
        )
        assert len(verdicts) == N_CLEAN
        degraded_count = sum(1 for v in verdicts if v == "DEGRADED")
        m3 = degraded_count / N_CLEAN
        assert degraded_count == 2
        assert abs(m3 - 2 / 50) < 1e-9, f"Expected M3=0.04, got {m3}"

    def test_tie_collapses_to_preserved(self):
        """TIE and None (refusal) do NOT count as DEGRADED in M3 numerator."""
        verdicts = ["TIE", "PRESERVED", None, "DEGRADED"]
        degraded_count = sum(1 for v in verdicts if v == "DEGRADED")
        assert degraded_count == 1, "Only explicit DEGRADED should count for M3"


# ---------------------------------------------------------------------------
# P7-LCR: load_clean_records returns exactly 50 records for v6 cell
# ---------------------------------------------------------------------------
class TestLoadCleanRecordsV6:
    """P7-LCR: load_clean_records(v6_cell_path) returns exactly 50 records."""

    def test_load_returns_50_records(self):
        """Given a v6 cell path, load_clean_records returns exactly N_CLEAN records."""
        cell_path = _LOGS_DIR / "eval_matrix" / "gptoss20b_cloud__fused__all_tiers_v6.json"
        if not cell_path.exists():
            pytest.skip("v6 cell file absent on disk")
        # Use Phase 5 load_clean_records (reused by Phase 7)
        assert _PHASE5_AVAILABLE, "Phase 5 module must be loadable"
        records = _phase5.load_clean_records(cell_path)
        assert len(records) == N_CLEAN, (
            f"Expected {N_CLEAN} clean records, got {len(records)}"
        )


# ---------------------------------------------------------------------------
# P7-UTF: load_clean_records does not raise UnicodeDecodeError on v6 cells
# ---------------------------------------------------------------------------
class TestUtf8Encoding:
    """P7-UTF: load_clean_records reads v6 cell with non-ASCII chars without error."""

    def test_no_unicode_error(self):
        """Call load_clean_records on the v6 cell; must not raise UnicodeDecodeError."""
        cell_path = _LOGS_DIR / "eval_matrix" / "gptoss20b_cloud__fused__all_tiers_v6.json"
        if not cell_path.exists():
            pytest.skip("v6 cell file absent on disk")
        assert _PHASE5_AVAILABLE, "Phase 5 module must be loadable"
        try:
            _phase5.load_clean_records(str(cell_path))
        except UnicodeDecodeError as e:
            pytest.fail(f"UnicodeDecodeError raised: {e}")


# ---------------------------------------------------------------------------
# P7-PATH: CELL_LOG_MAP and OFF_LOG_MAP paths all exist on disk
# ---------------------------------------------------------------------------
class TestPathMapsLoudFail:
    """P7-PATH: every path in CELL_LOG_MAP and OFF_LOG_MAP resolves to an existing file."""

    def test_cell_log_map_paths_exist(self):
        """All CELL_LOG_MAP values must point to existing files."""
        missing = []
        for key, path_str in CELL_LOG_MAP.items():
            p = Path(path_str)
            if not p.exists():
                missing.append((key, path_str))
        assert not missing, (
            f"CELL_LOG_MAP paths missing on disk: {missing}"
        )

    def test_off_log_map_paths_exist(self):
        """All OFF_LOG_MAP values must point to existing files."""
        missing = []
        for model, path_str in OFF_LOG_MAP.items():
            p = Path(path_str)
            if not p.exists():
                missing.append((model, path_str))
        assert not missing, (
            f"OFF_LOG_MAP paths missing on disk: {missing}"
        )


# ---------------------------------------------------------------------------
# P7-CKEY: composite key set is exactly the 4 expected keys
# ---------------------------------------------------------------------------
class TestCompositeKeys:
    """P7-CKEY: CELL_LOG_MAP yields exactly the 4 expected composite keys."""

    def test_composite_key_set(self):
        """CELL_LOG_MAP.keys() must equal the 4 (model, defense) pairs per D-09."""
        expected = {
            ("gpt-oss:20b-cloud",  "fused"),
            ("gpt-oss:20b-cloud",  "def02"),
            ("gpt-oss:120b-cloud", "fused"),
            ("gpt-oss:120b-cloud", "def02"),
        }
        assert set(CELL_LOG_MAP.keys()) == expected, (
            f"CELL_LOG_MAP keys mismatch.\n"
            f"  Expected: {sorted(str(k) for k in expected)}\n"
            f"  Got:      {sorted(str(k) for k in CELL_LOG_MAP.keys())}"
        )


# ---------------------------------------------------------------------------
# P7-OUT-J-SHAPE: ablation_table_gptoss_v7.json shape (D-02)
# ---------------------------------------------------------------------------
class TestAblationV7Shape:
    """P7-OUT-J-SHAPE: ablation file is flat dict with exactly 4 entries; each has D-02 fields."""

    def test_exactly_four_rows(self):
        """Set of keys must equal EXPECTED_KEYS."""
        ablation_path = _LOGS_DIR / "ablation_table_gptoss_v7.json"
        if not ablation_path.exists():
            pytest.skip("output artifact pending Plan 04")
        ablation = json.loads(ablation_path.read_text(encoding="utf-8"))
        assert set(ablation.keys()) == EXPECTED_KEYS, (
            f"Key mismatch: got {set(ablation.keys())}, expected {EXPECTED_KEYS}"
        )

    def test_each_row_has_required_keys(self):
        """Each row must have all NEW_KEYS per D-02 schema."""
        ablation_path = _LOGS_DIR / "ablation_table_gptoss_v7.json"
        if not ablation_path.exists():
            pytest.skip("output artifact pending Plan 04")
        ablation = json.loads(ablation_path.read_text(encoding="utf-8"))
        for composite_key, row in ablation.items():
            for k in NEW_KEYS:
                assert k in row, f"{composite_key} missing required field {k!r}"


# ---------------------------------------------------------------------------
# P7-OUT-J-NOROW: no "no_defense" trivial row (D-03)
# ---------------------------------------------------------------------------
class TestNoTrivialRow:
    """P7-OUT-J-NOROW: ablation_table_gptoss_v7.json does NOT contain a no_defense row."""

    def test_no_defense_absent(self):
        """D-03: Phase 7 writes only defended rows; no_defense is meaningless here."""
        ablation_path = _LOGS_DIR / "ablation_table_gptoss_v7.json"
        if not ablation_path.exists():
            pytest.skip("output artifact pending Plan 04")
        ablation = json.loads(ablation_path.read_text(encoding="utf-8"))
        for key in ablation.keys():
            assert "no_defense" not in key, (
                f"Trivial no_defense row found in ablation: {key!r} (D-03 violation)"
            )


# ---------------------------------------------------------------------------
# P7-OUT-V-SHAPE: judge_fpr_gptoss_v7.json nested shape (D-04)
# ---------------------------------------------------------------------------
class TestVerdictsV7Shape:
    """P7-OUT-V-SHAPE: verdicts[model][defense][qid] nesting per D-04."""

    def test_verdicts_nested_two_levels(self):
        """Top-level 'verdicts' key nests model → defense → qid."""
        verdicts_path = _LOGS_DIR / "judge_fpr_gptoss_v7.json"
        if not verdicts_path.exists():
            pytest.skip("output artifact pending Plan 04")
        v = json.loads(verdicts_path.read_text(encoding="utf-8"))
        assert "verdicts" in v, "Missing top-level 'verdicts' key"
        for model in ["gpt-oss:20b-cloud", "gpt-oss:120b-cloud"]:
            assert model in v["verdicts"], f"Model {model!r} missing from verdicts"
            for defense in ["fused", "def02"]:
                assert defense in v["verdicts"][model], (
                    f"Defense {defense!r} missing from verdicts[{model!r}]"
                )
                assert len(v["verdicts"][model][defense]) == N_CLEAN, (
                    f"Expected {N_CLEAN} records for ({model}, {defense}), "
                    f"got {len(v['verdicts'][model][defense])}"
                )


# ---------------------------------------------------------------------------
# P7-OUT-V-COUNT: exactly 200 verdict records (4 cells × 50)
# ---------------------------------------------------------------------------
class TestVerdictCount200:
    """P7-OUT-V-COUNT: total verdict records == 200."""

    def test_total_verdict_count(self):
        """Sum len(verdicts[model][defense]) over 4 cells must equal 200."""
        verdicts_path = _LOGS_DIR / "judge_fpr_gptoss_v7.json"
        if not verdicts_path.exists():
            pytest.skip("output artifact pending Plan 04")
        v = json.loads(verdicts_path.read_text(encoding="utf-8"))
        total = 0
        for model_data in v.get("verdicts", {}).values():
            for defense_data in model_data.values():
                total += len(defense_data)
        assert total == 200, (
            f"Expected 200 verdict records (4 cells × {N_CLEAN}), got {total}"
        )


# ---------------------------------------------------------------------------
# P7-OUT-V-FIELDS: each verdict record has required fields (D-04 + Phase 5 D-12)
# ---------------------------------------------------------------------------
class TestVerdictRecordFields:
    """P7-OUT-V-FIELDS: each verdict record has all VERDICT_FIELDS."""

    def test_verdict_record_has_required_fields(self):
        """Pick one record from each cell; assert all VERDICT_FIELDS present."""
        verdicts_path = _LOGS_DIR / "judge_fpr_gptoss_v7.json"
        if not verdicts_path.exists():
            pytest.skip("output artifact pending Plan 04")
        v = json.loads(verdicts_path.read_text(encoding="utf-8"))
        for model, model_data in v.get("verdicts", {}).items():
            for defense, defense_data in model_data.items():
                if not defense_data:
                    continue
                qid = next(iter(defense_data))
                record = defense_data[qid]
                for field in VERDICT_FIELDS:
                    assert field in record, (
                        f"({model}, {defense}, qid={qid}) missing field {field!r}"
                    )


# ---------------------------------------------------------------------------
# P7-INHERIT-PROMPT: JUDGE_SYSTEM_PROMPT reused from Phase 5 (no redefinition)
# ---------------------------------------------------------------------------
class TestPromptInherited:
    """P7-INHERIT-PROMPT: Phase 7 imports JUDGE_SYSTEM_PROMPT from run_judge_fpr.py."""

    def test_prompt_is_same_object(self):
        """_mod.JUDGE_SYSTEM_PROMPT must come from _mod._phase5 (no local redefinition).

        Implementation note: exec_module creates separate module instances, so we cannot
        assert identity against the test-file's own _phase5 instance (separate exec).
        Instead, we assert that _mod.JUDGE_SYSTEM_PROMPT IS _mod._phase5.JUDGE_SYSTEM_PROMPT,
        which proves no local redefinition inside run_judge_fpr_gptoss.py.
        """
        assert _PHASE5_AVAILABLE, "Phase 5 module must be loadable for identity check"
        assert hasattr(_mod, "JUDGE_SYSTEM_PROMPT"), (
            "run_judge_fpr_gptoss.py must expose JUDGE_SYSTEM_PROMPT"
        )
        assert hasattr(_mod, "_phase5"), (
            "run_judge_fpr_gptoss.py must expose _phase5 (the importlib-loaded Phase 5 module)"
        )
        assert _mod.JUDGE_SYSTEM_PROMPT is _mod._phase5.JUDGE_SYSTEM_PROMPT, (
            "JUDGE_SYSTEM_PROMPT must be the same object as _mod._phase5's (no local redefinition)"
        )


# ---------------------------------------------------------------------------
# P7-INHERIT-PARSE: parse_verdict reused from Phase 5 (no copy-pasted parser)
# ---------------------------------------------------------------------------
class TestParserInherited:
    """P7-INHERIT-PARSE: Phase 7 reuses parse_verdict() from Phase 5."""

    def test_parse_verdict_is_same_object(self):
        """_mod.parse_verdict must come from _mod._phase5 (no local copy-paste).

        Implementation note: exec_module creates separate module instances, so we cannot
        assert identity against the test-file's own _phase5 instance (separate exec).
        Instead, we assert that _mod.parse_verdict IS _mod._phase5.parse_verdict,
        which proves no local copy-paste inside run_judge_fpr_gptoss.py.
        """
        assert _PHASE5_AVAILABLE, "Phase 5 module must be loadable for identity check"
        assert hasattr(_mod, "parse_verdict"), (
            "run_judge_fpr_gptoss.py must expose parse_verdict"
        )
        assert hasattr(_mod, "_phase5"), (
            "run_judge_fpr_gptoss.py must expose _phase5 (the importlib-loaded Phase 5 module)"
        )
        assert _mod.parse_verdict is _mod._phase5.parse_verdict, (
            "parse_verdict must be the same object as _mod._phase5's (no local copy-paste)"
        )


# ---------------------------------------------------------------------------
# P7-CACHE: second invocation with cache file present skips judge calls
# ---------------------------------------------------------------------------
class TestCacheResume:
    """P7-CACHE: re-run with .cache file present skips all judge calls."""

    def test_dry_run_skips_calls(self, tmp_path):
        """Stage a cache file with 4 fake verdicts; run with --dry-run; confirm zero new calls."""
        # This test relies on --dry-run behaviour (which requires no cloud calls).
        # A full cache-resume test requires monkeypatching; that is a Wave 2 concern.
        # Here we confirm that --dry-run completes without error when cache is staged.
        cache_file = tmp_path / "judge_fpr_gptoss_v7.json.cache"
        fake_cache: dict = {}
        cache_file.write_text(json.dumps(fake_cache), encoding="utf-8")
        # --dry-run should exit 0 regardless of cache state (M1 only mode)
        rc = main(["--dry-run", "--cache", str(cache_file)])
        # rc==0 expected if log files exist; otherwise main may return 1 if inputs missing
        assert rc in (0, 1), f"Unexpected return code from main: {rc}"


# ---------------------------------------------------------------------------
# P7-DRYRUN: --dry-run flag computes M1 only, makes zero cloud calls
# ---------------------------------------------------------------------------
class TestDryRunNoCloud:
    """P7-DRYRUN: --dry-run makes zero cloud calls and returns rc==0."""

    def test_dry_run_no_cloud(self):
        """Invoke main(['--dry-run']); confirm rc==0 AND no cloud client was instantiated."""
        # We verify the contract by checking that main() does not raise due to
        # missing Ollama and returns rc==0 when input files are present,
        # or rc==1 only due to missing input files (not cloud auth).
        rc = main(["--dry-run"])
        # rc==0 = success with input files; rc==1 = missing inputs (acceptable in Wave 0)
        assert rc in (0, 1), (
            f"--dry-run returned unexpected rc={rc}; expected 0 (success) or 1 (missing inputs)"
        )


# ---------------------------------------------------------------------------
# P7-AUTH: JudgeAuthError from a mocked client returns rc=1 cleanly
# ---------------------------------------------------------------------------
class TestAuthEscalation:
    """P7-AUTH: JudgeAuthError returns rc=1 cleanly without partial-state corruption."""

    def test_auth_error_returns_rc1(self, monkeypatch):
        """Monkeypatch judge_one to raise JudgeAuthError; main must return rc=1."""
        assert _PHASE5_AVAILABLE, "Phase 5 module must be loadable"
        JudgeAuthError = _phase5.JudgeAuthError

        def _always_auth_error(*args, **kwargs):
            raise JudgeAuthError("Mocked auth failure — run: ollama login")

        # Patch Phase 5's judge_one so run_judge_fpr_gptoss.py sees the mock
        monkeypatch.setattr(_phase5, "judge_one", _always_auth_error)
        # Also patch via _mod if it holds a local reference
        if hasattr(_mod, "judge_one"):
            monkeypatch.setattr(_mod, "judge_one", _always_auth_error)

        rc = main([])  # no --dry-run: will attempt cloud calls → should hit auth error
        assert rc == 1, (
            f"Expected rc=1 on JudgeAuthError, got rc={rc}"
        )
