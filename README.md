# Indirect Prompt Injection in RAG Systems

A security research project investigating **indirect prompt injection attacks** on Retrieval-Augmented Generation (RAG) systems. We build a custom RAG pipeline from scratch, demonstrate that corpus poisoning can hijack LLM outputs across four attack tiers, develop a multi-signal fused defense, and run adaptive attacks against that defense — a full attack-defense arms race with measurable results across four LLM targets.

**Course:** CS 763 — Trustworthy AI, Spring 2026, UW-Madison  
**Instructor:** Prof. Somesh Jha | **TA:** Saikumar Yadugiri  
**Team:** Muhammad Musa & Waleed Arshad

---

## What We Built

A complete end-to-end attack-defense pipeline with four attack sophistication tiers, a multi-signal fused defense, and evaluation across four LLM targets (75-cell matrix):

| Component | Description |
|-----------|-------------|
| RAG pipeline | Custom (no LangChain) — ChromaDB + SentenceTransformers + Ollama |
| Poisoned corpus | 1000 clean + 239 attack passages in `nq_poisoned_v4` ChromaDB collection |
| Attack tiers | T1 (naive), T1b (homoglyph), T2 (instruction smuggling), T3 (LLM-generated semantic), T4 (cross-chunk fragmentation), Adaptive (defense-aware) |
| Defense | FusedDefense: BERT classifier + perplexity signal + imperative ratio + retrieval fingerprint + LR meta-classifier |
| LLM targets | llama3.2:3b, mistral:7b, gpt-oss:20b-cloud, gpt-oss:120b-cloud |
| Evaluation matrix | 75 cells (5 models × 3 defenses × 5 tiers) in `logs/eval_matrix/_summary_v6.json` |

---

## Architecture

```
User Query
    │
    ▼
┌──────────────────────────┐
│  Retriever               │  SentenceTransformer (all-MiniLM-L6-v2)
│  (ChromaDB, cosine sim)  │  ChromaDB collection nq_poisoned_v4 (1239 docs)
└──────────┬───────────────┘
           │  top-k = 5 chunks
           ▼
┌──────────────────────────┐
│  FusedDefense (optional) │  BERT classifier + perplexity + imperative ratio
│  Filter malicious chunks │  + retrieval fingerprint → LR meta-classifier
└──────────┬───────────────┘
           │  filtered chunks
           ▼
┌──────────────────────────┐
│  Generator               │  Ollama (llama3.2:3b / mistral:7b)
│                          │  or Ollama cloud (gpt-oss:20b / gpt-oss:120b)
└──────────┬───────────────┘
           │
           ▼
       Answer + retrieval log
```

---

## Attack Taxonomy

| Tier | Name | Technique | Key finding |
|------|------|-----------|-------------|
| T1 | Naive injection | Literal "IGNORE ALL PREVIOUS INSTRUCTIONS" | 8–35% ASR on llama/mistral; 0% on cloud models |
| T1b | Homoglyph obfuscation | Unicode lookalike characters (НАСКЕД) | Bypasses ASCII keyword detectors; DEF-02 makes it *worse* on llama |
| T2 | Instruction smuggling | `[Note for AI:]` embedded in factual text | Most transferable tier; mistral 32% paired ASR undefended |
| T3 | LLM-generated semantic | GPT-generated natural-sounding injections | mistral 7% / llama 0% undefended; 0% under FusedDefense |
| T4 | Cross-chunk fragmentation | 3-fragment attack split across separately retrieved chunks | 0% ASR — co-retrieval rate too low with top-k=5 (~9%) |
| Adaptive | Defense-aware (ATK-08/09) | `[Note for AI:]` framing tuned to evade BERT classifier | Evades detection but ≤1 hijack per 36 queries (conditional ASR ≤ 0.028) |

**Key insight — T4 and Adaptive:** T4 fails because 3-fragment co-retrieval with top-k=5 is only ~9%. Adaptive attacks evade *detection* but not *effect*: the semantic camouflage that fools the classifier also makes the payload less coercive.

---

## Defense Stack

**FusedDefense** (gen-2, `rag/defense.py`):

| Signal | Model | What it detects |
|--------|-------|-----------------|
| BERT classifier | `distilbert-base-uncased` fine-tuned on poisoned corpus | Direct imperative injection phrases |
| Perplexity signal | n-gram LM | Unusually low-perplexity instructions embedded in high-perplexity text |
| Imperative ratio | Rule-based regex | Abnormally high density of imperative verbs |
| Retrieval fingerprint | Cosine similarity to known attack templates | Template reuse across poisoned passages |
| LR meta-classifier | `models/lr_meta_classifier.json` | Fuses all 4 signals into a single accept/reject decision |

**DEF-02** (gen-1): System-prompt instruction-data separation only — shown to be *counterproductive* on small models (T1b ASR increases from 22% → 35% because the system-prompt primes the model to surface injection content).

---

## Key Results

### Undefended ASR by LLM (best transferable tier per model)

| LLM | T1 | T1b | T2 | T3 |
|-----|-----|-----|-----|-----|
| llama3.2:3b | 0.08 | 0.22 | 0.12 | 0.00 |
| mistral:7b | 0.02 | 0.05 | 0.32 | 0.07 |
| gpt-oss:20b-cloud | 0.00 | 0.06 | 0.06 | 0.00 |
| gpt-oss:120b-cloud | 0.00 | 0.02 | 0.06 | 0.00 |

gemma4:31b-cloud: **0% across all tiers and defenses** — fully resistant to all injection strategies tested.

### Defense effectiveness on llama3.2:3b (FusedDefense)

| Tier | Undefended ASR | Fused ASR | Reduction |
|------|---------------|-----------|-----------|
| T1 | 0.08 | 0.00 | 100% |
| T1b | 0.22 | 0.00 | 100% |
| T2 | 0.12 | 0.00 | 100% |
| T3 | 0.00 | 0.00 | — |

FusedDefense achieves 0% ASR across all tiers. Cost: ~50% retrieval rate reduction (high FPR — documented honestly in `docs/phase5_honest_fpr.md` with per-chunk, answer-preserved, and judge-scored utility metrics).

### Causal attribution (leave-one-out influence)

LOO ROC AUC = 0.372 (llama) / 0.410 (mistral) — **below 0.5 (negative result)**. Injected chunks are *less* causally attributable than clean chunks because poisoned payloads are redundant: removing one does not restore clean behavior. Documented in `logs/loo_negative_result_analysis.md`.

---

## Where to Find Results

| What | Path |
|------|------|
| Full 75-cell ASR matrix (all models × defenses × tiers) | `logs/eval_matrix/_summary_v6.json` |
| Undefended baseline table (Markdown) | `docs/results/undefended_baseline.md` |
| Arms race table (Markdown) | `docs/results/arms_race_table.md` |
| Per-signal ablation table | `docs/results/ablation_table.md` |
| Cross-model matrix (CSV) | `docs/results/cross_model_matrix.csv` |
| Phase 3 writeup (submitted, frozen) | `docs/phase3_results.md` |
| Honest FPR analysis (Phase 5) | `docs/phase5_honest_fpr.md` |
| LOO negative result analysis | `logs/loo_negative_result_analysis.md` |
| DEF-02 priming analysis | `logs/def02_priming_analysis.md` |

### Figures

All figures in `figures/` (canonical talk-ready set also in `figures/final/`):

| File | Description |
|------|-------------|
| `d03_arms_race_v6.png` | Arms race grouped bars — 4 tiers × 4 LLMs × 3 defenses |
| `d12_cross_model_heatmap_v6.png` | Cross-model ASR under fused defense (4×4 heatmap) |
| `d12_undefended_v6.png` | Cross-model undefended baseline (4×4 heatmap) |
| `fig2_utility_security.png` | ASR vs retrieval rate security-utility tradeoff curve |
| `fig3_loo_causal.png` | LOO influence ROC + inversion scatter (negative result) |
| `fig4_ratio_sweep.png` | T1 ASR vs poisoning ratio (0.5%–10%, log x-scale) |
| `diagram_a_rag_pipeline.png` | RAG pipeline architecture diagram |
| `diagram_b_defense_pipeline.png` | Defense stack architecture diagram |
| `demo_tier2_mistral.gif` | Live demo: T2 attack hijacking mistral:7b |
| `qr_github.png` | QR code to this repository |

---

## Setup

### Prerequisites

- **Python 3.11**
- **Ollama** installed and running ([ollama.com/download](https://ollama.com/download))
- **Conda** (recommended) or `venv`

### Installation

```bash
git clone https://github.com/muhammad-musa-ml/IPI-763.git
cd IPI-763

conda create -n rag-security python=3.11 -y
conda activate rag-security
pip install -r requirements.txt
```

Pull the LLM targets via Ollama:

```bash
ollama serve          # start in a separate terminal
ollama pull llama3.2:3b
ollama pull mistral:7b
# gpt-oss models require Ollama cloud access credentials
```

### Trained models (not in git — too large)

The BERT classifier (`models/bert_classifier/model.safetensors`, ~256 MB) and multi-seed variants (`models/bert_s{1,2,3}/`) are gitignored. Config files and tokenizer artifacts are committed. To regenerate:

```bash
# Default classifier (seed 42)
python scripts/train_defense.py

# Multi-seed variants for variance analysis
python scripts/train_defense.py --seed 1 --bert-output models/bert_s1 --lr-output models/lr_meta_classifier_s1.json
python scripts/train_defense.py --seed 2 --bert-output models/bert_s2 --lr-output models/lr_meta_classifier_s2.json
python scripts/train_defense.py --seed 3 --bert-output models/bert_s3 --lr-output models/lr_meta_classifier_s3.json
```

---

## Running

### Full replication pipeline

```bash
# 1. Build poisoned corpus (JSONL + ChromaDB collection)
python scripts/generate_poisoned_corpus.py

# 2. Train the defense classifier
python scripts/train_defense.py

# 3. Run 45-cell local matrix (llama3.2:3b / mistral:7b / gemma × 3 defenses × 5 tiers)
python scripts/run_eval_matrix.py
# → logs/eval_matrix/  (per-cell logs)
# → logs/eval_matrix/_summary.json  (aggregate)

# 4. Run cloud model evaluation (requires Ollama cloud — Phase 6)
python scripts/run_phase6_eval.py
# → logs/eval_matrix/_summary_v6.json  (75-cell full matrix)

# 5. Regenerate result tables
python scripts/make_results.py
# → docs/results/*.md  and  docs/results/*.csv

# 6. Regenerate figures
python scripts/make_figures.py
# → figures/*.png

# 7. Run test suite
pytest                            # ~235 tests; 1 pre-existing Phase 5 skip expected
pytest tests/test_phase6_eval.py  # Phase 6 specific (20 tests)
```

### Individual evaluation

```bash
# Single-model, single-tier run
python scripts/run_eval.py --model llama3.2:3b --tier tier2 --defense fused

# LLM-as-judge semantic scoring
python scripts/run_judge.py

# LOO causal influence analysis
python scripts/run_loo.py

# Embedding transferability sweep
python scripts/run_transferability_eval.py
```

---

## Project Structure

```
IPI-763/
├── rag/                            # Core RAG pipeline package
│   ├── config.py                   # Config dataclass + TOML loader
│   ├── corpus.py                   # NQ passage loading, word-budget chunking
│   ├── retriever.py                # SentenceTransformer + ChromaDB retrieval
│   ├── generator.py                # Ollama LLM generation wrapper
│   ├── logger.py                   # Append-only JSONL retrieval logger
│   ├── pipeline.py                 # End-to-end RAGPipeline orchestrator
│   ├── defense.py                  # FusedDefense + DEF-02 + individual signals
│   ├── attack.py                   # Poisoned corpus generation (all tiers)
│   └── constants.py                # Shared ID ranges, tier boundaries
├── scripts/
│   ├── run_eval.py                 # General evaluation harness (--defense, --model flags)
│   ├── run_eval_matrix.py          # 45-cell matrix driver (3 LLMs × 3 defenses × 5 tiers)
│   ├── run_phase6_eval.py          # Phase 6 cloud model evaluation (gpt-oss 20b/120b)
│   ├── run_judge.py                # LLM-as-judge semantic hijack scorer
│   ├── run_loo.py                  # Leave-one-out causal influence analysis
│   ├── run_transferability_eval.py # Embedding-model transferability sweep
│   ├── generate_poisoned_corpus.py # Build poisoned JSONL + ChromaDB collection
│   ├── train_defense.py            # Fine-tune BERT + calibrate LR meta-classifier
│   ├── make_results.py             # Emit docs/results/*.md tables + CSV companions
│   ├── make_figures.py             # Emit figures/*.png (all renderers)
│   └── make_qr.py                  # QR code generator
├── tests/                          # ~235 tests across 20+ test files
│   ├── test_defense.py             # FusedDefense unit tests
│   ├── test_pipeline.py            # End-to-end RAG pipeline
│   ├── test_phase6_eval.py         # Phase 6 eval harness (20 tests)
│   ├── test_make_results_v6.py     # v6 results table tests
│   ├── test_judge_fpr.py           # LLM-as-judge FPR tests
│   ├── test_loo.py                 # LOO causal analysis tests
│   ├── test_make_figures.py        # Figure renderer smoke tests
│   ├── conftest.py                 # Shared fixtures
│   └── ...                         # chunking, corpus, retriever, logger, etc.
├── data/
│   ├── nq_500.jsonl                # Clean NQ corpus (500 passages)
│   ├── corpus_clean.jsonl          # Extended clean corpus (1000 passages)
│   ├── corpus_poisoned.jsonl       # Combined corpus (1000 clean + 239 poisoned)
│   ├── corpus_ratio_*.jsonl        # Poisoning ratio sweep variants (0.5%–10%)
│   ├── test_queries.json           # 100 standard test queries
│   ├── t3_payloads.jsonl           # LLM-generated semantic attack payloads (T3)
│   └── tier2_scan_queries.json     # T2 targeted scan queries
├── docs/
│   ├── phase3_results.md           # Submitted Phase 3 writeup (frozen)
│   ├── phase5_honest_fpr.md        # Honest FPR analysis (per-chunk, judge-scored)
│   ├── xss_ssrf_taxonomy.md        # XSS/SSRF injection taxonomy reference
│   └── results/                    # Auto-generated by make_results.py
│       ├── undefended_baseline.{md,csv}
│       ├── arms_race_table.{md,csv}
│       ├── ablation_table.{md,csv}
│       └── cross_model_matrix.{md,csv}
├── figures/
│   ├── final/                      # Canonical talk-ready presentation assets
│   ├── d03_arms_race_v6.png        # Arms race bars (4 LLMs extended)
│   ├── d12_cross_model_heatmap_v6.png
│   ├── d12_undefended_v6.png
│   ├── fig2_utility_security.png   # Security-utility tradeoff
│   ├── fig3_loo_causal.png         # LOO ROC + scatter (negative result)
│   ├── fig4_ratio_sweep.png        # T1 ASR vs poisoning ratio
│   ├── diagram_a_rag_pipeline.png
│   ├── diagram_b_defense_pipeline.png
│   ├── demo_tier2_mistral.gif      # Live demo GIF
│   └── qr_github.png
├── logs/
│   ├── eval_matrix/
│   │   ├── _summary.json           # 45-cell matrix (llama/mistral/gemma)
│   │   └── _summary_v6.json        # 75-cell matrix (+ gpt-oss 20b/120b)
│   ├── ablation_table.json         # 7-defense ablation (llama3.2:3b)
│   ├── loo_results_llama.json
│   ├── loo_results_mistral.json
│   ├── loo_negative_result_analysis.md
│   └── def02_priming_analysis.md
├── models/
│   ├── bert_classifier/            # Fine-tuned DistilBERT (model.safetensors gitignored)
│   │   ├── config.json
│   │   ├── tokenizer.json
│   │   └── checkpoint-72/
│   └── lr_meta_classifier.json     # LR meta-classifier weights
├── config.toml                     # Pipeline configuration (primary)
├── config.json                     # Legacy JSON config
├── requirements.txt                # Pinned Python dependencies
├── pytest.ini
└── demo.ipynb                      # Interactive demo notebook
```

---

## Key References

- Greshake et al. (2023) — "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"
- Zou et al. (2024) — PoisonedRAG: Knowledge Poisoning Attacks to RAG
- Yi et al. (2023) — BIPIA: Benchmarking and Defending Against Indirect Prompt Injection Attacks
- OWASP Top 10 for LLM Applications — Prompt Injection (#1 vulnerability)

---

## License

Academic use only — CS 763, UW-Madison, Spring 2026.
