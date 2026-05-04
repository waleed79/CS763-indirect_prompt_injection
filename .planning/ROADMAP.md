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
- [x] **Phase 3.1: Multi-Signal Defense Fusion** - 4-signal ensemble defense (BERT + perplexity + imperative ratio + retrieval fingerprint) with meta-classifier (completed 2026-04-24)
- [x] **Phase 3.2: Adaptive Attacks & Causal Attribution** - Defense-aware attacks + leave-one-out causal influence analysis (completed 2026-04-24)
- [ ] **Phase 3.3: Quick Evaluation Additions** - Retriever transferability, human stealthiness evaluation, XSS/SSRF taxonomy mapping
- [ ] **Phase 3.4: Full Evaluation and Final Report** - Complete experiment matrix, arms race analysis, limitations, and Phase 3 writeup (due Apr 30)
- [ ] **Phase 4: Final Presentation** - 10-12 minute presentation with arms race narrative, plots, and demo (May 5-7)
- [x] **Phase 5: Honest FPR Metrics** - Per-chunk FPR, answer-preserved FPR, and LLM-as-judge utility cost to replace the coarse 76% query-level FPR (post-presentation refinement) (completed 2026-05-03)
- [ ] **Phase 7: Honest FPR Metrics — gpt-oss extension** - Extend Phase 5's three honest FPR metrics (M1 per-chunk, M2 answer-preserved, M3 judge-scored) to the gpt-oss-20b-cloud and gpt-oss-120b-cloud RAG targets on the {fused, def02} cells produced by Phase 6. Compute M1/M2 from existing Phase 6 v6 logs (no cloud calls); M3 requires ~200 cloud-judge calls (gpt-oss:20b-cloud as judge, mirroring Phase 5 setup). Output: logs/ablation_table_gptoss_v7.json + extended Phase 5 writeup. Wall-clock budget: ~26 min cloud + ~5 min downstream regen.

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
**Plans**: 7 plans
Plans:
- [x] 03.1-01-PLAN.md — Wave 0: test stubs (tests/test_defense.py, TestGenerateSystemPrompt), models/ dir, DistilBERT pre-flight (completed 2026-04-23)
- [x] 03.1-02-PLAN.md — rag/defense.py: FusedDefense + SingleSignalDefense + all 4 signal extractors (completed 2026-04-23)
- [x] 03.1-03-PLAN.md — DEF-02: DEF_02_SYSTEM_PROMPT in generator.py + system_prompt kwarg threading through pipeline.query() (completed 2026-04-23)
- [x] 03.1-04-PLAN.md — scripts/train_defense.py: offline BERT fine-tune + LR meta-classifier + Signal 4 calibration; run training (completed 2026-04-24)
- [x] 03.1-05-PLAN.md — scripts/run_eval.py: extend --defense to 7 modes, add FPR tracking, system_prompt threading (completed 2026-04-23)
- [x] 03.1-06-PLAN.md — Run ablation evaluations (7 modes x llama + 2 x mistral); assemble ablation_table.json; human checkpoint (completed 2026-04-23)
- [x] 03.1-07-PLAN.md — Wrap-up: run fused with tuned threshold, add retrieval_rate column to ablation_table, investigate DEF-02 counter-productive finding (priming vs. substring leak) (completed 2026-04-24)
**UI hint**: no

### Phase 3.2: Adaptive Attacks & Causal Attribution
**Goal**: The multi-signal defense is stress-tested with adaptive attacks (ATK-08, ATK-09), and causal influence attribution is implemented to detect cross-chunk fragmentation attacks that evade per-chunk defenses

**Priority reordering (decided 2026-04-23):** The Phase 3.1 ablation revealed BERT classifier scored suspiciously perfect (100% detection across all tiers), strongly suggesting memorization of the 5 anchor tokens (HACKED, COMPROMISED, INFILTRATED, SYSTEM_OVERRIDE, PAYLOAD_DELIVERED). The primary adaptive attack is therefore the **novel-anchor-token attack** (use synonym payloads the BERT classifier was never trained on, e.g., "BREACHED", "PWNED") to break BERT's detection floor. The imperative-free declarative attack is secondary but retained for defense-in-depth validation of the imperative-ratio signal.

**Depends on**: Phase 3.1
**Requirements**: ATK-08, ATK-09, DEF-05, EVAL-05
**Success Criteria** (what must be TRUE):
  1. **[Primary]** Novel-anchor-token adaptive attack (ATK-08 variant): payloads substitute the 5 trained anchor tokens with untrained synonyms (e.g., BREACHED, PWNED, OVERRIDDEN) to break the BERT classifier's suspiciously-perfect 100% detection floor observed in Phase 3.1; ASR measured against fused defense demonstrates the BERT signal's generalization gap
  2. **[Secondary]** ATK-09 (non-imperative declarative-only adaptive attack) is explicitly tested — targets the imperative-ratio signal specifically; its ASR demonstrates that single-signal gaps remain exploitable
  3. Adaptive attack ASR is measured and compared against non-adaptive tiers — demonstrating the arms race escalation narrative
  4. Leave-one-out causal influence is computed for a subset of queries (generate answer with/without each chunk, measure output divergence)
  5. The influence/relevance ratio anomaly metric distinguishes injected chunks from clean chunks (ROC curve or precision-recall on labeled data)
  6. Causal attribution is evaluated specifically on cross-chunk fragmentation attacks (Tier 4) where per-chunk defenses fail
  7. Results are aggregated over 3 random seeds (EVAL-05) — mean ± std dev reported for key ASR metrics across the arms race table
**Plans**: 4 plans
Plans:
- [x] 03.2-01-PLAN.md — Wave 0 test stubs: TestAdaptiveCorpus (ATK-08/09 payload validation), TestLooExcludeFn (DEF-05 contract), TestSeedVariance (EVAL-05 --seed flag) (completed 2026-04-24)
- [x] 03.2-02-PLAN.md — ATK-08/09 corpus (nq_poisoned_v5 collection), run_eval.py adaptive tier support (ADAPTIVE_ID_START, ADAPTIVE_HIJACK_STRS), train_defense.py --seed/--lr-output flags + 3 EVAL-05 seed runs (completed 2026-04-24)
- [x] 03.2-03-PLAN.md — scripts/run_loo.py (DEF-05: LOO causal attribution loop + judge calls + ROC AUC); run LOO for llama3.2:3b (AUC=0.372) and mistral:7b (AUC=0.410) (completed 2026-04-24)
- [x] 03.2-04-PLAN.md — Adaptive attack evals (ATK-08/09 vs fused, threshold sweep D-17, EVAL-05 aggregation), assemble arms race summary table in ablation_table.json + human checkpoint (completed 2026-04-24)
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

**Scope decisions (2026-04-23):**
- **EVAL-07 (human stealthiness study) removed**: 6-day timeline to Apr 30 deadline cannot accommodate IRB-style recruitment of 3 evaluators + blind classification + analysis. The automated defense's FPR (76% fused) already signals stealthiness from the detector side; human study becomes Future Work in Phase 3.4.
- **Minimax hard-target test (SC-7) demoted to Future Work**: removed from required criteria; parked as a "Future Work" footnote in the Phase 3.4 writeup. Rationale: gemma4 already fills the architectural-divergence slot, and a single minimax run is worth less than tightening the core arms race story.
- **Gemma4 kept as required** (not demoted to optional): the Google-lineage gap is load-bearing for the generalizability claim and cloud runs are cheap.
- **Remaining scope unchanged**: EVAL-06 retriever transfer, EVAL-08 XSS/SSRF taxonomy, ATK-02 poisoning ratio sweep, ATK-01b obfuscated tier, EVAL-V2-01 cross-model matrix all retained.

**Success Criteria** (what must be TRUE):
  1. Retriever transferability (EVAL-06): poisoned corpus ASR is measured with at least 3 embedding models — `nomic-embed-text` (primary, MTEB 62.4, 8192-token context), `mxbai-embed-large` (MTEB 64.7, strong BEIR performer), and `all-MiniLM-L6-v2` (legacy baseline, MTEB 56.3, preserved from Phase 2.1 for direct comparison) — novel finding as embedding-specific transfer for poisoning is not in published literature
  2. XSS/SSRF taxonomy (EVAL-08): formal mapping table connecting IPI attack classes to web security vulnerability classes with specific examples per mapping (stored XSS ↔ corpus poisoning, SSRF ↔ tool-call injection, CSP ↔ context sanitization)
  3. Poisoning ratio sweep (ATK-02, deferred from Phase 2.2): ASR measured at 5 poisoning ratios (0.5%, 1%, 2%, 5%, 10% of corpus size) — produces the ASR-vs-poisoning-ratio curve needed for the final results section
  4. Obfuscated encoding tier (ATK-01b, deferred from Phase 2.2): one additional attack variant using encoding obfuscation (Base64-encoded payload, Unicode homoglyphs, or whitespace-padded tokens) measured against the undefended pipeline to complete the 3-tier taxonomy
  5. Cross-model full matrix (EVAL-V2-01): the complete attack/defense experiment matrix (all **5 tiers** — T1, T1b, T2, T3, T4 — × 3 defense levels) is run against llama3.2:3b, mistral:7b, and `gemma4:31b-cloud` (Google lineage; added 2026-04-23, see rationale above) = **45 cells** in `logs/eval_matrix/`. T1b is included because Plan 02 (ATK-01b homoglyph tier) lands in Wave 1 before Plan 07 (matrix driver) in Wave 2. Demonstrates attack generalizability across LLM architectures and lineages; this is a differentiating result vs. single-model RAG attack papers

**Future Work (Phase 3.4 limitations footnote — not required to pass):**
- Human stealthiness study (EVAL-07): 3-evaluator blind classification task, deferred due to 6-day timeline
- Hard-target test against `minimax-m2.5:cloud`: all 5 tiers (T1, T1b, T2, T3, T4); informative regardless of outcome (breakthrough or documented resistance)

**Plans**: 7 plans
- [x] 03.3-01-PLAN.md — Wave 0 test stubs for all Phase 3.3 deliverables (ATK-01b, ATK-02, EVAL-06, EVAL-V2-01, EVAL-V2-02) (completed 2026-04-25)
- [x] 03.3-02-PLAN.md — ATK-01b Tier 1b Unicode homoglyph attack (TIER1B_ID_START=20150, HOMOGLYPH_HACKED, 50 passages IDs 20150-20199, run_eval tier1b metrics) (completed 2026-04-25)
- [x] 03.3-03-PLAN.md — ATK-02 poisoning ratio sweep driver + 5 corpora (0.5%/1%/2%/5%/10%; Tier-1 pool cycling into ATK02_SWEEP_ID_START 21000-21049) (completed 2026-04-25)
- [x] 03.3-04-PLAN.md — EVAL-06 retriever transferability (nomic, mxbai, MiniLM) with task-prefix support (completed 2026-04-25)
- [x] 03.3-05-PLAN.md — EVAL-V2-02 LLM-as-judge extension to 5 tiers (TIER_CONFIG + --tier flag) (completed 2026-04-25)
- [x] 03.3-06-PLAN.md — EVAL-08 XSS/SSRF taxonomy mapping table (docs/xss_ssrf_taxonomy.md) (completed 2026-04-25)
- [x] 03.3-07-PLAN.md — EVAL-V2-01 cross-model full matrix driver (3 LLMs × 3 defenses × 5 tiers = 45 cells in logs/eval_matrix/; causal→def02 fallback per CONTEXT D-12) (completed 2026-04-27)
**UI hint**: no

### Phase 3.4: Full Evaluation and Final Report
**Goal**: The complete arms race experiment matrix is run, results are analyzed honestly (including limitations and fundamental limits), and the Phase 3 Google Doc submission is written
**Depends on**: Phase 3.1, Phase 3.2, Phase 3.3
**Requirements**: EVAL-02, EVAL-03, EVAL-04, PH3-01, PH3-02, PH3-03, PH3-04, PH3-05
**Success Criteria** (what must be TRUE):
  1. Results tables aggregate evidence from three sources, all of which now exist:
     **(a) Phase 2.3 cross-LLM undefended baseline** — 4 LLMs (`llama3.2:3b`, `mistral:7b`, `gpt-oss:20b-cloud`, `gpt-oss:120b-cloud`) on Tier 1/2 attacks (`logs/eval_harness_undefended_*.json`).
     **(b) Phase 3.3 EVAL-V2-01 cross-model defense matrix** — 3 LLMs (`llama3.2:3b`, `mistral:7b`, `gemma4:31b-cloud`) × 3 defenses (`no_defense`, `fused`, `def02`) × 5 attack tiers (T1, T1b, T2, T3, T4) = 45 cells in `logs/eval_matrix/` and aggregated in `logs/eval_matrix/_summary.json`.
     **(c) Phase 3.1 single-LLM defense ablation** — `llama3.2:3b` × 7 defense modes (off, def02, bert, perplexity, imperative, fingerprint, fused) × 4 tiers in `logs/ablation_table.json`.
     The llama3.2:3b Tier-1/2 undefended row is seeded from `logs/attack_baseline.json` (Phase 2.2 10-query frozen reference) alongside the Phase 2.3 100-query canonical runs.
     **Note on the third defense column in (b):** `def02` is used in place of a runtime `causal` defense by deliberate design — Phase 3.2-03 measured LOO ROC AUC at 0.372 (llama) / 0.410 (mistral), both below random, so wiring LOO inline as a runtime filter would only confirm Phase 3.2's published negative result. `def02` (weak prompt-only baseline; counter-productive on llama per Phase 3.1-07) is the more informative third comparison point. See `.planning/phases/03.3-quick-evaluation-additions/03.3-07-SUMMARY.md` "On the third defense column" for the full framing.
     **Note on LLM column substitution in (b):** `gemma4:31b-cloud` (Google lineage) was added in Phase 3.3 CONTEXT (2026-04-23) for cross-architecture diversity. The four LLMs in (a) are still cited where Tier 1/2 undefended cross-LLM behavior is the question; the three LLMs in (b) cover the fully-defended matrix.
  2. At least one figure shows the escalation narrative (attack tier vs. defense generation effectiveness across the arms race)
  3. Adaptive attack results demonstrate the arms race dynamic (defense works → attacker adapts → need better defense)
  4. **Utility-Security Tradeoff subsection**: includes an ASR-vs-retrieval-rate figure and a per-mode FPR table drawn from `logs/ablation_table.json` (retrieval_rate column + fpr column). Explicitly shows the fused defense's 88% → 50% poisoned retrieval drop and its 76% clean-query FPR cost. This makes the utility price of the defense visible and honest rather than hiding behind ASR-only numbers.
  5. A limitations section honestly names at least 3 findings: (a) the **T3/T4 baseline puzzle** (paired ASR for Tier 3 and Tier 4 was 0% on llama3.2:3b undefended — defense cannot "reduce" what was never hitting; the result is methodologically correct but requires explanation rather than being framed as a defense win); (b) the **DEF-02 counter-productive finding** (system-prompt hardening *increased* paired ASR on llama3.2:3b from 2% → 8% on T1 and 12% → 38% on T2 — classified as priming/substring-leak/behavior-change per `logs/def02_priming_analysis.md`); (c) fundamental limits of per-chunk defenses vs. cross-chunk-aware approaches
  6. Comparison to PoisonedRAG/BadRAG (PH3-05) is included — methodology differences are described and expected ASR differences discussed; this positions the contribution relative to the 2024-2025 literature (required, not optional)
  7. The Phase 3 document is submitted to the course Google Doc by Apr 30
**Plans**: 6 plans
Plans:
- [x] 03.4-01-PLAN.md — Wave 0 scaffolding: pip install matplotlib/seaborn/tabulate, create figures/ + docs/results/ dirs, fix SSRF taxonomy citation API10:2023→API7:2023, run 5 ATK-02 ratio-sweep evals (D-06 inputs), schema-probe all log files, write 4 test stubs (test_make_results, test_make_figures, test_writeup_structure, test_loo_neg_doc) — **COMPLETE 2026-04-29**
- [x] 03.4-02-PLAN.md — Wave 1 (parallel): scripts/make_results.py — emit 4 Markdown + 4 CSV tables into docs/results/ from logs/ablation_table.json + _summary.json + eval_harness_undefended_*.json + attack_baseline.json; aggregates 3 sources per ROADMAP SC-1 — **COMPLETE 2026-04-29** (8 tables emitted, 4/4 unit tests PASS, DEFENSE_DISPLAY single-source-of-truth established)
- [x] 03.4-03-PLAN.md — Wave 1 (parallel): scripts/make_figures.py — render all 5 PNG figures (D-03 30-bar arms race, D-04 two-panel utility-security, D-05 two-panel inverted-ROC + scatter, D-06 log-scale ratio sweep, D-12 viridis_r heatmap) — **COMPLETE 2026-04-29** (5 PNGs emitted to figures/, 3/3 unit tests PASS, B-2 D-03 non-zero invariants and W-5 D-12 fail-loud invariants asserted; AUC=0.372/0.414 computed live from loo_results_*.json)
- [x] 03.4-04-PLAN.md — Wave 1 (parallel): logs/loo_negative_result_analysis.md — D-16 6-section DEF-05 failed-hypothesis analysis doc parallel to def02_priming_analysis.md style — **COMPLETE 2026-04-29** (245 lines, 5/5 unit tests PASS, AUC 0.372/0.410 cited from loo_results_*.json with 0.414 JSON-rounded form footnoted)
- [x] 03.4-05-PLAN.md — Wave 2: docs/phase3_results.md — 13-section writeup per CONTEXT D-09 (hero findings to §8(e)+(f), CR-02 disclosure in §1, SSRF API7:2023 in §12, AttriBoT≠LODO disambiguation in §11) — **COMPLETE 2026-04-29** (656 lines, 12/12 unit tests PASS)
- [x] 03.4-06-PLAN.md — Wave 3 (manual checkpoint): paste docs/phase3_results.md into existing Phase 1 Google Doc, upload 5 PNGs, verify paste fidelity, submit by Apr 30, record evidence in 03.4-SUBMISSION.md — **COMPLETE 2026-04-30** (submitted to course Google Doc)

**Optional:** EVAL-02 (utility metrics), EVAL-03 (ASR-utility curve), EVAL-04 (held-out attack evaluation), PH3-04 (failure case analysis)

**Future Work section** (from Phase 3.3 descope): EVAL-07 human stealthiness study, minimax-m2.5:cloud hard-target test

### Phase 4: Final Presentation
**Goal**: A 10-12 minute presentation is ready that communicates the problem, approach, results, and conclusions clearly to fellow CS 763 students
**Depends on**: Phase 3.2
**Requirements**: PRES-01, PRES-02, PRES-03, PRES-04
**Success Criteria** (what must be TRUE):
  1. The slide deck fits a 10-12 minute delivery with problem, approach, results, and conclusions covered
  2. At least two visualizations are included (e.g., ASR bar chart and system architecture diagram)
  3. RAG and indirect prompt injection are defined on slides in terms a security student without RAG background can follow
**Goal**: Deliver a 36×48" academic poster (May 4) AND a 10-12 minute Google Slides talk deck (May 5-7) for CS 763. Both leverage Phase 3.4 results (5 PNG figures + canonical writeup) plus 2 new architecture diagrams (RAG attack surface, 4-signal defense pipeline), a pre-recorded Tier-2 demo GIF on mistral:7b, and a QR code linking to the public GitHub repo.

**Plans**: 7 plans
Plans:
- [x] 04-01-PLAN.md — Wave 0 setup: install qrcode[pil]==8.2, create tests/test_phase4_assets.py stubs, capture verified GitHub URL + figure inventory + course poster template check
- [x] 04-02-PLAN.md — Wave 1: scripts/make_diagrams.py — render Diagram A (RAG pipeline w/ poisoned chunk highlighted #D62728) + Diagram B (4-signal defense pipeline) at 300 DPI
- [x] 04-03-PLAN.md — Wave 1: scripts/make_qr.py — emit figures/qr_github.png encoding the verified GitHub repo URL
- [x] 04-04-PLAN.md — Wave 1: scripts/make_demo_gif.md recipe + manual Win+G capture of Tier-2 mistral:7b hijack → figures/demo_tier2_mistral.gif (≤2 MB, 30-45s)
- [ ] 04-05-PLAN.md — Wave 2: compose 36×48" Google Slides poster per CONTEXT D-15 (9 sections: header/problem/diagrams/attacks/defense/2 hero panels/findings/limitations/QR); export PDF; ship by May 4
- [ ] 04-06-PLAN.md — Wave 3: compose 12-15 slide Google Slides 16:9 talk deck per CONTEXT D-11 (title/hook/RAG/threat model/5 tiers/demo GIF/defense/arms race hero/DEF-02/ATK-08/cross-model/limitations/conclusion/Q&A); ship by May 5-7
- [ ] 04-07-PLAN.md — Wave 4: stopwatch dry-run (PRES-01 timing) + 2-person pedagogical clarity review (PRES-04) + final poster + talk submission record in 04-SUBMISSION.md (mirrors 03.4-SUBMISSION.md pattern)

**Optional requirements in this phase:** PRES-03 (live or recorded attack demo) — Plan 04 satisfies via pre-recorded GIF (D-12)

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
| 3.1 Multi-Signal Defense Fusion | 7/7 | Complete | 2026-04-24 |
| 3.2 Adaptive Attacks & Causal Attribution | 4/4 | Complete | 2026-04-24 |
| 3.3 Quick Evaluation Additions | 7/7 | Complete | 2026-04-27 |
| 3.4 Full Evaluation and Final Report | 6/6 | Complete | 2026-04-30 |
| 4 Final Presentation | 4/7 | In Progress|  |
| 5 Honest FPR Metrics | 5/5 | Complete | 2026-05-03 |

### Phase 5: Honest FPR metrics — per-chunk, answer-preserved, and LLM-as-judge utility cost

**Goal:** Replace the project's coarse query-level FPR (currently 76%, "any chunk removed on a clean query") with three more honest utility-cost metrics so the defense's user-visible cost is pinned down rather than reported as an upper bound.

**Depends on:** Phase 3.4 (uses existing clean-query eval set + ablation infrastructure); Phase 4 narrative is downstream consumer

**Requirements**:
- New: per-chunk FPR = (clean chunks flagged) / (total clean chunks) across all clean queries
- New: answer-preserved FPR = clean queries where defense removed ≥1 chunk AND the LLM answer degraded vs defense-off
- New: LLM-as-judge FPR = degradation rate from pairwise judge over (defense-on answer, defense-off answer) on clean queries
- Update ablation table in Phase 3.4 report with the three new columns
- Update writeup sections that currently cite the 76% number to cite the new metrics with the original as upper bound

**Plans:** 1/5 plans executed

Plans:
- [x] 05-01-test-scaffolding-PLAN.md — Wave 0: tests/test_judge_fpr.py + tests/conftest.py with V-01..V-09 stubs
- [x] 05-02-judge-fpr-script-PLAN.md — Wave 1: scripts/run_judge_fpr.py (M1/M2/M3 + checkpoint cache + atomic ablation write)
- [x] 05-03-execute-judge-run-PLAN.md — Wave 2: live judge run, populate logs/judge_fpr_llama.json + extend logs/ablation_table.json
- [x] 05-04-writeup-PLAN.md — Wave 3: docs/phase5_honest_fpr.md (6-section writeup)
- [x] 05-05-callout-and-warning-PLAN.md — Wave 3: docs/phase3_results.md addendum + scripts/_build_ablation_table.py WARNING comment

**Notes:**
- Reuse existing clean-query eval set from Phase 3.4; no new data collection unless judge run requires re-inference
- Judge model selection (e.g. gpt-oss:20b-cloud, gemma4:31b-cloud, or smaller local model) to be locked in plan phase
- "Answer degraded" definition to be locked in plan phase (exact-match drop vs judge-scored)

### Phase 6: Cross-LLM undefended baseline gap fill: run gpt-oss:20b-cloud and gpt-oss:120b-cloud undefended on the existing combined poisoned corpus, single eval run per model, post-hoc per-tier tagging from passage_id to obtain T1, T1b, T2, T3, T4 ASR simultaneously. Fills the cross-LLM undefended baseline gap (Phase 2.3 only ran T1/T2 for these two cloud models). ~26 minutes total. Goal: emit two new logs/eval_harness_undefended_*.json artifacts that integrate with scripts/make_results.py aggregate-source format. Undefended (no_defense) only — no defense changes.

**Goal:** Emit cross-LLM undefended (gpt-oss:20b-cloud and gpt-oss:120b-cloud) AND defended (fused, def02) eval logs against nq_poisoned_v4 with all 5 tier ASRs surfaced post-hoc; auto-rerun downstream make_results.py + make_figures.py to produce "_v6" suffixed CSVs and PNGs without overwriting Phase 3.4 originals. Closes the cross-LLM gap with 6 single-pass cloud runs (~78 min) per CONTEXT D-09.
**Requirements**: P6-PRE, P6-RUN-20b-UND, P6-RUN-120b-UND, P6-PRO, P6-DEF, P6-MTX, P6-RES-PR, P6-RES-INT, P6-MD, P6-CSV, P6-D12-FUSED, P6-D12-UND, P6-D03, P6-FIG-INT, P6-AUTH, P6-ERR, P6-ENC
**Depends on:** Phase 5
**Plans:** 4/6 plans executed

Plans:
- [x] 06-01-PLAN.md — Wave 0 test stubs (tests/test_phase6_eval.py + tests/test_make_results_v6.py — 12 + 3 stub classes for all P6-* requirements)
- [x] 06-02-PLAN.md — Wave 1 driver scripts/run_phase6_eval.py (sanity-assert + ollama preflight + 6 cell plan + provenance mutation + _summary_v6.json composer; logic only, no cloud calls)
- [ ] 06-03-PLAN.md — Wave 2 [BLOCKING] cloud execution: invoke driver against gpt-oss:{20b,120b}-cloud × {off,fused,def02} = 6 runs, ~78 min total
- [x] 06-04-PLAN.md — Wave 3 make_results.py edits (path resolvers, disclosure header constant, emit_table extension, _v6.csv emissions) + regenerate docs/results/ MDs and CSVs
- [x] 06-05-PLAN.md — Wave 4 make_figures.py — 3 new renderers (5×5 fused heatmap, 5×4 undefended heatmap, arms-race v6 bars) + render 3 v6 PNGs
- [ ] 06-06-PLAN.md — Wave 5 verification: full pytest, originals-untouched audit, manual figure eyeball, write 06-VERIFICATION.md

### Phase 7: Honest FPR Metrics — gpt-oss extension

**Goal:** Extend Phase 5's three honest FPR metrics (M1 per-chunk, M2 answer-preserved, M3 judge-scored) from llama3.2:3b to the two cloud RAG targets (gpt-oss:20b-cloud and gpt-oss:120b-cloud) on the {fused, def02} defense cells produced by Phase 6, so the project's user-visible defense cost is reported across all three RAG targets rather than just the local llama baseline.

**Depends on:** Phase 5 (M1/M2/M3 metric definitions + scripts/run_judge_fpr.py infrastructure); Phase 6 (clean-query v6 logs for the gpt-oss × {fused, def02} cells)

**Requirements:**
- M1 (per-chunk FPR) computed for {gpt-oss:20b-cloud, gpt-oss:120b-cloud} × {fused, def02} = 4 cells from existing Phase 6 v6 clean-query logs (no cloud calls)
- M2 (answer-preserved FPR) computed for the same 4 cells from existing Phase 6 v6 logs (no cloud calls)
- M3 (LLM-as-judge FPR) — pairwise judge run over (defense-on answer, defense-off answer) on clean queries, ~200 cloud-judge calls using gpt-oss:20b-cloud as judge, mirroring Phase 5 setup
- Emit logs/ablation_table_gptoss_v7.json with M1/M2/M3 × 4 cells
- Extend docs/phase5_honest_fpr.md so the M1/M2/M3 table covers 3 RAG targets (llama + gpt-oss:20b + gpt-oss:120b), preserving the original llama row verbatim

**Plans:** 3/6 plans executed

Plans:
- [x] 07-01-PLAN.md — Wave 0 test stubs (tests/test_phase7_judge_fpr.py + tests/test_make_results_v7.py — 24 P7-* IDs) + UTF-8 fix to scripts/run_judge_fpr.py:101
- [x] 07-02-PLAN.md — Wave 1 sibling script scripts/run_judge_fpr_gptoss.py (importlib reuse of Phase 5 helpers, CELL_LOG_MAP, --dry-run M1-only fast path)
- [x] 07-03-PLAN.md — Wave 1 scripts/make_results.py v7 path-resolver branch + emit_honest_fpr_gptoss_v7 (parallel with Plan 02; disjoint files)
- [ ] 07-04-PLAN.md — Wave 2 [BLOCKING] live cloud judge run (~26 min, 200 calls) + emit logs/ablation_table_gptoss_v7.json + logs/judge_fpr_gptoss_v7.json + docs/results/honest_fpr_gptoss_v7.{md,csv} + human-verify checkpoint on M3 numbers
- [ ] 07-05-PLAN.md — Wave 3 docs/phase5_honest_fpr.md addendum (10-row M1/M2/M3 table + 1-2 paragraph cross-LLM analysis + methodology note; in-place append; original prose untouched; docs/phase3_results.md untouched)
- [ ] 07-06-PLAN.md — Wave 4 verification: full pytest, originals-untouched audit, numerical-fidelity audit (30/30 cells); produce 07-VERIFICATION.md

**Notes:**
- M1/M2 are pure log-replay (no cloud calls) — near-instant
- M3 wall-clock: ~26 min cloud (~200 judge calls × ~8 sec/call) + ~5 min downstream regen
- Judge model locked: gpt-oss:20b-cloud (mirrors Phase 5 setup for cross-target comparability)
- "Answer degraded" definition inherited from Phase 5 (do not redefine)
- gemma4:31b-cloud is NOT in scope — Phase 6 only generated {fused, def02} cells for the two gpt-oss models; gemma4's cross-model matrix in Phase 3.3 uses a different schema and is excluded to avoid mixing data sources

---
*Roadmap created: 2026-03-31*
*Restructured: 2026-04-13 — Direction A (arms race) added*
*Audited: 2026-04-21 — Phase 2.2 marked complete; deferred items (ATK-01b, ATK-02, EVAL-V2-01) captured in Phase 3.3; cross-model baseline added to Phase 2.4; DEF-02 ablation added to Phase 3.1; ATK-09 and EVAL-05 (multi-seed) added to Phase 3.2; Phase 3.3 expanded from 3 to 6 criteria; PH3-05 made required in Phase 3.4; novelty positioning vs. PoisonedRAG/BadRAG/AttriBoT literature added throughout*
*Phase 2.3 replanned: 2026-04-21 — full replan from scratch; plan list updated to reflect corpus expansion + harness fixes*
*Phase 2.4 planned: 2026-04-22 — 3 plans in 2 waves; Tier 3 (kimi-k2.5:cloud originally specified) + Tier 4 (3-fragment fragmentation) + cross-model eval (llama + mistral) + EVAL-V2-02 judge pilot*
*Phase 2.4 executed: 2026-04-23 — Rule 3 deviation: Tier 3 attacker LLM substituted kimi-k2.5:cloud → gpt-oss:20b-cloud (kimi requires paid Ollama subscription; research objective preserved). All 3 plans complete, 7/7 must-haves verified.*
*Phase 3.3 updated: 2026-04-23 — added gemma4:31b-cloud as required attack target (Google lineage gap, divergent ASR expected) and minimax-m2.5:cloud as stretch target (hardened model, informative regardless of outcome); both discovered available during Phase 2.4 execution; added late to preserve Phase 2.4 result integrity and because Phase 3.3 is the correct "generalizability" slot*
*Phase 3.1 post-mortem (2026-04-23): plan 03.1-06 ablation revealed 3 gaps requiring a plan 03.1-07 wrap-up: (1) fused_tuned_threshold row was a placeholder, (2) ablation table missing retrieval_rate column (the 88%→50% drop is the utility story for Phase 3.4), (3) DEF-02 increased paired ASR on llama3.2:3b (2%→8% T1, 12%→38% T2) — classified as priming vs. substring-leak vs. behavior-change. BERT classifier scored 100% detection across all tiers → strong anchor-token-memorization signal, which reshapes Phase 3.2 adaptive-attack priority (novel-anchor-token attack now primary).*
*Phase 3.3 descoped (2026-04-23): EVAL-07 (human stealthiness) removed due to 6-day timeline, moved to Future Work. Minimax hard-target (SC-7) demoted from required to Future Work footnote. Gemma4 remains required. Remaining 5 criteria unchanged.*
*Phase 3.4 amended (2026-04-23): added SC-4 utility-security tradeoff subsection requirement (ASR vs retrieval_rate figure + FPR table); expanded SC-5 limitations to require explicit coverage of T3/T4 zero-baseline puzzle and DEF-02 counter-productive finding; added Future Work section for descoped EVAL-07 and minimax test.*
*Phase 3.2 planned: 2026-04-24 — 4 plans in 4 sequential waves; ATK-08/09 adaptive payloads (novel anchor tokens + declarative rewrites), nq_poisoned_v5 collection, DEF-05 LOO causal attribution (run_loo.py), EVAL-05 3-seed aggregation, FPR threshold sweep D-17; all requirements ATK-08/ATK-09/DEF-05/EVAL-05 covered.*
*Course deadlines: Phase 1 Mar 27 (done), Phase 2 Apr 12 (done), Phase 3 Apr 30, Presentation May 5-7*

*Phase 3.3 planned: 2026-04-24 — 7 plans in 2 waves; Wave 1 (6 parallel plans) covers Wave 0 test stubs + ATK-01b + ATK-02 + EVAL-06 + EVAL-V2-02 + EVAL-08; Wave 2 (1 plan) covers EVAL-V2-01 cross-model matrix and depends on Phase 3.2 causal artifacts with DEF-02 fallback per CONTEXT D-12.*
*Phase 7 detail section added: 2026-05-04 — Phase 7 was registered in the checklist but lacked a `### Phase 7:` detail section, blocking gsd-sdk init.phase-op. Detail section drafted from the line-29 description (extends Phase 5 M1/M2/M3 metrics to gpt-oss:20b-cloud and gpt-oss:120b-cloud on the {fused, def02} cells from Phase 6).*
