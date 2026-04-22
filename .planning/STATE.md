---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: milestone
status: Phase 02.4 context gathered � ready for planning
stopped_at: Phase 02.4 context gathered via discuss-phase
last_updated: "2026-04-22T00:00:00.000Z"
P26-04-22
progress:
  total_phases: 11
  completed_phases: 4
  total_plans: 12
  completed_plans: 10
  percent: 72
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-31)

**Core value:** Demonstrate an attack-defense arms race for indirect prompt injection in RAG systems — 4 attack tiers, 2 defense generations, showing per-chunk defenses are fundamentally insufficient.
**Current focus:** Phase 02.4 — advanced attack tiers (Tier 3 LLM-generated + Tier 4 cross-chunk)

## Current Position

Phase: 02.3 (evaluation-harness) — COMPLETE
Plan: 2 of 2
Next phase: 02.4 — advanced attack tiers
Last activity: 2026-04-21

Progress: [████████░░] 72%

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
| 02.2 | 2 | Complete |
| 02.3 | 2 | Complete (verified 2026-04-21) |

**Recent Trend:**

- Last 5 plans: 02.2-01, 02.2-02, 02.3-01, 02.3-02
- Trend: On track

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
- [Phase 02.3]: Tier-2 EXFILTRATED token replaced with attacker.com URL payload — LLMs echo URLs reliably but not metadata tokens
- [Phase 02.3]: paired_asr metrics computed over indices 0-49 only — isolates attack signal from clean-query false positive noise
- [Phase 02.3]: Mistral:7b shows highest Tier-2 susceptibility (32% paired ASR) — stronger instruction-following makes it more likely to follow embedded [Note for AI:] directives
- [Phase 02.3]: Cloud models (gpt-oss:20b/120b) resist Tier-1 naive injection (0% ASR) but succumb to Tier-2 URL smuggling — confirms scale doesn't defeat instruction smuggling
- [Phase 02.3]: --model flag added to run_eval.py — enables multi-model eval without config.toml mutation

### Pending Todos

None.

### Blockers/Concerns

- Defense classifier training data source not yet determined (needed for Phase 3.1)
- Phase 02.4 (advanced attack tiers: Tier 3 LLM-generated + Tier 4 cross-chunk) not yet planned

## Session Continuity

Last session: 2026-04-21T23:00:00.000Z
Stopped at: Phase 02.3 complete — 4-model baselines produced, all must-haves verified
Resume file: .planning/phases/02.4-advanced-attack-tiers/ (needs planning)
