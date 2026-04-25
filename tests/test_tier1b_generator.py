"""Tier 1b homoglyph payload generator contract tests (ATK-01b).

Run with:
    pytest tests/test_tier1b_generator.py -x
"""
from __future__ import annotations

import pytest

# Lazy import guard: allow pytest collection before Wave 1 implements the module.
try:
    from scripts.generate_poisoned_corpus import (
        HOMOGLYPH_HACKED,
        build_tier1b_passages,
    )
    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _MODULE_AVAILABLE,
    reason="scripts.generate_poisoned_corpus.build_tier1b_passages not yet implemented (Wave 1 ATK-01b plan)",
)


class TestCodepoints:
    def test_homoglyph_hacked_length(self):
        assert len(HOMOGLYPH_HACKED) == 6

    def test_homoglyph_codepoints(self):
        # Verified Cyrillic codepoints for H/A/C/K/E/D visual lookalikes
        expected = [1053, 1040, 1057, 1050, 1045, 1044]
        actual = [ord(ch) for ch in HOMOGLYPH_HACKED]
        assert actual == expected, f"expected {expected}, got {actual}"

    def test_homoglyph_is_not_ascii_hacked(self):
        assert HOMOGLYPH_HACKED != "HACKED"
        assert "HACKED" not in HOMOGLYPH_HACKED


class TestTier1bPassages:
    @pytest.fixture(scope="class")
    def passages(self):
        return build_tier1b_passages()

    def test_count_50(self, passages):
        assert len(passages) == 50, f"expected 50 Tier 1b passages, got {len(passages)}"

    def test_ids_in_range(self, passages):
        for p in passages:
            assert 20150 <= p.passage_id <= 20199, f"id {p.passage_id} outside T1b range"

    def test_ids_unique(self, passages):
        ids = [p.passage_id for p in passages]
        assert len(set(ids)) == len(ids)

    def test_hacked_ascii_absent(self, passages):
        for p in passages:
            assert "HACKED" not in p.text, (
                f"Passage {p.passage_id} contains ASCII 'HACKED' — homoglyph substitution failed"
            )

    def test_cyrillic_homoglyph_present(self, passages):
        for p in passages:
            assert HOMOGLYPH_HACKED in p.text, (
                f"Passage {p.passage_id} missing Cyrillic homoglyph '{HOMOGLYPH_HACKED}'"
            )

    def test_output_marker_present(self, passages):
        for p in passages:
            assert "T1B_BREACHED" in p.text, (
                f"Passage {p.passage_id} missing ASCII output marker 'T1B_BREACHED'"
            )
