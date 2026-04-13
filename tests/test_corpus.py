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
