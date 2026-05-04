---
phase: "07"
plan: "01"
subsystem: test-stubs
tags: [wave-0, test-stubs, utf8-fix, phase7, judge-fpr, make-results]
dependency_graph:
  requires: []
  provides:
    - tests/test_phase7_judge_fpr.py
    - tests/test_make_results_v7.py
    - scripts/run_judge_fpr.py (utf-8 encoding fix)
  affects:
    - Wave 1 production code in scripts/run_judge_fpr_gptoss.py
    - Wave 1 production code in scripts/make_results.py
tech_stack:
  added: []
  patterns:
    - importlib.util.spec_from_file_location skip-guard (Phase 03.4-01 lineage)
    - pytestmark module-level skipif
    - _SKIP_V7 per-method mark sentinel
key_files:
  created:
    - tests/test_phase7_judge_fpr.py
    - tests/test_make_results_v7.py
  modified:
    - scripts/run_judge_fpr.py
decisions:
  - "Phase 5 load_clean_records read_text hardened with encoding='utf-8' (one-line fix at line 101) to prevent cp1252 UnicodeDecodeError on Windows for v6 cells with smart quotes / non-ASCII answer chars"
  - "test_phase7_judge_fpr.py uses double importlib load: _phase5 for inheritance identity checks (P7-INHERIT-PROMPT/PARSE) and _mod for the Phase 7 module itself"
  - "test_idempotent_with_cache in tests/test_judge_fpr.py already failed pre-change (ollama package unavailable); documented as pre-existing, not introduced by this plan"
  - "Full-suite pytest --collect-only INTERNALERROR traced to tests/test_judge_per_tier.py bare module-level 'from scripts.run_judge import' (pre-existing, out-of-scope for Plan 01)"
metrics:
  duration: "6m 16s"
  completed: "2026-05-04"
  tasks: 3
  files: 3
---

# Phase 07 Plan 01: Wave 0 Test Stubs + UTF-8 Hardening Summary

Wave 0 test stubs establishing the 24 P7-* validation contract for Phase 7 (gpt-oss honest-FPR extension), plus one-line UTF-8 encoding fix on Phase 5's `load_clean_records` to prevent Windows cp1252 crashes on v6 cells.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | UTF-8 fix to scripts/run_judge_fpr.py:101 | 3022139 | scripts/run_judge_fpr.py |
| 2 | Create tests/test_phase7_judge_fpr.py with 17 P7-* stubs | 10a201a | tests/test_phase7_judge_fpr.py |
| 3 | Create tests/test_make_results_v7.py with 7 P7-RESV/DOC stubs | 463dee0 | tests/test_make_results_v7.py |

## Test-Class Counts

| File | Classes | Tests Collected | Status |
|------|---------|-----------------|--------|
| tests/test_phase7_judge_fpr.py | 17 | 21 | All SKIP (importlib skip-guard active) |
| tests/test_make_results_v7.py | 7 | 9 | 7 SKIP, 2 PASS (compat + phase3-unchanged) |
| **Total** | **24** | **30** | **0 FAIL, 0 ERROR** |

## P7-* ID Mapping

| P7-ID | Class | File |
|-------|-------|------|
| P7-M1 | TestM1Numerator | test_phase7_judge_fpr.py |
| P7-M2 | TestM2Aggregation | test_phase7_judge_fpr.py |
| P7-M3 | TestM3Aggregation | test_phase7_judge_fpr.py |
| P7-LCR | TestLoadCleanRecordsV6 | test_phase7_judge_fpr.py |
| P7-UTF | TestUtf8Encoding | test_phase7_judge_fpr.py |
| P7-PATH | TestPathMapsLoudFail | test_phase7_judge_fpr.py |
| P7-CKEY | TestCompositeKeys | test_phase7_judge_fpr.py |
| P7-OUT-J-SHAPE | TestAblationV7Shape | test_phase7_judge_fpr.py |
| P7-OUT-J-NOROW | TestNoTrivialRow | test_phase7_judge_fpr.py |
| P7-OUT-V-SHAPE | TestVerdictsV7Shape | test_phase7_judge_fpr.py |
| P7-OUT-V-COUNT | TestVerdictCount200 | test_phase7_judge_fpr.py |
| P7-OUT-V-FIELDS | TestVerdictRecordFields | test_phase7_judge_fpr.py |
| P7-INHERIT-PROMPT | TestPromptInherited | test_phase7_judge_fpr.py |
| P7-INHERIT-PARSE | TestParserInherited | test_phase7_judge_fpr.py |
| P7-CACHE | TestCacheResume | test_phase7_judge_fpr.py |
| P7-DRYRUN | TestDryRunNoCloud | test_phase7_judge_fpr.py |
| P7-AUTH | TestAuthEscalation | test_phase7_judge_fpr.py |
| P7-RESV | TestV7Resolver | test_make_results_v7.py |
| P7-RESV-EMIT | TestV7Emit | test_make_results_v7.py |
| P7-RESV-COMPAT | TestV7Compat | test_make_results_v7.py |
| P7-DOC-UNTOUCHED | TestPhase5ProseUntouched | test_make_results_v7.py |
| P7-DOC-ADDENDUM | TestAddendumPresent | test_make_results_v7.py |
| P7-DOC-TABLE-10ROW | TestAddendumTable10Rows | test_make_results_v7.py |
| P7-DOC-PHASE3-UNTOUCHED | TestPhase34NotEdited | test_make_results_v7.py |

All 24 P7-* IDs from 07-VALIDATION.md are covered.

## UTF-8 Fix

```
git diff --stat scripts/run_judge_fpr.py (HEAD~3..HEAD):
 scripts/run_judge_fpr.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

Line 101 changed from:
```python
data = json.loads(Path(log_path).read_text())
```
to:
```python
data = json.loads(Path(log_path).read_text(encoding="utf-8"))
```

## Phase 5 + Phase 6 Regression Status

| Suite | Result |
|-------|--------|
| tests/test_judge_fpr.py | 8/9 PASS — 1 pre-existing failure (test_idempotent_with_cache requires ollama package, unavailable) |
| tests/test_make_results.py | 4/4 PASS |
| tests/test_make_results_v6.py | 6/6 PASS |

The `test_idempotent_with_cache` failure in `tests/test_judge_fpr.py` is pre-existing (present before this plan, caused by `ollama` package not installed in the Python 3.13 environment). Not introduced by this plan.

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

### Out-of-Scope Issues Observed (logged, not fixed)

**Pre-existing: full-suite INTERNALERROR during pytest --collect-only**
- **Found during:** Task 3 verification
- **Cause:** `tests/test_judge_per_tier.py` uses bare `from scripts.run_judge import ...` at module level; `scripts/run_judge.py` imports `ollama` which is absent in Python 3.13 env → pytest INTERNALERROR
- **Status:** Pre-existing before Plan 01. Out of scope (different file, different phase). Logged to deferred items.
- **Fix:** Upgrade `tests/test_judge_per_tier.py` to use importlib skip-guard pattern (Phase 03.4-01 lineage).

## Known Stubs

All test stubs SKIP appropriately — no data is fabricated or silently missing. The skip conditions are explicit and tied to file existence or `_AVAILABLE` sentinel. No Wave 0 stub prevents the plan's goal (establishing the validation contract).

## Threat Flags

No new network endpoints, auth paths, or file access patterns introduced. Wave 0 is test-only code plus a single encoding-parameter change. No new trust boundary surfaces.

## Self-Check: PASSED

- [x] tests/test_phase7_judge_fpr.py exists and has 17 classes
- [x] tests/test_make_results_v7.py exists and has 7 classes
- [x] scripts/run_judge_fpr.py line 101 contains `encoding="utf-8"`
- [x] Commit 3022139 exists (UTF-8 fix)
- [x] Commit 10a201a exists (Phase 7 judge-FPR stubs)
- [x] Commit 463dee0 exists (Phase 7 make_results v7 stubs)
