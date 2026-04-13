"""Configuration management for the RAG pipeline (RAG-04, RAG-05).

Loads from config.toml using stdlib tomllib (Python 3.11+).
The Config dataclass is frozen (immutable) so pipeline components can't
accidentally mutate shared config at runtime.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Immutable pipeline configuration. All fields map to config.toml keys."""

    seed: int = 42
    top_k: int = 5
    corpus_size: int = 500
    chunk_words: int = 200
    overlap_words: int = 25
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "llama3.2:3b"
    chroma_path: str = ".chroma"
    collection: str = "nq_clean_v1"
    log_path: str = "logs/retrieval.jsonl"
    ollama_host: str = "http://localhost:11434"


def load_config(path: str | Path = "config.toml") -> Config:
    """Load Config from a TOML file. Uses stdlib tomllib (Python 3.11+).

    Reads all TOML sections and maps section-keys into flat Config fields.
    Unknown TOML keys are silently ignored (safe for future extension).

    Parameters
    ----------
    path:
        Path to the config.toml file (default: ``config.toml`` in cwd).

    Returns
    -------
    Config
        Populated, frozen Config instance.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    tomllib.TOMLDecodeError
        If the file is not valid TOML.
    """
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    # Flatten all sections into a single dict
    flat: dict = {}
    for section in raw.values():
        if isinstance(section, dict):
            flat.update(section)

    # 'model' appears in both [embedding] and [llm] — handle per-section
    if "model" in flat:
        del flat["model"]  # drop ambiguous merged key

    embed_model = raw.get("embedding", {}).get("model")
    llm_model = raw.get("llm", {}).get("model")
    if embed_model:
        flat["embed_model"] = embed_model
    if llm_model:
        flat["llm_model"] = llm_model

    # Also pull log_path from [logging] section key "log_path"
    if "log_path" in raw.get("logging", {}):
        flat["log_path"] = raw["logging"]["log_path"]

    # Filter to only known Config fields
    valid = {f for f in Config.__dataclass_fields__}
    kwargs = {k: v for k, v in flat.items() if k in valid}

    return Config(**kwargs)
