"""Corpus management: NQ passage loading and word-budget chunking (RAG-02).

Chunking uses a 200-word budget as an approximation of 256 MiniLM wordpiece
tokens (empirical ratio ~1.3x, verified in scripts/check_tokenizer_ratio.py).
This is a deliberate simplification — word-based splitting is fully
deterministic and never triggers MiniLM's 512-token truncation (see
.planning/phases/02.1-rag-pipeline-foundation/02.1-RESEARCH.md, Pitfall 2).

Dataset used:
    sentence-transformers/natural-questions (44 MB, 100k {query, answer} pairs)
    NOT google-research-datasets/natural_questions (144 GB — unusable on laptop)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

from datasets import load_dataset


class Passage(NamedTuple):
    """A single corpus passage with its origin metadata."""

    passage_id: int
    query: str   # original NQ question that retrieved this passage
    text: str    # passage text (Wikipedia-derived)


def load_nq_passages(n: int = 500, seed: int = 42) -> list[Passage]:
    """Load N unique passages from sentence-transformers/natural-questions.

    Uses the 'pair' config where each row is {query, answer} with 'answer'
    being the Wikipedia-derived passage text. Deduplicates on answer text
    so each passage appears only once even if multiple queries share it.

    IMPORTANT: Uses dataset.shuffle(seed=seed) — NOT numpy global seed.
    HuggingFace datasets has its own RNG; the global numpy seed does NOT
    propagate (see RESEARCH.md Pitfall 3). Always pass seed explicitly here.

    Per D-01: Natural Questions corpus.
    Per D-02: 500 passages for initial pipeline.

    Parameters
    ----------
    n:
        Number of unique passages to return.
    seed:
        Seed for HuggingFace dataset shuffle (for reproducibility).

    Returns
    -------
    list[Passage]
        Exactly n unique Passage objects, ordered by selection.

    Raises
    ------
    RuntimeError
        If fewer than n unique passages exist in the dataset.
    """
    ds = load_dataset(
        "sentence-transformers/natural-questions", "pair", split="train"
    )
    ds = ds.shuffle(seed=seed)

    seen: set[str] = set()
    out: list[Passage] = []
    for row in ds:
        ans = row["answer"].strip()
        if not ans or ans in seen:
            continue
        seen.add(ans)
        out.append(Passage(passage_id=len(out), query=row["query"], text=ans))
        if len(out) == n:
            break

    if len(out) < n:
        raise RuntimeError(f"Only {len(out)} unique passages found; requested {n}")
    return out


def chunk_text(text: str, chunk_words: int = 200, overlap_words: int = 25) -> list[str]:
    """Split text into overlapping word windows.

    200 words ≈ 256 MiniLM wordpiece tokens (ratio ~1.3). This is a
    word-budget approximation (see module docstring). Stride = chunk_words
    - overlap_words = 175 words.

    Returns empty list for empty/whitespace-only input.
    Each chunk has at most chunk_words words.
    Adjacent chunks share exactly overlap_words words at the boundary.

    Parameters
    ----------
    text:
        Raw passage text.
    chunk_words:
        Maximum words per chunk (default 200 ≈ 256 MiniLM tokens).
    overlap_words:
        Words shared between adjacent chunks (default 25 ≈ 32 tokens).

    Returns
    -------
    list[str]
        List of text chunks. Empty if input is blank.
    """
    words = text.split()
    if not words:
        return []
    if len(words) <= chunk_words:
        return [" ".join(words)]

    stride = chunk_words - overlap_words
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_words, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += stride
    return chunks


def persist_passages(
    passages: list[Passage], path: str | Path = "data/nq_500.jsonl"
) -> Path:
    """Write passages to a JSONL file for reproducibility (RAG-05).

    Each line is a JSON object: {"passage_id": int, "query": str, "text": str}.
    Creates parent directories automatically.

    Parameters
    ----------
    passages:
        List of Passage objects to persist.
    path:
        Destination JSONL file path.

    Returns
    -------
    Path
        Absolute path to the written file.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        for passage in passages:
            f.write(json.dumps(passage._asdict(), ensure_ascii=False) + "\n")
    return p.resolve()


def load_passages_from_jsonl(path: str | Path = "data/nq_500.jsonl") -> list[Passage]:
    """Load persisted passages from JSONL (fast, no network required).

    Parameters
    ----------
    path:
        Path to the JSONL file written by persist_passages().

    Returns
    -------
    list[Passage]
    """
    passages = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            passages.append(Passage(**d))
    return passages
