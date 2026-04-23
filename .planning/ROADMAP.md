# Roadmap: Indirect Prompt Injection in RAG Systems

## Overview

This project investigates indirect prompt injection attacks on RAG systems through an **attack-defense arms race** methodology. Rather than a simple "build attack, build defense" pipeline, the project escalates through four attack tiers and two defense generations, demonstrating that naive per-chunk defenses are fundamentally insufficient and that multi-signal defense fusion with causal attribution is required.

Work is structured around four fixed course deadlines: Phase 1 submission (Mar 27, done), Phase 2 submission (Apr 12, done), Phase 3 submission (Apr 30), and the final presentation (May 5-7). Phase 3 is the core research contribution: advanced attacks (LLM-generated payloads, cross-chunk fragmentation), a novel multi-signal defense, adaptive attacks against that defense, and causal influence analysis.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Course milestone groups
- Decimal phases (1.1, 1.2, 2.1, ...): Sub-phases within each milestone

Sub-phases execute in numeric order within each milestone group.

- [x] **Phase 1.1: Phase 1 Submission Writeup** - Problem statement, motivation, literature survey, threat model, and execution plan (due Mar 27 — OVERDUE) (completed 2026-04-01)
- [ ] **Phase 1.2: Initial RAG Pipeline** - [optional] Basic RAG pipeline running as Phase 1 initial results
- [ ] **Phase 2.1: RAG Pipeline Foundation** - Functional RAG pipeline with corpus, embedder, vector store, and LLM (needed for Apr 12 submission)
- [ ] **Phase 2.2: Attack Module** - Corpus poisoning attacks at 2 sophistication tiers with baseline ASR measurement
- [x] **Phase 2.3: Evaluation Harness** - Automated ASR measurement infrastructure with retrieval rate decomposition (completed 2026-04-21)
- [x] **Phase 2.4: Advanced Attack Tiers** - LLM-generated payloads (Tier 3) and cross-chunk fragmentation attacks (Tier 4) (completed 2026-04-23)
- [ ] **Phase 3.1: Multi-Signal Defense Fusion** - 4-signal ensemble defense (BERT + perplexity + imperative ratio + retrieval fingerprint) with meta-classifier
- [ ] **Phase 3.2: Adaptive Attacks & Causal Attribution** - Defense-aware attacks + leave-one-out causal influence analysis
- [ ] **Phase 3.3: Quick Evaluation Additions** - Retriever transferability, human stealthiness evaluation, XSS/SSRF taxonomy mapping
- [ ] **Phase 3.4: Full Evaluation and Final Report** - Complete experiment matrix, arms race analysis, limitations, and Phase 3 writeup (due Apr 30)
- [ ] **Phase 4: Final Presentation** - 10-12 minute presentation with arms race narrative, plots, and demo (May 5-7)

## Phase Details

### Phase 1.1: Phase 1 Submission Writeup
**Goal**: The Phase 1 Google Doc submission is complete with a clear problem statement, motivation, literature survey, threat model, and execution plan that satisfies course requirements
**Depends on**: Nothing (first phase)
**Requirements**: PH1-01, PH1-02, PH1-03, PH1-04, PH1-05, PH1-06, PH1-07
**Success Criteria** (what must be TRUE):
  1. The document distinguishes indirect prompt injection from direct injection and explains why RAG creates a new attack surface
  2. The document cites at least 4 prior works (Greshake 2023, PoisonedRAG, BIPIA, and one more) with substantive discussion of each
  3. The threat model specifies what the attacker can and cannot control (corpus write access, no LLM access, etc.)
  4. The document maps remaining work to Phase 2 (Apr 12) and Phase 3 (Apr 30) deadlines with clear deliverables per deadline
  5. The pivot from TVRID is explained in one paragraph with rationale
**Plans**: 2 plans
Plans:
- [x] 01.1-01-PLAN.md — Write abstract, pivot note, problem statement, motivation, literature survey (Sections 1-5)
- [x] 01.1-02-PLAN.md — Write threat model, methodology, execution plan + human verification checkpoint (Sections 6-8)

### Phase 1.2: Initial RAG Pipeline [optional]
**Goal**: A minimal working RAG pipeline exists that can be referenced as initial results in the Phase 1 submission
**Depends on**: Phase 1.1
**Requirements**: PH1-08
**Success Criteria** (what must be TRUE):
  1. A query can be submitted to the pipeline and an LLM-generated answer is returned that uses retrieved context
  2. Retrieval quality on clean queries is logged and can be reported as a baseline metric
**Plans**: TBD

### Phase 2.1: RAG Pipeline Foundation
**Goal**: A reproducible, custom RAG pipeline is running end-to-end on an established corpus, with retrieval logging that enables all downstream attack and defense experiments
**Depends on**: Phase 1.1
**Requirements**: RAG-01, RAG-02, RAG-03, RAG-04, RAG-05
**Success Criteria** (what must be TRUE):
  1. A user query returns an LLM-generated answer grounded in retrieved corpus chunks (end-to-end RAG query works)
  2. Retrieved documents per query are logged with document IDs, similarity scores, and chunk content
  3. A clean corpus of 500+ passages is indexed and queryable; scaling to 1000+ is optional (RAG-02 scale note)
  4. The setup is reproducible: pinned package versions, random seeds, and a config file produce identical retrieval results on rerun
**Plans**: 4 plans
Plans:
- [x] 02.1-01-PLAN.md — Conda env setup, requirements.txt, pytest scaffolding (7 test stubs)
- [x] 02.1-02-PLAN.md — Config system (config.toml + rag/config.py), corpus loader, word-budget chunker, data/nq_500.jsonl
- [x] 02.1-03-PLAN.md — Retriever (ChromaDB + SentenceTransformer), Generator (Ollama), Logger (JSONL), Pipeline orchestrator
- [x] 02.1-04-PLAN.md — Demo notebook (demo.ipynb) + full pipeline verification checkpoint

### Phase 2.2: Attack Module
**Goal**: At least two tiers of corpus poisoning attacks are implemented, attack corpus generation is scripted, and baseline ASR on the undefended pipeline is measured
**Depends on**: Phase 2.1
**Requirements**: ATK-01, ATK-01b, ATK-02, ATK-03, ATK-04, ATK-05
**Success Criteria** (what must be TRUE):
  1. Naive attack (literal "ignore previous instructions" style) successfully hijacks LLM output on a measurable fraction of test queries
  2. At least one more sophisticated attack tier (obfuscated or context-blending) achieves measurable ASR distinct from the naive tier
  3. At least two payload types are demonstrated: instruction override and one of misinformation injection or data exfiltration
  4. Poisoned corpus generation is scripted and reproducible — running the script produces a deterministic poisoned corpus
  5. Baseline ASR is recorded numerically for the undefended pipeline (this number motivates the defense)
**Plans**: 2 plans

**Deferred to Phase 3.3:** ATK-01b (obfuscated/encoding tier), ATK-02 (poisoning ratio sweep), EVAL-V2-02 (LLM-as-judge ASR)

### Phase 2.3: Evaluation Harness
**Goal**: Automated experiment infrastructure measures ASR with retrieval rate decomposition, so defense development in Phase 3 has immediate quantitative feedback
**Depends on**: Phase 2.2
**Requirements**: EVAL-01
**Success Criteria** (what must be TRUE):
  1. Running the evaluation harness on a (corpus, attack, query set) triple produces a structured results file with ASR, retrieval rate, and conditional ASR
  2. The harness can run the same experiment with/without a defense active, producing comparable paired results
  3. Tier-2 ASR is non-zero (payload fixed from 0% baseline in Phase 2.2)
**Plans**: 2 plans
Plans:
- [x] 02.3-01-PLAN.md — Expand test_queries.json to 100 entries (50 paired/50 clean), fix generate_poisoned_corpus.py for 50 topics + URL-based Tier-2, regenerate corpus_poisoned.jsonl
- [x] 02.3-02-PLAN.md — Fix run_eval.py bugs (passage IDs, collection default, paired field, paired_asr aggregates, --model/--delay flags), run canonical undefended evals for 4 models: llama3.2:3b, mistral:7b, gpt-oss:20b-cloud, gpt-oss:120b-cloud

**Optional:** EVAL-01 retrieval rate breakdown (conditional ASR per tier)

### Phase 2.4: Advanced Attack Tiers
**Goal**: Two novel attack tiers are implemented — LLM-generated payloads (Tier 3) and cross-chunk fragmentation (Tier 4) — with ASR measured on the undefended pipeline

**Attacker LLM for Tier 3 payload generation:** `gpt-oss:20b-cloud` (actual; Rule 3 deviation from original plan). Originally specified as `kimi-k2.5:cloud` (Moonshot AI, 256K context) but at execution time kimi-k2.5:cloud required a paid Ollama subscription the team does not have. Substituted with gpt-oss:20b-cloud — the research objective (generate semantically coherent factual prose with an embedded anchor token so the payload evades per-chunk injection detectors) is identical. Run via `ollama run gpt-oss:20b-cloud` (requires `ollama login`; no code changes beyond passing the model name). `--model` flag on `run_eval.py` preserves forward compatibility if kimi access becomes available.

**Depends on**: Phase 2.3
**Requirements**: ATK-06, ATK-07
**Success Criteria** (what must be TRUE):
  1. An attacker LLM generates at least 20 distinct injection payloads via automated red-teaming prompts; ASR of LLM-generated payloads is measured and compared against hand-crafted Tier 1/2 payloads
  2. At least 3 cross-chunk fragmented payloads are crafted where each individual chunk passes naive inspection but the combined context window triggers the injection
  3. Co-retrieval rate is measured (probability that all fragments land in the same top-k retrieval) and reported
  4. Reassembly ASR is measured (conditional on co-retrieval, does the LLM follow the fragmented instruction?)
  5. All 4 attack tiers (naive, context-blending, LLM-generated, cross-chunk) have comparable ASR measurements
  6. Cross-model baseline is established: all 4 tiers are run against both llama3.2:3b and mistral:7b, producing the first cross-model ASR comparison in the project — results table covers both models
  7. LLM-as-judge semantic ASR is piloted alongside substring matching on Tier 3 payloads — measures agreement rate between the two methods (EVAL-V2-02 bootstrap)
**Plans**: 3 plans
Plans:
- [x] 02.4-01-PLAN.md — Wave 0 test stubs (test_corpus.py, test_pipeline.py, test_generator.py) + Tier 3 batch generation script + data/t3_payloads.jsonl (completed 2026-04-23)
- [x] 02.4-02-PLAN.md — Extend generate_poisoned_corpus.py with Tier 4 static fragments + assemble data/corpus_poisoned.jsonl (all 4 tiers) (completed 2026-04-23)
- [x] 02.4-03-PLAN.md — Extend run_eval.py (4-tier predicate fix + metrics) + create run_judge.py + build nq_poisoned_v4 + cross-model eval (completed 2026-04-23)

### Phase 3.1: Multi-Signal Defense Fusion
**Goal**: A 4-signal ensemble defense is trained and integrated into the RAG pipeline, combining BERT classifier, perplexity anomaly detection, imperative sentence ratio, and retrieval score fingerprinting via a learned meta-classifier — reducing ASR on Tiers 1-3 measurably
**Depends on**: Phase 2.4
**Requirements**: DEF-01, DEF-02, DEF-03, DEF-04
**Success Criteria** (what must be TRUE):
  1. Each of the 4 individual signals produces a numeric score per retrieved chunk (independently testable)
  2. The meta-classifier (logistic regression or gradient boosting) combines the 4 signals into a single injection probability per chunk
  3. The fused defense is wired into the pipeline between retrieval and generation via the existing `defense_fn` hook
  4. Individual signal ASR reduction is measured (BERT alone, perplexity alone, etc.) showing each is insufficient against all tiers — per-signal ablation table included
  5. The fused defense achieves lower ASR than any individual signal on at least 2 attack tiers
  6. False positive rate on clean queries is measured (defense should not filter legitimate chunks excessively)
  7. DEF-02 prompt-engineering baseline (system-prompt instruction-data separation) is implemented and measured as an ablation comparison — establishes that rule-based instruction separation alone is insufficient, motivating the statistical multi-signal approach
**Plans**: 6 plans
Plans:
- [x] 03.1-01-PLAN.md — Wave 0: test stubs (tests/test_defense.py, TestGenerateSystemPrompt), models/ dir, DistilBERT pre-flight (completed 2026-04-23)
- [ ] 03.1-02-PLAN.md — rag/defense.py: FusedDefense + SingleSignalDefense + all 4 signal extractors
- [ ] 03.1-03-PLAN.md — DEF-02: DEF_02_SYSTEM_PROMPT in generator.py + system_prompt kwarg threading through pipeline.query()
- [ ] 03.1-04-PLAN.md — scripts/train_defense.py: offline BERT fine-tune + LR meta-classifier + Signal 4 calibration; run training
- [ ] 03.1-05-PLAN.md — scripts/run_eval.py: extend --defense to 7 modes, add FPR tracking, system_prompt threading
- [ ] 03.1-06-PLAN.md — Run ablation evaluations (7 modes x llama + 2 x mistral); assemble ablation_table.json; human checkpoint
**UI hint**: no

### Phase 3.2: Adaptive Attacks & Causal Attribution
**Goal**: The multi-signal defense is stress-tested with adaptive attacks (ATK-08, ATK-09), and causal influence attribution is implemented to detect cross-chunk fragmentation attacks that evade per-chunk defenses
**Depends on**: Phase 3.1
**Requirements**: ATK-08, ATK-09, DEF-05, EVAL-05
**Success Criteria** (what must be TRUE):
  1. At least 2 adaptive attack strategies are tested against the fused defense (natural-language-only payloads with low perplexity, payloads that avoid imperative mood)
  2. ATK-09 (non-imperative declarative-only adaptive attack) is explicitly tested — targets the imperative-ratio signal specifically; its ASR demonstrates that single-signal gaps remain exploitable
  3. Adaptive attack ASR is measured and compared against non-adaptive tiers — demonstrating the arms race escalation narrative
  4. Leave-one-out causal influence is computed for a subset of queries (generate answer with/without each chunk, measure output divergence)
  5. The influence/relevance ratio anomaly metric distinguishes injected chunks from clean chunks (ROC curve or precision-recall on labeled data)
  6. Causal attribution is evaluated specifically on cross-chunk fragmentation attacks (Tier 4) where per-chunk defenses fail
  7. Results are aggregated over 3 random seeds (EVAL-05) — mean ± std dev reported for key ASR metrics across the arms race table
**Plans**: TBD
**UI hint**: no

### Phase 3.3: Quick Evaluation Additions
**Goal**: Six targeted evaluations — capturing all items deferred from earlier phases — that collectively strengthen generalizability, reproduce key literature comparisons, and add novel dimensions not found in existing RAG attack papers
**Depends on**: Phase 2.3 (can run in parallel with Phase 3.1/3.2)
**Requirements**: EVAL-06, EVAL-07, EVAL-08, ATK-01b, ATK-02, EVAL-V2-01, EVAL-V2-02

**Extended model targets (added 2026-04-23):** During Phase 2.4 execution we discovered two additional cloud models available in the project's Ollama installation: `gemma4:31b-cloud` (Google, 32.7B dense, 262K context) and `minimax-m2.5:cloud` (MoE 230B/10B active, 204K context). Both were absent from the original model matrix because the plan was written before their availability was confirmed. They are added to Phase 3.3 (not earlier phases) because:
- The Phase 2.4 two-model cross-model eval (llama + mistral) is already a complete, committed result; retrofitting it would break reproducibility of Phase 2.4 verification artifacts.
- Phase 3.3 is the natural "extended evaluation" slot, explicitly scoped for additions that strengthen generalizability.
- **Gemma4 rationale** (primary addition): fills the Google RLHF lineage gap — current matrix covers Meta (llama3.2), Mistral, and OpenAI (gpt-oss) lineages; gemma4 is architecturally distinct enough that divergent ASR is expected and publishable. Its 262K context window also stress-tests Tier 4 fragment co-retrieval under longer contexts. Public Gemma-family jailbreak reports suggest non-zero attack surface, unlike cloud OpenAI models that floor Tier 1 to 0%.
- **Minimax rationale** (stretch target): reported 100% jailbreak resistance makes it a "hard target" — either our Tier 4 fragmentation attack breaks it (strong paper claim) or it doesn't (informative negative result showing architecture matters). Added as lower-priority stretch; dropped if time is tight.

**Success Criteria** (what must be TRUE):
  1. Retriever transferability (EVAL-06): poisoned corpus ASR is measured with at least 3 embedding models — `nomic-embed-text` (primary, MTEB 62.4, 8192-token context), `mxbai-embed-large` (MTEB 64.7, strong BEIR performer), and `all-MiniLM-L6-v2` (legacy baseline, MTEB 56.3, preserved from Phase 2.1 for direct comparison) — novel finding as embedding-specific transfer for poisoning is not in published literature
  2. Human stealthiness (EVAL-07): at least 3 evaluators classify a blind mix of clean and poisoned passages; human detection accuracy compared against automated defense
  3. XSS/SSRF taxonomy (EVAL-08): formal mapping table connecting IPI attack classes to web security vulnerability classes with specific examples per mapping (stored XSS ↔ corpus poisoning, SSRF ↔ tool-call injection, CSP ↔ context sanitization)
  4. Poisoning ratio sweep (ATK-02, deferred from Phase 2.2): ASR measured at 5 poisoning ratios (0.5%, 1%, 2%, 5%, 10% of corpus size) — produces the ASR-vs-poisoning-ratio curve needed for the final results section
  5. Obfuscated encoding tier (ATK-01b, deferred from Phase 2.2): one additional attack variant using encoding obfuscation (Base64-encoded payload, Unicode homoglyphs, or whitespace-padded tokens) measured against the undefended pipeline to complete the 3-tier taxonomy
  6. Cross-model full matrix (EVAL-V2-01): the complete attack/defense experiment matrix (all 4 tiers × 3 defense levels) is run against llama3.2:3b and mistral:7b, and additionally against `gemma4:31b-cloud` (Google lineage; added 2026-04-23, see rationale above) — demonstrates attack generalizability across LLM architectures and lineages; this is a differentiating result vs. single-model RAG attack papers
  7. **[Stretch]** Hard-target test: run all 4 attack tiers against `minimax-m2.5:cloud` and report ASR — either a breakthrough result (Tier 4 penetrates a reportedly jailbreak-resistant model) or a documented negative finding; drop if time does not permit
**Plans**: TBD
**UI hint**: no

### Phase 3.4: Full Evaluation and Final Report
**Goal**: The complete arms race experiment matrix is run, results are analyzed honestly (including limitations and fundamental limits), and the Phase 3 Google Doc submission is written
**Depends on**: Phase 3.1, Phase 3.2, Phase 3.3
**Requirements**: EVAL-02, EVAL-03, EVAL-04, PH3-01, PH3-02, PH3-03, PH3-04, PH3-05
**Success Criteria** (what must be TRUE):
  1. Results tables show ASR for all 4 attack tiers × 3 defense levels (no defense, individual signals, fused defense, causal attribution) across 4 LLM columns: llama3.2:3b, mistral:7b, gpt-oss:20b-cloud, gpt-oss:120b-cloud — with per-variant Tier-1 breakdown included. The llama3.2:3b Tier-1/2 undefended row is seeded from `logs/attack_baseline.json` (Phase 2.2, 10-query frozen reference) alongside the Phase 2.3 100-query canonical runs.
  2. At least one figure shows the escalation narrative (attack tier vs. defense generation effectiveness across the arms race)
  3. Adaptive attack results demonstrate the arms race dynamic (defense works → attacker adapts → need better defense)
  4. A limitations section honestly names at least 2 things that did not work as expected, plus discusses fundamental limits of per-chunk defenses vs. cross-chunk-aware approaches
  5. Comparison to PoisonedRAG/BadRAG (PH3-05) is included — methodology differences are described and expected ASR differences discussed; this positions the contribution relative to the 2024-2025 literature (required, not optional)
  6. The Phase 3 document is submitted to the course Google Doc by Apr 30
**Plans**: TBD

**Optional:** EVAL-02 (utility metrics), EVAL-03 (ASR-utility curve), EVAL-04 (held-out attack evaluation), PH3-04 (failure case analysis)

### Phase 4: Final Presentation
**Goal**: A 10-12 minute presentation is ready that communicates the problem, approach, results, and conclusions clearly to fellow CS 763 students
**Depends on**: Phase 3.2
**Requirements**: PRES-01, PRES-02, PRES-03, PRES-04
**Success Criteria** (what must be TRUE):
  1. The slide deck fits a 10-12 minute delivery with problem, approach, results, and conclusions covered
  2. At least two visualizations are included (e.g., ASR bar chart and system architecture diagram)
  3. RAG and indirect prompt injection are defined on slides in terms a security student without RAG background can follow
**Plans**: TBD

**Optional requirements in this phase:** PRES-03 (live or recorded attack demo)

## Progress

**Execution Order:**
1.1 → 2.1 → 2.2 → 2.3 → 2.4 → 3.1 → 3.2 → 3.3 (parallel with 3.1/3.2) → 3.4 → 4

**Arms Race Flow:**
```
Tier 1-2 attacks (2.2) → Eval harness (2.3) → Tier 3-4 attacks (2.4)
                                                       ↓
                                              Multi-signal defense (3.1)
                                                       ↓
                                              Adaptive attacks + causal attribution (3.2)
                                                       ↓
                                              Full evaluation & report (3.4)

Quick additions (3.3) runs in parallel with 3.1/3.2
```

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1.1 Phase 1 Submission Writeup | 2/2 | Complete | 2026-04-01 |
| 1.2 Initial RAG Pipeline [optional] | — | Skipped | — |
| 2.1 RAG Pipeline Foundation | 4/4 | Complete | 2026-04-12 |
| 2.2 Attack Module | 2/2 | Complete | 2026-04-15 |
| 2.3 Evaluation Harness | 2/2 | Complete | 2026-04-21 |
| 2.4 Advanced Attack Tiers | 3/3 | Complete | 2026-04-23 |
| 3.1 Multi-Signal Defense Fusion | 1/6 | In progress | 2026-04-23 |
| 3.2 Adaptive Attacks & Causal Attribution | 0/? | Not started | - |
| 3.3 Quick Evaluation Additions | 0/? | Not started | - |
| 3.4 Full Evaluation and Final Report | 0/? | Not started | - |
| 4 Final Presentation | 0/? | Not started | - |

---
*Roadmap created: 2026-03-31*
*Restructured: 2026-04-13 — Direction A (arms race) added*
*Audited: 2026-04-21 — Phase 2.2 marked complete; deferred items (ATK-01b, ATK-02, EVAL-V2-01) captured in Phase 3.3; cross-model baseline added to Phase 2.4; DEF-02 ablation added to Phase 3.1; ATK-09 and EVAL-05 (multi-seed) added to Phase 3.2; Phase 3.3 expanded from 3 to 6 criteria; PH3-05 made required in Phase 3.4; novelty positioning vs. PoisonedRAG/BadRAG/AttriBoT literature added throughout*
*Phase 2.3 replanned: 2026-04-21 — full replan from scratch; plan list updated to reflect corpus expansion + harness fixes*
*Phase 2.4 planned: 2026-04-22 — 3 plans in 2 waves; Tier 3 (kimi-k2.5:cloud originally specified) + Tier 4 (3-fragment fragmentation) + cross-model eval (llama + mistral) + EVAL-V2-02 judge pilot*
*Phase 2.4 executed: 2026-04-23 — Rule 3 deviation: Tier 3 attacker LLM substituted kimi-k2.5:cloud → gpt-oss:20b-cloud (kimi requires paid Ollama subscription; research objective preserved). All 3 plans complete, 7/7 must-haves verified.*
*Phase 3.3 updated: 2026-04-23 — added gemma4:31b-cloud as required attack target (Google lineage gap, divergent ASR expected) and minimax-m2.5:cloud as stretch target (hardened model, informative regardless of outcome); both discovered available during Phase 2.4 execution; added late to preserve Phase 2.4 result integrity and because Phase 3.3 is the correct "generalizability" slot*
*Course deadlines: Phase 1 Mar 27 (done), Phase 2 Apr 12 (done), Phase 3 Apr 30, Presentation May 5-7*
