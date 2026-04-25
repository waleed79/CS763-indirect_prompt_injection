"""EVAL-06 Retriever prefix-injection contract tests.

Run with:
    pytest tests/test_retriever_prefix.py -x
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

try:
    from rag.retriever import (
        _DOCUMENT_PREFIXES,
        _QUERY_PREFIXES,
        Retriever,
    )
    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _MODULE_AVAILABLE,
    reason="rag.retriever._DOCUMENT_PREFIXES / _QUERY_PREFIXES not yet implemented (Wave 1 EVAL-06 plan)",
)

NOMIC = "nomic-ai/nomic-embed-text-v1.5"
MXBAI = "mixedbread-ai/mxbai-embed-large-v1"
MINILM = "sentence-transformers/all-MiniLM-L6-v2"


class TestPrefixTables:
    def test_nomic_doc_prefix(self):
        assert _DOCUMENT_PREFIXES[NOMIC] == "search_document: "

    def test_nomic_query_prefix(self):
        assert _QUERY_PREFIXES[NOMIC] == "search_query: "

    def test_mxbai_query_prefix(self):
        assert (
            _QUERY_PREFIXES[MXBAI]
            == "Represent this sentence for searching relevant passages: "
        )

    def test_mxbai_doc_prefix_empty(self):
        assert _DOCUMENT_PREFIXES[MXBAI] == ""

    def test_minilm_no_prefix(self):
        assert _DOCUMENT_PREFIXES[MINILM] == ""
        assert _QUERY_PREFIXES[MINILM] == ""


class TestRetrieverInitStoresPrefixes:
    @patch("rag.retriever.SentenceTransformer")
    @patch("rag.retriever.chromadb.PersistentClient")
    def test_nomic_retriever_has_prefixes(self, mock_client, mock_st):
        mock_st.return_value = MagicMock()
        mock_client.return_value = MagicMock()
        r = Retriever(model_name=NOMIC, collection_name="tmp", chroma_path="/tmp/x")
        assert r._doc_prefix == "search_document: "
        assert r._query_prefix == "search_query: "

    @patch("rag.retriever.SentenceTransformer")
    @patch("rag.retriever.chromadb.PersistentClient")
    def test_minilm_retriever_has_empty_prefixes(self, mock_client, mock_st):
        mock_st.return_value = MagicMock()
        mock_client.return_value = MagicMock()
        r = Retriever(model_name=MINILM, collection_name="tmp", chroma_path="/tmp/x")
        assert r._doc_prefix == ""
        assert r._query_prefix == ""


class TestEncodeApplication:
    @patch("rag.retriever.SentenceTransformer")
    @patch("rag.retriever.chromadb.PersistentClient")
    def test_query_prefix_applied_at_retrieve_time(self, mock_client, mock_st):
        fake_encoder = MagicMock()
        # encode returns a 1x4 numpy-like stand-in; retrieve code takes [0]
        import numpy as np
        fake_encoder.encode.return_value = np.array([[0.1, 0.2, 0.3, 0.4]])
        mock_st.return_value = fake_encoder
        fake_collection = MagicMock()
        fake_collection.query.return_value = {
            "ids": [[]], "distances": [[]], "metadatas": [[]], "documents": [[]]
        }
        mock_client.return_value.get_or_create_collection.return_value = fake_collection

        r = Retriever(model_name=NOMIC, collection_name="tmp", chroma_path="/tmp/x")
        r.retrieve("what is RAG?")
        # First positional arg of first encode call should be ["search_query: what is RAG?"]
        first_call_args = fake_encoder.encode.call_args_list[0][0][0]
        assert first_call_args == ["search_query: what is RAG?"], (
            f"expected prefixed query, got {first_call_args}"
        )


class TestStoredDocUnprefixed:
    def test_stored_documents_do_not_contain_prefix(self):
        """After index() with nomic, ChromaDB documents must be un-prefixed.

        This is filled in by Wave 1 EVAL-06 plan using a real (tmp_path) indexing run.
        """
        pytest.skip(
            "Full indexing integration test — filled in by Wave 1 EVAL-06 plan "
            "after prefix injection is wired into index()."
        )
