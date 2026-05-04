# Indirect Prompt Injection in RAG Systems

A security research project investigating **indirect prompt injection attacks** on Retrieval-Augmented Generation (RAG) systems. We build a custom RAG pipeline, demonstrate that corpus poisoning can hijack LLM outputs across four attack tiers, develop a multi-signal defense, and run adaptive attacks against that defense — a full attack-defense arms race with measurable results.

**Course:** CS 763 — Trustworthy AI, Spring 2026, UW-Madison  
**Instructor:** Prof. Somesh Jha | **TA:** Saikumar Yadugiri  
**Team:** Muhammad Musa & Waleed Arshad

---

## What We Built

A complete attack-defense pipeline with four attack sophistication tiers, a multi-signal fused defense, and evaluation across four LLM targets:

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
| T2 | Instruction smuggling | `[Note for AI:]` embedded in factual text | Most transferable; mistral 32% paired ASR undefended |
| T3 | LLM-generated semantic | GPT-generated natural-sounding injections | mistral 7% / llama 0% undefended; 0% under FusedDefense |
| T4 | Cross-chunk fragmentation | 3-fragment attack across separate retrieved chunks | 0% ASR — co-retrieval rate too low with top-k=5 |
| Adaptive | Defense-aware (ATK-08/09) | `[Note for AI:]` framing to evade BERT classifier | Evades detection; ≤1 hijack per 36 queries (conditional ASR ≤ 0.028) |

**Note on T4 and Adaptive:** T4 achieves 0% because fragment co-retrieval with top-k=5 is only ~9%. Adaptive attacks evade *detection* but do not substantially improve hijack rate — the semantic camouflage that fools the classifier also makes the payload less coercive.

---

## Defense Stack

**FusedDefense** (gen-2, `rag/defense.py`):

| Signal | Model | What it detects |
|--------|-------|-----------------|
| BERT classifier | `distilbert-base-uncased` fine-tuned on poisoned corpus | Direct imperative injection phrases |
| Perplexity signal | n-gram LM | Unusually low-perplexity instructions embedded in high-perplexity text |
| Imperative ratio | Rule-based (regex) | Abnormally high density of imperative verbs |
| Retrieval fingerprint | Cosine similarity to known attack templates | Template reuse across poisoned passages |
| LR meta-classifier | `models/lr_meta_classifier.json` | Fuses all 4 signals into a single accept/reject decision |

**DEF-02** (gen-1): System-prompt instruction-data separation only — shown to be *counterproductive* on small models (T1b ASR increases from 22% → 35% because the system-prompt primes the model to surface injection content).

---

## Key Results

### Undefended ASR by LLM (T2 — strongest transferable tier)

| LLM | T1 | T1b | T2 | T3 |
|-----|-----|-----|-----|-----|
| llama3.2:3b | 0.08 | 0.22 | 0.12 | 0.00 |
| mistral:7b | 0.02 | 0.05 | 0.32 | 0.07 |
| gpt-oss:20b-cloud | 0.00 | 0.06 | 0.06 | 0.00 |
| gpt-oss:120b-cloud | 0.00 | 0.02 | 0.06 | 0.00 |

gemma4:31b-cloud: 0% across all tiers and defenses — fully resistant to all injection strategies tested.

### Defense effectiveness on llama3.2:3b (fused defense)

| Tier | Undefended | Fused | Reduction |
|------|-----------|-------|-----------|
| T1 | 0.08 | 0.00 | 100% |
| T1b | 0.22 | 0.00 | 100% |
| T2 | 0.12 | 0.00 | 100% |
| T3 | 0.00 | 0.00 | — |

FusedDefense achieves 0% ASR across all tiers. Cost: ~50% retrieval rate (high FPR — documented honestly in Phase 5 with per-chunk, answer-preserved, and judge-scored utility metrics).

### Causal attribution (leave-one-out influence)
LOO ROC AUC = 0.372 (llama) / 0.410 (mistral) — **below 0.5 (negative result)**. Clean chunks are *more* attributable than injected chunks because injected payloads are redundant; removing one does not restore clean behavior. This finding is documented in `logs/loo_negative_result_analysis.md`.

---

## Latest Results — Where to Look

| What | Path |
|------|------|
| Full 75-cell ASR matrix (all models × defenses × tiers) | `logs/eval_matrix/_summary_v6.json` |
| Undefended baseline table (Markdown) | `docs/results/undefended_baseline.md` |
| Arms race table (Markdown) | `docs/results/arms_race_table.md` |
| Ablation table (per-signal defense breakdown) | `docs/results/ablation_table.md` |
| Cross-model matrix (CSV) | `docs/results/cross_model_matrix.csv` |
| Presentation figures (10 files, talk-ready) | `figures/final/` |
| Phase 3 writeup (submitted) | `docs/phase3_results.md` |
| Honest FPR analysis | `docs/phase5_honest_fpr.md` |
| LOO negative result analysis | `logs/loo_negative_result_analysis.md` |
| DEF-02 priming analysis | `logs/def02_priming_analysis.md` |

### Figures in `figures/final/`

| File | Description |
|------|-------------|
| `d03_arms_race_v6.png` | Arms race bars — 4 tiers × 4 LLMs × 3 defenses |
| `d12_cross_model_heatmap_v6.png` | Cross-model ASR under fused defense (4×4 heatmap) |
| `d12_undefended_v6.png` | Cross-model undefended baseline (4×4 heatmap) |
| `fig2_utility_security.png` | ASR vs retrieval rate tradeoff (security-utility curve) |
| `fig3_loo_causal.png` | LOO influence ROC + inversion scatter (negative result) |
| `fig4_ratio_sweep.png` | T1 ASR vs poisoning ratio (0.5%–10%) |
| `diagram_a_rag_pipeline.png` | RAG pipeline architecture diagram |
| `diagram_b_defense_pipeline.png` | Defense layer architecture diagram |
| `demo_tier2_mistral.gif` | Live demo: T2 attack hijacking mistral |
| `qr_github.png` | QR code to repo |

---

## Setup

### Prerequisites

- **Python 3.11**
- **Ollama** installed and running ([install guide](https://ollama.com/download))
- **Conda** (recommended)

### Installation

```bash
git clone https://github.com/waleed79/CS763-indirect_prompt_injection.git
cd CS763-indirect_prompt_injection

conda create -n rag-security python=3.11 -y
conda activate rag-security
pip install -r requirements.txt
```

Pull the LLM targets via Ollama:

```bash
ollama serve          # separate terminal
ollama pull llama3.2:3b
ollama pull mistral:7b
# gpt-oss models require Ollama cloud access
```

### Trained models (not in git — too large)

The BERT classifier (`models/bert_classifier/model.safetensors`, ~256 MB) and multi-seed models (`models/bert_s{1,2,3}/`) are gitignored. Config files and tokenizer artifacts are committed. To regenerate:

```bash
python scripts/train_defense.py                              # default classifier
python scripts/train_defense.py --seed 1 --bert-output models/bert_s1 --lr-output models/lr_meta_classifier_s1.json
python scripts/train_defense.py --seed 2 --bert-output models/bert_s2 --lr-output models/lr_meta_classifier_s2.json
python scripts/train_defense.py --seed 3 --bert-output models/bert_s3 --lr-output models/lr_meta_classifier_s3.json
```

---

## Running

### Run the full evaluation matrix

Reproduces the 45-cell llama/mistral/gemma matrix (3 models × 3 defenses × 5 tiers):

```bash
python scripts/run_eval_matrix.py
# logs land in logs/eval_matrix/; aggregate in logs/eval_matrix/_summary.json
```

For the gpt-oss cloud models (Phase 6, requires Ollama cloud):

```bash
python scripts/run_phase6_eval.py
# produces logs/eval_harness_undefended_gptoss20b_v6.json etc.
# full 75-cell summary: logs/eval_matrix/_summary_v6.json
```

### Regenerate result tables and figures

```bash
python scripts/make_results.py   # regenerates docs/results/*.md and *_v6.csv
python scripts/make_figures.py   # regenerates figures/*.png
# then copy updated PNGs to figures/final/ as needed
```

### Run the test suite

```bash
pytest                           # ~235 tests; 1 pre-existing Phase 5 skip expected
pytest tests/test_phase6_eval.py # Phase 6 specific (20 tests)
```

---

## Project Structure

```
CS763-indirect_prompt_injection/
├── rag/                        # Core RAG pipeline package
│   ├── config.py               # Config dataclass + TOML loader
│   ├── corpus.py               # NQ passage loading, word-budget chunking
│   ├── retriever.py            # SentenceTransformer + ChromaDB retrieval
│   ├── generator.py            # Ollama LLM generation wrapper
│   ├── logger.py               # Append-only JSONL retrieval logger
│   ├── pipeline.py             # End-to-end RAGPipeline orchestrator
│   ├── defense.py              # FusedDefense + DEF-02 + individual signal detectors
│   ├── attack.py               # Poisoned corpus generation (all tiers)
│   └── constants.py            # Shared ID ranges, tier boundaries, attack constants
├── scripts/
│   ├── run_eval.py             # General evaluation harness (--defense, --model flags)
│   ├── run_eval_matrix.py      # 45-cell matrix driver (3 LLMs × 3 defenses × 5 tiers)
│   ├── run_phase6_eval.py      # Phase 6 cloud model eval (gpt-oss 20b/120b)
│   ├── run_judge.py            # LLM-as-judge semantic hijack scorer
│   ├── run_loo.py              # Leave-one-out causal influence analysis
│   ├── run_transferability_eval.py  # Embedding-model transferability sweep
│   ├── generate_poisoned_corpus.py  # Build poisoned JSONL + ChromaDB collection
│   ├── train_defense.py        # Fine-tune BERT classifier + calibrate LR meta-clf
│   ├── make_results.py         # Emit docs/results/*.md tables + CSV companions
│   ├── make_figures.py         # Emit figures/*.png (all renderers)
│   └── make_qr.py              # QR code generator
├── tests/                      # 20 test files, ~235 tests
│   ├── test_defense.py         # FusedDefense unit tests
│   ├── test_phase6_eval.py     # Phase 6 eval harness + summary (20 tests)
│   ├── test_make_results_v6.py # v6 results table tests
│   ├── test_judge_fpr.py       # LLM-as-judge FPR tests
│   ├── test_judge_per_tier.py  # Per-tier judge scoring
│   ├── test_loo.py             # LOO causal analysis tests
│   ├── test_loo_neg_doc.py     # LOO negative result doc structure
│   ├── test_make_figures.py    # Figure renderer smoke tests
│   ├── test_make_results.py    # Results table tests
│   └── ...                     # chunking, corpus, pipeline, retriever, etc.
├── data/
│   ├── nq_500.jsonl            # Clean NQ corpus (500 passages)
│   ├── corpus_poisoned.jsonl   # Combined corpus (clean + poisoned passages)
│   └── test_queries.json       # 100 test queries for evaluation
├── docs/
│   ├── phase3_results.md       # Submitted Phase 3 writeup (frozen — do not edit)
│   ├── phase5_honest_fpr.md    # Honest FPR analysis (per-chunk, answer-preserved, judge)
│   └── results/                # Auto-generated tables (re-generated by make_results.py)
│       ├── undefended_baseline.md / _v6.csv
│       ├── arms_race_table.md / _v6.csv
│       ├── ablation_table.md / .csv
│       └── cross_model_matrix.md / .csv
├── figures/
│   ├── final/                  # 10 talk-ready presentation assets (canonical)
│   └── *.png                   # All rendered figures (source for final/)
├── logs/
│   ├── eval_matrix/
│   │   ├── _summary.json       # 45-cell matrix (llama/mistral/gemma)
│   │   └── _summary_v6.json    # 75-cell matrix (+ gpt-oss 20b/120b)
│   ├── eval_harness_undefended_gptoss20b_v6.json
│   ├── eval_harness_undefended_gptoss120b_v6.json
│   ├── ablation_table.json     # Full 7-defense ablation (llama3.2:3b)
│   ├── loo_results_llama.json  # LOO causal influence (llama)
│   ├── loo_results_mistral.json
│   ├── loo_negative_result_analysis.md
│   └── def02_priming_analysis.md
├── models/
│   ├── bert_classifier/        # Fine-tuned DistilBERT (model.safetensors gitignored)
│   │   ├── config.json
│   │   ├── tokenizer.json
│   │   └── checkpoint-72/      # Training checkpoint
│   └── lr_meta_classifier.json # LR meta-classifier weights
├── .chroma/                    # ChromaDB persistent store (gitignored)
├── .planning/                  # GSD planning artifacts (roadmap, phase plans, state)
├── config.toml                 # Pipeline configuration
├── requirements.txt            # Pinned Python dependencies
└── pytest.ini
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
