"""Unit and integration tests for rag/retriever.py.

Unit tests use a tiny in-memory corpus — no HF download required.
Integration tests (marked slow) index a small subset of real NQ data.

Run unit tests only:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_retriever.py -v -m "not slow" --timeout=60
Run full suite:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_retriever.py -v --timeout=300
"""
import pytest

from rag.corpus import Passage
from rag.retriever import RetrievalResult, Retriever


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def tiny_passages() -> list[Passage]:
    """5 short passages — fits in memory, fast to embed."""
    texts = [
        "Python is a high-level programming language known for readability.",
        "Machine learning is a subset of artificial intelligence.",
        "The Eiffel Tower is located in Paris, France.",
        "Water boils at 100 degrees Celsius at standard pressure.",
        "Shakespeare wrote Hamlet, Macbeth, and King Lear.",
    ]
    return [Passage(passage_id=i, query=f"q{i}", text=t) for i, t in enumerate(texts)]


@pytest.fixture(scope="module")
def indexed_retriever(tmp_path_factory, tiny_passages):
    """Retriever with the tiny passage set indexed (module-scoped for speed)."""
    chroma_dir = str(tmp_path_factory.mktemp("chroma"))
    r = Retriever(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        collection_name="test_tiny",
        chroma_path=chroma_dir,
        top_k=3,
    )
    r.index(tiny_passages, chunk_words=50, overlap_words=5)
    return r


# ── RetrievalResult ───────────────────────────────────────────────────────────


class TestRetrievalResultInterface:
    def test_is_named_tuple(self):
        r = RetrievalResult(chunk_id="c-0", text="hello", score=0.9, metadata={})
        assert isinstance(r, tuple)

    def test_fields_accessible(self):
        r = RetrievalResult(chunk_id="c-1", text="world", score=0.75, metadata={"x": 1})
        assert r.chunk_id == "c-1"
        assert r.text == "world"
        assert r.score == 0.75
        assert r.metadata == {"x": 1}


# ── Retriever unit tests (no network) ────────────────────────────────────────


class TestRetrieverInit:
    def test_init_creates_chroma_collection(self, tmp_path):
        r = Retriever(
            collection_name="init_test",
            chroma_path=str(tmp_path / "chroma"),
            top_k=3,
        )
        assert r.count == 0

    def test_index_empty_passages(self, tmp_path):
        r = Retriever(
            collection_name="empty_test",
            chroma_path=str(tmp_path / "chroma"),
        )
        total = r.index([], chunk_words=200, overlap_words=25)
        assert total == 0


class TestRetrieverIndexing:
    @pytest.mark.timeout(60)
    def test_index_produces_chunks(self, tmp_path, tiny_passages):
        r = Retriever(
            collection_name="idx_test",
            chroma_path=str(tmp_path / "chroma"),
            top_k=3,
        )
        # All 5 passages are short (<50 words) → 1 chunk each → 5 total
        total = r.index(tiny_passages, chunk_words=50, overlap_words=5)
        assert total == 5

    @pytest.mark.timeout(60)
    def test_index_is_idempotent(self, tmp_path, tiny_passages):
        """Calling index() twice must not duplicate chunks."""
        r = Retriever(
            collection_name="idem_test",
            chroma_path=str(tmp_path / "chroma"),
            top_k=3,
        )
        total1 = r.index(tiny_passages, chunk_words=50, overlap_words=5)
        total2 = r.index(tiny_passages, chunk_words=50, overlap_words=5)
        assert total1 == total2


class TestRetrieverRetrieval:
    @pytest.mark.timeout(60)
    def test_retrieve_returns_top_k(self, indexed_retriever):
        results = indexed_retriever.retrieve("programming language")
        assert len(results) == 3

    @pytest.mark.timeout(60)
    def test_retrieve_scores_in_range(self, indexed_retriever):
        """Cosine similarity scores must be in [0, 1]."""
        results = indexed_retriever.retrieve("Paris France")
        for r in results:
            assert 0.0 <= r.score <= 1.0, f"Score out of range: {r.score}"

    @pytest.mark.timeout(60)
    def test_retrieve_sorted_descending(self, indexed_retriever):
        results = indexed_retriever.retrieve("boiling point of water")
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.timeout(60)
    def test_retrieve_top1_semantically_relevant(self, indexed_retriever):
        """Best hit for a Shakespeare query should mention Shakespeare."""
        results = indexed_retriever.retrieve("who wrote Hamlet?")
        assert len(results) >= 1
        assert "Shakespeare" in results[0].text

    @pytest.mark.timeout(60)
    def test_retrieve_result_has_metadata(self, indexed_retriever):
        results = indexed_retriever.retrieve("machine learning AI")
        for r in results:
            assert "passage_id" in r.metadata
            assert "chunk_idx" in r.metadata

    @pytest.mark.timeout(60)
    def test_chunk_ids_are_strings(self, indexed_retriever):
        results = indexed_retriever.retrieve("Eiffel Tower")
        for r in results:
            assert isinstance(r.chunk_id, str)
            assert r.chunk_id.startswith("chunk_")
