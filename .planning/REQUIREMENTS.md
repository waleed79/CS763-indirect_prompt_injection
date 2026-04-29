# Requirements: Indirect Prompt Injection in RAG Systems

**Defined:** 2026-03-31
**Core Value:** Demonstrate a practical, end-to-end attack + defense pipeline for indirect prompt injection in RAG systems, with measurable attack success rates and defense effectiveness.

> **Scope note:** This is a ~1 month, 2-person class project (Phase 2 due Apr 12, Phase 3 due Apr 30).
> Requirements marked **[optional]** are stretch goals — include if time permits, skip if not.

## v1 Requirements

### Phase 1 — Problem Statement & Literature Survey (Due: Fri Mar 27)

Per course slides: "A clear problem statement with strong motivation. Literature survey to justify problem's importance / background of problem. Initial results encouraged but not needed."

- [x] **PH1-01**: Clear problem statement defining indirect prompt injection in RAG systems and distinguishing it from direct prompt injection
- [x] **PH1-02**: Motivation section explaining why RAG security matters (OWASP #1 LLM vulnerability, enterprise adoption)
- [x] **PH1-03**: Brief note on project pivot from TVRID with rationale (1 paragraph max)
- [x] **PH1-04**: Literature survey covering key prior work (Greshake et al. 2023, PoisonedRAG, BIPIA, at least 4 papers)
- [x] **PH1-05**: Threat model definition (attacker capabilities, assumptions, goals — what the attacker can and cannot do)
- [x] **PH1-06**: Proposed methodology overview (planned attack + defense approach with justification)
- [x] **PH1-07**: Execution plan mapping remaining work to Phase 2 and Phase 3 deadlines
- [ ] **PH1-08**: **[optional]** Initial results — basic RAG pipeline running on sample corpus with baseline retrieval working

### RAG Pipeline (Foundation — needed for Phase 2)

- [x] **RAG-01**: Custom RAG pipeline with embedding model (all-MiniLM-L6-v2), vector store (ChromaDB), and LLM generation (Ollama) *(completed Phase 2.1)*
- [x] **RAG-02**: Corpus manager to load and index documents (1000-passage MS-MARCO corpus) *(completed Phase 2.1/2.2)*
- [x] **RAG-03**: Retrieval logging capturing which documents are retrieved per query *(completed Phase 2.1)*
- [x] **RAG-04**: Configurable retrieval parameters (top-k, similarity threshold via config.toml) *(completed Phase 2.1)*
- [x] **RAG-05**: Reproducible setup with pinned package versions, random seeds, and config file *(completed Phase 2.1)*

### Attack Module (Phase 2 Core)

- [x] **ATK-01**: At least 2 attack tiers: naive (5-variant Tier-1) + context-blending (instruction-smuggling Tier-2) *(completed Phase 2.2)*
- [x] **ATK-01b**: Full 3-tier taxonomy: naive + context-blending + obfuscated/encoding tier *(completed Phase 3.3-02 — Unicode homoglyph Cyrillic НАСКЕД, 50 passages IDs 20150-20199, T1B_BREACHED ASCII output marker)*
- [x] **ATK-02**: Poisoning ratio sweep (0.5%, 1%, 2%, 5%, 10% of corpus) *(completed Phase 3.3-03 — 5 corpora, ATK02_SWEEP_ID_START=21000-21049 for Tier-1 pool cycling)*
- [x] **ATK-03**: 2 payload types: instruction override (Tier-1) + instruction smuggling/exfiltration (Tier-2) *(completed Phase 2.2)*
- [x] **ATK-04**: Attack corpus generation scripted via generate_poisoned_corpus.py — deterministic output *(completed Phase 2.2)*
- [x] **ATK-05**: Baseline ASR measured: 50% Tier-1, 0% Tier-2 (pre-fix), 50% overall against llama3.2:3b *(completed Phase 2.2)*

### Defense Module (Phase 2–3)

- [x] **DEF-01**: BERT-based context sanitization classifier detecting imperative/instructional commands in retrieved chunks *(completed Phase 3.1-02/04 — DistilBERT fine-tuned, retained as Signal 1 within FusedDefense)*
- [x] **DEF-02**: Prompt-engineering instruction-data separation (system-prompt instructs LLM to treat retrieved context as data-only) — implemented as ablation baseline *(completed Phase 3.1-03 — DEF_02_SYSTEM_PROMPT in generator.py; honest negative finding: counter-productive on llama3.2:3b per Phase 3.1-07 priming analysis)*
- [x] **DEF-03**: Defense integrated into RAG pipeline as a filter between retrieval and generation via `defense_fn` hook *(completed Phase 3.1-02 — Callable[[list[dict]], list[dict]] hook in pipeline.query)*

### Evaluation Harness (Phase 2–3)

- [x] **EVAL-01**: ASR measurement — track how often attacks succeed *(completed Phase 2.3 — run_eval.py emits asr_overall, asr_tier{1,1b,2,3,4,adaptive}, retrieval_rate, conditional_asr_*, paired_asr_*)*
- [ ] **EVAL-02**: **[optional]** Utility preservation metrics — measure answer quality on benign queries with/without defense active
- [x] **EVAL-03**: **[optional]** ASR-utility tradeoff curve as a results graphic — delivered as figures/fig2_utility_security.png (D-04 two-panel) by Phase 03.4-03
- [ ] **EVAL-04**: **[optional]** Held-out attack category evaluation (test defense on attack types not seen during training)
- [x] **EVAL-05**: Results aggregated over 3+ random seeds with standard deviation *(completed Phase 3.2-04 — eval05_aggregation block in logs/ablation_table.json with mean+std for asr_tier{1,2,3,4,adaptive}, fpr, retrieval_rate across seeds 1/2/3)*

### Phase 3 — Final Results & Analysis (Due: Thu Apr 30)

Per course slides: "Final results, evaluations, and findings. Mention any limitations or technical hurdles. Strong analysis matters more than perfect results."

- [ ] **PH3-01**: Complete experiment results for all implemented attacks and at least one defense
- [ ] **PH3-02**: Defense effectiveness analysis with clear before/after ASR comparison
- [ ] **PH3-03**: Limitations section — honest about what didn't work and why (course explicitly asks for this)
- [ ] **PH3-04**: **[optional]** Failure case analysis (when attacks succeed despite defense)
- [ ] **PH3-05**: **[optional]** Comparison table to related work results

### Final Presentation (Due: Tue May 5 & Thu May 7)

Per course slides: "10-12 min presentation per team. If you have a clear write-up, it will be easy. This is for fellow students."

- [ ] **PRES-01**: 10-12 minute presentation covering problem, approach, results, and conclusions
- [ ] **PRES-02**: At least 2 plots/visualizations (e.g., ASR bar chart, architecture diagram)
- [ ] **PRES-03**: **[optional]** Live or recorded demo of the attack pipeline
- [ ] **PRES-04**: Presentation accessible to fellow students (define RAG and prompt injection clearly)

## v2 Requirements — Direction A: Attack-Defense Arms Race

### Advanced Attacks (Phase 2.4)

- [x] **ATK-06**: LLM-generated injection payloads (Tier 3) *(completed Phase 2.4-01/02/03 — gpt-oss:20b-cloud generates 50 semantically-natural payloads with t3.evilcorp.io anchor; kimi-k2.5:cloud Rule-3 substitution per Phase 2.4-01 STATE entry)*
- [x] **ATK-07**: Cross-chunk payload fragmentation (Tier 4) *(completed Phase 2.4-02 — declarative editorial-note fragments A/B/C; Tier 4 ASR=0% across all 45 EVAL-V2-01 cells confirms co-retrieval limit per Phase 2.4-03)*
- [x] **ATK-08**: Adaptive attacks against multi-signal defense *(completed Phase 3.2-02 — NOVEL_ANCHOR_TOKENS = [BREACHED, PWNED, OVERRIDDEN, JAILBROKEN, EXFILTRATED]; ATK-08 ASR=7% vs fused on llama)*
- [x] **ATK-09**: Non-imperative declarative-only adaptive attack *(completed Phase 3.2-02 — ATK09_DECLARATIVE_TEMPLATE; ATK-09 vs imperative-only signal = 6% ASR vs 1% baseline; novel: not found in published adaptive attack literature)*

### Multi-Signal Defense (Phase 3.1 — replaces simple BERT classifier)

- [x] **DEF-04**: Multi-signal defense fusion — combine 4 independent detection signals via a meta-classifier *(completed Phase 3.1-02/04/05/06 — FusedDefense class in rag/defense.py; LR meta-classifier in models/lr_meta_classifier.json; achieves 0% ASR on T1/T2/T3 for llama3.2:3b at FPR=76%; tuned threshold=0.10 reduces retrieval_rate 50%→34%)*
  - Signal 1: BERT/DistilBERT classifier (P(injection) score) — `models/bert_classifier/`
  - Signal 2: Perplexity anomaly (max windowed NLL via GPT-2)
  - Signal 3: Imperative sentence ratio (regex-based mood detection)
  - Signal 4: Retrieval score fingerprint anomaly (z-score vs `models/signal4_baseline.json` mu/std)
- [x] **DEF-05**: Causal influence attribution — leave-one-out analysis measuring per-chunk influence/relevance ratio *(implementation completed Phase 3.2-03; SC reclassified per 03.2-VERIFICATION.md framing B, 2026-04-28: AUC=0.372 llama / 0.410 mistral both below random ⇒ DEF-05 is a **failed defense hypothesis with a citable mechanistic explanation** (injected chunks are redundant — removing one does not restore clean behavior). The implementation requirement is met; the empirical SC ("metric distinguishes injected from clean") is NOT satisfied. The negative result is the contribution. Goes into Phase 3.4 limitations as one of the three required bullets.)*
- [x] **DEF-01**: BERT-based context sanitization classifier detecting imperative/instructional commands in retrieved chunks *(retained as Signal 1 within DEF-04 — see above)*
- [x] **DEF-03**: Defense integrated into RAG pipeline as a filter between retrieval and generation *(see above — defense_fn hook in pipeline.query)*

### Quick Evaluation Additions (Phase 3.3)

- [x] **EVAL-06**: Retriever transferability — ASR across 3 embedding models *(completed Phase 3.3-04 — `nomic-embed-text-v1.5`, `mxbai-embed-large-v1`, `all-MiniLM-L6-v2`; per-model collections + scripts/run_transferability_eval.py with --embedding-model flag)*
- [ ] **EVAL-07**: Human stealthiness evaluation — blind passage classification by 3+ humans vs. automated defense *(deferred to Future Work per Phase 3.3 CONTEXT D-19; 6-day timeline + IRB-style 3-evaluator study not feasible)*
- [x] **EVAL-08**: XSS/SSRF taxonomy mapping — formal table connecting IPI attack classes to web security vulnerabilities with specific examples *(completed Phase 3.3-06 — docs/xss_ssrf_taxonomy.md)*
- [x] **ATK-02**: Poisoning ratio sweep at 5 ratios (0.5%, 1%, 2%, 5%, 10%) *(completed Phase 3.3-03 — see ATK-02 above in v1)*
- [x] **ATK-01b**: Obfuscated/encoding attack tier (Unicode homoglyphs) *(completed Phase 3.3-02 — see ATK-01b above in v1)*
- [x] **EVAL-V2-01**: Cross-model full attack/defense matrix — 3 LLMs (llama3.2:3b, mistral:7b, gemma4:31b-cloud) × 3 defenses (no_defense, fused, def02 fallback) × 5 tiers = 45 cells in `logs/eval_matrix/` *(Phase 3.3 Plan 07 — completed 2026-04-27; Phase 3.2 causal artifacts not yet present so def02 substituted per CONTEXT D-12)*

### Extended Evaluation (deferred/optional)

- **EVAL-V2-02**: LLM-as-judge for semantic ASR scoring — piloted in Phase 2.4 on Tier 3 payloads; full implementation if time permits in Phase 3.4

## Out of Scope

| Feature | Reason |
|---------|--------|
| Direct prompt injection (user-side) | Focus is on indirect/corpus-based attacks |
| Real-world corpus poisoning (Wikipedia edits) | Ethical/legal concerns; simulated poisoning only |
| Multi-modal attacks (images in docs) | Text-only scope for 2-person team in 1 month |
| Production UI/dashboard | Research prototype, not production system |
| LangChain/LlamaIndex frameworks | Abstract away the attack surface being studied |
| Custom embedding model training | Use existing models; training is out of scope |
| Cloud deployment | Local-first stack for cost and reproducibility |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PH1-01 | Phase 1.1 | **Complete** |
| PH1-02 | Phase 1.1 | **Complete** |
| PH1-03 | Phase 1.1 | **Complete** |
| PH1-04 | Phase 1.1 | **Complete** |
| PH1-05 | Phase 1.1 | **Complete** |
| PH1-06 | Phase 1.1 | **Complete** |
| PH1-07 | Phase 1.1 | **Complete** |
| PH1-08 [optional] | Phase 1.2 | Skipped |
| RAG-01 | Phase 2.1 | **Complete** |
| RAG-02 | Phase 2.1 | **Complete** |
| RAG-03 | Phase 2.1 | **Complete** |
| RAG-04 | Phase 2.1 | **Complete** |
| RAG-05 | Phase 2.1 | **Complete** |
| ATK-01 | Phase 2.2 | **Complete** |
| ATK-01b | Phase 3.3 Plan 02 | **Complete** |
| ATK-02 | Phase 3.3 Plan 03 | **Complete** |
| ATK-03 | Phase 2.2 | **Complete** |
| ATK-04 | Phase 2.2 | **Complete** |
| ATK-05 | Phase 2.2 | **Complete** |
| EVAL-01 | Phase 2.3 | **Complete** |
| DEF-01 | Phase 3.1 Plan 02/04 | **Complete** (Signal 1 of DEF-04) |
| DEF-02 | Phase 3.1 Plan 03 | **Complete** (counter-productive on llama — Phase 3.1-07) |
| DEF-03 | Phase 3.1 Plan 02 | **Complete** (defense_fn hook in pipeline.query) |
| DEF-04 | Phase 3.1 Plans 02/04/05/06 | **Complete** (FusedDefense; 0% ASR on T1/T2/T3 at FPR=76%) |
| DEF-05 | Phase 3.2 Plan 03 | **Implementation complete; SC re-classified as negative result** (LOO AUC=0.372 llama / 0.410 mistral, both below random — feeds Phase 3.4 limitations) |
| ATK-06 | Phase 2.4 Plan 01 | **Complete** (gpt-oss:20b-cloud Rule-3 substitution for kimi) |
| ATK-07 | Phase 2.4 Plan 02 | **Complete** (Tier 4 fragments A/B/C; co-retrieval limited per design) |
| ATK-08 | Phase 3.2 Plan 02 | **Complete** (novel-anchor-token adaptive) |
| ATK-09 | Phase 3.2 Plan 02 | **Complete** (declarative-only adaptive; novel) |
| EVAL-05 | Phase 3.2 Plan 04 | **Complete** (3-seed mean+std in ablation_table) |
| EVAL-06 | Phase 3.3 Plan 04 | **Complete** (3-embedding-model transferability) |
| EVAL-07 | Phase 3.3 | **Deferred to Future Work** (6-day window insufficient for IRB human study) |
| EVAL-08 | Phase 3.3 Plan 06 | **Complete** |
| EVAL-V2-01 | Phase 3.3 Plan 07 | **Complete** (3 LLMs × 3 defenses × 5 tiers = 45 cells) |
| EVAL-V2-02 | Phase 3.3 Plan 05 | **Complete** |
| EVAL-02 [optional] | Phase 3.4 | Pending |
| EVAL-03 [optional] | Phase 3.4 Plan 03 | **Complete** (D-04 two-panel figure rendered to figures/fig2_utility_security.png) |
| EVAL-04 [optional] | Phase 3.4 | Pending |
| PH3-01 | Phase 3.4 | Pending |
| PH3-02 | Phase 3.4 | Pending |
| PH3-03 | Phase 3.4 | Pending |
| PH3-04 [optional] | Phase 3.4 | Pending |
| PH3-05 | Phase 3.4 | Pending (required, not optional) |
| PRES-01 | Phase 4 | Pending |
| PRES-02 | Phase 4 | Pending |
| PRES-03 [optional] | Phase 4 | Pending |
| PRES-04 | Phase 4 | Pending |

**Coverage** (as of Phase 3.3 close, 2026-04-27):
- v1 required requirements (22): **20 complete** (PH1-01..07, RAG-01..05, ATK-01..05, EVAL-01, DEF-01..03), 2 remain in Phase 3.4 (PH3-01, PH3-02, PH3-03, PH3-05 — writeup deliverables)
- v1 optional requirements (5): 1 complete (EVAL-05 was upgraded to required by Phase 3.2 scope), 4 still optional (PH3-04, EVAL-02, EVAL-03, EVAL-04, PRES-03)
- v2 Direction-A requirements (13): **11 complete** (ATK-06..09, DEF-04, DEF-05, EVAL-05, EVAL-06, EVAL-08, EVAL-V2-01, EVAL-V2-02); 1 deferred to Future Work (EVAL-07 human stealthiness); ATK-01b and ATK-02 already complete in v1 row above
- Mapped to phases: 47/47
- Unmapped: 0 ✓

**Remaining (all Phase 3.4 / Phase 4 deliverables):** PH3-01, PH3-02, PH3-03, PH3-04, PH3-05, EVAL-02, EVAL-03, EVAL-04, PRES-01..04.

---
*Requirements defined: 2026-03-31*
*Last updated: 2026-04-28 — v4 audit (post-Phase 3.3): all v1 implementation requirements complete (DEF-01..03, EVAL-01); all Phase 2.4 + 3.1 + 3.2 + 3.3 attack/defense/eval requirements complete (ATK-01b, ATK-02, ATK-06..09, DEF-04, DEF-05, EVAL-05, EVAL-06, EVAL-08, EVAL-V2-01, EVAL-V2-02); EVAL-07 explicitly deferred to Future Work; all checkbox states reflect actual implementation state; traceability table fully updated.*
*Last updated: 2026-04-21 — v3 audit: Phase 2.1/2.2 marked complete; deferred items (ATK-01b, ATK-02, EVAL-V2-01) moved to Phase 3.3; ATK-09 (non-imperative adaptive attack) and EVAL-05 (multi-seed) added to Phase 3.2; DEF-02 made required ablation in Phase 3.1; PH3-05 made required in Phase 3.4; traceability fully updated*
