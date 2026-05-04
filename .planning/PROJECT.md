# Indirect Prompt Injection in RAG Systems

## What This Is

A security research project investigating indirect prompt injection attacks on Retrieval-Augmented Generation (RAG) systems. We build a working RAG pipeline, demonstrate that corpus poisoning can hijack LLM outputs, and develop a defense mechanism (context sanitization layer) that reduces attack success rate while maintaining retrieval utility. This is the CS 763 (Computer Security) final project at UW-Madison.

## Core Value

Demonstrate an **attack-defense arms race** for indirect prompt injection in RAG systems — escalating through 5 attack tiers (T1 naive, T1b Unicode-homoglyph obfuscation, T2 context-blending, T3 LLM-generated semantic, T4 cross-chunk fragmentation) plus an adaptive tier (ATK-08/09), and 2 defense generations (multi-signal fusion, causal attribution), showing that per-chunk defenses are fundamentally insufficient and multi-signal defense-in-depth is required.

## Requirements

### Validated

- [x] Build a functional RAG pipeline with retrieval corpus, embedding model, vector store, and LLM — *Validated in Phase 2.1*
- [x] Design and implement indirect prompt injection attacks via corpus poisoning (5 tiers: T1 naive, T1b Unicode-homoglyph, T2 context-blend, T3 LLM-generated, T4 cross-chunk fragmentation) — *Validated in Phases 2.2, 2.4, 3.3*
- [x] Measure ASR across multiple attack strategies with retrieval rate decomposition — *Validated in Phase 2.3*
- [x] Develop multi-signal defense fusion (BERT + perplexity + imperative ratio + retrieval fingerprint) — *Validated in Phase 3.1*
- [x] Implement adaptive attacks (ATK-08 novel anchors, ATK-09 declarative) stress-testing the fused defense — *Validated in Phase 3.2* — ATK-08 mean ASR=4.7% vs fused (BERT generalization gap confirmed)
- [x] Leave-one-out causal influence attribution (DEF-05) with honest negative result — *Validated in Phase 3.2* — LOC AUC=0.372/0.410 (below chance); mechanistically explained as redundant-payload attribution failure
- [x] Multi-seed evaluation (EVAL-05) with mean±std reporting — *Validated in Phase 3.2* — asr_adaptive std=3.3%, fpr std=15.1%

### Active

- [ ] Build a functional RAG pipeline with retrieval corpus, embedding model, vector store, and LLM
- [ ] Design and implement indirect prompt injection attacks via corpus poisoning
- [ ] Measure attack success rate (ASR) across multiple attack strategies
- [ ] Develop a defense mechanism (context sanitization layer) to filter malicious retrieved content
- [ ] Evaluate defense effectiveness: reduction in ASR while maintaining retrieval utility
- [ ] Provide clear literature survey and motivation for the problem
- [ ] Produce reproducible results with documented methodology
- [ ] Deliver final presentation (10-12 min) with plots and analysis

### Out of Scope

- Direct prompt injection (user-side attacks) — focus is on indirect/corpus-based attacks
- Production-grade deployment — this is a research prototype
- Multi-modal attacks (images in retrieved docs) — text-only scope for feasibility
- Real-world corpus poisoning (Wikipedia edits, etc.) — simulated poisoning only
- Gradient-based adversarial passage generation (HotFlip/AGGD) — requires white-box retriever access and significant compute
- Supply chain attacks on embedding models — backdooring retrievers is out of scope for timeline

## Context

**Course:** CS 763 Computer Security, Spring 2026, Prof. Somesh Jha
**TA:** Saikumar Yadugiri (saikumar@cs.wisc.edu)
**Team:** Muhammad Musa & Waleed Arshad
**Advisor:** Prof. Karu Sankaralingam (karu@cs.wisc.edu)

**Project pivot:** Originally proposed TVRID competition (cross-modal RGB-Depth person re-identification for ICPR 2026). Pivoted to RAG prompt injection because it is more LLM-relevant, more practical, and offers stronger career signal for LLM security/safety roles. Pre-proposal was submitted for the TVRID project.

**Problem:** RAG is the industry standard for enterprise LLMs, but introduces a new attack surface via the retrieval corpus. An attacker who controls a subset of the retrieval database can inject malicious instructional triggers that override the LLM's system prompts. OWASP lists prompt injection as the #1 LLM vulnerability.

**Approach:**
1. **Attack escalation:** Four tiers of increasingly sophisticated corpus poisoning — (1) naive instruction override, (2) context-blending, (3) LLM-generated payloads via automated red-teaming, (4) cross-chunk fragmentation where payloads split across chunks reassemble in the context window
2. **Defense-in-depth:** Multi-signal fusion combining BERT classifier, perplexity anomaly detection, imperative sentence ratio, and retrieval score fingerprinting via a meta-classifier; plus causal influence attribution via leave-one-out analysis
3. **Arms race analysis:** Adaptive attacks against the defense, demonstrating the fundamental limits of per-chunk detection and the need for chunk-interaction-aware defenses
4. **Generalizability:** Retriever transferability across embedding models, human stealthiness evaluation, and formal XSS/SSRF parallel taxonomy

**Key references:**
- OWASP Top 10 for LLMs (prompt injection as #1 vulnerability)
- Karu's Idea 5.1 project description (detailed methodology)

## Constraints

- **Timeline**: Phase 1 due 2026-03-27, Phase 2 due 2026-04-12, Phase 3 due 2026-04-30, Presentation May 5-7
- **Team size**: 2 people (Musa & Waleed)
- **Deliverables**: GitHub repo with replication instructions, shared Google Doc, final presentation
- **Grade weight**: 40% of course grade (Pre-proposal 10%, Phase 1 20%, Phase 2 20%, Phase 3 20%, Presentation 30%)
- **Compute**: University resources / personal machines (no dedicated GPU cluster assumed)

## Development Environment

**Python environment**: All scripts must be run inside the `rag-security` conda environment. Never use bare `python` — always prefix with `conda run -n rag-security python` or activate the env first (`conda activate rag-security`).

```bash
# Correct — always use this form for all phases
conda run -n rag-security python scripts/run_eval.py ...
conda run -n rag-security python scripts/generate_poisoned_corpus.py

# Wrong — system Python is 3.13.5 and has none of the project packages
python scripts/run_eval.py ...
```

**Ollama**: LLM inference runs via the Ollama server at `http://localhost:11434`. Start with `ollama serve` if not running. Cloud models (`gpt-oss:20b-cloud`, `gpt-oss:120b-cloud`, `kimi-k2.5:cloud`) require `ollama login` (free account) and use `--delay 3` to avoid hourly rate limits.

**Embedding model**: `nomic-ai/nomic-embed-text-v1.5` loaded via `sentence-transformers` with `trust_remote_code=True` (already wired in `rag/retriever.py`). Requires `einops` package (already in `requirements.txt` and installed in `rag-security` env).

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pivot from TVRID to RAG injection | Better LLM relevance, practical results, career signal | — Pending |
| Full attack + defense scope | Course expects iterative results; both sides make stronger contribution | — Pending |
| Tech stack TBD | Will be decided after research phase | — Pending |
| Phase 3.1 DEF-02 counter-productive finding (2026-04-23) | System-prompt hardening *increased* paired ASR on llama3.2:3b (T1 2%→8%, T2 12%→38%) — unexpected result flagged as priming vs. substring-leak vs. behavior-change; plan 03.1-07 resolves the mechanism classification | Keep as honest negative finding in Phase 3.4 limitations; informs Phase 3.2 by motivating the novel-anchor-token adaptive attack as primary strategy |
| BERT signal anchor-token memorization (2026-04-23) | BERT classifier scored 100% detection on all tiers — strongly suggesting memorization of the 5 trained anchor tokens (HACKED, COMPROMISED, INFILTRATED, SYSTEM_OVERRIDE, PAYLOAD_DELIVERED) rather than generalized injection detection | Reorder Phase 3.2 adaptive attacks: novel-anchor-token attack (synonyms like BREACHED, PWNED) now primary; imperative-free declarative attack remains secondary |
| Phase 3.3 descope (2026-04-23) | 6-day runway to Apr 30 deadline cannot accommodate IRB-style human evaluator recruitment; minimax hard-target is a single-run nice-to-have vs. tightening the core arms race story | EVAL-07 human stealthiness removed; minimax demoted to Future Work footnote; gemma4 kept required to preserve cross-lineage generalizability claim |
| Phase 3.4 utility-security honesty (2026-04-23) | Fused defense has a 76% FPR on clean queries and drops poisoned retrieval 88%→50% — must not bury the utility cost under ASR-only numbers | Added explicit utility-security tradeoff subsection to Phase 3.4; added T3/T4 baseline-already-zero caveat to limitations so defense reductions are framed honestly |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

## Current Status (2026-04-24)

- **Phase 3.1**: ✅ COMPLETE — verified 2026-04-24, 12/12 must-haves passed, 115 tests green. Fused defense achieves 0% ASR across all 4 tiers. Ablation table complete with retrieval_rate column. DEF-02 priming classified. Code review open: CR-01 (run_eval.py KeyError on missing passage_id metadata) and CR-02 (Signal 4 constant overwrite in LR training — fused classifier is effectively 3-signal). Run `/gsd-code-review-fix 3.1` before Phase 3.4 analysis.
- **Next**: Phase 3.2 (adaptive attacks + causal attribution — novel-anchor-token attack primary) and Phase 3.3 (retriever transfer, XSS/SSRF taxonomy, gemma4) can now proceed.
- **Phase 3.4 writeup**: ~60% of tables and limitations content already populated by Phase 3.1 results. Skeleton can start in parallel.
- **Deadline**: Phase 3 Google Doc due 2026-04-30 (6 calendar days remaining).

### Validated Requirements (Phase 3.1)
- ✅ Defense mechanism implemented: 4-signal FusedDefense (BERT + perplexity + imperative ratio + retrieval z-score) with LR meta-classifier
- ✅ ASR reduction demonstrated: fused achieves 0% ASR on T1/T2/T3/T4 (vs 2–88% no-defense baseline)
- ✅ Utility cost quantified: FPR=76%, retrieval_rate drops 88%→50% (fixed) / 34% (tuned threshold=0.10)
- ✅ Cross-model generalizability: mistral:7b fused drops T2 28%→0%, T3 12%→0%

---
*Last updated: 2026-04-24 — Phase 3.1 verified complete*
