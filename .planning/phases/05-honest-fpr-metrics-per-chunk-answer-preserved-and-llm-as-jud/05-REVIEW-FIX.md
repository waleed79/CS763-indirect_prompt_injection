---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
fixed_at: 2026-05-04T00:45:00Z
review_path: .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 05: Code Review Fix Report

**Fixed at:** 2026-05-04T00:45:00Z
**Source review:** `.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 8 (CR-01, WR-01..WR-07)
- Fixed: 8
- Skipped: 0
- Out of scope (Info — not in this pass): IN-01, IN-02, IN-03

The 8 in-scope findings were applied across 3 atomic commits, grouped by file
to keep each commit self-contained and bisectable. Production artifact
`logs/ablation_table.json` was preserved bit-for-bit
(md5 `d66791c9b1bf836e5f72402989c06597` before and after every fix).

## Fixed Issues

### CR-01: `_build_ablation_table.py` executes at import time — writes files, prints stdout

**Files modified:** `scripts/_build_ablation_table.py`
**Commit:** `435d8a5`
**Applied fix:** Wrapped all module-level file I/O and stdout in
`if __name__ == "__main__":` via two new helpers, `_build_table()` (pure dict
construction from per-defense logs) and `_print_summary(table)` (stdout-only
SC-5/D-17/D-08 verifications). Also added `encoding="utf-8"` to the
`json.dump(open(OUTPUT, "w"))` call (folds in IN-02 for this file as a
free win, since the rewrite touches that line). After the edit,
`importlib.util.spec_from_file_location` followed by `exec_module` produces no
file write to `logs/ablation_table.json` and no stdout — confirmed via the Tier 2
import probe and `md5sum` re-check.

### WR-07: SC-5 verification defaults missing ASR keys to `1.0`, masking data gaps

**Files modified:** `scripts/_build_ablation_table.py`
**Commit:** `435d8a5` (folded into the CR-01 commit since both touch the
same file and the same SC-5 logic block)
**Applied fix:** Replaced
`min_signal_asr = min(table[s].get(tier, 1.0) for s in available_signals)` with
an explicit pre-scan that detects any signal row missing the tier key. When a
signal is missing, the comparison for that tier is skipped with a clear
`WARNING: {signal} missing {tier} key — SC-5 comparison skipped for this tier`,
so the SC-5 pass count can no longer be silently inflated by `1.0` defaults.

### WR-01: Windows non-atomic file replacement may corrupt `ablation_table.json`

**Files modified:** `scripts/run_judge_fpr.py`
**Commit:** `8bb606e`
**Applied fix:** Adopted the stronger fix from the review's "as a stronger fix"
branch — accumulate per-defense `(m1, m2, m3, n_calls)` tuples in
`accumulated_metrics: dict` inside the loop, then do a single
read-modify-`atomic_write_json` of `ablation_table.json` once at the end (after
adding the `no_defense` row). Cuts the corruption window on Windows from ~8
non-atomic replaces down to 1, and as a bonus removes the duplicated tmp+replace
boilerplate. The cache file (`logs/judge_fpr_llama.json.cache`) is still written
inside the loop because it is a recoverable derived artifact and preserves the
checkpoint-resume semantics required by V-06. Also added a try/except around
the ablation-file read to give an informative error if the base table is missing.

### WR-02: `sys.exit(1)` called inside library function `judge_one`

**Files modified:** `scripts/run_judge_fpr.py`
**Commit:** `8bb606e`
**Applied fix:** Introduced a dedicated `JudgeAuthError(RuntimeError)` exception
class. `judge_one` now `raise JudgeAuthError(...) from exc` on auth/login
failures instead of calling `sys.exit(1)`. Wrapped the per-defense loop in
`main()` with `try: ... except JudgeAuthError as exc: print("FATAL: ..."); return 1`
so the user-facing exit behavior is unchanged but the function is testable and
no longer terminates the entire pytest process when triggered by a unit test.

### WR-03: `judge_one` does not catch `TypeError` from response parsing

**Files modified:** `scripts/run_judge_fpr.py`
**Commit:** `8bb606e`
**Applied fix:** Wrapped the `resp.message`/`resp["message"]` plus
`.content`/`["content"]` parsing in its own
`try: ... except (AttributeError, KeyError, TypeError) as parse_exc:` that
prints `[ERROR] Unexpected response shape from judge model: ...`, sleeps the
configured delay (matching the call-failure branch above), and returns
`(None, "", str(parse_exc))`. The existing D-12 retry-once path already handles
`verdict is None`, so this slots in cleanly: a malformed response triggers one
retry, and if that also fails, the conservative PRESERVED default kicks in
instead of crashing the entire 7-defense run after hours of judge calls.

### WR-04: `no_defense` key access without existence check

**Files modified:** `scripts/run_judge_fpr.py`
**Commit:** `8bb606e`
**Applied fix:** Before each `ablation[key].update({...})` call (both for the
6 defense rows in the loop and the trivial `no_defense` row), check
`if key not in ablation: print("WARNING: ... missing — creating it."); ablation[key] = {}`.
This converts a late-stage `KeyError` after all 7 evaluations have completed
into a recoverable warning, preserving the metrics output. The `atomic_write_json`
helper now also explicitly passes `encoding="utf-8"` on the temp-file write
(folds in IN-02 for this file as a free win, since the helper is touched).

### WR-05: Test hardcodes `50` denominator instead of using `N_CLEAN`

**Files modified:** `tests/test_judge_fpr.py`
**Commit:** `69bf260`
**Applied fix:** Changed `expected = degraded_count / 50` to
`expected = degraded_count / N_CLEAN` in `test_m3_consistency`, and updated the
assertion-failure message to interpolate `N_CLEAN` instead of literal `50` so
the diagnostic stays consistent. The module already imports `N_CLEAN` from
`run_judge_fpr.py` at line 27 (and the import-failure path also defines a
fallback `N_CLEAN = 50`), so no additional import is needed.

### WR-06: Broad `except Exception` silently hides import errors in test module

**Files modified:** `tests/test_judge_fpr.py`
**Commit:** `69bf260`
**Applied fix:** Split the single
`except (AttributeError, FileNotFoundError, Exception):` block into two:
the first handler still catches the expected `(AttributeError, FileNotFoundError)`
for the "Plan 02 not yet landed" fallthrough silently; the second handler
catches everything else (`SyntaxError`, `ImportError`, etc.), prints the
traceback via `traceback.print_exc()`, and only then sets `_AVAILABLE = False`.
The misleading "not yet implemented" skip reason is preserved as the default,
but real bugs in `run_judge_fpr.py` will now surface their actual traceback
in the pytest output instead of being swallowed.

## Verification

**Production artifact preserved:**
- `logs/ablation_table.json` md5 before fixes: `d66791c9b1bf836e5f72402989c06597`
- `logs/ablation_table.json` md5 after all 3 commits: `d66791c9b1bf836e5f72402989c06597`
- Verified by re-running `md5sum` after each commit and after the test run.

**Tier 1 (re-read):** all 4 modified files re-read post-edit; fix text present
and surrounding code intact.

**Tier 2 (syntax check):** `python -c "import ast; ast.parse(...)"` passed for
all 3 modified Python files (`scripts/_build_ablation_table.py`,
`scripts/run_judge_fpr.py`, `tests/test_judge_fpr.py`). For
`_build_ablation_table.py` the additional import probe via
`importlib.util.spec_from_file_location + exec_module` confirmed zero
side effects on import (CR-01 acceptance criterion). For `run_judge_fpr.py`
the same probe confirmed `JudgeAuthError` is exposed and is a
`RuntimeError` subclass.

**Test suite (`pytest tests/test_judge_fpr.py -x -q -o addopts=`):**
- 8 of 9 tests pass: V-01 (no_defense_zero), V-02 (m2_le_m1), V-03
  (judge_n_calls_min), V-04 (m1_in_range), V-05 (m1_numerator_bounded),
  V-07 (m3_consistency — exercises the WR-05 fix), V-08 (schema_extension),
  V-09 (back_compat_fpr_unchanged).
- 1 test (V-06, `test_idempotent_with_cache`) fails with
  `ERROR: ollama package not found. Install it or use --dry-run.` — this is
  a pre-existing environment-only failure: the `ollama` Python package is not
  installed in the current venv (`python -c "import ollama"` raises
  `ModuleNotFoundError`), and the test calls live `main()` which short-circuits
  at the `if not _OLLAMA_AVAILABLE: return 1` check on line 401 (a code path
  that pre-dates this review pass and was NOT touched by any of the 8 fixes).
  V-06 will pass on the dev box where ollama is installed.

## Out of Scope (deferred to a future pass)

The following Info findings from the review were intentionally not fixed in
this pass (`fix_scope: critical_warning`):

- **IN-01:** cwd-sensitive relative paths in fixtures and tests
- **IN-02:** missing `encoding="utf-8"` on remaining `open()` / `write_text()` calls
  (NOTE: partially addressed as side effects of CR-01 in
  `_build_ablation_table.py` and WR-04 in `run_judge_fpr.py:atomic_write_json`,
  but `tests/conftest.py:60` and any other untouched call sites remain.)
- **IN-03:** redundant `n_pairs` variable in `run_for_defense`

---

_Fixed: 2026-05-04T00:45:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
