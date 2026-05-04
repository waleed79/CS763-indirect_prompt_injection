---
phase: "06"
plan: "01"
subsystem: test-stubs
tags: [wave-0, pytest, stubs, phase6, p6-pre, p6-run, p6-pro, p6-def, p6-mtx, p6-auth, p6-err, p6-enc, p6-res-pr, p6-md, p6-csv]
dependency_graph:
  requires: []
  provides:
    - tests/test_phase6_eval.py (Wave 0 stub — 12 classes covering P6-PRE through P6-ENC)
    - tests/test_make_results_v6.py (Wave 0 stub — 3 classes covering P6-RES-PR, P6-MD, P6-CSV)
  affects:
    - scripts/run_phase6_eval.py (Wave 1 target — must expose main(), passes TestEncodingExplicit)
    - scripts/make_results.py (Wave 3 target — must expose PHASE6_DISCLOSURE or _resolve_v6_path)
tech_stack:
  added: [pytest-timeout]
  patterns:
    - importlib.util.spec_from_file_location with try/except (AttributeError, FileNotFoundError) + traceback fallback
    - _AVAILABLE flag + pytestmark.skipif for module-level gating
    - _V6_AVAILABLE flag + _SKIP_V6 decorator for feature-level gating on already-importable modules
    - pytest.skip() with explicit reason inside test body for runtime-condition stubs
key_files:
  created:
    - tests/test_phase6_eval.py
    - tests/test_make_results_v6.py
  modified: []
decisions:
  - "_V6_AVAILABLE flag added to test_make_results_v6.py because make_results.py already exists from Phase 3.4, so module-level pytestmark.skipif(_AVAILABLE) would not gate the v6 tests; Wave 3 unlocks by exposing PHASE6_DISCLOSURE or _resolve_v6_path constant"
metrics:
  duration: "5m 0s"
  completed: "2026-05-04T07:08:37Z"
  tasks_completed: 2
  files_created: 2
  files_modified: 0
---

# Phase 06 Plan 01: Wave 0 Test Stub Creation Summary

Wave 0 pytest stub scaffolding for Phase 6 — two new test files (15 test classes total, 18 test methods) that lock the verification contract before Wave 1+ production code lands. All 18 tests skip cleanly; zero failures.

## What Was Built

Two test files were created as pytest stubs:

**`tests/test_phase6_eval.py`** — 12 stub classes mapping 1:1 to P6-* requirements:

| Class | Requirement | Skip Condition |
|---|---|---|
| TestSanityAssert | P6-PRE | pytestmark (run_phase6_eval.py absent) |
| TestUndefendedRuns20b | P6-RUN-20b-UND | log file absent |
| TestUndefendedRuns120b | P6-RUN-120b-UND | log file absent |
| TestProvenanceFields | P6-PRO | log file absent |
| TestDefendedRuns | P6-DEF | defended cell absent |
| TestMatrixSummary | P6-MTX | summary_v6.json absent |
| TestD12FusedV6 | P6-D12-FUSED | figure file absent |
| TestD12UndefendedV6 | P6-D12-UND | figure file absent |
| TestD03V6 | P6-D03 | figure file absent |
| TestPreflightCloudAuth | P6-AUTH | pytest.skip() in body |
| TestErrorPolicy | P6-ERR | pytest.skip() in body |
| TestEncodingExplicit | P6-ENC | skips if run_phase6_eval.py absent |

**`tests/test_make_results_v6.py`** — 3 stub classes for make_results.py Phase 6 extensions:

| Class | Requirement | Skip Condition |
|---|---|---|
| TestPathResolver | P6-RES-PR | _V6_AVAILABLE flag (Wave 3 symbol absent) |
| TestMarkdownDisclosure | P6-MD | _V6_AVAILABLE flag (Wave 3 symbol absent) |
| TestCsvCompanions | P6-CSV | _V6_AVAILABLE flag (Wave 3 symbol absent) |

## Verification Results

```
pytest --collect-only tests/test_phase6_eval.py tests/test_make_results_v6.py
=> 18 tests collected in 0.86s

pytest tests/test_phase6_eval.py tests/test_make_results_v6.py -v
=> 18 skipped in 0.91s  (0 failed, 0 errors)
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added _V6_AVAILABLE two-level guard to test_make_results_v6.py**

- **Found during:** Task 2 verification
- **Issue:** `make_results.py` already exists from Phase 3.4, so `_AVAILABLE=True` and the module-level `pytestmark.skipif(not _AVAILABLE)` did not protect the v6 test methods. All 6 v6 tests ran against the pre-Wave-3 `make_results.py` and FAILED (missing v6 features: resolver, disclosure header, CSV companions).
- **Fix:** Added `_V6_AVAILABLE` flag (checked via `hasattr(_mod, "PHASE6_DISCLOSURE") or hasattr(_mod, "_resolve_v6_path")`) plus a `_SKIP_V6` decorator applied to every test method. Wave 3 unlocks by exposing either symbol.
- **Files modified:** `tests/test_make_results_v6.py`
- **Commit:** 8938787

**2. [Rule 3 - Blocking] Installed pytest-timeout**

- **Found during:** Task 1 verification
- **Issue:** `pytest.ini` has `addopts = --timeout=60` but `pytest-timeout` was not installed. `pytest --collect-only` exited with error "unrecognized arguments: --timeout=60".
- **Fix:** `pip install pytest-timeout` (non-breaking; no code change).
- **Commit:** N/A (environment fix, no file change)

### Out-of-Scope Pre-existing Issues (deferred)

- `tests/test_make_results.py` fails with `ImportError: Missing optional dependency 'tabulate'` — pre-existing from Phase 3.4 (`tabulate` was not installed in the test environment). Fixed in passing by installing `tabulate` (same `pip install` session as pytest-timeout). Not caused by this plan's changes.

## Known Stubs

All test methods in both files are intentional stubs. The following methods use `pytest.skip()` in their body rather than a decorator (they test runtime behavior that cannot be mocked at import time):

- `TestSanityAssert.test_missing_tier_range_raises` — needs chromadb mock
- `TestPreflightCloudAuth.test_ollama_list_contains_gptoss_models` — run-time only check
- `TestErrorPolicy.test_error_policy_increments_count` — needs failure path simulation

These are expected. They will be activated when Wave 1 production code lands.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Test files write only to `pytest`'s `tmp_path` fixture tree (auto-cleaned). No threat flags.

## Self-Check

```
[ -f "tests/test_phase6_eval.py" ] => FOUND
[ -f "tests/test_make_results_v6.py" ] => FOUND
git log --oneline includes 2ce5ba3 => FOUND
git log --oneline includes 6deccad => FOUND
git log --oneline includes 8938787 => FOUND
```

## Self-Check: PASSED
