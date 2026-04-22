"""Reproducibility tests (RAG-05).

Tests that:
- config.toml loads into a Config with correct values
- requirements.txt pins all 7 core libraries
- load_nq_passages is deterministic across calls with same seed

Run with:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_reproducibility.py -v --timeout=120
"""
import re
from pathlib import Path

import pytest

from rag.config import Config, load_config

# ── 1. Config tests ────────────────────────────────────────────────────────────


class TestConfigLoads:
    def test_config_loads(self):
        """config.toml must load without errors into a populated Config."""
        c = load_config("config.toml")
        assert isinstance(c, Config)

    def test_config_seed_is_42(self):
        c = load_config("config.toml")
        assert c.seed == 42

    def test_config_top_k_is_5(self):
        c = load_config("config.toml")
        assert c.top_k == 5

    def test_config_corpus_size_is_1000(self):
        c = load_config("config.toml")
        assert c.corpus_size == 1000

    def test_config_chunk_words_is_200(self):
        c = load_config("config.toml")
        assert c.chunk_words == 200

    def test_config_overlap_words_is_25(self):
        c = load_config("config.toml")
        assert c.overlap_words == 25

    def test_config_embed_model(self):
        c = load_config("config.toml")
        assert c.embed_model == "nomic-ai/nomic-embed-text-v1.5"

    def test_config_llm_model(self):
        c = load_config("config.toml")
        assert c.llm_model == "mistral:7b"

    def test_config_collection(self):
        c = load_config("config.toml")
        assert c.collection == "nq_clean_v2"

    def test_config_is_frozen(self):
        c = load_config("config.toml")
        with pytest.raises(Exception):  # FrozenInstanceError
            c.seed = 99  # type: ignore[misc]


# ── 2. requirements.txt tests ──────────────────────────────────────────────────


PINNED_PACKAGES = [
    "torch",
    "transformers",
    "sentence-transformers",
    "chromadb",
    "ollama",
    "datasets",
    "pytest",
]


class TestRequirementsPinned:
    def test_requirements_file_exists(self):
        assert Path("requirements.txt").exists(), "requirements.txt not found"

    @pytest.mark.parametrize("package", PINNED_PACKAGES)
    def test_package_is_pinned(self, package):
        """Each core package must appear in requirements.txt with a pinned version."""
        content = Path("requirements.txt").read_text(encoding="utf-8")
        # Match lines like: torch==2.11.0 or sentence-transformers==5.4.0
        pattern = re.compile(
            rf"^{re.escape(package)}==\d+\.\d+", re.MULTILINE | re.IGNORECASE
        )
        assert pattern.search(content), (
            f"'{package}' not found as pinned (==X.Y) in requirements.txt"
        )


# ── 3. Corpus determinism tests ────────────────────────────────────────────────


class TestCorpusDeterminism:
    """These tests download the dataset (~44 MB on first run, then cached)."""

    @pytest.mark.timeout(120)
    def test_load_deterministic_across_calls(self):
        """Same seed must produce the same passages in both calls."""
        from rag.corpus import load_nq_passages

        p1 = load_nq_passages(n=10, seed=42)
        p2 = load_nq_passages(n=10, seed=42)
        assert [p.text for p in p1] == [p.text for p in p2]
        assert [p.passage_id for p in p1] == [p.passage_id for p in p2]

    @pytest.mark.timeout(120)
    def test_different_seeds_differ(self):
        """Different seeds must produce different ordering."""
        from rag.corpus import load_nq_passages

        p_42 = load_nq_passages(n=10, seed=42)
        p_99 = load_nq_passages(n=10, seed=99)
        # Very unlikely to match for the first 10 items
        assert [p.text for p in p_42] != [p.text for p in p_99]
