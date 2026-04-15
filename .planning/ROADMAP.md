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
- [ ] **Phase 2.3: Evaluation Harness** - Automated ASR measurement infrastructure with retrieval rate decomposition
- [ ] **Phase 2.4: Advanced Attack Tiers** - LLM-generated payloads (Tier 3) and cross-chunk fragmentation attacks (Tier 4)
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
**Plans**: TBD

**Optional requirements in this phase:** ATK-01b (3-tier taxonomy), ATK-02 (poisoning ratio sweep 0.1%-10%)

### Phase 2.3: Evaluation Harness
**Goal**: Automated experiment infrastructure measures ASR with retrieval rate decomposition, so defense development in Phase 3 has immediate quantitative feedback
**Depends on**: Phase 2.2
**Requirements**: EVAL-01
**Success Criteria** (what must be TRUE):
  1. Running the evaluation harness on a (corpus, attack, query set) triple produces a structured results file with ASR, retrieval rate, and conditional ASR
  2. The harness can run the same experiment with/without a defense active, producing comparable paired results
**Plans**: TBD

**Optional requirements in this phase:** EVAL-01 retrieval rate breakdown (flagged as optional in requirements)

### Phase 2.4: Advanced Attack Tiers
**Goal**: Two novel attack tiers are implemented — LLM-generated payloads (Tier 3) and cross-chunk fragmentation (Tier 4) — with ASR measured on the undefended pipeline
**Depends on**: Phase 2.3
**Requirements**: ATK-06, ATK-07
**Success Criteria** (what must be TRUE):
  1. An attacker LLM generates at least 20 distinct injection payloads via automated red-teaming prompts; ASR of LLM-generated payloads is measured and compared against hand-crafted Tier 1/2 payloads
  2. At least 3 cross-chunk fragmented payloads are crafted where each individual chunk passes naive inspection but the combined context window triggers the injection
  3. Co-retrieval rate is measured (probability that all fragments land in the same top-k retrieval) and reported
  4. Reassembly ASR is measured (conditional on co-retrieval, does the LLM follow the fragmented instruction?)
  5. All 4 attack tiers (naive, context-blending, LLM-generated, cross-chunk) have comparable ASR measurements
**Plans**: TBD
**UI hint**: no

### Phase 3.1: Multi-Signal Defense Fusion
**Goal**: A 4-signal ensemble defense is trained and integrated into the RAG pipeline, combining BERT classifier, perplexity anomaly detection, imperative sentence ratio, and retrieval score fingerprinting via a learned meta-classifier — reducing ASR on Tiers 1-3 measurably
**Depends on**: Phase 2.4
**Requirements**: DEF-01, DEF-03, DEF-04
**Success Criteria** (what must be TRUE):
  1. Each of the 4 individual signals produces a numeric score per retrieved chunk (independently testable)
  2. The meta-classifier (logistic regression or gradient boosting) combines the 4 signals into a single injection probability per chunk
  3. The fused defense is wired into the pipeline between retrieval and generation via the existing `defense_fn` hook
  4. Individual signal ASR reduction is measured (BERT alone, perplexity alone, etc.) showing each is insufficient against all tiers
  5. The fused defense achieves lower ASR than any individual signal on at least 2 attack tiers
  6. False positive rate on clean queries is measured (defense should not filter legitimate chunks excessively)
**Plans**: TBD
**UI hint**: no

### Phase 3.2: Adaptive Attacks & Causal Attribution
**Goal**: The multi-signal defense is stress-tested with adaptive attacks (ATK-08), and causal influence attribution is implemented to detect cross-chunk fragmentation attacks that evade per-chunk defenses
**Depends on**: Phase 3.1
**Requirements**: ATK-08, DEF-05
**Success Criteria** (what must be TRUE):
  1. At least 2 adaptive attack strategies are tested against the fused defense (e.g., natural-language-only payloads that maintain low perplexity, payloads that avoid imperative mood)
  2. Adaptive attack ASR is measured and compared against non-adaptive tiers — demonstrating the arms race
  3. Leave-one-out causal influence is computed for a subset of queries (generate answer with/without each chunk, measure output divergence)
  4. The influence/relevance ratio anomaly metric is shown to distinguish injected chunks from clean chunks (ROC curve or precision-recall on labeled data)
  5. Causal attribution is evaluated specifically on cross-chunk fragmentation attacks (Tier 4) where per-chunk defenses fail
**Plans**: TBD
**UI hint**: no

### Phase 3.3: Quick Evaluation Additions
**Goal**: Three low-effort evaluations strengthen the generalizability and presentation impact of the project
**Depends on**: Phase 2.3 (can run in parallel with Phase 3.1/3.2)
**Requirements**: EVAL-06, EVAL-07, EVAL-08
**Success Criteria** (what must be TRUE):
  1. Retriever transferability: poisoned corpus ASR is measured with at least 3 embedding models (all-MiniLM-L6-v2, BAAI/bge-small-en-v1.5, all-mpnet-base-v2) and transfer rates reported
  2. Human stealthiness: at least 3 evaluators classify a blind mix of clean and poisoned passages; human detection accuracy is compared against the automated defense
  3. XSS/SSRF taxonomy: a formal mapping table exists connecting IPI attack classes to web security vulnerability classes (stored XSS ↔ corpus poisoning, reflected XSS ↔ query-time injection, CSP ↔ context sanitization, etc.)
**Plans**: TBD
**UI hint**: no

### Phase 3.4: Full Evaluation and Final Report
**Goal**: The complete arms race experiment matrix is run, results are analyzed honestly (including limitations and fundamental limits), and the Phase 3 Google Doc submission is written
**Depends on**: Phase 3.1, Phase 3.2, Phase 3.3
**Requirements**: EVAL-02, EVAL-03, EVAL-04, EVAL-05, PH3-01, PH3-02, PH3-03, PH3-04, PH3-05
**Success Criteria** (what must be TRUE):
  1. Results tables show ASR for all 4 attack tiers × 3 defense levels (no defense, individual signals, fused defense, causal attribution)
  2. At least one figure shows the escalation narrative (attack tier vs. defense generation effectiveness)
  3. Adaptive attack results demonstrate the arms race dynamic (defense works → attacker adapts → need better defense)
  4. A limitations section honestly names at least 2 things that did not work as expected, plus discusses fundamental limits of per-chunk defenses
  5. The Phase 3 document is submitted to the course Google Doc by Apr 30
**Plans**: TBD

**Optional requirements in this phase:** EVAL-02 (utility metrics), EVAL-03 (ASR-utility curve), EVAL-04 (held-out attack evaluation), EVAL-05 (multi-seed aggregation), PH3-04 (failure case analysis), PH3-05 (comparison to related work)

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
| 2.2 Attack Module | 1/2 | In progress | - |
| 2.3 Evaluation Harness | 0/2 | Planned | - |
| 2.4 Advanced Attack Tiers | 0/? | Not started | - |
| 3.1 Multi-Signal Defense Fusion | 0/? | Not started | - |
| 3.2 Adaptive Attacks & Causal Attribution | 0/? | Not started | - |
| 3.3 Quick Evaluation Additions | 0/? | Not started | - |
| 3.4 Full Evaluation and Final Report | 0/? | Not started | - |
| 4 Final Presentation | 0/? | Not started | - |

---
*Roadmap created: 2026-03-31*
*Restructured: 2026-04-13 — Direction A (arms race) added with advanced attack tiers, multi-signal defense fusion, causal attribution, and quick evaluation additions*
*Course deadlines: Phase 1 Mar 27 (done), Phase 2 Apr 12 (done), Phase 3 Apr 30, Presentation May 5-7*
