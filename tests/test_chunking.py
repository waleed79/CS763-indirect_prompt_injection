"""Unit tests for rag/corpus.py :: chunk_text() boundary cases.

Run with:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_chunking.py -v --timeout=30
"""
import pytest

from rag.corpus import chunk_text


class TestChunkTextEmpty:
    def test_empty_string_returns_empty_list(self):
        assert chunk_text("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert chunk_text("   \n\t  ") == []


class TestChunkTextShortPassage:
    def test_short_text_single_chunk(self):
        text = " ".join(["word"] * 50)
        result = chunk_text(text, chunk_words=200, overlap_words=25)
        assert len(result) == 1
        assert result[0] == text

    def test_exact_chunk_size_single_chunk(self):
        text = " ".join(["word"] * 200)
        result = chunk_text(text, chunk_words=200, overlap_words=25)
        assert len(result) == 1

    def test_one_word_single_chunk(self):
        result = chunk_text("hello", chunk_words=200, overlap_words=25)
        assert result == ["hello"]


class TestChunkTextMultiChunk:
    def test_long_text_produces_multiple_chunks(self):
        text = " ".join(["word"] * 400)
        result = chunk_text(text, chunk_words=200, overlap_words=25)
        # stride = 175 words; 400 words → at least 2 chunks
        assert len(result) >= 2

    def test_chunk_word_count_at_most_chunk_words(self):
        text = " ".join([f"w{i}" for i in range(500)])
        result = chunk_text(text, chunk_words=200, overlap_words=25)
        for chunk in result:
            assert len(chunk.split()) <= 200

    def test_overlap_content_preserved(self):
        """Last overlap_words words of chunk[i] == first overlap_words of chunk[i+1]."""
        words = [f"w{i}" for i in range(600)]
        text = " ".join(words)
        chunks = chunk_text(text, chunk_words=200, overlap_words=25)
        assert len(chunks) >= 2
        tail = chunks[0].split()[-25:]
        head = chunks[1].split()[:25]
        assert tail == head

    def test_last_chunk_ends_at_text_boundary(self):
        """The last chunk must end with the last word of the input."""
        words = [f"w{i}" for i in range(380)]
        text = " ".join(words)
        chunks = chunk_text(text, chunk_words=200, overlap_words=25)
        assert chunks[-1].split()[-1] == words[-1]

    def test_all_words_covered(self):
        """Every word in the input appears in at least one chunk."""
        words = [f"w{i}" for i in range(450)]
        text = " ".join(words)
        chunks = chunk_text(text, chunk_words=200, overlap_words=25)
        covered = set()
        for chunk in chunks:
            covered.update(chunk.split())
        assert covered == set(words)

    def test_no_empty_chunks(self):
        text = " ".join(["word"] * 300)
        chunks = chunk_text(text, chunk_words=200, overlap_words=25)
        assert all(len(c) > 0 for c in chunks)
