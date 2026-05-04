---
phase: "07"
plan: "02"
subsystem: scripts
tags: [wave-1, run-judge-fpr-gptoss, importlib-reuse, dry-run, phase7, honest-fpr]
dependency_graph:
  requires:
    - 07-01 (Wave 0 stubs + UTF-8 fix)
    - logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json
    - logs/eval_matrix/gptoss20b_cloud__def02__all_tiers_v6.json
    - logs/eval_matrix/gptoss120b_cloud__fused__all_tiers_v6.json
    - logs/eval_matrix/gptoss120b_cloud__def02__all_tiers_v6.json
    - logs/eval_harness_undefended_gptoss20b_v6.json
    - logs/eval_harness_undefended_gptoss120b_v6.json
  provides:
    - scripts/run_judge_fpr_gptoss.py (Phase 7 entry-point script)
    - tests/test_phase7_judge_fpr.py (updated: 3 test assertions fixed)
  affects:
    - Wave 2 Plan 04 (cloud M3 run consumes this script)
    - logs/ablation_table_gptoss_v7.json (written by Plan 04)
    - logs/judge_fpr_gptoss_v7.json (written by Plan 04)
tech_stack:
  added: []
  patterns:
    - importlib.util.spec_from_file_location reuse (single source of truth)
    - per-cell M1/M2/M3 generalization from Phase 5 per-defense loop
    - atomic_write_json via _phase5 (reused)
    - CELL_LOG_MAP hardcoded path map (D-09)
    - --dry-run zero-cloud-call path with SKIP_DRYRUN sentinel
    - JudgeAuthError try/except returns rc=1 cleanly (WR-02)
key_files:
  created:
    - scripts/run_judge_fpr_gptoss.py
  modified:
    - tests/test_phase7_judge_fpr.py (3 test assertion bug fixes)
decisions:
  - "exec_module creates separate class/string objects per call; identity checks must use _mod._phase5.X not test's separate _phase5.X"
  - "dry-run skips cache write to prevent SKIP_DRYRUN sentinel pollution in shared cache"
  - "TestAuthEscalation uses _mod.JudgeAuthError (not _phase5.JudgeAuthError) to match the except clause's class object"
  - "TestAuthEscalation uses fresh tmp_path cache to ensure no pre-existing entries serve all queries from cache before judge_one is reached"
metrics:
  duration: "14m 37s"
  completed: "2026-05-04"
  tasks: 2
  files: 2
---

# Phase 07 Plan 02: Phase 7 Entry-Point Script (run_judge_fpr_gptoss.py) Summary

Phase 7 entry-point script for computing honest FPR metrics (M1/M2/M3) across 4 cells — {gpt-oss:20b-cloud, gpt-oss:120b-cloud} x {fused, def02} — using importlib reuse of Phase 5 helpers and a per-cell loop generalizing Phase 5's per-defense loop.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Module skeleton, importlib reuse, path maps, argparse + test identity bug fixes | 931f582 | scripts/run_judge_fpr_gptoss.py, tests/test_phase7_judge_fpr.py |
| 2 | Full per-cell loop, main() with --dry-run, atomic writes + test auth/escalation fixes | 4571f4b | tests/test_phase7_judge_fpr.py |
| (Rule 1) | Suppress cache write in --dry-run to prevent SKIP_DRYRUN sentinel pollution | 623561a | scripts/run_judge_fpr_gptoss.py |

## Script Output

**Final line count:** 393 lines

**`python scripts/run_judge_fpr_gptoss.py --dry-run` output (M1 for all 4 cells):**

```
  [(gpt-oss:20b-cloud, fused)] M1=0.0920  M2=0.0000  M3=0.0000  calls=0
[cell] (gpt-oss:20b-cloud, fused): M1=0.0920 M2=0.0000 M3=0.0000 n_calls=0
  [(gpt-oss:20b-cloud, def02)] M1=0.0000  M2=0.0000  M3=0.0000  calls=0
[cell] (gpt-oss:20b-cloud, def02): M1=0.0000 M2=0.0000 M3=0.0000 n_calls=0
  [(gpt-oss:120b-cloud, fused)] M1=0.0920  M2=0.0000  M3=0.0000  calls=0
[cell] (gpt-oss:120b-cloud, fused): M1=0.0920 M2=0.0000 M3=0.0000 n_calls=0
  [(gpt-oss:120b-cloud, def02)] M1=0.0000  M2=0.0000  M3=0.0000  calls=0
[cell] (gpt-oss:120b-cloud, def02): M1=0.0000 M2=0.0000 M3=0.0000 n_calls=0
[dry-run] M1-only summary:
  gptoss20b_cloud__fused: M1=0.0920
  gptoss20b_cloud__def02: M1=0.0000
  gptoss120b_cloud__fused: M1=0.0920
  gptoss120b_cloud__def02: M1=0.0000
[dry-run] Skipping ablation/verdicts write (zero cloud calls made).
```

Note: M1=0.0920 for fused cells (46 total chunks removed across 50 queries / (5 * 50) = 9.2% per-chunk FPR). M1=0.0000 for def02 cells (zero chunks removed by def02 defense on these clean queries).

## Test Pass/SKIP Table (tests/test_phase7_judge_fpr.py)

| P7-ID | Class | Status |
|-------|-------|--------|
| P7-M1 | TestM1Numerator::test_m1_formula | PASS |
| P7-M1 | TestM1Numerator::test_m1_in_range | SKIP (pending Plan 04 output) |
| P7-M2 | TestM2Aggregation::test_m2_formula | PASS |
| P7-M3 | TestM3Aggregation::test_m3_formula | PASS |
| P7-M3 | TestM3Aggregation::test_tie_collapses_to_preserved | PASS |
| P7-LCR | TestLoadCleanRecordsV6::test_load_returns_50_records | PASS |
| P7-UTF | TestUtf8Encoding::test_no_unicode_error | PASS |
| P7-PATH | TestPathMapsLoudFail::test_cell_log_map_paths_exist | PASS |
| P7-PATH | TestPathMapsLoudFail::test_off_log_map_paths_exist | PASS |
| P7-CKEY | TestCompositeKeys::test_composite_key_set | PASS |
| P7-OUT-J-SHAPE | TestAblationV7Shape::test_exactly_four_rows | SKIP (pending Plan 04) |
| P7-OUT-J-SHAPE | TestAblationV7Shape::test_each_row_has_required_keys | SKIP (pending Plan 04) |
| P7-OUT-J-NOROW | TestNoTrivialRow::test_no_defense_absent | SKIP (pending Plan 04) |
| P7-OUT-V-SHAPE | TestVerdictsV7Shape::test_verdicts_nested_two_levels | SKIP (pending Plan 04) |
| P7-OUT-V-COUNT | TestVerdictCount200::test_total_verdict_count | SKIP (pending Plan 04) |
| P7-OUT-V-FIELDS | TestVerdictRecordFields::test_verdict_record_has_required_fields | SKIP (pending Plan 04) |
| P7-INHERIT-PROMPT | TestPromptInherited::test_prompt_is_same_object | PASS |
| P7-INHERIT-PARSE | TestParserInherited::test_parse_verdict_is_same_object | PASS |
| P7-CACHE | TestCacheResume::test_dry_run_skips_calls | PASS |
| P7-DRYRUN | TestDryRunNoCloud::test_dry_run_no_cloud | PASS |
| P7-AUTH | TestAuthEscalation::test_auth_error_returns_rc1 | PASS |

**Total: 14 PASS, 7 SKIP (all SKIP pending Plan 04 cloud-run output artifacts)**

## Phase 5/6 Regression Status

| Suite | Result |
|-------|--------|
| tests/test_judge_fpr.py | 8/9 PASS — 1 pre-existing failure (test_idempotent_with_cache; ollama absent) |
| tests/test_make_results.py | 4/4 PASS |
| tests/test_make_results_v6.py | 6/6 PASS |

No files from Phase 5 or Phase 6 were modified by this plan.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] TestPromptInherited and TestParserInherited: is-identity check cannot hold across two separate exec_module() calls**
- **Found during:** Task 1 verification
- **Issue:** The tests asserted `_mod.JUDGE_SYSTEM_PROMPT is _phase5.JUDGE_SYSTEM_PROMPT` where `_phase5` was the test file's own `exec_module()` instance. Two separate `exec_module()` calls on the same source file produce separate string and function objects — Python does NOT intern 201-char strings across separately-compiled bytecode modules. The assertion could never pass regardless of script design.
- **Fix:** Changed assertions to `_mod.X is _mod._phase5.X` — proves no local redefinition inside `run_judge_fpr_gptoss.py` (the intended invariant: detect copy-paste vs. importlib reuse). Intent fully preserved.
- **Files modified:** tests/test_phase7_judge_fpr.py
- **Commit:** 931f582

**2. [Rule 1 - Bug] TestAuthEscalation: main() returned rc=2 (ollama unavailable) instead of rc=1 (JudgeAuthError)**
- **Found during:** Task 2 verification
- **Issue:** The test called `main([])` without mocking `_OLLAMA_AVAILABLE`. Since ollama is not installed in the Python 3.13 test environment, `main()` returned rc=2 before ever reaching the `run_for_cell` call where `JudgeAuthError` would be raised.
- **Fix:** Added `monkeypatch.setattr(_mod, "_OLLAMA_AVAILABLE", True)` and `monkeypatch.setattr(_mod, "Client", _DummyClient)` to bypass the ollama guard.
- **Files modified:** tests/test_phase7_judge_fpr.py
- **Commit:** 4571f4b

**3. [Rule 1 - Bug] TestAuthEscalation: raised _phase5.JudgeAuthError not caught by main()'s except JudgeAuthError**
- **Found during:** Task 2 verification (after Bug 2 was fixed)
- **Issue:** The test raised `_phase5.JudgeAuthError` (test's exec_module instance), but `main()`'s `except JudgeAuthError` catches `_mod.JudgeAuthError` (the mod's exec_module instance). Two separate `exec_module()` calls produce different class objects; Python's exception matching uses `isinstance()` which requires the class hierarchy to match.
- **Fix:** Changed `JudgeAuthError = _phase5.JudgeAuthError` to `JudgeAuthError = _mod.JudgeAuthError` in the test.
- **Files modified:** tests/test_phase7_judge_fpr.py
- **Commit:** 4571f4b

**4. [Rule 1 - Bug] TestAuthEscalation: pre-existing cache with SKIP_DRYRUN entries caused rc=0 (all queries served from cache)**
- **Found during:** Task 2 verification (after Bugs 2 and 3 were fixed)
- **Issue:** A cache file from a prior dry-run test had SKIP_DRYRUN entries for all 200 queries. When the auth test ran, all queries were served from cache and `judge_one` was never called, so `JudgeAuthError` was never raised, and `main()` returned rc=0 instead of rc=1.
- **Fix:** (a) Added `tmp_path` parameter to test; test now uses a fresh empty cache path. (b) Also fixed the script to skip cache writes in `--dry-run` mode to prevent future SKIP_DRYRUN sentinel pollution of the shared cache.
- **Files modified:** tests/test_phase7_judge_fpr.py, scripts/run_judge_fpr_gptoss.py
- **Commit:** 4571f4b (test fix), 623561a (script fix)

## Known Stubs

None. The script is fully implemented and the tests that SKIP do so because they depend on Plan 04's cloud-run output artifacts (`logs/ablation_table_gptoss_v7.json`, `logs/judge_fpr_gptoss_v7.json`), not because of placeholder code.

## Threat Flags

No new network endpoints introduced by this plan. The script's cloud-call path (M3 via `judge_one`) was already analyzed in the plan's `<threat_model>` (T-7-01, T-7-02, T-7-03). The dry-run path (this plan's scope) makes zero network calls. No new trust boundary surfaces.

## Self-Check: PASSED

- [x] `scripts/run_judge_fpr_gptoss.py` exists with 393 lines
- [x] `grep -c CELL_LOG_MAP scripts/run_judge_fpr_gptoss.py` = 5 (>= 3 required)
- [x] `grep -c spec_from_file_location scripts/run_judge_fpr_gptoss.py` = 1
- [x] `grep -c "_phase5\." scripts/run_judge_fpr_gptoss.py` = 11 (>= 1 required)
- [x] `grep -c "m1 = m1_numerator / (TOP_K \* N_CLEAN)" scripts/run_judge_fpr_gptoss.py` = 1
- [x] `grep -cE "no_defense|D-03 violation" scripts/run_judge_fpr_gptoss.py` = 2
- [x] Commit 931f582 exists (Task 1: skeleton)
- [x] Commit 4571f4b exists (Task 2: test fixes)
- [x] Commit 623561a exists (dry-run cache fix)
- [x] 14 tests PASS, 7 SKIP in tests/test_phase7_judge_fpr.py
- [x] No Phase 5/6 files modified (pre-existing test_idempotent_with_cache failure unchanged)
- [x] `python scripts/run_judge_fpr_gptoss.py --dry-run` exits 0 with M1 numbers for all 4 cells
- [x] `python scripts/run_judge_fpr_gptoss.py --dry-run` does NOT write logs/ablation_table_gptoss_v7.json
- [x] `python scripts/run_judge_fpr_gptoss.py --dry-run` does NOT write logs/judge_fpr_gptoss_v7.json.cache
