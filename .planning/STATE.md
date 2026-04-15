---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: milestone
status: Ready to execute
stopped_at: "Completed 02.2-01-PLAN.md — MS-MARCO corpus, upgraded attacks, mistral:7b config"
last_updated: "2026-04-15T16:50:43.117Z"
last_activity: 2026-04-15
progress:
  total_phases: 11
  completed_phases: 3
  total_plans: 10
  completed_plans: 8
  percent: 60
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-31)

**Core value:** Demonstrate an attack-defense arms race for indirect prompt injection in RAG systems — 4 attack tiers, 2 defense generations, showing per-chunk defenses are fundamentally insufficient.
**Current focus:** Phase 02.2 — attack-module

## Current Position

Phase: 02.2 (attack-module) — EXECUTING
Plan: 2 of 2
Next phase: 02.2 — corpus poisoning attack
Last activity: 2026-04-15

Progress: [██████░░░░] 60%

## Performance Metrics

**Velocity:**

- Total plans completed: 6
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 01.1 | 2 | Complete |
| 02.1 | 4 | Complete (verified) |

**Recent Trend:**

- Last 5 plans: 02.1-01, 02.1-02, 02.1-03, 02.1-04
- Trend: On track

*Updated after each plan completion*
| Phase 01.1 P02 | 115 | 3 tasks | 1 files |
| Phase 02.1 P01 | env + scaffolding | complete |
| Phase 02.1 P02 | config + corpus | complete |
| Phase 02.1 P03 | retriever + generator + logger + pipeline | complete |
| Phase 02.1 P04 | demo.ipynb | complete (checkpoint pending) |
| Phase 02.2 P01 | 25 | 6 tasks | 6 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Pivoted from TVRID to RAG prompt injection — better LLM relevance and career signal
- [Init]: Custom RAG stack (sentence-transformers + ChromaDB + Ollama), no LangChain/LlamaIndex
- [Init]: Full attack + defense scope — both sides required for credible course contribution
- [Phase 01.1]: Threat model uses structured bullet format (D-01): scenario intro + capabilities + goals + explicit cannot-control list — no mathematical formalism
- [Phase 01.1]: Methodology preview uses high-level narrative with no library names (D-07): 'a BERT-based classifier', 'a vector store', 'a local language model'
- [Phase 01.1]: ASR defined verbatim per D-08 in Section 7: 'Attack Success Rate (ASR): the fraction of test queries for which the attack successfully hijacks the LLM response'
- [Phase 02.2]: dataclasses.replace used to override frozen Config collection field for poisoned pipeline — pattern established for all future collection overrides
- [Phase 02.2]: Tier-2 instruction smuggling replaces broken HTTP exfiltration — local Ollama cannot make HTTP requests so URL-based exfil produces 0% ASR
- [Phase 02.2]: 5 Tier-1 injection variants with distinct keywords (HACKED/COMPROMISED/INFILTRATED/SYSTEM_OVERRIDE/PAYLOAD_DELIVERED) enable per-style ASR measurement
- [Phase 02.2]: mistral:7b chosen over llama3.2:3b as primary LLM target for stronger instruction-following and more meaningful ASR numbers
- [Phase 02.2]: MS-MARCO v1.1 chosen over NQ-500 for 1000-passage corpus — web-search passages are more heterogeneous and realistic for RAG

### Pending Todos

None yet.

### Blockers/Concerns

- Defense classifier training data source not yet determined (needed for Phase 3.1)
- Phase 02.2 (corpus poisoning attack) not yet planned — next step

## Session Continuity

Last session: 2026-04-15T16:50:43.113Z
Stopped at: Completed 02.2-01-PLAN.md — MS-MARCO corpus, upgraded attacks, mistral:7b config
Resume file: None
