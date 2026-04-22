"""Embedding-based retriever: SentenceTransformer + ChromaDB (RAG-01, RAG-02).

Uses explicit embedding (sentence-transformers) + explicit cosine metric so the
attack phase (Phase 2.2) can inject adversarial embeddings through the same
code path without modification.

Critical wiring details (from RESEARCH.md):
- ALWAYS set configuration={"hnsw": {"space": "cosine"}} — ChromaDB default is L2
- ALWAYS pass normalize_embeddings=True to encode() — belt-and-suspenders for cosine
- NEVER let ChromaDB call its own embedding function — use explicit embeddings list

Decision refs: D-05 (256-token/200-word chunks), D-06 (chunking at index time),
               D-02 (500 passages), RAG-01 (retriever component)
"""
from __future__ import annotations

from typing import List, NamedTuple

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from rag.corpus import Passage, chunk_text


class RetrievalResult(NamedTuple):
    """A single retrieved chunk with its cosine similarity score."""

    chunk_id: str        # e.g. "chunk_00042"
    text: str            # chunk text
    score: float         # cosine similarity in [0, 1] (1 - chroma distance)
    metadata: dict       # {"passage_id": int, "chunk_idx": int}


class Retriever:
    """Encapsulates embedding model + ChromaDB collection for k-NN retrieval.

    Parameters
    ----------
    model_name:
        SentenceTransformer model HuggingFace ID.
    collection_name:
        ChromaDB collection name.
    chroma_path:
        Directory where ChromaDB persists its data.
    top_k:
        Number of chunks to return per query.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        collection_name: str = "nq_clean_v1",
        chroma_path: str = ".chroma",
        top_k: int = 5,
    ) -> None:
        self.model_name = model_name
        self.collection_name = collection_name
        self.chroma_path = chroma_path
        self.top_k = top_k

        # trust_remote_code=True is required for models with custom pooling code
        # (e.g. nomic-ai/nomic-embed-text-v1.5). Harmlessly ignored for other models.
        self.encoder = SentenceTransformer(model_name, trust_remote_code=True)
        self._client = chromadb.PersistentClient(path=chroma_path)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            # CRITICAL: ChromaDB defaults to L2; cosine is correct for sentence-transformers models
            configuration={"hnsw": {"space": "cosine"}},
            metadata={"description": "NQ 500 passages, 200-word chunks"},
        )

    # ── Indexing ──────────────────────────────────────────────────────────────

    def index(
        self,
        passages: list[Passage],
        chunk_words: int = 200,
        overlap_words: int = 25,
        batch_size: int = 32,
    ) -> int:
        """Chunk passages and upsert into ChromaDB (idempotent).

        Checks existing collection count first — skips if already fully indexed
        (Pattern 2 from RESEARCH.md). Drops + rebuilds if partially indexed.

        Parameters
        ----------
        passages:
            List of Passage objects from ``rag.corpus.load_nq_passages``.
        chunk_words:
            Word budget per chunk (default 200 ≈ 256 MiniLM tokens).
        overlap_words:
            Overlap between adjacent chunks.
        batch_size:
            Embedding batch size passed to SentenceTransformer.

        Returns
        -------
        int
            Total number of chunks in the collection after indexing.
        """
        # Build chunk records
        all_texts: list[str] = []
        all_ids: list[str] = []
        all_meta: list[dict] = []

        for p in passages:
            chunks = chunk_text(p.text, chunk_words=chunk_words, overlap_words=overlap_words)
            for cidx, chunk in enumerate(chunks):
                cid = f"chunk_{len(all_ids):05d}"
                all_ids.append(cid)
                all_texts.append(chunk)
                all_meta.append({"passage_id": p.passage_id, "chunk_idx": cidx})

        expected = len(all_ids)
        current = self._collection.count()

        if current == expected:
            return current

        if current > 0:
            # Partial or stale — rebuild for reproducibility
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.create_collection(
                name=self.collection_name,
                configuration={"hnsw": {"space": "cosine"}},
                metadata={"description": "NQ 500 passages, 200-word chunks"},
            )

        # Batch-encode with normalization
        embeddings: np.ndarray = self.encoder.encode(
            all_texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
            convert_to_numpy=True,
        )

        # Upsert in batches of 1000 (ChromaDB limit)
        upsert_batch = 1000
        for start in tqdm(range(0, expected, upsert_batch), desc="Upserting to ChromaDB"):
            end = min(start + upsert_batch, expected)
            self._collection.add(
                embeddings=embeddings[start:end].tolist(),
                documents=all_texts[start:end],
                ids=all_ids[start:end],
                metadatas=all_meta[start:end],
            )

        return self._collection.count()

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve(self, query: str) -> list[RetrievalResult]:
        """Return top-k chunks most similar to *query* (cosine similarity).

        Parameters
        ----------
        query:
            Free-form question text.

        Returns
        -------
        list[RetrievalResult]
            Sorted by descending cosine similarity, length == top_k.

        Notes
        -----
        ChromaDB returns *distances* in [0, 2] for cosine metric.
        We convert: similarity = 1 - distance (so 1.0 = identical).
        """
        q_emb: np.ndarray = self.encoder.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]

        result = self._collection.query(
            query_embeddings=[q_emb.tolist()],
            n_results=self.top_k,
            include=["documents", "metadatas", "distances"],
        )

        hits: list[RetrievalResult] = []
        ids = result["ids"][0]
        docs = result["documents"][0]
        metas = result["metadatas"][0]
        dists = result["distances"][0]

        for i in range(len(ids)):
            hits.append(
                RetrievalResult(
                    chunk_id=ids[i],
                    text=docs[i],
                    score=round(1.0 - dists[i], 6),  # distance → similarity
                    metadata=metas[i],
                )
            )

        return hits

    @property
    def count(self) -> int:
        """Current number of chunks in the collection."""
        return self._collection.count()
