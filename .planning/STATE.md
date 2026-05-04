---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: Phase complete — ready for verification
stopped_at: Phase 6 context gathered
last_updated: "2026-05-04T08:47:43.416Z"
last_activity: 2026-05-04
progress:
  total_phases: 13
  completed_phases: 10
  total_plans: 55
  completed_plans: 52
  percent: 95
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-31)

**Core value:** Demonstrate an attack-defense arms race for indirect prompt injection in RAG systems — 5 attack tiers (T1, T1b, T2, T3, T4) plus an adaptive tier (ATK-08/09), 2 defense generations, showing per-chunk defenses are fundamentally insufficient.
**Current focus:** Phase 05 complete — honest FPR metrics

## Current Position

Phase: 04 (final-presentation) — EXECUTING
Plan: 7 of 7
Last activity: 2026-05-04

Progress: [██████████] 100% (research phases)

## Performance Metrics

**Velocity:**

- Total plans completed: 31
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
| 03.3 | 7/7 | Complete (03.3-07 EVAL-V2-01 cross-model 3×3×5 matrix complete 2026-04-27) |
| 03.4 | 6/6 | Complete (submitted to Google Doc 2026-04-30) |
| 05 | 5/5 | Complete (verified 2026-05-03) |

**Recent Trend:**

- Last 5 plans: 03.4-04, 03.4-05, 03.4-06, 04-03, 04-04
- Trend: Complete

| Phase 06 P05 | 10m | 2 tasks | 4 files |

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
- [Phase 03.3-03]: ATK02_SWEEP_ID_START (21000-21049) used for cycle-1 Tier-1 pool extension — NOT p.passage_id + 50 which collides with T2 range (20050-20099); threat T-3.3-03-03 mitigated
- [Phase 03.3-03]: p._replace() used for NamedTuple field update — Passage is NamedTuple not dataclass; dataclasses.replace() raises TypeError; Rule 1 auto-fix at execution time
- [Phase 03.3-03]: math.ceil(ratio * n_clean) with dynamic n_clean=len(clean) — PoisonedRAG adversary-favoring rounding; n_clean never hardcoded; 5/10/20/50/100 poisoned docs at 0.5%/1%/2%/5%/10%
- [Phase 03.3-04]: Prefix application is encode-time only — index() encodes prefixed texts but stores documents=all_texts (un-prefixed) in ChromaDB; retrieve() encodes prefixed query but RetrievalResult.text is un-prefixed; prevents prefix leakage into LLM prompts
- [Phase 03.3-04]: EVAL-06 driver uses option (A) — indexes each per-model collection in-process via Retriever.index(), then invokes run_eval.py via subprocess with --embedding-model to match eval model to indexed collection
- [Phase 03.3-04]: subprocess.run(list_argv, check=True) with no shell=True — enforces T-3.3-01 threat mitigation in run_transferability_eval.py
- [Phase 03.3-05]: TIER_CONFIG dict is single source of truth for per-tier anchor/retrieved_key/hijack_key — build_judge_user_message reads anchor from TIER_CONFIG[tier]["anchor"]; eliminates hardcoded JUDGE_USER_TEMPLATE and TIER3_ANCHOR_SUBSTRING
- [Phase 03.3-05]: --tier default=tier3 preserves Phase 2.4 pilot CLI behavior; empty-tier guard generalized to n_tier==0 check avoiding ZeroDivisionError for any tier including tier4
- [Phase 03.3-07]: subprocess.run(list_argv, check=False) with no shell=True — T-3.3-07-01 mitigation enforced by tests/test_eval_v2_01_driver.py; check=False (not check=True) so single-cell failure does not abort the 45-cell matrix
- [Phase 03.3-07]: resolve_defenses() falls back to DEFENSES_FALLBACK = [no_defense, fused, def02] when models/causal_attribution/ready.flag absent — fired at execution time per CONTEXT D-12 since Phase 3.2 causal artifacts not yet present; stderr warning contains literal "causal artifact not found" for greppability
- [Phase 03.3-07]: Cross-model finding — gemma4:31b-cloud is 0% ASR across all 5 tiers × 3 defenses; cloud-scale instruction-following is robust to substring-level injection independent of defense layer (citable result for Phase 3.4)
- [Phase 03.3-07]: Tier 1b (Unicode homoglyph) is the strongest naive injection on llama3.2:3b — 22% no_defense rising to 35% under DEF-02 (DEF-02 substring detector keyed on ASCII HACKED is bypassed by Cyrillic НАСКЕД payload) — confirms ATK-01b stealth hypothesis
- [Phase 03.4-01]: OQ2 resolved (UNPAIRED) — logs/eval_matrix/_summary.json asr_overall column matches per-cell aggregate.asr_overall (all 100 queries), NOT paired_asr_tier1 (50 paired); Plans 02 and 03 must read paired numbers from per-cell .log files when paired ASR is required
- [Phase 03.4-01]: Wave 0 stubs use importlib.util.spec_from_file_location guards (NOT plain `from scripts.X import main`) — pattern carried from Phase 3.2 test_loo.py; lets pytest --collect-only succeed cleanly before production code lands; 24 tests SKIP across 4 stub files
- [Phase 03.4-01]: ratio-sweep evals use --tier-filter tier1 (NOT --tier; that flag does not exist) and --defense off (NOT --defense no_defense; that value does not exist); plan front-loaded these CLI verifications after RESEARCH found stale references in 03.4-CONTEXT.md
- [Phase 03.4-01]: D-06 ratio-sweep ASR climbs 4%→16% over 0.5%→10% poisoning ratio with mild non-monotonicity at 0010→0020 and 0050→0100 (LLM stochasticity at n=100); retrieval_rate climbs monotonically 29%→82%; FPR=0% (no defense to false-positive on); shape matches PoisonedRAG Fig. 3
- [Phase 03.4-01]: ASCII-safe head display in schema probes (encode/backslashreplace) — avoids cp1252 cascade in conda run on Windows when source files contain non-ASCII chars (e.g. ↔ U+2194 in xss_ssrf_taxonomy.md heading); pattern documented for future probe scripts
- [Phase 03.4-02]: ablation_table.json `defense_mode` inner field uses run_eval CLI short-names (`bert`, `fused`, `off`) which collapse `fused_fixed_0.5` and `fused_tuned_threshold` into a single `fused` value — load_ablation in scripts/make_results.py uses the dict KEY as the canonical `defense_mode` and preserves the inner field as `defense_mode_raw`; without this fix the ablation table loses the "Fused (tuned)" distinction
- [Phase 03.4-02]: DEFENSE_DISPLAY in scripts/make_results.py is the single source of truth for defense column display labels (T-3.4-W1-05) — handles BOTH ablation top-level keys (bert_only, fused_fixed_0.5) AND inner short-names (bert, fused, off); to be mirrored verbatim by Plan 03 figure renderer to prevent label drift between tables and figures
- [Phase 03.4-02]: Adaptive arms-race row uses paired_asr_adaptive (not asr_adaptive) — adaptive_fused_*.json has both keys; the paired number is the citable headline for Plan 05 §2 continuity with Phase 2.3 paired ASR; FPR=nan for source (a) Undefended baseline rows (no defense to false-positive on; honest absence rather than fabricated 0)
- [Phase 03.4-03]: matplotlib infers savefig format from file extension and rejects `.tmp` ("Format 'tmp' is not supported"); save_atomic helper passes `format="png"` explicitly so the atomic-write idiom (write to .tmp + os.replace) works. Caught Rule-1 bug on first execution; one-line fix.
- [Phase 03.4-03]: B-2 fail-loud invariants on D-03 data matrix in render_d03_arms_race — assert np.nansum(data)>0 AND np.nanmax(data)>0.05 AND non-zero-cell-count>=5 BEFORE save_atomic. Catches the all-zero placeholder regression class (silent figure with all bars at zero height). Verified live: nansum=1.44, nanmax=0.38, 10 non-zero cells.
- [Phase 03.4-03]: W-5 fail-loud invariants on D-12 cross-model heatmap in render_d12_cross_model_heatmap — assert matrix.shape==(5,3) AND not matrix.isna().any().any() before sns.heatmap. Catches model-name schema drift (underscore vs colon) with explicit AssertionError; main() returns 2 on failure so CI/scripted callers see the error instead of a silently degraded figure.
- [Phase 03.4-03]: DEFENSE_DISPLAY copied verbatim from scripts/make_results.py (T-3.4-W1-05 single source of truth) rather than imported. Importing scripts/ modules without __init__.py requires importlib.util.spec_from_file_location; copying with a comment pointer is simpler. Future label additions land in make_results.py first and are mirrored here within the same plan/PR.
- [Phase 03.4-04]: Mistral LOO ROC AUC has two canonical decimal forms in the project: **0.410** (used in Phase 03.2-03 SUMMARY, the test literal in tests/test_loo_neg_doc.py, and most downstream prose) vs **0.414** (the JSON-rounded form 0.41379→0.414, used in the Phase 03.4-03 ROC figure label). Both refer to the same logs/loo_results_mistral.json aggregate.roc_auc=0.41379... measurement; logs/loo_negative_result_analysis.md cites 0.410 in the table with a dagger footnote disclosing 0.414. Future writeup edits should preserve both forms or pick one and update both places consistently.
- [Phase 03.4-04]: logs/ is gitignored (.gitignore line 15); canonical analysis docs are force-added with `git add -f`. Pattern established by logs/def02_priming_analysis.md (commit cd1b804) and logs/ablation_table.json; logs/loo_negative_result_analysis.md follows the same pattern (commit c7b8e7b).
- [Phase 03.4-04]: D-16 6-section contract enforced via tests/test_loo_neg_doc.py: f'## {n}.' literal heading checks for n in 1..6. Future analysis-doc plans following the same pattern should use exact `## N. Title` heading literals (no `### N`, no other heading levels) so a single grep `^## [1-6]\.` matches all required section anchors.
- [Phase 03.4-05]: Writeup follows the same `## N.` heading-literal pattern (n in 1..13) for tests/test_writeup_structure.py; tables are inlined as Markdown pipe tables (NOT raw `| col |` text per RESEARCH Pitfall 3); references use plain numbered list (NOT `[^N]` footnote syntax per RESEARCH Pitfall 4) so Google Docs paste preserves them; 12 collected tests in tests/test_writeup_structure.py (plan-prompt's "11 tests" was a count mismatch — the test class added test_cr02_disclosure since plan was written, bringing total to 12).
- [Phase 03.4-05]: Figure 5 (cross-model heatmap) placed at start of §8(e) where it directly supports the gemma4 hero finding rather than at §7 retriever-transferability; the figure is a 5-tier × 3-LLM heatmap whose visual story is the gemma4 column being uniformly zero, not embedding-model variance. Plan outline ambiguous; this placement maximizes narrative coherence with no contract violation (figure filename literal still present, satisfying test_all_five_figures_referenced).
- [Phase 03.4-05]: W-6 safety checkpoint pattern executed verbatim: intermediate commit ecdbc7f after initial Write completes (mirrors Phase-3.3 atomic-write `os.replace` pattern at the document level), final commit 7573e52 supersedes with one-line `Document status:` enhancement; both commits in `git log -- docs/phase3_results.md` per acceptance contract.
- [Phase 06-04]: Used fillna('—') instead of na_rep='—' in to_markdown() — installed tabulate version lacks na_rep kwarg; functionally equivalent
- [Phase 06-04]: emit_undefended_baseline and arms_race use markdown-only format to preserve original CSVs as Phase 3.4 deliverables; _v6.csv companions carry post-Phase-6 schema
- [Phase 06-04]: _resolve_v6_path alias added for _resolve_matrix_path to satisfy test_make_results_v6.py skip-guard (checks hasattr _resolve_v6_path)
- [Phase ?]: T1b for llama/mistral filled 0.0 in undefended heatmap (not measured pre-Phase-3.3-02)

### Pending Todos

None.

### Blockers/Concerns

- kimi-k2.5:cloud is available in `ollama list` but queries require a paid Ollama subscription the team does not have (403 at request time); Phase 02.4 Tier 3 payloads were generated with gpt-oss:20b-cloud instead — research objective preserved, forward compatibility kept via `--model` flag

### Roadmap Evolution

- Phase 5 added (2026-05-03): Honest FPR metrics — per-chunk, answer-preserved, and LLM-as-judge utility cost. Reviewer-driven follow-up to replace coarse 76% query-level FPR with three more honest user-visible-cost metrics on the existing clean-query eval set. Run `/gsd-plan-phase 5` to break down.
- Phase 6 added (2026-05-04): Cross-LLM undefended baseline gap fill — run gpt-oss:20b-cloud and gpt-oss:120b-cloud undefended on the existing combined poisoned corpus, single eval run per model with post-hoc per-tier tagging from passage_id to obtain T1, T1b, T2, T3, T4 ASR simultaneously. Closes the cross-LLM undefended baseline gap (Phase 2.3 only ran T1/T2 for these two cloud models). ~26 min total. Run `/gsd-plan-phase 6` to break down.

## Session Continuity

Last session: 2026-05-04T08:47:36.359Z
Stopped at: Phase 6 context gathered
Resume file: None
