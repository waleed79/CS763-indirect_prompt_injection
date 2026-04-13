# Indirect Prompt Injection in RAG Systems

## What This Is

A security research project investigating indirect prompt injection attacks on Retrieval-Augmented Generation (RAG) systems. We build a working RAG pipeline, demonstrate that corpus poisoning can hijack LLM outputs, and develop a defense mechanism (context sanitization layer) that reduces attack success rate while maintaining retrieval utility. This is the CS 763 (Computer Security) final project at UW-Madison.

## Core Value

Demonstrate a practical, end-to-end attack + defense pipeline for indirect prompt injection in RAG systems, with measurable attack success rates and defense effectiveness.

## Requirements

### Validated

(None yet — ship to validate)

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

## Context

**Course:** CS 763 Computer Security, Spring 2026, Prof. Somesh Jha
**TA:** Saikumar Yadugiri (saikumar@cs.wisc.edu)
**Team:** Muhammad Musa & Waleed Arshad
**Advisor:** Prof. Karu Sankaralingam (karu@cs.wisc.edu)

**Project pivot:** Originally proposed TVRID competition (cross-modal RGB-Depth person re-identification for ICPR 2026). Pivoted to RAG prompt injection because it is more LLM-relevant, more practical, and offers stronger career signal for LLM security/safety roles. Pre-proposal was submitted for the TVRID project.

**Problem:** RAG is the industry standard for enterprise LLMs, but introduces a new attack surface via the retrieval corpus. An attacker who controls a subset of the retrieval database can inject malicious instructional triggers that override the LLM's system prompts. OWASP lists prompt injection as the #1 LLM vulnerability.

**Approach:**
1. **Attack:** Design optimized trigger phrases that, when retrieved via cosine similarity, force the LLM to execute payloads (e.g., data exfiltration instructions) instead of answering the user's query
2. **Defense:** Develop a context sanitization layer — either a BERT-based classifier detecting imperative commands in retrieved chunks, or attention mask separation forcing the LLM to treat retrieved context as data-only

**Key references:**
- OWASP Top 10 for LLMs (prompt injection as #1 vulnerability)
- Karu's Idea 5.1 project description (detailed methodology)

## Constraints

- **Timeline**: Phase 1 due 2026-03-27, Phase 2 due 2026-04-12, Phase 3 due 2026-04-30, Presentation May 5-7
- **Team size**: 2 people (Musa & Waleed)
- **Deliverables**: GitHub repo with replication instructions, shared Google Doc, final presentation
- **Grade weight**: 40% of course grade (Pre-proposal 10%, Phase 1 20%, Phase 2 20%, Phase 3 20%, Presentation 30%)
- **Compute**: University resources / personal machines (no dedicated GPU cluster assumed)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pivot from TVRID to RAG injection | Better LLM relevance, practical results, career signal | — Pending |
| Full attack + defense scope | Course expects iterative results; both sides make stronger contribution | — Pending |
| Tech stack TBD | Will be decided after research phase | — Pending |

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

---
*Last updated: 2026-03-31 after initialization*
