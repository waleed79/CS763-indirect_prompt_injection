# Roadmap: Indirect Prompt Injection in RAG Systems

## Overview

This project builds and evaluates an end-to-end attack-and-defense pipeline for indirect prompt injection in RAG systems. Work is structured around four fixed course deadlines: Phase 1 submission (Mar 27, already past), Phase 2 submission (Apr 12), Phase 3 submission (Apr 30), and the final presentation (May 5-7). Sub-phases within each deadline group the natural work clusters — writing and pipeline work are separated because they have different execution patterns, and attacks must be demonstrated before defenses can be evaluated.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Course milestone groups
- Decimal phases (1.1, 1.2, 2.1, ...): Sub-phases within each milestone

Sub-phases execute in numeric order within each milestone group.

- [x] **Phase 1.1: Phase 1 Submission Writeup** - Problem statement, motivation, literature survey, threat model, and execution plan (due Mar 27 — OVERDUE) (completed 2026-04-01)
- [ ] **Phase 1.2: Initial RAG Pipeline** - [optional] Basic RAG pipeline running as Phase 1 initial results
- [ ] **Phase 2.1: RAG Pipeline Foundation** - Functional RAG pipeline with corpus, embedder, vector store, and LLM (needed for Apr 12 submission)
- [ ] **Phase 2.2: Attack Module** - Corpus poisoning attacks at 2-3 sophistication tiers with baseline ASR measurement
- [ ] **Phase 2.3: Evaluation Harness** - Automated ASR measurement infrastructure with retrieval rate decomposition
- [ ] **Phase 3.1: Defense Module** - BERT-based context sanitization classifier integrated into RAG pipeline
- [ ] **Phase 3.2: Full Evaluation and Final Report** - Complete experiment results, defense analysis, limitations, and Phase 3 writeup (due Apr 30)
- [ ] **Phase 4: Final Presentation** - 10-12 minute presentation with plots and demo (May 5-7)

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
- [ ] 02.1-01-PLAN.md — Conda env setup, requirements.txt, pytest scaffolding (7 test stubs)
- [ ] 02.1-02-PLAN.md — Config system (config.toml + rag/config.py), corpus loader, word-budget chunker, data/nq_500.jsonl
- [ ] 02.1-03-PLAN.md — Retriever (ChromaDB + SentenceTransformer), Generator (Ollama), Logger (JSONL), Pipeline orchestrator
- [ ] 02.1-04-PLAN.md — Demo notebook (demo.ipynb) + full pipeline verification checkpoint

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

### Phase 3.1: Defense Module
**Goal**: A BERT-based context sanitization classifier is trained, integrated as middleware in the RAG pipeline, and reduces ASR measurably on at least one attack tier
**Depends on**: Phase 2.3
**Requirements**: DEF-01, DEF-02, DEF-03
**Success Criteria** (what must be TRUE):
  1. The BERT classifier correctly labels at least one attack tier's poisoned chunks as malicious (precision/recall measured on a labeled test set)
  2. The defense is wired into the pipeline between retrieval and generation — enabling the defense flag changes which chunks the LLM sees
  3. Defended ASR is lower than baseline ASR on at least one attack tier (measured by the evaluation harness)
**Plans**: TBD

**Optional requirements in this phase:** DEF-02 (attention mask / prompt-engineering complement to DEF-01)

### Phase 3.2: Full Evaluation and Final Report
**Goal**: The complete experiment matrix is run, results are analyzed honestly (including limitations), and the Phase 3 Google Doc submission is written
**Depends on**: Phase 3.1
**Requirements**: EVAL-02, EVAL-03, EVAL-04, EVAL-05, PH3-01, PH3-02, PH3-03, PH3-04, PH3-05
**Success Criteria** (what must be TRUE):
  1. Results tables show before/after ASR for all implemented attack tiers with the defense active
  2. At least one figure shows the ASR-utility tradeoff (or ASR bar chart comparing attack tiers with and without defense)
  3. A limitations section exists that honestly names at least 2 things that did not work as expected or could not be tested
  4. The Phase 3 document is submitted to the course Google Doc by Apr 30
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
1.1 → 1.2 → 2.1 → 2.2 → 2.3 → 3.1 → 3.2 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1.1 Phase 1 Submission Writeup | 2/2 | Complete | 2026-04-01 |
| 1.2 Initial RAG Pipeline [optional] | 0/? | Not started | - |
| 2.1 RAG Pipeline Foundation | 0/4 | Planning complete | - |
| 2.2 Attack Module | 0/? | Not started | - |
| 2.3 Evaluation Harness | 0/? | Not started | - |
| 3.1 Defense Module | 0/? | Not started | - |
| 3.2 Full Evaluation and Final Report | 0/? | Not started | - |
| 4 Final Presentation | 0/? | Not started | - |

---
*Roadmap created: 2026-03-31*
*Course deadlines: Phase 1 Mar 27 (OVERDUE), Phase 2 Apr 12, Phase 3 Apr 30, Presentation May 5-7*
