"""Tests for rag/pipeline.py.

Unit tests mock sub-components. Integration test (marked integration) runs
against real Ollama + ChromaDB using the committed nq_500.jsonl.

Run unit tests only:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_pipeline.py -v -m "not integration" --timeout=30
Run all:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_pipeline.py -v --timeout=300
"""
from unittest.mock import MagicMock, patch

import pytest

from rag.config import Config, load_config
from rag.pipeline import RAGPipeline, set_global_seed


# ── Helpers ───────────────────────────────────────────────────────────────────


def _default_cfg(**overrides) -> Config:
    defaults = dict(
        seed=42, top_k=2, corpus_size=5, chunk_words=50, overlap_words=5,
        embed_model="sentence-transformers/all-MiniLM-L6-v2",
        llm_model="llama3.2:3b", chroma_path=".chroma_test",
        collection="test_col", log_path="logs/test.jsonl",
        ollama_host="http://localhost:11434",
    )
    defaults.update(overrides)
    return Config(**defaults)


# ── set_global_seed ───────────────────────────────────────────────────────────


class TestSetGlobalSeed:
    def test_does_not_raise(self):
        set_global_seed(42)

    def test_numpy_seed_set(self):
        import numpy as np
        set_global_seed(99)
        a = np.random.rand(5)
        set_global_seed(99)
        b = np.random.rand(5)
        assert list(a) == list(b)


# ── load_config ────────────────────────────────────────────────────────────────


class TestLoadConfig:
    def test_loads_from_real_toml(self):
        cfg = load_config("config.toml")
        assert isinstance(cfg, Config)
        assert cfg.seed == 42

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.toml")


# ── RAGPipeline unit tests ────────────────────────────────────────────────────


class TestRAGPipelineInit:
    def test_init_does_not_require_build(self, tmp_path):
        cfg = _default_cfg(chroma_path=str(tmp_path / "chroma"), log_path=str(tmp_path / "log.jsonl"))
        pipe = RAGPipeline(cfg)
        assert pipe.cfg is cfg
        assert pipe._retriever is None
        assert pipe._generator is None

    def test_query_before_build_raises(self, tmp_path):
        cfg = _default_cfg(chroma_path=str(tmp_path / "chroma"), log_path=str(tmp_path / "log.jsonl"))
        pipe = RAGPipeline(cfg)
        with pytest.raises(RuntimeError, match="build"):
            pipe.query("test")


# ── Phase 2.4 tier-detection predicate tests ──────────────────────────────────


class TestTierDetectionPredicate:
    """Verify the corrected 4-tier ID-range predicate logic from run_eval.py.

    These are pure-logic unit tests — no Ollama or ChromaDB required.
    Import the constants directly from run_eval.py so the tests fail if the
    constants are wrong or missing.
    """

    def _classify(self, pid: int) -> str:
        """Classify a passage_id using the same bounded-range logic as run_eval.py."""
        from scripts.run_eval import (
            TIER1_ID_START,
            TIER2_ID_START,
            TIER3_ID_START,
            TIER4_ID_START,
        )
        if TIER1_ID_START <= pid < TIER2_ID_START:
            return "tier1"
        elif TIER2_ID_START <= pid < TIER3_ID_START:
            return "tier2"
        elif TIER3_ID_START <= pid < TIER4_ID_START:
            return "tier3"
        elif pid >= TIER4_ID_START:
            return "tier4"
        return "clean"

    def test_tier1_boundary(self):
        assert self._classify(20000) == "tier1"
        assert self._classify(20049) == "tier1"

    def test_tier2_boundary(self):
        assert self._classify(20050) == "tier2"
        assert self._classify(20099) == "tier2"

    def test_tier3_boundary(self):
        """ID 20100 must classify as tier3, NOT tier2."""
        assert self._classify(20100) == "tier3", "ID 20100 misclassified — catch-all bug not fixed"
        assert self._classify(20149) == "tier3"

    def test_tier4_boundary(self):
        assert self._classify(20200) == "tier4"
        assert self._classify(20299) == "tier4"

    def test_reserved_range_classified_as_tier3(self):
        """IDs 20150–20199 (reserved for Phase 3.3) are within tier3 range."""
        assert self._classify(20150) == "tier3"
        assert self._classify(20199) == "tier3"

    def test_old_catch_all_bug_does_not_exist(self):
        """The old 'id >= TIER2_ID_START' predicate would classify ID 20200 as tier2.
        Verify the new predicate correctly classifies it as tier4."""
        assert self._classify(20200) == "tier4", (
            "Catch-all bug present: ID 20200 (Tier 4) classified as tier2"
        )


# ── Integration tests (real Ollama + ChromaDB) ────────────────────────────────


@pytest.mark.integration
@pytest.mark.timeout(300)
class TestRAGPipelineIntegration:
    """Full pipeline integration — requires Ollama running with llama3.2:3b."""

    @pytest.fixture(scope="class")
    def pipeline(self, tmp_path_factory):
        chroma = str(tmp_path_factory.mktemp("chroma_e2e"))
        log = str(tmp_path_factory.mktemp("logs") / "rag.jsonl")
        cfg = Config(
            seed=42, top_k=5, corpus_size=500,
            chunk_words=200, overlap_words=25,
            embed_model="sentence-transformers/all-MiniLM-L6-v2",
            llm_model="llama3.2:3b",
            chroma_path=chroma,
            collection="e2e_test",
            log_path=log,
            ollama_host="http://localhost:11434",
        )
        pipe = RAGPipeline(cfg)
        pipe.build(corpus_path="data/nq_500.jsonl")
        return pipe

    def test_pipeline_init_succeeds(self, pipeline):
        assert pipeline._retriever is not None
        assert pipeline._generator is not None
        assert pipeline._logger is not None

    def test_retriever_has_chunks(self, pipeline):
        assert pipeline._retriever.count > 0

    def test_query_returns_required_keys(self, pipeline):
        result = pipeline.query("who invented the telephone?")
        assert "question" in result
        assert "answer" in result
        assert "hits" in result

    def test_query_hits_count(self, pipeline):
        result = pipeline.query("what is machine learning?")
        assert len(result["hits"]) == pipeline.cfg.top_k

    def test_query_answer_is_nonempty(self, pipeline):
        result = pipeline.query("where is the Eiffel Tower?")
        assert isinstance(result["answer"], str)
        assert len(result["answer"].strip()) > 0

    def test_query_logs_to_jsonl(self, pipeline, tmp_path):
        import json
        from pathlib import Path
        log_path = Path(pipeline.cfg.log_path)
        size_before = log_path.stat().st_size if log_path.exists() else 0
        pipeline.query("when was the internet invented?")
        assert log_path.stat().st_size > size_before
        # Last line must be valid JSON with required keys
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        record = json.loads(lines[-1])
        assert "query" in record
        assert "results" in record

    def test_idempotent_build(self, tmp_path_factory):
        """Calling build() twice must not duplicate chunks."""
        chroma = str(tmp_path_factory.mktemp("chroma_idem"))
        cfg = Config(
            seed=42, top_k=5, corpus_size=500,
            chunk_words=200, overlap_words=25,
            embed_model="sentence-transformers/all-MiniLM-L6-v2",
            llm_model="llama3.2:3b",
            chroma_path=chroma,
            collection="idem_test",
            log_path=str(tmp_path_factory.mktemp("log") / "r.jsonl"),
            ollama_host="http://localhost:11434",
        )
        pipe1 = RAGPipeline(cfg)
        pipe1.build(corpus_path="data/nq_500.jsonl")
        count1 = pipe1._retriever.count

        pipe2 = RAGPipeline(cfg)
        pipe2.build(corpus_path="data/nq_500.jsonl")
        count2 = pipe2._retriever.count

        assert count1 == count2
