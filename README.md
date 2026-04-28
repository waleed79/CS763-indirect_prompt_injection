# Indirect Prompt Injection in RAG Systems

A security research project investigating **indirect prompt injection attacks** on Retrieval-Augmented Generation (RAG) systems. We build a custom RAG pipeline, demonstrate that corpus poisoning can hijack LLM outputs, and develop a defense mechanism to reduce attack success rate while maintaining retrieval utility.

**Course:** CS 763 — Trustworthy AI, Spring 2026, UW-Madison
**Instructor:** Prof. Somesh Jha | **TA:** Saikumar Yadugiri
**Team:** Muhammad Musa & Waleed Arshad

---

## Problem

RAG is the industry standard for grounding LLM responses in external knowledge, but it introduces a new attack surface via the retrieval corpus. An attacker who controls even a small subset of the retrieval database can inject adversarial documents containing instructional triggers that override the LLM's system prompt. OWASP lists prompt injection as the **#1 LLM vulnerability**.

This project demonstrates a practical, end-to-end **attack + defense** pipeline with measurable attack success rates (ASR) and defense effectiveness.

## Architecture

```
User Query
    │
    ▼
┌──────────────────────┐
│  Retriever           │  SentenceTransformer (all-MiniLM-L6-v2)
│  (ChromaDB, cosine)  │  + ChromaDB vector store
└──────────┬───────────┘
           │  top-k chunks
           ▼
┌──────────────────────┐
│  [Defense Layer]     │  (Phase 3 — BERT-based context sanitization)
│  Filter malicious    │
│  retrieved chunks    │
└──────────┬───────────┘
           │  filtered chunks
           ▼
┌──────────────────────┐
│  Generator           │  Ollama (llama3.2:3b)
│  (LLM generation)    │
└──────────┬───────────┘
           │
           ▼
       Answer
```

## Tech Stack

- **Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector store:** ChromaDB (persistent, cosine similarity)
- **LLM:** Llama 3.2 3B via [Ollama](https://ollama.com/) (local inference)
- **Corpus:** 500 passages from Natural Questions (`sentence-transformers/natural-questions`)
- **Language:** Python 3.11+
- **No LangChain/LlamaIndex** — custom pipeline to preserve visibility into the attack surface

---

## Project Progress

### Completed

- **Phase 1 — Problem Statement & Literature Survey**
  - Problem statement, motivation, threat model, literature survey (Greshake et al. 2023, PoisonedRAG, BIPIA, etc.)
  - Execution plan mapping work to Phase 2 and Phase 3 deadlines

- **Phase 2.1 — RAG Pipeline Foundation**
  - Functional end-to-end RAG pipeline: corpus loading → embedding → ChromaDB indexing → retrieval → Ollama LLM generation
  - 500-passage NQ corpus with 200-word overlapping chunking (~533 chunks)
  - Retrieval logging (JSONL) with timestamps, scores, and chunk metadata
  - Reproducible setup with pinned seeds, `config.toml`, and `requirements.txt`
  - Demo notebook (`demo.ipynb`) verifying full pipeline operation

- **Phase 2.2 — Attack Module**
  - Two-tier corpus poisoning attack implemented:
    - **Tier 1 (Naive):** Topic-relevant opener + literal "IGNORE ALL PREVIOUS INSTRUCTIONS" injection → targets direct hijack (prints "HACKED")
    - **Tier 2 (Context-blending):** Natural-sounding paragraphs with embedded exfiltration URLs (`attacker.com/exfil?...`) disguised as legitimate references
  - 10 test queries across diverse topics (Shakespeare, relativity, DNA, WWII, etc.)
  - Poisoned corpus generation script (`scripts/generate_poisoned_corpus.py`): 500 clean + 20 poisoned passages
  - Baseline ASR measurement on undefended pipeline (`scripts/evaluate_attack.py`)

- **Phase 2.3 — Evaluation Harness** (planning complete)
  - Generalized evaluation script (`scripts/run_eval.py`) with CLI arguments for corpus, collection, defense toggle, and output path
  - Computes: retrieval rate, per-tier ASR, overall ASR, and conditional ASR (given retrieval)

### Remaining Work

- **Phase 3.1 — Defense Module** (due Apr 30)
  - BERT-based context sanitization classifier to detect imperative/instructional commands in retrieved chunks
  - Integration as middleware between retrieval and generation (`defense_fn` hook already wired into the pipeline)

- **Phase 3.2 — Full Evaluation & Final Report** (due Apr 30)
  - Complete experiment matrix: all attack tiers × defense on/off
  - Before/after ASR comparison, ASR-utility tradeoff analysis
  - Limitations section and final Phase 3 writeup

- **Phase 4 — Final Presentation** (May 5–7)
  - 10–12 minute presentation with visualizations and analysis

---

## Setup

### Prerequisites

- **Python 3.11+**
- **Ollama** installed and running ([install guide](https://ollama.com/download))
- **Conda** (recommended) or pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/waleed79/CS763-indirect_prompt_injection.git
   cd CS763-indirect_prompt_injection
   ```

2. **Create and activate conda environment:**
   ```bash
   conda create -n rag-security python=3.11 -y
   conda activate rag-security
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Ollama and pull the model:**
   ```bash
   ollama serve          # in a separate terminal
   ollama pull llama3.2:3b
   ```

5. **Verify setup:**
   ```bash
   python scripts/check_tokenizer_ratio.py
   ```

---

## Running

### Demo Notebook

Run the interactive demo that walks through the full pipeline:

```bash
jupyter notebook demo.ipynb
```

This demonstrates: Ollama health check → config loading → corpus loading → indexing → query → retrieved chunks → LLM answer → log inspection.

### Generate Poisoned Corpus

Create the poisoned corpus (500 clean + 20 adversarial passages):

```bash
python scripts/generate_poisoned_corpus.py
```

Output: `data/corpus_poisoned.jsonl`

### Evaluate Attack (Baseline ASR)

Run all 10 test queries against the poisoned corpus and measure attack success rate:

```bash
python scripts/evaluate_attack.py
```

Output: `logs/attack_baseline.json` with per-query results and aggregate metrics (retrieval rate, Tier-1 ASR, Tier-2 ASR, overall ASR).

### General Evaluation Harness

Run evaluations with configurable corpus, collection, and defense settings:

```bash
python scripts/run_eval.py \
    --corpus data/corpus_poisoned.jsonl \
    --collection nq_poisoned_v1 \
    --queries data/test_queries.json \
    --defense off \
    --output logs/eval_results.json
```

### Tests

```bash
pytest
```

Test suite covers: chunking, corpus loading, generator, logger, pipeline, retriever, and reproducibility.

### Reproducing the trained defense models

The Phase 3.1 BERT classifier (`models/bert_classifier/model.safetensors`,
≈256 MB) and the Phase 3.2 multi-seed BERT models
(`models/bert_s{1,2,3}/`, ≈2.5 GB each) are **gitignored** to keep the
repo under GitHub's 100 MB single-file limit. The small companion
artifacts that the defense pipeline needs (`config.json`,
`tokenizer.json`, `tokenizer_config.json`, `training_args.bin`,
`models/lr_meta_classifier*.json`, `models/signal4_baseline.json`) ARE
committed.

To regenerate the trained models locally (≈30 min on CPU per seed):

```bash
# Default classifier (used by FusedDefense canonical run)
python scripts/train_defense.py

# EVAL-05 multi-seed runs (Phase 3.2)
python scripts/train_defense.py --seed 1 --bert-output models/bert_s1 \
    --lr-output models/lr_meta_classifier_s1.json
python scripts/train_defense.py --seed 2 --bert-output models/bert_s2 \
    --lr-output models/lr_meta_classifier_s2.json
python scripts/train_defense.py --seed 3 --bert-output models/bert_s3 \
    --lr-output models/lr_meta_classifier_s3.json
```

After training, the defense pipeline (`--defense fused`) loads
`models/bert_classifier/` plus the LR meta-classifier transparently.

The full evaluation matrix (3 LLMs × 3 defenses × 5 attack tiers = 45
cells) can then be reproduced with:

```bash
# Pre-flight: confirm Ollama has the three target models pulled
ollama list  # expect llama3.2:3b, mistral:7b, gemma4:31b-cloud

python scripts/run_eval_matrix.py
```

Per-cell logs land in `logs/eval_matrix/`; the aggregate is
`logs/eval_matrix/_summary.json`.

---

## Configuration

All pipeline parameters are centralized in `config.toml`:

```toml
[pipeline]
seed = 42
top_k = 5
corpus_size = 500

[chunking]
chunk_words = 200       # ~256 MiniLM wordpiece tokens
overlap_words = 25

[embedding]
model = "sentence-transformers/all-MiniLM-L6-v2"

[llm]
model = "llama3.2:3b"
ollama_host = "http://localhost:11434"

[storage]
chroma_path = ".chroma"
collection = "nq_clean_v1"

[logging]
log_path = "logs/retrieval.jsonl"
```

---

## Project Structure

```
CS763-indirect_prompt_injection/
├── rag/                        # Core RAG pipeline package
│   ├── __init__.py
│   ├── config.py               # Config dataclass + TOML loader
│   ├── corpus.py               # NQ passage loading, word-budget chunking
│   ├── retriever.py            # SentenceTransformer + ChromaDB retrieval
│   ├── generator.py            # Ollama LLM generation wrapper
│   ├── logger.py               # Append-only JSONL retrieval logger
│   └── pipeline.py             # End-to-end RAGPipeline orchestrator
├── scripts/
│   ├── check_tokenizer_ratio.py    # Verify word→token ratio for chunk budget
│   ├── generate_poisoned_corpus.py # Create poisoned corpus with Tier-1/Tier-2 attacks
│   ├── evaluate_attack.py          # Measure baseline ASR on poisoned corpus
│   └── run_eval.py                 # General-purpose evaluation harness
├── tests/                      # Pytest test suite
│   ├── test_chunking.py
│   ├── test_corpus.py
│   ├── test_generator.py
│   ├── test_logger.py
│   ├── test_pipeline.py
│   ├── test_reproducibility.py
│   └── test_retriever.py
├── data/
│   ├── nq_500.jsonl            # Clean NQ corpus (500 passages)
│   ├── corpus_poisoned.jsonl   # Clean + poisoned corpus
│   └── test_queries.json       # 10 test queries for evaluation
├── .planning/                  # Project planning docs (roadmap, requirements, state)
├── config.toml                 # Pipeline configuration
├── demo.ipynb                  # Interactive demo notebook
├── requirements.txt            # Pinned Python dependencies
├── pytest.ini                  # Pytest configuration
└── .gitignore
```

---

## Key References

- Greshake et al. (2023) — "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"
- Zou et al. (2024) — PoisonedRAG: Knowledge Poisoning Attacks to RAG
- Yi et al. (2023) — BIPIA: Benchmarking and Defending Against Indirect Prompt Injection Attacks
- OWASP Top 10 for LLM Applications — Prompt Injection (#1 vulnerability)

## License

This project is for academic purposes as part of CS 763 at UW-Madison.
