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
