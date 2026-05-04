"""Wave 0 stub for Phase 7 make_results.py v7 extensions.

Tests path resolver (_resolve_v7_ablation_path), emitter
(emit_honest_fpr_gptoss_v7), regression (P7-RESV-COMPAT),
and docs/phase5_honest_fpr.md addendum integrity (P7-DOC-*).
Skips until Wave 1 edits land in scripts/make_results.py.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
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
    main = None  # type: ignore[assignment]
except Exception:
    import traceback
    traceback.print_exc()
    _AVAILABLE = False
    main = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason="scripts/make_results.py not importable",
)

# ---------------------------------------------------------------------------
# V7 availability sentinel — True only when Wave 1 has added Phase 7 v7 support
# ---------------------------------------------------------------------------
_V7_AVAILABLE: bool = (
    _AVAILABLE and (
        hasattr(_mod, "_resolve_v7_ablation_path") or hasattr(_mod, "load_honest_fpr_v7")
    )
) if _AVAILABLE else False

_SKIP_V7 = pytest.mark.skipif(
    not _V7_AVAILABLE,
    reason="scripts/make_results.py Phase 7 v7 extensions not yet implemented",
)

# Doc-addendum sentinel — True only when Plan 05 has appended the addendum
_DOCS_DIR = Path(__file__).parent.parent / "docs"
_PHASE5_DOC = _DOCS_DIR / "phase5_honest_fpr.md"
_DOC_ADDENDUM_HEADING = "## Phase 7 addendum"
_DOC_ADDENDUM_AVAILABLE = (
    _PHASE5_DOC.exists()
    and _DOC_ADDENDUM_HEADING in _PHASE5_DOC.read_text(encoding="utf-8")
) if _PHASE5_DOC.exists() else False

_SKIP_DOC = pytest.mark.skipif(
    not _DOC_ADDENDUM_AVAILABLE,
    reason="Phase 7 addendum not yet appended to docs/phase5_honest_fpr.md (Plan 05)",
)


# ---------------------------------------------------------------------------
# Fixture: stage minimal inputs (verbatim from test_make_results_v6.py:54-74)
# ---------------------------------------------------------------------------
def _stage_minimal_inputs(tmp_path: Path) -> "tuple[Path, Path]":
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


# ---------------------------------------------------------------------------
# P7-RESV: v7 resolver returns Path when v7 ablation exists, None otherwise
# ---------------------------------------------------------------------------
class TestV7Resolver:
    """P7-RESV: _resolve_v7_ablation_path returns Path when file present, None when absent."""

    @_SKIP_V7
    def test_returns_path_when_present(self, tmp_path):
        """Stage v7 file; resolver must return a Path pointing to it."""
        logs_dir, _ = _stage_minimal_inputs(tmp_path)
        v7_file = logs_dir / "ablation_table_gptoss_v7.json"
        v7_file.write_text(json.dumps({"gptoss20b_cloud__fused": {
            "model": "gpt-oss:20b-cloud", "defense_mode": "fused",
            "per_chunk_fpr": 0.10, "answer_preserved_fpr": 0.05,
            "judge_fpr": 0.08, "judge_model": "gpt-oss:20b-cloud",
            "judge_n_calls": 50,
        }}), encoding="utf-8")
        result = _mod._resolve_v7_ablation_path(logs_dir)
        assert result is not None, "Resolver returned None when v7 file is present"
        assert Path(result).exists(), f"Resolved path does not exist: {result}"
        assert Path(result).name == "ablation_table_gptoss_v7.json"

    @_SKIP_V7
    def test_returns_none_when_absent(self, tmp_path):
        """No v7 file staged; resolver must return None or falsy."""
        logs_dir, _ = _stage_minimal_inputs(tmp_path)
        # No v7 file staged
        result = _mod._resolve_v7_ablation_path(logs_dir)
        assert not result, (
            f"Resolver returned {result!r} when v7 file is absent — expected None/falsy"
        )


# ---------------------------------------------------------------------------
# P7-RESV-EMIT: v7 emitter produces honest_fpr_gptoss_v7.md when file present
# ---------------------------------------------------------------------------
class TestV7Emit:
    """P7-RESV-EMIT: when v7 file present, honest_fpr_gptoss_v7.md produced; absent → no-op."""

    @_SKIP_V7
    def test_v7_path_returned_when_present(self, tmp_path):
        """Stage v7 file; run main(); assert honest_fpr_gptoss_v7.md exists and contains M1."""
        logs_dir, out_dir = _stage_minimal_inputs(tmp_path)
        # Stage a minimal v7 ablation file
        v7_file = logs_dir / "ablation_table_gptoss_v7.json"
        v7_file.write_text(json.dumps({
            "gptoss20b_cloud__fused": {
                "model": "gpt-oss:20b-cloud",
                "defense_mode": "fused",
                "per_chunk_fpr": 0.10,
                "answer_preserved_fpr": 0.05,
                "judge_fpr": 0.08,
                "judge_model": "gpt-oss:20b-cloud",
                "judge_n_calls": 50,
            }
        }), encoding="utf-8")
        rc = main(["--logs-dir", str(logs_dir), "--output-dir", str(out_dir)])
        assert rc == 0, f"main() returned rc={rc}"
        md_path = out_dir / "honest_fpr_gptoss_v7.md"
        assert md_path.exists(), "honest_fpr_gptoss_v7.md not emitted"
        md = md_path.read_text(encoding="utf-8")
        assert "0.10" in md, f"M1=0.10 not found in emitted markdown: {md[:400]!r}"

    @_SKIP_V7
    def test_v7_no_op_when_absent(self, tmp_path):
        """No v7 file staged; run main(); assert honest_fpr_gptoss_v7.md does NOT exist."""
        logs_dir, out_dir = _stage_minimal_inputs(tmp_path)
        # No v7 file staged
        rc = main(["--logs-dir", str(logs_dir), "--output-dir", str(out_dir)])
        assert rc == 0, f"main() returned rc={rc}"
        md_path = out_dir / "honest_fpr_gptoss_v7.md"
        assert not md_path.exists(), (
            "honest_fpr_gptoss_v7.md emitted even when no v7 ablation file was present"
        )


# ---------------------------------------------------------------------------
# P7-RESV-COMPAT: existing Phase 5/6 test suites stay green
# ---------------------------------------------------------------------------
class TestV7Compat:
    """P7-RESV-COMPAT: existing test_make_results.py and test_make_results_v6.py stay green."""

    def test_prior_test_files_exist(self):
        """Sanity check: both prior test files are present on disk.

        Full regression enforcement happens when the full test suite is run
        (pytest tests/test_make_results.py tests/test_make_results_v6.py -x).
        This guard ensures neither file was accidentally deleted.
        """
        assert Path("tests/test_make_results.py").exists(), (
            "tests/test_make_results.py missing — Phase 5 regression suite deleted"
        )
        assert Path("tests/test_make_results_v6.py").exists(), (
            "tests/test_make_results_v6.py missing — Phase 6 regression suite deleted"
        )


# ---------------------------------------------------------------------------
# P7-DOC-UNTOUCHED: original Phase 5 prose is bit-for-bit unchanged above addendum
# ---------------------------------------------------------------------------
class TestPhase5ProseUntouched:
    """P7-DOC-UNTOUCHED: Phase 5 prose above the addendum is bit-for-bit unchanged."""

    @_SKIP_DOC
    def test_prose_prefix_unchanged(self):
        """Split doc at addendum heading; prefix must match git-HEAD bytes."""
        if not _PHASE5_DOC.exists():
            pytest.skip("docs/phase5_honest_fpr.md not found")
        current_text = _PHASE5_DOC.read_text(encoding="utf-8")
        # Split at the addendum heading
        idx = current_text.find(_DOC_ADDENDUM_HEADING)
        assert idx >= 0, "Addendum heading not found (should have been caught by sentinel)"
        prefix = current_text[:idx]

        # Get git-HEAD version
        try:
            result = subprocess.run(
                ["git", "show", "HEAD:docs/phase5_honest_fpr.md"],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
            head_text = result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("git not available or docs/phase5_honest_fpr.md not in HEAD")

        # HEAD text should not contain the addendum (it was added in Plan 05)
        if _DOC_ADDENDUM_HEADING in head_text:
            # If HEAD already has addendum, compare only above it
            head_idx = head_text.find(_DOC_ADDENDUM_HEADING)
            head_prefix = head_text[:head_idx]
        else:
            head_prefix = head_text

        assert prefix == head_prefix, (
            "Phase 5 original prose has been modified above the addendum heading. "
            "Only addendum content should be added; existing prose must be unchanged."
        )


# ---------------------------------------------------------------------------
# P7-DOC-ADDENDUM: addendum heading present exactly once
# ---------------------------------------------------------------------------
class TestAddendumPresent:
    """P7-DOC-ADDENDUM: docs/phase5_honest_fpr.md contains the addendum heading exactly once."""

    @_SKIP_DOC
    def test_addendum_heading_once(self):
        """The addendum heading must appear exactly once."""
        if not _PHASE5_DOC.exists():
            pytest.skip("docs/phase5_honest_fpr.md not found")
        text = _PHASE5_DOC.read_text(encoding="utf-8")
        count = text.count("## Phase 7 addendum")
        assert count == 1, (
            f"Expected addendum heading exactly once, found {count} times"
        )


# ---------------------------------------------------------------------------
# P7-DOC-TABLE-10ROW: addendum's M1/M2/M3 table has exactly 10 data rows
# ---------------------------------------------------------------------------
class TestAddendumTable10Rows:
    """P7-DOC-TABLE-10ROW: the addendum table has exactly 10 pipe-table data rows."""

    @_SKIP_DOC
    def test_table_has_ten_data_rows(self):
        """Extract the addendum section; count pipe-table data rows (excl. header + sep)."""
        if not _PHASE5_DOC.exists():
            pytest.skip("docs/phase5_honest_fpr.md not found")
        text = _PHASE5_DOC.read_text(encoding="utf-8")
        # Extract addendum section (from heading to end or next ## heading)
        match = re.search(
            r"## Phase 7 addendum.*?(?=^## |\Z)",
            text,
            re.S | re.M,
        )
        assert match is not None, "Could not extract addendum section with regex"
        addendum = match.group(0)
        # Count pipe-table data rows: lines starting with | but NOT the separator (---)
        data_rows = [
            line for line in addendum.splitlines()
            if line.strip().startswith("|")
            and not re.match(r"^\|[-| :]+\|", line.strip())
            and not line.strip().startswith("| Model")  # skip header row
            and not line.strip().startswith("| model")  # skip header row (lowercase)
        ]
        # Strip the header row if it was matched (contains column names, not numbers)
        data_rows = [r for r in data_rows if "|" in r]
        assert len(data_rows) == 10, (
            f"Expected exactly 10 data rows in addendum table, found {len(data_rows)}.\n"
            f"Rows found: {data_rows}"
        )


# ---------------------------------------------------------------------------
# P7-DOC-PHASE3-UNTOUCHED: docs/phase3_results.md is unchanged
# ---------------------------------------------------------------------------
class TestPhase34NotEdited:
    """P7-DOC-PHASE3-UNTOUCHED: docs/phase3_results.md is bit-for-bit unchanged vs git HEAD."""

    def test_phase3_doc_unchanged(self):
        """git diff --exit-code docs/phase3_results.md must return 0."""
        phase3_doc = Path("docs") / "phase3_results.md"
        if not phase3_doc.exists():
            pytest.skip("docs/phase3_results.md not present")
        try:
            result = subprocess.run(
                ["git", "diff", "--exit-code", str(phase3_doc)],
                capture_output=True,
            )
            assert result.returncode == 0, (
                f"docs/phase3_results.md has uncommitted changes:\n"
                f"{result.stdout.decode(errors='replace')}"
            )
        except FileNotFoundError:
            pytest.skip("git not available in this environment")
