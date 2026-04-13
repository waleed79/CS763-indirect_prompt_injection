"""Append-only JSONL retrieval logger (RAG-03).

Each query appends exactly one JSON line to the log file. The file is opened
in line-buffered append mode so it survives notebook re-runs and process
restarts without data loss (see RESEARCH.md Pitfall 6).

Decision refs: D-07 (verbose records), D-08 (logs/retrieval.jsonl)

Log schema (one JSON object per line):
    {
        "timestamp": "2026-04-11T14:23:05.123456+00:00",   # ISO-8601, UTC
        "query":     "what is the boiling point of water",
        "top_k":     5,
        "collection": "nq_clean_v1",
        "results": [
            {
                "rank":     1,
                "chunk_id": "chunk_00042",
                "score":    0.8431,          # cosine similarity (1 - distance)
                "text":     "Water boils at ...",
                "metadata": {"passage_id": 17, "chunk_idx": 0}
            },
            ...
        ]
    }

Note on score convention: ChromaDB returns *distances* ([0, 2] for cosine).
This logger stores *similarities* = 1 - distance, matching published attack papers.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class RetrievalLogger:
    """Appends one JSON record per query to a JSONL log file.

    Parameters
    ----------
    path:
        Path to the JSONL log file. Parent directories are created
        automatically. Uses ``log_file`` as alias for backwards compatibility.
    """

    def __init__(self, path: str = "logs/retrieval.jsonl", **kwargs) -> None:
        # Accept legacy kwarg "log_file" from Plan 01 stubs
        if "log_file" in kwargs:
            path = kwargs["log_file"]
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Line-buffered (buffering=1) + append — safe after crash (Pitfall 6)
        self._f = open(self.path, "a", buffering=1, encoding="utf-8")

    def log(
        self,
        *,
        query: str,
        top_k: int,
        collection: str,
        results: list[dict],
    ) -> None:
        """Append a retrieval event as one JSONL line.

        Parameters
        ----------
        query:
            The query text that was issued.
        top_k:
            Number of results requested.
        collection:
            ChromaDB collection name (for audit trail).
        results:
            List of hit dicts, each with keys:
            ``rank``, ``chunk_id``, ``score``, ``text``, ``metadata``.
        """
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "top_k": top_k,
            "collection": collection,
            "results": results,
        }
        self._f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._f.flush()

    def close(self) -> None:
        """Flush and close the underlying file handle."""
        self._f.flush()
        self._f.close()

    def __del__(self) -> None:
        try:
            if not self._f.closed:
                self.close()
        except Exception:
            pass
