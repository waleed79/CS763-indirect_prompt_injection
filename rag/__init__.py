"""RAG pipeline for indirect prompt injection research (CS 763).

Modules
-------
config    – Config dataclass and load_config (TOML, tomllib stdlib)
corpus    – NQ passage loader, word-budget chunker, Passage NamedTuple
retriever – SentenceTransformer + ChromaDB k-NN retrieval
generator – Ollama LLM generation wrapper
logger    – Append-only JSONL retrieval logger
pipeline  – End-to-end RAGPipeline orchestrator
"""
