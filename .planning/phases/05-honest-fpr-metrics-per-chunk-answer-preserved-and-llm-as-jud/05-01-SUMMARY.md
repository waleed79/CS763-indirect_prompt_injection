---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
plan: "01"
subsystem: testing
tags: [testing, scaffolding, pytest, wave-0, fixtures]
dependency_graph:
  requires: []
  provides:
    - tests/conftest.py (ablation_snapshot + frozen_judge_cache fixtures)
    - tests/test_judge_fpr.py (9 Wave-0 stub tests V-01..V-09)
  affects:
    - tests/ (all test files can now use conftest.py fixtures)
tech_stack:
  added: []
  patterns:
    - importlib.util.spec_from_file_location skip-guard (mirrors test_make_results.py:1-26)
    - pytest tmp_path fixture for isolation without mutating real artifacts
key_files:
  created:
    - tests/conftest.py
    - tests/test_judge_fpr.py
  modified: []
decisions:
  - "Module-level pytestmark = skipif(not _AVAILABLE, ...) causes entire file to skip until scripts/run_judge_fpr.py lands in Plan 02"
  - "Broad except (AttributeError, FileNotFoundError, Exception) ensures pytest --collect-only succeeds before production code exists"
  - "_DEFENSE_KEYS list in conftest.py kept in sync manually with DEFENSE_LOG_MAP in run_judge_fpr.py per PATTERNS.md guidance"
metrics:
  duration: "3m 12s"
  completed: "2026-05-04"
  tasks_completed: 2
  files_created: 2
  files_modified: 0
---

# Phase 05 Plan 01: Test Scaffolding Summary

**One-liner:** Wave-0 pytest scaffolding with 9 stub tests (V-01..V-09) gating scripts/run_judge_fpr.py contract, plus ablation_snapshot and frozen_judge_cache fixtures in the repo's first conftest.py.

---

## What Was Built

### 9 Stub Tests Created (tests/test_judge_fpr.py)

All 9 tests SKIP cleanly today because `scripts/run_judge_fpr.py` does not yet exist. After Plan 02 lands the production module, all 9 tests will auto-unmark via `_AVAILABLE` flip.

| V-Tag | Test Method | Class | Behavior |
|-------|-------------|-------|----------|
| V-01 | `test_no_defense_zero` | `TestMetricBounds` | no_defense row has all three new metrics == 0 (D-02 trivial fill) |
| V-02 | `test_m2_le_m1` | `TestMetricBounds` | M2 numerator (chunks_removed>0 AND DEGRADED) <= M1 numerator (chunks_removed>0) |
| V-03 | `test_judge_n_calls_min` | `TestJudgeConsistency` | judge_n_calls >= 50 for each of the 6 defense rows |
| V-04 | `test_m1_in_range` | `TestMetricBounds` | 0.0 <= per_chunk_fpr <= 1.0 for all 6 defense rows |
| V-05 | `test_m1_numerator_bounded` | `TestMetricBounds` | M1 numerator <= TOP_K * N_CLEAN = 250 (sanity bound) |
| V-06 | `test_idempotent_with_cache` | `TestJudgeConsistency` | Re-running main() with frozen_judge_cache produces byte-identical ablation_table.json |
| V-07 | `test_m3_consistency` | `TestJudgeConsistency` | judge_fpr * 50 == count(verdict == "DEGRADED") in logs/judge_fpr_llama.json |
| V-08 | `test_schema_extension` | `TestSchemaExtension` | Each defense row has the 5 new keys; no_defense row also has them (D-02 trivial fill) |
| V-09 | `test_back_compat_fpr_unchanged` | `TestSchemaExtension` | Existing "fpr" key value on every row unchanged after main() runs (back-compat) |

### 2 Fixtures Created (tests/conftest.py)

First conftest.py in the repo (no prior analog; pytest stdlib patterns used).

- **`ablation_snapshot(tmp_path)`** — copies `logs/ablation_table.json` to `tmp_path/ablation_table.json`. Tests can mutate it freely without touching the real artifact. Skips if source file absent. Used by V-09 (back-compat test).

- **`frozen_judge_cache(tmp_path)`** — writes a minimal pre-populated cache JSON to `tmp_path/judge_fpr_llama.json.cache`. 7 defense keys × 50 query indices (indices 50-99), each with `verdict="PRESERVED"`. Ensures V-06 (idempotency test) re-runs main() with zero cloud calls, producing deterministic output for comparison.

---

## Pytest Output Before Plan 02

```
collected 9 items
tests\test_judge_fpr.py sssssssss                [100%]
========================= 9 skipped in 0.08s ==========
```

All 9 tests SKIP with reason: `scripts/run_judge_fpr.py not yet implemented (Phase 5 Plan 02)`.

---

## Importlib Skip-Guard Pattern

The header block in `tests/test_judge_fpr.py` copies the pattern verbatim from `tests/test_make_results.py:1-26` with these substitutions:
- `make_results` -> `run_judge_fpr`
- reason string -> `"scripts/run_judge_fpr.py not yet implemented (Phase 5 Plan 02)"`

Key invariants preserved:
- `importlib.util.spec_from_file_location` (NOT `from scripts.run_judge_fpr import ...` — fragile without `scripts/__init__.py`)
- Module-level `pytestmark = pytest.mark.skipif(not _AVAILABLE, ...)` so the entire file skips as a unit
- Broad `except (AttributeError, FileNotFoundError, Exception)` swallows all import errors during collect-only

---

## Deviations from Plan

None — plan executed exactly as written. Both files match the verbatim code blocks from the PLAN.md action sections.

---

## Self-Check

### Files exist:

- `tests/conftest.py`: FOUND
- `tests/test_judge_fpr.py`: FOUND

### Commits exist:

- `fca3dab`: feat(05-01): add tests/conftest.py — FOUND
- `24ff032`: test(05-01): add tests/test_judge_fpr.py — FOUND

### Test outcomes:

- `pytest tests/test_judge_fpr.py -q` → 9 skipped (as expected pre-Plan-02)
- `pytest tests/ --collect-only -q | grep -i error | wc -l` → 0 (no collection errors)
- `grep -c "@pytest.fixture" tests/conftest.py` → 2
- `grep -c "def test_" tests/test_judge_fpr.py` → 9
- Fixtures importable via importlib: True True

## Self-Check: PASSED
