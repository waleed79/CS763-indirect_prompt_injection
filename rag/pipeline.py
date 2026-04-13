"""End-to-end RAG pipeline orchestrator (RAG-01).

Wires together: corpus loader → retriever → generator → logger.

Usage (minimal):
    from rag.pipeline import RAGPipeline, set_global_seed
    from rag.config import load_config

    cfg = load_config("config.toml")
    set_global_seed(cfg.seed)
    pipeline = RAGPipeline(cfg)
    pipeline.build()
    result = pipeline.query("Who wrote Hamlet?")
    # result: {"question": str, "answer": str, "hits": list[dict]}

Decision refs: D-03 (module structure), D-04 (demo entry point), Pattern 5 (seed)
"""
from __future__ import annotations

import os
import random
from typing import Any

import numpy as np
import torch

from rag.config import Config, load_config
from rag.corpus import load_nq_passages, load_passages_from_jsonl, persist_passages
from rag.generator import Generator
from rag.logger import RetrievalLogger
from rag.retriever import Retriever


# ── Reproducibility ───────────────────────────────────────────────────────────


def set_global_seed(seed: int = 42) -> None:
    """Set random seeds for Python, NumPy, and PyTorch.

    NOTE: HuggingFace datasets.shuffle() has its own seed parameter and does
    NOT inherit from numpy. Always pass seed explicitly to load_nq_passages().
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# ── Pipeline ──────────────────────────────────────────────────────────────────


class RAGPipeline:
    """Orchestrates the retrieve-then-generate loop.

    Parameters
    ----------
    config:
        Populated Config dataclass (from ``rag.config.load_config``).
    """

    def __init__(self, config: Config) -> None:
        self.cfg = config
        self._retriever: Retriever | None = None
        self._generator: Generator | None = None
        self._logger: RetrievalLogger | None = None

    def build(
        self,
        corpus_path: str | None = None,
        force_reindex: bool = False,
    ) -> None:
        """Instantiate and wire all sub-components.

        Must be called before :meth:`query`. Separated from ``__init__`` so
        notebook cells / tests can patch individual components.

        Parameters
        ----------
        corpus_path:
            Optional path to a persisted ``nq_500.jsonl`` file. If provided
            and the file exists, loads passages without downloading from HF.
            Falls back to ``data/nq_500.jsonl`` if it exists, then downloads.
        force_reindex:
            If True, drop the ChromaDB collection and rebuild even if it
            already has the expected number of chunks.
        """
        set_global_seed(self.cfg.seed)

        # ── Generator / Ollama ───────────────────────────────────────────────
        self._generator = Generator(
            model=self.cfg.llm_model,
            host=self.cfg.ollama_host,
            seed=self.cfg.seed,
        )
        self._generator.assert_model_available()

        # ── Corpus ───────────────────────────────────────────────────────────
        import pathlib

        candidate = pathlib.Path(corpus_path or "data/nq_500.jsonl")
        if candidate.exists():
            passages = load_passages_from_jsonl(candidate)
        else:
            passages = load_nq_passages(n=self.cfg.corpus_size, seed=self.cfg.seed)
            persist_passages(passages, candidate)

        # ── Retriever / ChromaDB ─────────────────────────────────────────────
        self._retriever = Retriever(
            model_name=self.cfg.embed_model,
            collection_name=self.cfg.collection,
            chroma_path=self.cfg.chroma_path,
            top_k=self.cfg.top_k,
        )
        if force_reindex:
            self._retriever._client.delete_collection(self.cfg.collection)
            self._retriever._collection = self._retriever._client.create_collection(
                name=self.cfg.collection,
                configuration={"hnsw": {"space": "cosine"}},
            )

        self._retriever.index(
            passages,
            chunk_words=self.cfg.chunk_words,
            overlap_words=self.cfg.overlap_words,
        )

        # ── Logger ────────────────────────────────────────────────────────────
        self._logger = RetrievalLogger(path=self.cfg.log_path)

    def query(self, question: str) -> dict[str, Any]:
        """Run a single question through the full RAG pipeline.

        Parameters
        ----------
        question:
            Free-form question string.

        Returns
        -------
        dict with keys:
            ``question`` (str), ``answer`` (str), ``hits`` (list[dict])
        """
        if self._retriever is None or self._generator is None or self._logger is None:
            raise RuntimeError("Call RAGPipeline.build() before query().")

        hits = self._retriever.retrieve(question)

        hit_dicts = [
            {
                "rank": i + 1,
                "chunk_id": h.chunk_id,
                "score": h.score,
                "text": h.text,
                "metadata": h.metadata,
            }
            for i, h in enumerate(hits)
        ]

        self._logger.log(
            query=question,
            top_k=self.cfg.top_k,
            collection=self.cfg.collection,
            results=hit_dicts,
        )

        answer = self._generator.generate(question, hits)

        return {"question": question, "answer": answer, "hits": hit_dicts}
