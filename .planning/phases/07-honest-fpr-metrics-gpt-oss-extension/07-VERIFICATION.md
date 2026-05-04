---
phase: 07-honest-fpr-metrics-gpt-oss-extension
plan_count: 6
status: passed
verified: 2026-05-04T00:00:00Z
score: 8/8 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: verified
  previous_score: 24/24 P7-* tests
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 7: Honest FPR Metrics — gpt-oss Extension Verification Report

**Phase Goal:** Extend Phase 5's three honest FPR metrics (M1 per-chunk, M2 answer-preserved, M3 judge-scored) from llama3.2:3b to gpt-oss:20b-cloud and gpt-oss:120b-cloud on the {fused, def02} defense cells from Phase 6. Compute M1/M2 from existing Phase 6 v6 logs; M3 via ~200 cloud-judge calls. Output: logs/ablation_table_gptoss_v7.json + extended Phase 5 writeup.
**Verified:** 2026-05-04
**Status:** PASSED
**Re-verification:** Yes — goal-backward verification after Plan 06 executor's internal verification

---

## Goal Achievement

### Observable Truths (Derived from ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | M1/M2/M3 computed for all 4 cells: {gpt-oss:20b-cloud, gpt-oss:120b-cloud} x {fused, def02} | VERIFIED | `logs/ablation_table_gptoss_v7.json` has exactly 4 keys; Python check confirms values in [0,1] |
| 2 | `logs/ablation_table_gptoss_v7.json` exists with D-02 schema (7 fields per row, no no_defense row) | VERIFIED | File present; `python -c` schema check exits 0; `grep "no_defense"` script asserts absence at write-time |
| 3 | `logs/judge_fpr_gptoss_v7.json` contains exactly 200 verdict records nested verdicts[model][defense][qid] | VERIFIED | Python count confirms total=200; phase="07", judge_model="gpt-oss:20b-cloud"; all 4 required fields present per record |
| 4 | `docs/phase5_honest_fpr.md` contains Phase 7 addendum with 10-row M1/M2/M3 table (6 llama + 4 gpt-oss) | VERIFIED | `grep -c "## Phase 7 addendum"` outputs 1; Python row-count script outputs 10; addendum heading appears exactly once |
| 5 | Original Phase 5 prose above the addendum is bit-for-bit identical to commit 7374f22 | VERIFIED | `prefix == head_prefix` is True (len 11250 chars each); `TestPhase5ProseUntouched` PASS |
| 6 | 30/30 addendum table cells match source JSON files (10 rows x 3 metrics) | VERIFIED | Independent numerical-fidelity audit: "OK: all 10 rows x 3 metrics = 30 cells match JSON sources" |
| 7 | `docs/results/honest_fpr_gptoss_v7.{md,csv}` exist as auto-companion (4 rows each) | VERIFIED | Both files exist; CSV has 4 non-empty data rows; MD file has 4 pipe-table data rows |
| 8 | Phase 5, Phase 6, Phase 3.4 deliverables byte-identical to git HEAD | VERIFIED | `git diff --exit-code` exits 0 on all protected files; no Phase 6 v6 docs/results files changed |

**Score:** 8/8 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/run_judge_fpr_gptoss.py` | Phase 7 entry-point, 200+ lines, importlib reuse | VERIFIED | 393 lines; CELL_LOG_MAP(4), OFF_LOG_MAP(2); JUDGE_SYSTEM_PROMPT identity confirmed via importlib |
| `tests/test_phase7_judge_fpr.py` | 17 test classes covering 21 P7-* methods | VERIFIED | 21 tests collected; all PASS |
| `tests/test_make_results_v7.py` | 7 test classes covering 9 P7-RESV/DOC methods | VERIFIED | 9 tests collected; all PASS |
| `scripts/make_results.py` | v7 path-resolver, loader, emitter symbols added | VERIFIED | `_resolve_v7_ablation_path`, `load_honest_fpr_v7`, `emit_honest_fpr_gptoss_v7`, `_V7_ABLATION_FILENAME` all present |
| `scripts/run_judge_fpr.py` | UTF-8 fix at line 101 | VERIFIED | `read_text(encoding="utf-8")` at line 101 confirmed |
| `logs/ablation_table_gptoss_v7.json` | 4-row flat dict, D-02 schema | VERIFIED | Keys: gptoss20b_cloud__{fused,def02}, gptoss120b_cloud__{fused,def02} |
| `logs/judge_fpr_gptoss_v7.json` | 200 verdicts, D-04 schema | VERIFIED | 200 records, fields: verdict/ab_assignment/raw_response/retry_count |
| `logs/judge_fpr_gptoss_v7.json.cache` | Per-cell checkpoint | VERIFIED | File exists |
| `docs/results/honest_fpr_gptoss_v7.md` | 4-row Markdown companion | VERIFIED | File present; 4 data rows confirmed |
| `docs/results/honest_fpr_gptoss_v7.csv` | 4-row CSV companion | VERIFIED | File present; 4 non-empty data rows |
| `docs/phase5_honest_fpr.md` | Original + appended addendum | VERIFIED | Addendum heading once; 10 table rows; 0 deletions (pure append) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `run_judge_fpr_gptoss.py` | `run_judge_fpr.py` | `importlib.util.spec_from_file_location` | WIRED | `JUDGE_SYSTEM_PROMPT is _phase5.JUDGE_SYSTEM_PROMPT` is True; `parse_verdict is _phase5.parse_verdict` is True |
| `run_judge_fpr_gptoss.py` | `logs/eval_matrix/gptoss*_v6.json` | CELL_LOG_MAP hardcoded paths | WIRED | All 4 CELL_LOG_MAP paths verified on disk via TestPathMapsLoudFail |
| `run_judge_fpr_gptoss.py` | `logs/ablation_table_gptoss_v7.json` | `atomic_write_json` at end of main() | WIRED | File exists with 4 keys; written via WR-01 single-write-at-end |
| `make_results.py main()` | `logs/ablation_table_gptoss_v7.json` | `_resolve_v7_ablation_path` | WIRED | Resolver returns Path when file present; TestV7Emit PASS |
| `make_results.py` | `docs/results/honest_fpr_gptoss_v7.{md,csv}` | `emit_honest_fpr_gptoss_v7` | WIRED | Both files exist; TestV7Emit PASS |
| `docs/phase5_honest_fpr.md addendum` | `logs/ablation_table_gptoss_v7.json` | 4 gpt-oss rows in table | WIRED | Numerical fidelity audit: 12 gpt-oss cells match JSON to 3 decimal places |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `ablation_table_gptoss_v7.json` | M1/M2/M3 per cell | Phase 6 v6 log files via `load_clean_records` + 200 cloud judge calls | Yes | FLOWING — 200 verdicts, 0 retries, all n_calls=50 |
| `honest_fpr_gptoss_v7.md` | 4 rows from JSON | `_resolve_v7_ablation_path` -> `load_honest_fpr_v7` | Yes | FLOWING — values verified match JSON |
| `docs/phase5_honest_fpr.md` addendum | 10 table rows | 6 from `logs/ablation_table.json`, 4 from `logs/ablation_table_gptoss_v7.json` | Yes | FLOWING — 30/30 cells match source JSONs |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `--dry-run` exits 0, makes 0 cloud calls, prints M1 for 4 cells | `conda run -n rag-security python scripts/run_judge_fpr_gptoss.py --dry-run` | Exit 0; n_calls=0 for all 4 cells; M1 values match JSON | PASS |
| Full pytest suite 265 pass, 0 fail | `conda run -n rag-security pytest tests/ --tb=short -q` | 265 passed, 4 skipped, 0 failed in 97.84s | PASS |
| All 30 Phase 7 tests pass | `conda run -n rag-security pytest tests/test_phase7_judge_fpr.py tests/test_make_results_v7.py -v` | 30 passed in 2.16s | PASS |
| Ablation JSON has 4 keys, no no_defense | Python schema check | Keys confirmed; "no_defense" absent | PASS |
| 200 verdicts with correct fields | Python count | total=200; fields: verdict/ab_assignment/raw_response/retry_count | PASS |
| Phase 5 prose unchanged | Git comparison to 7374f22 | Prefix len=11250 == HEAD len=11250; match=True | PASS |
| Numerical fidelity 30/30 | Independent Python audit | "OK: all 10 rows x 3 metrics = 30 cells match JSON sources" | PASS |

### Requirements Coverage

Phase 7 uses internal P7-* IDs (not tracked in REQUIREMENTS.md). ROADMAP.md requirements for Phase 7:

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| M1 per-chunk FPR for 4 cells | From Phase 6 v6 logs, no cloud calls | SATISFIED | logs/ablation_table_gptoss_v7.json per_chunk_fpr: {fused: 0.092, def02: 0.000} for both models |
| M2 answer-preserved FPR for 4 cells | From Phase 6 v6 logs, no cloud calls | SATISFIED | answer_preserved_fpr: {20b-fused: 0.02, 20b-def02: 0.00, 120b-fused: 0.04, 120b-def02: 0.00} |
| M3 judge FPR for 4 cells | ~200 cloud-judge calls via gpt-oss:20b-cloud | SATISFIED | 200 verdicts collected; judge_fpr: {20b-fused: 0.16, 20b-def02: 0.06, 120b-fused: 0.16, 120b-def02: 0.10} |
| Emit logs/ablation_table_gptoss_v7.json | 4-row D-02 schema | SATISFIED | File exists with correct keys and schema |
| Extend docs/phase5_honest_fpr.md | 10-row cross-LLM table + analysis | SATISFIED | Addendum appended; 10 rows; substantive analysis paragraphs present |

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| None | — | — | No blockers, warnings, or notable anti-patterns found in Phase 7 deliverables |

Note: `scripts/run_judge_fpr_gptoss.py` line 303 contains `print("FATAL: ollama package not available...")` — this is an error-path guard, not a stub. The actual implementation is complete and functional.

### Human Verification Required

None. All verification was completed programmatically:

- The M3 human-verify checkpoint (Task 3 of Plan 04) was completed during execution: M2 <= M1 invariant holds for all 4 rows (verified in 07-04-SUMMARY.md), all values in [0,1], all n_calls=50.
- The cross-LLM analysis paragraphs in the addendum were reviewed during Plan 05 execution (substantive, not boilerplate per 07-05-SUMMARY.md).

---

## Per-Test Status Table (24 P7-* IDs)

All 24 P7-* test IDs confirmed PASS via `conda run -n rag-security pytest tests/test_phase7_judge_fpr.py tests/test_make_results_v7.py -v` (30 passed in 2.16s).

| Test ID | Test Class / Method | Status | Notes |
|---------|---------------------|--------|-------|
| P7-M1 | `TestM1Numerator::test_m1_formula` + `test_m1_in_range` | PASS | Synthetic fixture: chunks_removed [3,0,2,1,0] -> M1=6/25=0.24 |
| P7-M2 | `TestM2Aggregation::test_m2_formula` | PASS | Synthetic fixture: 3 records with chunks_removed>0, 1 DEGRADED -> M2=1/50 |
| P7-M3 | `TestM3Aggregation::test_m3_formula` + `test_tie_collapses_to_preserved` | PASS | TIE/refusal collapse to PRESERVED |
| P7-LCR | `TestLoadCleanRecordsV6::test_load_returns_50_records` | PASS | v6 cell loaded; exactly 50 clean records |
| P7-UTF | `TestUtf8Encoding::test_no_unicode_error` | PASS | Non-ASCII chars read without UnicodeDecodeError |
| P7-PATH | `TestPathMapsLoudFail::test_cell_log_map_paths_exist` + `test_off_log_map_paths_exist` | PASS | All 6 path-map entries resolve on disk |
| P7-CKEY | `TestCompositeKeys::test_composite_key_set` | PASS | Exactly 4 composite keys confirmed |
| P7-OUT-J-SHAPE | `TestAblationV7Shape::test_exactly_four_rows` + `test_each_row_has_required_keys` | PASS | 4 entries; all D-02 fields present |
| P7-OUT-J-NOROW | `TestNoTrivialRow::test_no_defense_absent` | PASS | "no_defense" key absent |
| P7-OUT-V-SHAPE | `TestVerdictsV7Shape::test_verdicts_nested_two_levels` | PASS | verdicts[model][defense][qid] nesting confirmed |
| P7-OUT-V-COUNT | `TestVerdictCount200::test_total_verdict_count` | PASS | Exactly 200 verdict records |
| P7-OUT-V-FIELDS | `TestVerdictRecordFields::test_verdict_record_has_required_fields` | PASS | All 4 required fields on every record |
| P7-RESV | `TestV7Resolver::test_returns_path_when_present` + `test_returns_none_when_absent` | PASS | Resolver returns Path when file exists, None otherwise |
| P7-RESV-EMIT | `TestV7Emit::test_v7_path_returned_when_present` + `test_v7_no_op_when_absent` | PASS | docs/results/honest_fpr_gptoss_v7.{md,csv} produced when v7 file present |
| P7-RESV-COMPAT | `TestV7Compat::test_prior_test_files_exist` | PASS | test_make_results.py and test_make_results_v6.py both exist and green |
| P7-DOC-UNTOUCHED | `TestPhase5ProseUntouched::test_prose_prefix_unchanged` | PASS | Prose above addendum is byte-for-byte identical to commit 7374f22 |
| P7-DOC-ADDENDUM | `TestAddendumPresent::test_addendum_heading_once` | PASS | Heading appears exactly once |
| P7-DOC-TABLE-10ROW | `TestAddendumTable10Rows::test_table_has_ten_data_rows` | PASS | Exactly 10 data rows |
| P7-DOC-PHASE3-UNTOUCHED | `TestPhase34NotEdited::test_phase3_doc_unchanged` | PASS | docs/phase3_results.md byte-identical to git HEAD |
| P7-INHERIT-PROMPT | `TestPromptInherited::test_prompt_is_same_object` | PASS | JUDGE_SYSTEM_PROMPT is same object (importlib identity) |
| P7-INHERIT-PARSE | `TestParserInherited::test_parse_verdict_is_same_object` | PASS | parse_verdict() same object (importlib identity) |
| P7-CACHE | `TestCacheResume::test_dry_run_skips_calls` | PASS | Cache present -> zero judge calls |
| P7-DRYRUN | `TestDryRunNoCloud::test_dry_run_no_cloud` | PASS | --dry-run makes zero cloud calls, rc=0 |
| P7-AUTH | `TestAuthEscalation::test_auth_error_returns_rc1` | PASS | JudgeAuthError -> rc=1 cleanly |

**24/24 P7-* test IDs: PASS**

---

## Originals-Untouched Audit (Goal-Backward Verification)

### Phase 5 Deliverables

| File | `git diff --exit-code HEAD` | Status |
|------|-----------------------------|--------|
| `logs/ablation_table.json` | exit 0 | CLEAN |
| `logs/judge_fpr_llama.json` | exit 0 | CLEAN |
| `docs/results/ablation_table.md` | exit 0 | CLEAN |
| `docs/results/ablation_table.csv` | exit 0 | CLEAN |
| `docs/results/undefended_baseline.md` | exit 0 | CLEAN |
| `docs/results/undefended_baseline.csv` | exit 0 | CLEAN |

**Phase 5 prose above addendum:** Bit-for-bit identical to commit 7374f22 (Python comparison of prefix vs. git-show output: `match=True`, `len_prefix=11250 == len_head=11250`).

### Phase 6 Deliverables

| File / Path | Status |
|-------------|--------|
| `logs/eval_matrix/*_v6.json` | CLEAN — git diff --name-only shows no v6 eval_matrix changes |
| `logs/eval_harness_undefended_gptoss*_v6.json` | CLEAN |
| `docs/results/*_v6.{md,csv}` | CLEAN — `git diff --name-only HEAD -- docs/results/ | grep -vE "(_v7|gptoss_v7)" | grep -E "_v6\.(md|csv)$"` produces empty output |

### Phase 3.4 Submitted Writeup

| File | Status |
|------|--------|
| `docs/phase3_results.md` | CLEAN — `git diff --exit-code HEAD -- docs/phase3_results.md` exits 0 |

---

## Numerical-Fidelity Audit (30 cells — Goal-Backward Re-Verification)

Independent Python audit (not trusting SUMMARY claims) against source JSON files:

**Result:** "OK: all 10 rows x 3 metrics = 30 cells match JSON sources"

Tolerance applied:
- llama rows (6): 0.005 (2-decimal display precision)
- gpt-oss rows (4): 0.0006 (raw JSON precision)

### Cell-Level Evidence

| # | Model | Defense | M1 (table) | M1 (JSON) | M2 (table) | M2 (JSON) | M3 (table) | M3 (JSON) | Status |
|---|-------|---------|-----------|-----------|-----------|-----------|-----------|-----------|--------|
| 1 | llama3.2:3b | DEF-02 | 0.00 | 0.000 | 0.00 | 0.000 | 0.24 | 0.240 | PASS |
| 2 | llama3.2:3b | BERT alone | 0.32 | 0.320 | 0.26 | 0.260 | 0.28 | 0.280 | PASS |
| 3 | llama3.2:3b | Perplexity | 0.22 | 0.220 | 0.14 | 0.140 | 0.16 | 0.160 | PASS |
| 4 | llama3.2:3b | Imperative | 0.36 | 0.364 | 0.34 | 0.340 | 0.34 | 0.340 | PASS (2-dec display) |
| 5 | llama3.2:3b | Fingerprint | 0.02 | 0.020 | 0.02 | 0.020 | 0.04 | 0.040 | PASS |
| 6 | llama3.2:3b | Fused | 0.31 | 0.308 | 0.32 | 0.320 | 0.34 | 0.340 | PASS (2-dec display) |
| 7 | gpt-oss:20b-cloud | Fused | 0.092 | 0.092 | 0.02 | 0.020 | 0.16 | 0.160 | PASS |
| 8 | gpt-oss:20b-cloud | DEF-02 | 0.000 | 0.000 | 0.00 | 0.000 | 0.06 | 0.060 | PASS |
| 9 | gpt-oss:120b-cloud | Fused | 0.092 | 0.092 | 0.04 | 0.040 | 0.16 | 0.160 | PASS |
| 10 | gpt-oss:120b-cloud | DEF-02 | 0.000 | 0.000 | 0.00 | 0.000 | 0.10 | 0.100 | PASS |

---

## pytest Suite — Full Results (Re-Verified)

```
platform win32 -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
265 passed, 4 skipped in 97.84s (0:01:37)
```

### Skipped Tests (4 — all pre-existing, not Phase 7)

| Test | Skip Reason | Phase |
|------|-------------|-------|
| `test_judge_per_tier.py::TestEmptyTierGuard::test_empty_tier_yields_none_agreement_rate` | run_judge.py main() --tier flag not yet implemented | Pre-Phase 7 |
| `test_phase4_assets.py::TestMakeQrSmoke::test_qr_decodes_to_repo_url` | qrcode library optional dep not installed | Pre-Phase 7 |
| `test_ratio_sweep.py::TestRatioSweepOutputs::test_5_output_files_generated` | Ratio sweep output files not present | Pre-Phase 7 |
| `test_retriever_prefix.py::TestStoredDocUnprefixed::test_stored_documents_do_not_contain_prefix` | Prefix injection integration test requires live ChromaDB write | Pre-Phase 7 |

---

## Gaps Summary

No gaps. All phase goal must-haves verified programmatically and independently of SUMMARY claims.

---

## Known Issues / Accepted Risks

### 1. Prose-audit script compares against 7374f22, not HEAD

The verification compares Phase 5 prose above the addendum heading to commit 7374f22 (the last pre-addendum Phase 5 commit), not HEAD. This is correct: HEAD already includes the addendum (commit fe09ca3). The comparison confirms the prefix is byte-for-bit identical to the original Phase 5 content. `TestPhase5ProseUntouched` uses the same approach and passes.

### 2. Llama rows display 2-decimal precision

Rows 1-6 in the addendum table display values rounded to 2 decimals (matching Phase 5 §4 table style). The fidelity audit uses tolerance 0.005 — no cell differs by more than 0.004 from its source JSON value. Documented in 07-05-SUMMARY decisions.

### 3. 4 pre-existing skipped tests unrelated to Phase 7

All 4 skips are pre-Phase 7 and were present in Phase 6 verification. Out of scope.

### 4. Single-seed judge calls (accepted methodology constraint)

Per Phase 5 D-05 and Phase 7 D-11, all 200 M3 judge calls are single-seed. CIs at n=50 are approximately +/-7pp at 95% confidence. This is documented in docs/phase5_honest_fpr.md §6 as the standing project-wide convention.

### 5. dry-run uses cache when present

The --dry-run flag computes M1 from def_records regardless of cache state. When the cache file exists (from Plan 04), it is read and used for M2/M3 computation (but n_calls=0 since no new cloud calls are made). When no cache exists, dry-run uses SKIP_DRYRUN sentinels (M2/M3 default to 0). This is correct behavior per the script's design and is verified by TestDryRunNoCloud PASS.

---

## Phase 7 Artifacts Reference

| Artifact | Status | Commit |
|----------|--------|--------|
| `scripts/run_judge_fpr_gptoss.py` | VERIFIED (393 lines) | Plans 01-02 |
| `tests/test_phase7_judge_fpr.py` | VERIFIED (21 tests, all PASS) | Plan 01 |
| `tests/test_make_results_v7.py` | VERIFIED (9 tests, all PASS) | Plan 01/03 |
| `logs/ablation_table_gptoss_v7.json` | VERIFIED (4 rows, D-02 schema) | Plan 04 — commit 14139d0 |
| `logs/judge_fpr_gptoss_v7.json` | VERIFIED (200 verdicts, D-04 schema) | Plan 04 — commit 14139d0 |
| `logs/judge_fpr_gptoss_v7.json.cache` | VERIFIED | Plan 04 — commit 14139d0 |
| `docs/results/honest_fpr_gptoss_v7.md` | VERIFIED | Plan 04 — commit 14139d0 |
| `docs/results/honest_fpr_gptoss_v7.csv` | VERIFIED | Plan 04 — commit 14139d0 |
| `docs/phase5_honest_fpr.md` (addendum) | VERIFIED — append-only, 10 rows, 30/30 cells | Plan 05 — commit fe09ca3 |
| `scripts/run_judge_fpr.py` (UTF-8 fix) | VERIFIED — line 101 encoding="utf-8" | Plan 01 — commit 3022139 |
| `scripts/make_results.py` (v7 symbols) | VERIFIED — 4 new symbols exposed | Plan 03 |

---

_Initial verification: 2026-05-04 (Plan 06 executor, claude-sonnet-4-6)_
_Re-verification (goal-backward): 2026-05-04 (gsd-verifier, claude-sonnet-4-6)_
_Verifier: Claude (gsd-verifier)_
