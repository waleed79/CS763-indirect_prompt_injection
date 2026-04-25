"""run_eval.py Tier 1b integration contract tests (ATK-01b).

Run with:
    pytest tests/test_eval_tier1b.py -x
"""
from __future__ import annotations

import inspect
import pytest

try:
    from rag.constants import TIER1B_ID_START, TIER1_ID_START, TIER2_ID_START, TIER3_ID_START, TIER4_ID_START
    from scripts.run_eval import TIER1B_HIJACK_STR
    import scripts.run_eval as run_eval_mod
    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _MODULE_AVAILABLE,
    reason="TIER1B_ID_START / TIER1B_HIJACK_STR not yet implemented (Wave 1 ATK-01b plan)",
)


class TestTier1bConstants:
    def test_tier1b_id_start_value(self):
        assert TIER1B_ID_START == 20150

    def test_tier1b_hijack_str_value(self):
        assert TIER1B_HIJACK_STR == "T1B_BREACHED"

    def test_tier_boundaries_are_consistent(self):
        # Ordering must be: T1 < T2 < T3 < T1B < T4
        assert TIER1_ID_START == 20000
        assert TIER2_ID_START == 20050
        assert TIER3_ID_START == 20100
        assert TIER1B_ID_START == 20150
        assert TIER4_ID_START == 20200


class TestT3UpperBoundUpdated:
    def test_run_eval_source_uses_tier1b_id_start_for_t3_upper(self):
        """T3's upper bound must be TIER1B_ID_START (20150), NOT TIER4_ID_START (20200).

        This is the ID-ordering bug flagged in CONTEXT D-04. T1b sits between T3 and T4.
        """
        src = inspect.getsource(run_eval_mod)
        # Expect a line like: tier3_retrieved = any(TIER3_ID_START <= _pid(h) < TIER1B_ID_START ...)
        assert "TIER3_ID_START" in src and "TIER1B_ID_START" in src
        # Reject the old (buggy) pattern where T3 upper bound is TIER4_ID_START
        # Accept either whitespace style; we specifically verify presence of the fixed predicate.
        fixed_pattern_present = "< TIER1B_ID_START" in src
        assert fixed_pattern_present, (
            "tier3_retrieved predicate should use '< TIER1B_ID_START' as upper bound; "
            "old pattern '< TIER4_ID_START' is a correctness bug since T1b sits inside 20150–20199."
        )


class TestTier1bRetrievedFlag:
    def test_tier1b_retrieved_field_appears_in_source(self):
        src = inspect.getsource(run_eval_mod)
        assert "tier1b_retrieved" in src, "run_eval.py must define/emit 'tier1b_retrieved' field"

    def test_hijacked_tier1b_field_appears_in_source(self):
        src = inspect.getsource(run_eval_mod)
        assert "hijacked_tier1b" in src, "run_eval.py must define/emit 'hijacked_tier1b' field"
