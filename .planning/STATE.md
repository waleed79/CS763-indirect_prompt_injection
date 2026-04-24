---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: milestone
status: Phase 03.1 in progress — Plan 05 complete
stopped_at: Phase 03.1 Plan 05 complete — run_eval.py extended with 7-mode --defense, FPR tracking, system_prompt threading
last_updated: "2026-04-23T00:30:00.000Z"
progress:
  total_phases: 11
  completed_phases: 5
  total_plans: 12
  completed_plans: 14
  percent: 89
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-31)

**Core value:** Demonstrate an attack-defense arms race for indirect prompt injection in RAG systems — 4 attack tiers, 2 defense generations, showing per-chunk defenses are fundamentally insufficient.
**Current focus:** Phase 03.1 — multi-signal defense fusion (next phase)

## Current Position

Phase: 03.1 (multi-signal-defense-fusion) — IN PROGRESS
Plan: 5 of 6 COMPLETE
Last activity: 2026-04-23

Progress: [█████████░] 87%

## Performance Metrics

**Velocity:**

- Total plans completed: 9
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 01.1 | 2 | Complete |
| 02.1 | 4 | Complete (verified) |
| 02.2 | 2 | Complete |
| 02.3 | 2 | Complete (verified 2026-04-21) |
| 02.4 | 3 | Complete (verified 2026-04-23) |
| 03.1 | 5/6 | In progress (Plan 05 complete 2026-04-23) |

**Recent Trend:**

- Last 5 plans: 02.3-01, 02.3-02, 02.4-01, 02.4-02, 02.4-03
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
- [Phase 02.4-01]: gpt-oss:20b-cloud substituted for kimi-k2.5:cloud (Rule 3 deviation) — kimi requires paid subscription (403); research objective identical; --model flag preserves forward compatibility
- [Phase 02.4-01]: Wave 0 stubs reference downstream module imports to enforce interface contract — TestTierDetectionPredicate imports TIER3/4_ID_START from run_eval.py; TestJudgeOutputParsing imports parse_judge_output from run_judge.py
- [Phase 02.4-02]: Tier 4 Fragment C uses declarative editorial-note style (not imperative) — defeats per-chunk injection detectors by construction; no imperative verb in any single fragment
- [Phase 02.4-02]: TIER4_SETS targets shakespeare_hamlet/einstein_relativity/vaccines_immunity (attack-paired indices 0, 1, 9) — highest-traffic paired queries for maximum co-retrieval signal
- [Phase 02.4-02]: load_tier3_from_jsonl() filters to IDs 20100-20149 after loading to guard against stale/wrong-range entries in the JSONL
- [Phase 02.4-03]: LLM-as-judge agreement_rate=1.0 (79/79) — substring-based ASR detection validated as accurate proxy for semantic compliance
- [Phase 02.4-03]: Tier 4 ASR=0% both models — co-retrieval of all 3 fragments not achieved in top-k=3; co-retrieval rate only 9%; expected empirical finding per RESEARCH.md Pitfall 3
- [Phase 02.4-03]: mistral:7b shows 7% Tier 3 ASR (12% paired) vs 0% llama3.2:3b — stronger instruction-following increases susceptibility to LLM-generated semantic injections
- [Phase 03.1-01]: Module-level try/except ImportError for rag.defense import in test stubs — collection exits 0 before defense module exists; all 9 dependent tests skip, TestDef02Prompt fails red
- [Phase 03.1-01]: DistilBERT download via external script (scripts/_download_distilbert.py) — Windows conda 23.7.4 does not support multiline strings in -c arguments; external script is equivalent and reusable
- [Phase 03.1-03]: Module-level alias DEF_02_SYSTEM_PROMPT = Generator.DEF_02_SYSTEM_PROMPT added — test imports as module-level name; class constant and module alias both maintained
- [Phase 03.1-03]: system_prompt None-guard uses `is not None` (not truthiness) — empty string is a valid override per T-03.1-07
- [Phase 03.1-04]: accelerate>=1.1.0 installed (not in original env) — required by transformers 5.5.3 HF Trainer; Rule 3 auto-fix
- [Phase 03.1-04]: Signal 4 baseline calibrated with real pipeline queries: mu=0.5891, std=0.0514 from 147 clean passage scores on nq_poisoned_v4
- [Phase 03.1-04]: LR coef[3] (retrieval_z) = 0.0 expected — all training examples use uniform synthetic retrieval score; real variance present at eval time
- [Phase 03.1-04]: Wave 0 pytest.skip() stubs removed from test_defense.py — all 10 tests now active and passing with trained models
- [Phase 03.1-05]: DEFENSE_CHOICES constant at module level (not inline in argparse) — single source of truth; importable by test code
- [Phase 03.1-05]: chunks_removed uses eval_cfg.top_k (from config) not hardcoded — mitigates T-03.1-12 threat
- [Phase 03.1-05]: defense_active bool replaced by defense_mode string — mode name directly usable in ablation table assembly
- [Phase 03.1-05]: FPR computed over unpaired_results only (paired=False) — measures false positives on clean queries, not attack queries

### Pending Todos

None.

### Blockers/Concerns

- Defense classifier training data source not yet determined (needed for Phase 3.1)
- kimi-k2.5:cloud is available in `ollama list` but queries require a paid Ollama subscription the team does not have (403 at request time); Phase 02.4 Tier 3 payloads were generated with gpt-oss:20b-cloud instead — research objective preserved, forward compatibility kept via `--model` flag

## Session Continuity

Last session: 2026-04-23T00:30:00.000Z
Stopped at: Phase 03.1 Plan 05 complete — run_eval.py 7-mode --defense + FPR tracking + system_prompt threading
Resume file: None (continue with Phase 03.1 Plan 06 — ablation evaluation runs)
