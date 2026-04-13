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

- [ ] **RAG-01**: Custom RAG pipeline with embedding model (all-MiniLM-L6-v2), vector store (ChromaDB), and LLM generation (Ollama)
- [ ] **RAG-02**: Corpus manager to load and index documents (start with 100-500 docs; scale to 1000+ is **[optional]**)
- [ ] **RAG-03**: Retrieval logging capturing which documents are retrieved per query
- [ ] **RAG-04**: **[optional]** Configurable retrieval parameters (top-k, similarity threshold)
- [ ] **RAG-05**: Reproducible setup with pinned package versions, random seeds, and config file

### Attack Module (Phase 2 Core)

- [ ] **ATK-01**: At least 2 attack tiers: naive (literal instruction override) + one more sophisticated tier (obfuscated or context-blending)
- [ ] **ATK-01b**: **[optional]** Full 3-tier taxonomy: naive + obfuscated + context-blending
- [ ] **ATK-02**: **[optional]** Configurable poisoning ratio sweep (0.1% to 10% of corpus) — include if time permits after basic attacks work
- [ ] **ATK-03**: At least 2 payload types: instruction override + one of (misinformation injection, data exfiltration prompt)
- [ ] **ATK-04**: Attack corpus generation scripts that inject poisoned documents into a clean corpus
- [ ] **ATK-05**: Baseline ASR measurement on undefended RAG pipeline

### Defense Module (Phase 2–3)

- [ ] **DEF-01**: BERT-based context sanitization classifier detecting imperative/instructional commands in retrieved chunks
- [ ] **DEF-02**: **[optional]** Attention mask separation via prompt engineering (instruct LLM to treat retrieved context as data-only) — simpler alternative or complement to DEF-01
- [ ] **DEF-03**: Defense integrated into RAG pipeline as a filter between retrieval and generation

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

## v2 Requirements

### Advanced Attacks

- **ATK-V2-01**: Retrieval-aware attack crafting (co-optimize for retrieval relevance and attack success)
- **ATK-V2-02**: Gradient-based trigger optimization for maximum retrieval probability

### Advanced Defense

- **DEF-V2-01**: Perplexity-based filtering for anomalous retrieved chunks
- **DEF-V2-02**: Ensemble defense combining multiple strategies

### Extended Evaluation

- **EVAL-V2-01**: Cross-model validation with 2+ LLMs (Llama + Mistral)
- **EVAL-V2-02**: LLM-as-judge for semantic ASR scoring instead of substring matching

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
| PH1-01 | Phase 1.1 | Complete |
| PH1-02 | Phase 1.1 | Complete |
| PH1-03 | Phase 1.1 | Complete |
| PH1-04 | Phase 1.1 | Complete |
| PH1-05 | Phase 1.1 | Complete |
| PH1-06 | Phase 1.1 | Complete |
| PH1-07 | Phase 1.1 | Complete |
| PH1-08 [optional] | Phase 1.2 | Pending |
| RAG-01 | Phase 2.1 | Pending |
| RAG-02 | Phase 2.1 | Pending |
| RAG-03 | Phase 2.1 | Pending |
| RAG-04 [optional] | Phase 2.1 | Pending |
| RAG-05 | Phase 2.1 | Pending |
| ATK-01 | Phase 2.2 | Pending |
| ATK-01b [optional] | Phase 2.2 | Pending |
| ATK-02 [optional] | Phase 2.2 | Pending |
| ATK-03 | Phase 2.2 | Pending |
| ATK-04 | Phase 2.2 | Pending |
| ATK-05 | Phase 2.2 | Pending |
| EVAL-01 | Phase 2.3 | Pending |
| DEF-01 | Phase 3.1 | Pending |
| DEF-02 [optional] | Phase 3.1 | Pending |
| DEF-03 | Phase 3.1 | Pending |
| EVAL-02 [optional] | Phase 3.2 | Pending |
| EVAL-03 [optional] | Phase 3.2 | Pending |
| EVAL-04 [optional] | Phase 3.2 | Pending |
| EVAL-05 [optional] | Phase 3.2 | Pending |
| PH3-01 | Phase 3.2 | Pending |
| PH3-02 | Phase 3.2 | Pending |
| PH3-03 | Phase 3.2 | Pending |
| PH3-04 [optional] | Phase 3.2 | Pending |
| PH3-05 [optional] | Phase 3.2 | Pending |
| PRES-01 | Phase 4 | Pending |
| PRES-02 | Phase 4 | Pending |
| PRES-03 [optional] | Phase 4 | Pending |
| PRES-04 | Phase 4 | Pending |

**Coverage:**
- v1 required requirements: 22 total
- v1 optional requirements: 13 total
- Mapped to phases: 35/35
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-31*
*Last updated: 2026-03-31 — traceability updated to reflect ROADMAP.md sub-phase structure (1.1, 1.2, 2.1, 2.2, 2.3, 3.1, 3.2, 4)*
