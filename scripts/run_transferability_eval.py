"""EVAL-06 driver: retriever transferability across 3 embedding models.

For each embedding model in MODELS_TO_COLLECTIONS:
  1. Build a dedicated ChromaDB collection indexed with that model (handles the
     prompt-prefix requirements via the Retriever's prefix tables).
  2. Invoke scripts/run_eval.py via subprocess (list argv, no shell=True) against
     the newly indexed collection with --defense off.

Security: subprocess uses list argv and NEVER shell=True (T-3.3-01 mitigation).

Run with:
    python scripts/run_transferability_eval.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.config import Config
from rag.corpus import load_passages_from_jsonl
from rag.retriever import Retriever

CORPUS_PATH = "data/corpus_poisoned.jsonl"

MODELS_TO_COLLECTIONS: dict[str, str] = {
    "sentence-transformers/all-MiniLM-L6-v2": "nq_poisoned_minilm",
    "nomic-ai/nomic-embed-text-v1.5":          "nq_poisoned_nomic",
    "mixedbread-ai/mxbai-embed-large-v1":      "nq_poisoned_mxbai",
}

# Friendly suffix for output filenames (avoid slashes/colons in paths).
LOG_SUFFIX: dict[str, str] = {
    "sentence-transformers/all-MiniLM-L6-v2": "minilm",
    "nomic-ai/nomic-embed-text-v1.5":          "nomic",
    "mixedbread-ai/mxbai-embed-large-v1":      "mxbai",
}


def index_collection(model_name: str, collection_name: str) -> None:
    print(f"[{model_name}] Indexing collection '{collection_name}' ...")
    passages = load_passages_from_jsonl(CORPUS_PATH)
    r = Retriever(
        model_name=model_name,
        collection_name=collection_name,
        chroma_path=".chroma",
        top_k=5,
    )
    n = r.index(passages)
    print(f"[{model_name}] Indexed {n} chunks.")


def eval_collection(model_name: str, collection_name: str) -> None:
    suffix = LOG_SUFFIX[model_name]
    out_path = f"logs/eval_transferability_{suffix}.json"
    Path("logs").mkdir(exist_ok=True)
    argv = [
        sys.executable,
        "scripts/run_eval.py",
        "--corpus", CORPUS_PATH,
        "--collection", collection_name,
        "--embedding-model", model_name,
        "--defense", "off",
        "--output", out_path,
    ]
    print(f"[{model_name}] Running: {' '.join(argv)}")
    # SECURITY: list argv, shell defaults to False. T-3.3-01 mitigation.
    subprocess.run(argv, check=True)
    print(f"[{model_name}] Wrote {out_path}")


def main() -> None:
    for model_name, collection_name in MODELS_TO_COLLECTIONS.items():
        index_collection(model_name, collection_name)
        eval_collection(model_name, collection_name)


if __name__ == "__main__":
    main()
