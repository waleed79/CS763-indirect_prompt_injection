"""Tests for rag/corpus.py — Passage NamedTuple, load_nq_passages, chunk_text, persist/load.

The corpus load tests download sentence-transformers/natural-questions (~44 MB)
on first run — cached in ~/.cache/huggingface/ for subsequent runs.

Run with:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_corpus.py -v --timeout=120
"""
import json
import tempfile
from pathlib import Path

import pytest

from rag.corpus import (
    Passage,
    chunk_text,
    load_nq_passages,
    load_passages_from_jsonl,
    persist_passages,
)


class TestPassageDataclass:
    def test_passage_has_required_fields(self):
        p = Passage(passage_id=0, query="who is alan turing?", text="Turing was a mathematician.")
        assert p.passage_id == 0
        assert p.query == "who is alan turing?"
        assert p.text == "Turing was a mathematician."

    def test_passage_is_named_tuple(self):
        p = Passage(passage_id=1, query="q", text="t")
        assert isinstance(p, tuple)
        d = p._asdict()
        assert set(d.keys()) == {"passage_id", "query", "text"}


class TestPersistAndLoad:
    def test_persist_creates_jsonl(self, tmp_path):
        passages = [
            Passage(passage_id=i, query=f"q{i}", text=f"text {i}")
            for i in range(5)
        ]
        out = persist_passages(passages, path=tmp_path / "out.jsonl")
        assert out.exists()
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 5

    def test_persist_valid_json_lines(self, tmp_path):
        passages = [Passage(passage_id=0, query="q", text="t")]
        out = persist_passages(passages, path=tmp_path / "out.jsonl")
        record = json.loads(out.read_text().strip())
        assert record["passage_id"] == 0
        assert record["query"] == "q"
        assert record["text"] == "t"

    def test_load_roundtrip(self, tmp_path):
        passages = [Passage(passage_id=i, query=f"q{i}", text=f"t{i}") for i in range(10)]
        path = tmp_path / "data.jsonl"
        persist_passages(passages, path=path)
        loaded = load_passages_from_jsonl(path)
        assert len(loaded) == 10
        for orig, reloaded in zip(passages, loaded):
            assert orig == reloaded


class TestLoadNqPassages:
    """These tests download the NQ dataset on first run (~44 MB, cached)."""

    @pytest.mark.timeout(120)
    def test_load_500_unique(self):
        """Corpus loader must return exactly 500 unique passages."""
        passages = load_nq_passages(n=500, seed=42)
        assert len(passages) == 500
        texts = [p.text for p in passages]
        assert len(set(texts)) == 500, "Passages are not unique"

    @pytest.mark.timeout(120)
    def test_load_deterministic_across_calls(self):
        """Same n + same seed → same passages."""
        p1 = load_nq_passages(n=10, seed=42)
        p2 = load_nq_passages(n=10, seed=42)
        assert [p.text for p in p1] == [p.text for p in p2]

    @pytest.mark.timeout(120)
    def test_passage_ids_sequential(self):
        passages = load_nq_passages(n=5, seed=42)
        assert [p.passage_id for p in passages] == list(range(5))

    @pytest.mark.timeout(120)
    def test_passages_have_nonempty_text(self):
        passages = load_nq_passages(n=10, seed=42)
        for p in passages:
            assert p.text.strip(), f"Empty text for passage_id={p.passage_id}"


# ── Phase 2.4 corpus validation ───────────────────────────────────────────────

CORPUS_POISONED_PATH = Path("data/corpus_poisoned.jsonl")
T3_PAYLOADS_PATH = Path("data/t3_payloads.jsonl")


@pytest.mark.skipif(not CORPUS_POISONED_PATH.exists(), reason="corpus_poisoned.jsonl not yet generated")
class TestPoisonedCorpusTier3:
    """Tier 3 passages: IDs 20100–20149, each containing anchor token."""

    def test_tier3_ids_in_range(self):
        """Exactly 50 Tier 3 passages with passage_id in [20100, 20149]."""
        passages = load_passages_from_jsonl(CORPUS_POISONED_PATH)
        tier3 = [p for p in passages if 20100 <= p.passage_id <= 20149]
        assert len(tier3) == 50, f"Expected 50 Tier 3 passages, found {len(tier3)}"

    def test_tier3_anchor_present(self):
        """Every Tier 3 passage text must contain 't3.evilcorp.io'."""
        passages = load_passages_from_jsonl(CORPUS_POISONED_PATH)
        tier3 = [p for p in passages if 20100 <= p.passage_id <= 20149]
        assert len(tier3) > 0, "No Tier 3 passages found — run generate_poisoned_corpus.py first"
        for p in tier3:
            assert "t3.evilcorp.io" in p.text, (
                f"Anchor absent in passage_id={p.passage_id}: {p.text[:120]!r}"
            )

    def test_tier1b_ids_in_range(self):
        """IDs 20150–20199 are Phase 3.3 Tier 1b (homoglyph ATK-01b) — must contain exactly 50 passages."""
        passages = load_passages_from_jsonl(CORPUS_POISONED_PATH)
        tier1b = [p for p in passages if 20150 <= p.passage_id <= 20199]
        assert len(tier1b) == 50, (
            f"Expected 50 Tier 1b passages in range 20150–20199, found {len(tier1b)}"
        )
        for p in tier1b:
            assert "T1B_BREACHED" in p.text, (
                f"Tier 1b passage {p.passage_id} missing T1B_BREACHED output marker"
            )
            assert "HACKED" not in p.text, (
                f"Tier 1b passage {p.passage_id} contains ASCII 'HACKED' — homoglyph substitution failed"
            )


@pytest.mark.skipif(not CORPUS_POISONED_PATH.exists(), reason="corpus_poisoned.jsonl not yet generated")
class TestPoisonedCorpusTier4:
    """Tier 4 passages: IDs 20200–20299, exactly 3 contiguous fragments per attack set."""

    def test_tier4_ids_in_range(self):
        """At least 9 Tier 4 passages (3 sets × 3 fragments) with passage_id in [20200, 20299]."""
        passages = load_passages_from_jsonl(CORPUS_POISONED_PATH)
        tier4 = [p for p in passages if 20200 <= p.passage_id <= 20299]
        assert len(tier4) >= 9, f"Expected at least 9 Tier 4 passages, found {len(tier4)}"
        assert len(tier4) % 3 == 0, f"Tier 4 passage count must be multiple of 3, got {len(tier4)}"

    def test_tier4_three_fragments_per_set(self):
        """Each attack set must have exactly 3 contiguous passage IDs starting at a multiple-of-3 offset."""
        passages = load_passages_from_jsonl(CORPUS_POISONED_PATH)
        tier4 = sorted([p for p in passages if 20200 <= p.passage_id <= 20299], key=lambda p: p.passage_id)
        assert len(tier4) >= 9, "Need at least 3 complete sets"
        # IDs should be contiguous: 20200, 20201, 20202, 20203, 20204, 20205, ...
        ids = [p.passage_id for p in tier4]
        for i in range(len(ids)):
            assert ids[i] == 20200 + i, f"Gap in Tier 4 IDs at index {i}: expected {20200 + i}, got {ids[i]}"

    def test_tier4_anchor_present(self):
        """Every Tier 4 Fragment C (IDs 20202, 20205, 20208, ...) must contain 't4.evilcorp.io'."""
        passages = load_passages_from_jsonl(CORPUS_POISONED_PATH)
        tier4 = sorted([p for p in passages if 20200 <= p.passage_id <= 20299], key=lambda p: p.passage_id)
        # Fragment C is index 2 of each set (0-indexed): 20202, 20205, 20208, ...
        fragment_cs = [p for i, p in enumerate(tier4) if i % 3 == 2]
        assert len(fragment_cs) > 0, "No Fragment C passages found"
        for p in fragment_cs:
            assert "t4.evilcorp.io" in p.text, (
                f"Anchor 't4.evilcorp.io' absent in Fragment C passage_id={p.passage_id}: {p.text[:120]!r}"
            )


# ── Phase 3.2 adaptive attack corpus validation ───────────────────────────────

import importlib.util as _importlib_util
import sys as _sys
from pathlib import Path as _Path

_SCRIPTS_DIR = _Path(__file__).parent.parent / "scripts"

try:
    _spec = _importlib_util.spec_from_file_location(
        "generate_poisoned_corpus",
        _SCRIPTS_DIR / "generate_poisoned_corpus.py",
    )
    _gpc = _importlib_util.module_from_spec(_spec)
    _spec.loader.exec_module(_gpc)
    ADAPTIVE_ID_START = _gpc.ADAPTIVE_ID_START
    NOVEL_ANCHOR_TOKENS = _gpc.NOVEL_ANCHOR_TOKENS
    build_adaptive_passages = _gpc.build_adaptive_passages
    _adaptive_available = True
except (AttributeError, FileNotFoundError, Exception):
    _adaptive_available = False


class TestAdaptiveCorpus:
    """Phase 3.2 ATK-08/09 adaptive payload corpus validation.

    All tests skip until plan 03.2-02 adds ADAPTIVE_ID_START, NOVEL_ANCHOR_TOKENS,
    and build_adaptive_passages() to generate_poisoned_corpus.py.
    """

    def test_adaptive_id_range(self):
        """All adaptive passages must have passage_id in [ADAPTIVE_ID_START, ADAPTIVE_ID_START+99].

        Ensures ATK-08/09 entries occupy the reserved 20500–20599 block and do not
        collide with earlier tiers (T1: 20000–20049, T2: 20050–20099,
        T3: 20100–20149, T1b: 20150–20199, T4: 20200–20299, gap: 20300–20499).
        """
        if not _adaptive_available:
            pytest.skip("generate_poisoned_corpus missing adaptive symbols — Wave 1 not yet implemented")
        passages = build_adaptive_passages()
        assert len(passages) >= 10, (
            f"Expected at least 10 adaptive passages (5 novel anchors × 2 variants + declarative), "
            f"found {len(passages)}"
        )
        for p in passages:
            assert p.passage_id >= ADAPTIVE_ID_START, (
                f"Passage {p.passage_id} below ADAPTIVE_ID_START={ADAPTIVE_ID_START}"
            )
            assert p.passage_id < ADAPTIVE_ID_START + 100, (
                f"Passage {p.passage_id} above reserved block end {ADAPTIVE_ID_START + 99}"
            )

    def test_atk08_no_trained_anchors(self):
        """ATK-08 novel anchor tokens must not overlap the 5 trained Tier-1 tokens.

        Rationale: if novel tokens appear in training data the BERT classifier has
        already memorized them; using them produces no adaptive evasion signal.
        Each novel token must also appear in at least one adaptive passage.
        """
        if not _adaptive_available:
            pytest.skip("generate_poisoned_corpus missing adaptive symbols — Wave 1 not yet implemented")
        assert len(NOVEL_ANCHOR_TOKENS) >= 3, (
            f"Expected at least 3 novel anchor tokens, found {len(NOVEL_ANCHOR_TOKENS)}"
        )
        # TIER1_KEYWORDS is importable because generate_poisoned_corpus was loaded above
        tier1_keywords = _gpc.TIER1_KEYWORDS
        for token in NOVEL_ANCHOR_TOKENS:
            assert token not in tier1_keywords, (
                f"Novel anchor token '{token}' is in TIER1_KEYWORDS — not novel"
            )
        passages = build_adaptive_passages()
        for token in NOVEL_ANCHOR_TOKENS:
            found = any(token in p.text for p in passages)
            assert found, (
                f"Novel anchor token '{token}' does not appear in any adaptive passage"
            )

    def test_atk09_no_imperative_verbs(self):
        """ATK-09 declarative passages must contain zero imperative verbs.

        ATK-09 tests single-chunk imperative-ratio bypass: passages carry an existing
        Tier-1 anchor token but are written in fully declarative style with no
        imperative verbs — bypassing the IMPERATIVE_VERBS heuristic signal.

        The ATK-09 entries are declarative passages that still contain one of the
        TIER1_KEYWORDS but do NOT contain any NOVEL_ANCHOR_TOKEN (those are ATK-08).
        """
        if not _adaptive_available:
            pytest.skip("generate_poisoned_corpus missing adaptive symbols — Wave 1 not yet implemented")
        from rag.defense import IMPERATIVE_VERBS
        tier1_keywords = _gpc.TIER1_KEYWORDS
        passages = build_adaptive_passages()
        # ATK-09 entries: contain a Tier-1 keyword but no novel anchor token
        atk09_entries = [
            p for p in passages
            if any(kw in p.text for kw in tier1_keywords)
            and not any(token in p.text for token in NOVEL_ANCHOR_TOKENS)
        ]
        assert len(atk09_entries) > 0, (
            "No ATK-09 declarative entries found — build_adaptive_passages() must return "
            "at least one passage that has a Tier-1 keyword but no novel anchor token"
        )
        for p in atk09_entries:
            assert not bool(IMPERATIVE_VERBS.search(p.text)), (
                f"ATK-09 passage {p.passage_id} contains imperative verb(s) — "
                f"must be fully declarative: {p.text[:120]!r}"
            )
