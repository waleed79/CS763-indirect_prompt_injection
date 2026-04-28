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
- [ ] **ATK-01b**: Full 3-tier taxonomy: naive + context-blending + obfuscated/encoding tier *(encoding tier deferred to Phase 3.3)*
- [ ] **ATK-02**: Poisoning ratio sweep (0.5%, 1%, 2%, 5%, 10% of corpus) — **moved to Phase 3.3** (deferred from Phase 2.2)
- [x] **ATK-03**: 2 payload types: instruction override (Tier-1) + instruction smuggling/exfiltration (Tier-2) *(completed Phase 2.2)*
- [x] **ATK-04**: Attack corpus generation scripted via generate_poisoned_corpus.py — deterministic output *(completed Phase 2.2)*
- [x] **ATK-05**: Baseline ASR measured: 50% Tier-1, 0% Tier-2 (pre-fix), 50% overall against llama3.2:3b *(completed Phase 2.2)*

### Defense Module (Phase 2–3)

- [ ] **DEF-01**: BERT-based context sanitization classifier detecting imperative/instructional commands in retrieved chunks *(Signal 1 of the ensemble — Phase 3.1)*
- [ ] **DEF-02**: Prompt-engineering instruction-data separation (system-prompt instructs LLM to treat retrieved context as data-only) — implemented as ablation baseline in Phase 3.1 to show rule-based separation alone is insufficient
- [ ] **DEF-03**: Defense integrated into RAG pipeline as a filter between retrieval and generation via `defense_fn` hook *(Phase 3.1)*

### Evaluation Harness (Phase 2–3)

- [ ] **EVAL-01**: ASR measurement — track how often attacks succeed (retrieval rate × conditional ASR breakdown is **[optional]** if time is tight)
- [ ] **EVAL-02**: **[optional]** Utility preservation metrics — measure answer quality on benign queries with/without defense active
- [ ] **EVAL-03**: **[optional]** ASR-utility tradeoff curve as a results graphic
- [ ] **EVAL-04**: **[optional]** Held-out attack category evaluation (test defense on attack types not seen during training)
- [ ] **EVAL-05**: **[optional]** Results aggregated over 3+ random seeds with standard deviation

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

- [ ] **ATK-06**: LLM-generated injection payloads (Tier 3) — use an attacker LLM to automatically craft injection payloads that evade simple pattern matching *(Phase 2.4)*
- [ ] **ATK-07**: Cross-chunk payload fragmentation (Tier 4) — split injection payloads across 2-3 chunks that individually appear benign but reassemble in the LLM context window *(Phase 2.4 — novel: no published work on this attack vector)*
- [ ] **ATK-08**: Adaptive attacks against multi-signal defense — craft payloads specifically designed to evade the multi-signal fusion defense *(Phase 3.2)*
- [ ] **ATK-09**: Non-imperative declarative-only adaptive attack — payload written entirely in declarative/factual language with no command syntax, specifically targeting the imperative-ratio signal *(Phase 3.2 — novel: not found in published adaptive attack literature)*

### Multi-Signal Defense (Phase 3.1 — replaces simple BERT classifier)

- [ ] **DEF-04**: Multi-signal defense fusion — combine 3+ independent detection signals via a meta-classifier:
  - Signal 1: BERT/DistilBERT classifier (P(injection) score)
  - Signal 2: Perplexity anomaly (windowed perplexity spike detection)
  - Signal 3: Imperative sentence ratio (fraction of imperative-mood sentences)
  - Signal 4: Retrieval score fingerprint anomaly (chunk score vs. canary query baseline)
- [x] **DEF-05**: Causal influence attribution — leave-one-out analysis measuring per-chunk influence/relevance ratio to detect chunks that disproportionately change LLM output *(completed Phase 3.2-03; llama AUC=0.372, mistral AUC=0.410 — honest negative result documented)*
- [ ] **DEF-01**: BERT-based context sanitization classifier detecting imperative/instructional commands in retrieved chunks *(retained as Signal 1 within DEF-04)*
- [ ] **DEF-03**: Defense integrated into RAG pipeline as a filter between retrieval and generation *(retained — applies to the fused defense)*

### Quick Evaluation Additions (Phase 3.3)

- [ ] **EVAL-06**: Retriever transferability — ASR across 3+ embedding models (`nomic-embed-text` primary MTEB 62.4, `mxbai-embed-large` MTEB 64.7, `all-MiniLM-L6-v2` legacy baseline MTEB 56.3) *(Phase 3.3 — novel: embedding-specific poison transfer not studied in published RAG security papers)*
- [ ] **EVAL-07**: Human stealthiness evaluation — blind passage classification by 3+ humans vs. automated defense *(Phase 3.3)*
- [x] **EVAL-08**: XSS/SSRF taxonomy mapping — formal table connecting IPI attack classes to web security vulnerabilities with specific examples *(Phase 3.3 — completed 2026-04-25, docs/xss_ssrf_taxonomy.md)*
- [ ] **ATK-02**: Poisoning ratio sweep at 5 ratios (0.5%, 1%, 2%, 5%, 10%) *(Phase 3.3 — deferred from Phase 2.2)*
- [ ] **ATK-01b**: Obfuscated/encoding attack tier (Base64, Unicode homoglyphs, or whitespace padding) *(Phase 3.3 — deferred from Phase 2.2)*
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
| ATK-01b | Phase 3.3 | Pending (deferred from 2.2) |
| ATK-02 | Phase 3.3 | Pending (deferred from 2.2) |
| ATK-03 | Phase 2.2 | **Complete** |
| ATK-04 | Phase 2.2 | **Complete** |
| ATK-05 | Phase 2.2 | **Complete** |
| EVAL-01 | Phase 2.3 | Pending |
| DEF-01 | Phase 3.1 | Pending |
| DEF-02 | Phase 3.1 | Pending |
| DEF-03 | Phase 3.1 | Pending |
| DEF-04 | Phase 3.1 | Pending |
| DEF-05 | Phase 3.2 | **Complete** |
| ATK-06 | Phase 2.4 | Pending |
| ATK-07 | Phase 2.4 | Pending |
| ATK-08 | Phase 3.2 | Pending |
| ATK-09 | Phase 3.2 | Pending (new — declarative adaptive attack) |
| EVAL-05 | Phase 3.2 | Pending |
| EVAL-06 | Phase 3.3 | Pending |
| EVAL-07 | Phase 3.3 | Pending |
| EVAL-08 | Phase 3.3 Plan 06 | Complete |
| EVAL-V2-01 | Phase 3.3 Plan 07 | Complete |
| EVAL-V2-02 | Phase 3.3 Plan 05 | Complete |
| EVAL-02 [optional] | Phase 3.4 | Pending |
| EVAL-03 [optional] | Phase 3.4 | Pending |
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

**Coverage:**
- v1 required requirements: 22 total — 12 complete, 10 pending
- v1 optional requirements: 5 pending (PH3-04, EVAL-02, EVAL-03, EVAL-04, PRES-03)
- v2 requirements (Direction A): 13 total — 0 complete, 13 pending
- Mapped to phases: 47/47
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-31*
*Last updated: 2026-04-21 — v3 audit: Phase 2.1/2.2 marked complete; deferred items (ATK-01b, ATK-02, EVAL-V2-01) moved to Phase 3.3; ATK-09 (non-imperative adaptive attack) and EVAL-05 (multi-seed) added to Phase 3.2; DEF-02 made required ablation in Phase 3.1; PH3-05 made required in Phase 3.4; traceability fully updated*
