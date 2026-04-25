---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: milestone
status: Phase 03.3 IN PROGRESS — Plan 02 (ATK-01b Tier 1b homoglyph attack) complete
stopped_at: Phase 03.3 Plan 02 complete — TIER1B_ID_START=20150, HOMOGLYPH_HACKED (Cyrillic НАСКЕД), build_tier1b_passages (50 passages IDs 20150-20199), run_eval.py Tier 1b metrics + T3 upper bound fix; 141 passed 35 skipped 0 failed
last_updated: "2026-04-25T06:56:21Z"
progress:
  total_phases: 11
  completed_phases: 6
  total_plans: 12
  completed_plans: 24
  percent: 93
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-31)

**Core value:** Demonstrate an attack-defense arms race for indirect prompt injection in RAG systems — 4 attack tiers, 2 defense generations, showing per-chunk defenses are fundamentally insufficient.
**Current focus:** Phase 03.3 — quick evaluation additions (Plan 02 ATK-01b Tier 1b complete)

## Current Position

Phase: 03.3 (quick-evaluation-additions) — IN PROGRESS
Plan: 2 of 7 COMPLETE
Last activity: 2026-04-25 (03.3-02 ATK-01b: Tier 1b homoglyph attack + corpus regeneration + run_eval metrics)

Progress: [█████████░] 93%

## Performance Metrics

**Velocity:**

- Total plans completed: 24
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
| 03.1 | 7/7 | Complete (verified 2026-04-24) |
| 03.2 | 4/4 | Complete (verified 2026-04-24) |
| 03.3 | 2/7 | In progress (03.3-02 ATK-01b Tier 1b complete 2026-04-25) |

**Recent Trend:**

- Last 5 plans: 03.2-02, 03.2-03, 03.2-04, 03.3-01, (next: 03.3-02)
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
- [Phase 03.1-06]: SC-5 PASS — fused_fixed_0.5 achieves 0% ASR on T1/T2/T3 for llama3.2:3b, ties or beats every individual signal on all tiers
- [Phase 03.1-06]: DEF-02 counter-productive finding (honest) — system-prompt instruction-data separation increased T1 ASR 2%→8% and T2 ASR 12%→38%; investigation deferred to plan 03.1-07
- [Phase 03.1-06]: D-08 confirmed — perplexity_only T3 ASR = 0% = no_defense T3 baseline; perplexity signal adds zero T3 protection, motivating fusion
- [Phase 03.1-06]: Cross-model transfer confirmed — mistral fused drops T2 28%→0% and T3 12%→0%; fused defense generalizes across LLM architectures
- [Phase 03.1-06]: FPR cost = 76% for fused defense — high utility cost documented for Phase 3.4 analysis; threshold tuning targeted in plan 03.1-07
- [Phase 03.1-07]: Tuned threshold=0.10 reduces retrieval_rate 50%->34% at same FPR=76% and 0% ASR — threshold tightens filtering at retrieval time without changing end-to-end security
- [Phase 03.1-07]: DEF-02 counter-productive effect classified as priming on llama3.2:3b — system prompt warning primes model to identify/surface injected instructions; substring leak ruled out (no anchor tokens in prompt); behavior change ruled out (shorter answers)
- [Phase 03.1-07]: Phase 3.4 practitioners warning established — naive prompt-only defenses counterproductive on small models; retrieval-side filtering is the correct intervention
- [Phase 03.2-01]: importlib.spec_from_file_location used to load scripts/ modules in tests — avoids sys.path mutation; handles FileNotFoundError gracefully for wave 0 stubs
- [Phase 03.2-01]: test_train_defense_has_no_seed_flag_yet uses regex add_argument.*--seed not bare string — '--seed' already appears in train_defense.py docstring on line 95
- [Phase 03.2-01]: TestLooJudge kept green (not skip-guard) — parse_judge_output satisfies full contract including edge cases; immediately usable by plan 03.2-03 LOO script
- [Phase 03.2-02]: Pre-filter TIER1_OPENERS to safe_openers pool (no IMPERATIVE_VERBS match) — several openers contain 'produce'/'override' which would false-positive on the ATK-08/09 assert; deterministic pool guards against future opener additions
- [Phase 03.2-02]: ATK08_INDIRECT_TEMPLATE uses 'response' not 'answer'; ATK09_DECLARATIVE_TEMPLATE uses 'conclusion' not 'answer' — 'answer' is in IMPERATIVE_VERBS; Rule 1 fix applied at template definition time
- [Phase 03.2-02]: ADAPTIVE_ID_START defined both in generate_poisoned_corpus.py (local constant for corpus build) and rag/constants.py (single-source-of-truth for evaluation); different modules, no shadow conflict
- [Phase 03.2-02]: Stale test_train_defense_has_no_seed_flag_yet replaced with positive presence assertion test_seed_flag_exists_in_train_defense — inverts guard once flag is implemented per plan 03.2-01 instructions
- [Phase 03.2-03]: LOO ROC AUC below 0.5 for both models (llama: 0.372, mistral: 0.410) — honest negative result: clean chunks appear MORE attributable by LOO divergence because they contain unique factual content; injected chunks are redundant (same payload repeated), removing one does not restore clean model behavior
- [Phase 03.2-03]: Only Tier 4 fragment A retrieved in top-3 (pids 20200/20203/20206); B/C never appear — co-retrieval rate insufficient for Tier 4 fragmentation attack, confirming Phase 02.4-03 finding; fragment A influence=1.0 when retrieved but retrieved only 3 times across 50 queries
- [Phase 03.2-03]: parse_judge_output copied directly into run_loo.py (no cross-script imports) — avoids importlib issues in test stubs; identical 8-line implementation maintained in both run_judge.py and run_loo.py
- [Phase 03.3-01]: test_eval_tier1b.py uses inspect.getsource(run_eval_mod) to enforce T3 upper bound uses TIER1B_ID_START not TIER4_ID_START — contract enforcement without importing internal functions
- [Phase 03.3-01]: test_eval_v2_01_driver.py shell=True assertion is a hard assertion not a skip — enforces T-3.3-01 threat mitigation (command injection risk) at contract time before Wave 2 implementation

### Pending Todos

None.

### Blockers/Concerns

- kimi-k2.5:cloud is available in `ollama list` but queries require a paid Ollama subscription the team does not have (403 at request time); Phase 02.4 Tier 3 payloads were generated with gpt-oss:20b-cloud instead — research objective preserved, forward compatibility kept via `--model` flag

## Session Continuity

Last session: 2026-04-25T06:56:21Z
Stopped at: Phase 03.3 Plan 02 complete — ATK-01b Tier 1b homoglyph attack: HOMOGLYPH_HACKED (Cyrillic НАСКЕД), 50 T1b passages (IDs 20150-20199), run_eval.py tier1b metrics + T3 upper bound fix; 141 passed 35 skipped; commits 8393d47/fe22288/ee1debb
Resume file: None (proceed to Phase 03.3 Plan 03 — ATK-02 poisoning ratio sweep)
