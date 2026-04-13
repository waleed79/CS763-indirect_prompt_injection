"""Unit tests for rag/logger.py — JSONL writer round-trip and append mode.

Run with:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_logger.py -v --timeout=30
"""
import json
from pathlib import Path

import pytest

from rag.logger import RetrievalLogger


def _make_results(n: int = 2) -> list[dict]:
    return [
        {
            "rank": i + 1,
            "chunk_id": f"chunk_{i:05d}",
            "score": round(0.9 - i * 0.05, 4),
            "text": f"Sample chunk text {i}.",
            "metadata": {"passage_id": i, "chunk_idx": 0},
        }
        for i in range(n)
    ]


class TestRetrievalLoggerBasic:
    def test_log_creates_file(self, tmp_path):
        log_path = tmp_path / "logs" / "test.jsonl"
        logger = RetrievalLogger(path=str(log_path))
        logger.log(query="q", top_k=5, collection="col", results=_make_results())
        logger.close()
        assert log_path.exists()

    def test_log_creates_parent_dirs(self, tmp_path):
        log_path = tmp_path / "deeply" / "nested" / "test.jsonl"
        logger = RetrievalLogger(path=str(log_path))
        logger.log(query="q", top_k=5, collection="col", results=[])
        logger.close()
        assert log_path.exists()

    def test_log_writes_valid_json_line(self, tmp_path):
        log_path = tmp_path / "test.jsonl"
        logger = RetrievalLogger(path=str(log_path))
        logger.log(query="who is Alan Turing?", top_k=5, collection="nq_clean_v1", results=_make_results(2))
        logger.close()
        line = log_path.read_text(encoding="utf-8").strip()
        record = json.loads(line)   # must not raise
        assert record["query"] == "who is Alan Turing?"
        assert record["top_k"] == 5
        assert record["collection"] == "nq_clean_v1"
        assert len(record["results"]) == 2

    def test_log_has_timestamp(self, tmp_path):
        log_path = tmp_path / "test.jsonl"
        logger = RetrievalLogger(path=str(log_path))
        logger.log(query="q", top_k=3, collection="col", results=[])
        logger.close()
        record = json.loads(log_path.read_text())
        assert "timestamp" in record
        assert "T" in record["timestamp"]   # ISO-8601

    def test_result_schema(self, tmp_path):
        log_path = tmp_path / "test.jsonl"
        logger = RetrievalLogger(path=str(log_path))
        logger.log(query="q", top_k=2, collection="col", results=_make_results(2))
        logger.close()
        record = json.loads(log_path.read_text())
        for hit in record["results"]:
            assert "rank" in hit
            assert "chunk_id" in hit
            assert "score" in hit
            assert "text" in hit
            assert "metadata" in hit


class TestRetrievalLoggerAppendMode:
    def test_append_preserves_prior_lines(self, tmp_path):
        """Second logger instance must not overwrite existing records."""
        log_path = tmp_path / "test.jsonl"

        logger1 = RetrievalLogger(path=str(log_path))
        logger1.log(query="first", top_k=5, collection="col", results=_make_results(1))
        logger1.close()

        logger2 = RetrievalLogger(path=str(log_path))
        logger2.log(query="second", top_k=5, collection="col", results=_make_results(1))
        logger2.close()

        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["query"] == "first"
        assert json.loads(lines[1])["query"] == "second"

    def test_multiple_logs_each_on_own_line(self, tmp_path):
        log_path = tmp_path / "test.jsonl"
        logger = RetrievalLogger(path=str(log_path))
        for i in range(5):
            logger.log(query=f"q{i}", top_k=3, collection="col", results=[])
        logger.close()
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 5
        for i, line in enumerate(lines):
            assert json.loads(line)["query"] == f"q{i}"

    def test_all_lines_are_valid_json(self, tmp_path):
        log_path = tmp_path / "test.jsonl"
        logger = RetrievalLogger(path=str(log_path))
        for _ in range(10):
            logger.log(query="q", top_k=5, collection="col", results=_make_results(3))
        logger.close()
        for line in log_path.read_text(encoding="utf-8").strip().splitlines():
            json.loads(line)   # must not raise
