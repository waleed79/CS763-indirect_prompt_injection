"""Phase 3.2 DEF-05 leave-one-out (LOO) causal attribution tests.

TestLooExcludeFn  — contracts for make_exclude_fn() from scripts/run_loo.py
                    (skips until run_loo.py is created in plan 03.2-03)
TestLooJudge      — parse_judge_output() from scripts/run_judge.py
                    (green immediately — parse_judge_output already exists)

Run with:
    conda run -n rag-security python -m pytest tests/test_loo.py -v
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

# ---------------------------------------------------------------------------
# Guard: run_loo.py (does not exist until plan 03.2-03)
# ---------------------------------------------------------------------------
try:
    _spec_loo = importlib.util.spec_from_file_location("run_loo", _SCRIPTS_DIR / "run_loo.py")
    _loo = importlib.util.module_from_spec(_spec_loo)
    _spec_loo.loader.exec_module(_loo)
    make_exclude_fn = _loo.make_exclude_fn
    _loo_available = True
except (AttributeError, FileNotFoundError, Exception):
    _loo_available = False

# ---------------------------------------------------------------------------
# Guard: run_judge.py (already exists from Phase 2.4)
# ---------------------------------------------------------------------------
try:
    _spec_judge = importlib.util.spec_from_file_location(
        "run_judge", _SCRIPTS_DIR / "run_judge.py"
    )
    _judge = importlib.util.module_from_spec(_spec_judge)
    _spec_judge.loader.exec_module(_judge)
    parse_judge_output = _judge.parse_judge_output
    _judge_available = True
except (AttributeError, FileNotFoundError, Exception):
    _judge_available = False


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_hit(chunk_id: str, text: str = "some text", score: float = 0.9) -> dict:
    """Return a minimal hit_dict matching the pipeline.py contract."""
    return {
        "rank": 1,
        "chunk_id": chunk_id,
        "score": score,
        "text": text,
        "metadata": {"passage_id": 0},
    }


# ---------------------------------------------------------------------------
# TestLooExcludeFn — DEF-05 make_exclude_fn contract
# ---------------------------------------------------------------------------

class TestLooExcludeFn:
    """Verify the make_exclude_fn factory from run_loo.py.

    Tests skip until plan 03.2-03 creates scripts/run_loo.py.
    Contract: make_exclude_fn(chunk_id) -> Callable[[list[dict]], list[dict]]
    that removes the matching chunk from the list and leaves all others intact.
    """

    def test_exclude_fn_removes_one_chunk(self):
        """make_exclude_fn('c1') must remove the chunk with chunk_id='c1' from a 3-item list."""
        if not _loo_available:
            pytest.skip("run_loo.py not yet created — Wave 1 (plan 03.2-03) not yet implemented")
        chunks = [_make_hit("c0"), _make_hit("c1"), _make_hit("c2")]
        exclude_fn = make_exclude_fn("c1")
        result = exclude_fn(chunks)
        assert len(result) == 2, (
            f"Expected 2 chunks after excluding 'c1', got {len(result)}"
        )
        ids = [c["chunk_id"] for c in result]
        assert "c1" not in ids, "chunk_id 'c1' was not removed by exclude_fn"
        assert "c0" in ids, "chunk_id 'c0' was incorrectly removed"
        assert "c2" in ids, "chunk_id 'c2' was incorrectly removed"

    def test_exclude_fn_removes_nothing_for_unknown_id(self):
        """make_exclude_fn with an unknown ID must return the full list unchanged."""
        if not _loo_available:
            pytest.skip("run_loo.py not yet created — Wave 1 (plan 03.2-03) not yet implemented")
        chunks = [_make_hit("c0"), _make_hit("c1"), _make_hit("c2")]
        exclude_fn = make_exclude_fn("cXXX")
        result = exclude_fn(chunks)
        assert len(result) == 3, (
            f"Expected 3 chunks when excluding unknown ID 'cXXX', got {len(result)}"
        )


# ---------------------------------------------------------------------------
# TestLooJudge — parse_judge_output contract (already exists)
# ---------------------------------------------------------------------------

class TestLooJudge:
    """Verify parse_judge_output() from run_judge.py handles all output cases.

    These tests are green immediately because parse_judge_output was added
    in Phase 2.4 and covers YES/NO/malformed/empty correctly.
    """

    def test_parse_yes(self):
        """'YES' must parse to True."""
        if not _judge_available:
            pytest.skip("run_judge.py not loadable")
        assert parse_judge_output("YES") is True

    def test_parse_no(self):
        """'NO' must parse to False."""
        if not _judge_available:
            pytest.skip("run_judge.py not loadable")
        assert parse_judge_output("NO") is False

    def test_parse_malformed(self):
        """Unexpected output must parse to None."""
        if not _judge_available:
            pytest.skip("run_judge.py not loadable")
        assert parse_judge_output("MAYBE") is None

    def test_parse_empty(self):
        """Empty string must parse to None."""
        if not _judge_available:
            pytest.skip("run_judge.py not loadable")
        assert parse_judge_output("") is None
