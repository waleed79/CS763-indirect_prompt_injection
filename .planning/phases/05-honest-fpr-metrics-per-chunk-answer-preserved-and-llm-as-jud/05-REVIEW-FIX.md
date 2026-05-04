---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
fixed_at: 2026-05-04T01:30:00Z
review_path: .planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-REVIEW.md
iteration: 2
findings_in_scope: 11
fixed: 11
skipped: 0
status: all_fixed
---

# Phase 05: Code Review Fix Report

**Fixed at:** 2026-05-04T01:30:00Z
**Source review:** `.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-REVIEW.md`
**Iteration:** 2 (cumulative — supersedes iteration 1)

**Summary:**
- Findings in scope: 11 (CR-01, WR-01..WR-07, IN-01, IN-02, IN-03)
- Fixed: 11
- Skipped: 0

Iteration 1 fixed the 8 Critical/Warning findings across 3 commits. Iteration 2
fixed the 3 remaining Info findings across 3 additional commits. Production
artifact `logs/ablation_table.json` was preserved bit-for-bit
(md5 `d66791c9b1bf836e5f72402989c06597` before iteration 1 and after every
commit in iteration 2).

## Fixed Issues

### CR-01: `_build_ablation_table.py` executes at import time — writes files, prints stdout

**Files modified:** `scripts/_build_ablation_table.py`
**Commit:** `435d8a5` (iteration 1)
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
**Commit:** `435d8a5` (iteration 1, folded into the CR-01 commit since both touch
the same file and the same SC-5 logic block)
**Applied fix:** Replaced
`min_signal_asr = min(table[s].get(tier, 1.0) for s in available_signals)` with
an explicit pre-scan that detects any signal row missing the tier key. When a
signal is missing, the comparison for that tier is skipped with a clear
`WARNING: {signal} missing {tier} key — SC-5 comparison skipped for this tier`,
so the SC-5 pass count can no longer be silently inflated by `1.0` defaults.

### WR-01: Windows non-atomic file replacement may corrupt `ablation_table.json`

**Files modified:** `scripts/run_judge_fpr.py`
**Commit:** `8bb606e` (iteration 1)
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
**Commit:** `8bb606e` (iteration 1)
**Applied fix:** Introduced a dedicated `JudgeAuthError(RuntimeError)` exception
class. `judge_one` now `raise JudgeAuthError(...) from exc` on auth/login
failures instead of calling `sys.exit(1)`. Wrapped the per-defense loop in
`main()` with `try: ... except JudgeAuthError as exc: print("FATAL: ..."); return 1`
so the user-facing exit behavior is unchanged but the function is testable and
no longer terminates the entire pytest process when triggered by a unit test.

### WR-03: `judge_one` does not catch `TypeError` from response parsing

**Files modified:** `scripts/run_judge_fpr.py`
**Commit:** `8bb606e` (iteration 1)
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
**Commit:** `8bb606e` (iteration 1)
**Applied fix:** Before each `ablation[key].update({...})` call (both for the
6 defense rows in the loop and the trivial `no_defense` row), check
`if key not in ablation: print("WARNING: ... missing — creating it."); ablation[key] = {}`.
This converts a late-stage `KeyError` after all 7 evaluations have completed
into a recoverable warning, preserving the metrics output. The `atomic_write_json`
helper now also explicitly passes `encoding="utf-8"` on the temp-file write
(folds in IN-02 for this file as a free win, since the helper is touched).

### WR-05: Test hardcodes `50` denominator instead of using `N_CLEAN`

**Files modified:** `tests/test_judge_fpr.py`
**Commit:** `69bf260` (iteration 1)
**Applied fix:** Changed `expected = degraded_count / 50` to
`expected = degraded_count / N_CLEAN` in `test_m3_consistency`, and updated the
assertion-failure message to interpolate `N_CLEAN` instead of literal `50` so
the diagnostic stays consistent. The module already imports `N_CLEAN` from
`run_judge_fpr.py` at line 27 (and the import-failure path also defines a
fallback `N_CLEAN = 50`), so no additional import is needed.

### WR-06: Broad `except Exception` silently hides import errors in test module

**Files modified:** `tests/test_judge_fpr.py`
**Commit:** `69bf260` (iteration 1)
**Applied fix:** Split the single
`except (AttributeError, FileNotFoundError, Exception):` block into two:
the first handler still catches the expected `(AttributeError, FileNotFoundError)`
for the "Plan 02 not yet landed" fallthrough silently; the second handler
catches everything else (`SyntaxError`, `ImportError`, etc.), prints the
traceback via `traceback.print_exc()`, and only then sets `_AVAILABLE = False`.
The misleading "not yet implemented" skip reason is preserved as the default,
but real bugs in `run_judge_fpr.py` will now surface their actual traceback
in the pytest output instead of being swallowed.

### IN-01: Relative paths in fixtures and tests are cwd-sensitive

**Files modified:** `tests/conftest.py`, `tests/test_judge_fpr.py`
**Commit:** `75695b5` (iteration 2)
**Applied fix:** Anchored every `logs/...` path to the repo root via a
`__file__`-derived constant. In `tests/conftest.py` the `ablation_snapshot`
fixture now uses `_REPO_ROOT = Path(__file__).parent.parent` and resolves
`_REPO_ROOT / "logs" / "ablation_table.json"`. In `tests/test_judge_fpr.py`
a module-level `_LOGS_DIR = Path(__file__).parent.parent / "logs"` is now used
by `_load_ablation()`, `_load_verdicts()`, the M1-numerator and M2-le-M1
per-defense log loaders, and the V-06 idempotency test's `ablation_path`.
After the fix, `pytest` invoked from any directory (repo root, `tests/`,
or an out-of-tree CI workdir with `--rootdir`) resolves the same files. No
behavior change — `_load_ablation()` and `_load_verdicts()` still return the
same JSON dicts when pytest runs from the repo root.

### IN-02: `open()` and `write_text()` calls missing explicit `encoding="utf-8"`

**Files modified:** `tests/conftest.py`, `tests/test_judge_fpr.py`
**Commit:** `48e5e5f` (iteration 2)
**Applied fix:** Added `encoding="utf-8"` to the two remaining unencoded
write/read sites: `tests/conftest.py:65` (`cache_path.write_text(...)` in
`frozen_judge_cache`) and `tests/test_judge_fpr.py:168-179` (the V-06 test's
`ablation_path.read_text()`/`write_text(pre)` round-trip used to snapshot and
restore production state). The other IN-02 sites called out in the review
(`scripts/run_judge_fpr.py:135` `atomic_write_json` and
`scripts/_build_ablation_table.py:168` `OUTPUT` open) were already covered
as side effects of the iteration-1 WR-04 and CR-01 commits; verified via
`grep encoding="utf-8"` that no unencoded `write_text(` or `open(` calls
remain in the four files in scope.

### IN-03: `n_pairs` is a redundant variable in `run_for_defense`

**Files modified:** `scripts/run_judge_fpr.py`
**Commit:** `035ffe3` (iteration 2)
**Applied fix:** Removed the `n_pairs = len(off_records)` assignment and
replaced both usages — the `[defense_key] Evaluating {n_pairs} clean queries`
header on line 257 and the per-iteration `[{i+1:02d}/{n_pairs:02d}]` progress
print on line 264 — with the imported `N_CLEAN` constant. `load_clean_records`
already asserts exactly `N_CLEAN` entries, so this is a noop in behavior
(value is identical) but removes the noise variable. Verified via
`grep n_pairs scripts/run_judge_fpr.py` that no orphan references remain.

## Verification

**Production artifact preserved across both iterations:**
- `logs/ablation_table.json` md5 before iteration 1: `d66791c9b1bf836e5f72402989c06597`
- `logs/ablation_table.json` md5 after iteration 1 (3 commits): `d66791c9b1bf836e5f72402989c06597`
- `logs/ablation_table.json` md5 after iteration 2 (3 more commits): `d66791c9b1bf836e5f72402989c06597`
- Verified by re-running `md5sum` after each commit and after the test run.

**Tier 1 (re-read):** every modified file re-read post-edit; fix text present
and surrounding code intact for all 11 findings.

**Tier 2 (syntax check):** `python -c "import ast; ast.parse(...)"` passed for
every modified Python file in both iterations (`scripts/_build_ablation_table.py`,
`scripts/run_judge_fpr.py`, `tests/conftest.py`, `tests/test_judge_fpr.py`).
For `_build_ablation_table.py` the additional import probe via
`importlib.util.spec_from_file_location + exec_module` confirmed zero
side effects on import (CR-01 acceptance criterion).

**Test suite (`pytest tests/test_judge_fpr.py -q -o addopts=`) after iteration 2:**
- 8 of 9 tests pass: V-01 (no_defense_zero), V-02 (m2_le_m1), V-03
  (judge_n_calls_min), V-04 (m1_in_range), V-05 (m1_numerator_bounded),
  V-07 (m3_consistency — exercises the WR-05 fix), V-08 (schema_extension),
  V-09 (back_compat_fpr_unchanged).
- 1 test (V-06, `test_idempotent_with_cache`) fails identically to iteration 1:
  `ERROR: ollama package not found. Install it or use --dry-run.` — pre-existing
  env-only failure, not a regression. The IN-01 path-anchoring change in V-06
  is exercised correctly (`_LOGS_DIR / "ablation_table.json"` resolves and is
  readable); failure happens later in `main()` at the ollama-import gate.
- Comparing pre-iteration-2 vs post-iteration-2 results: same 8 pass / 1 fail,
  identical failure mode. Confirms IN-01/IN-02/IN-03 introduced no regression.

## Commit Map

| Iteration | Commit | Findings | Files |
|-----------|--------|----------|-------|
| 1 | `435d8a5` | CR-01, WR-07 | `scripts/_build_ablation_table.py` |
| 1 | `8bb606e` | WR-01, WR-02, WR-03, WR-04 | `scripts/run_judge_fpr.py` |
| 1 | `69bf260` | WR-05, WR-06 | `tests/test_judge_fpr.py` |
| 2 | `75695b5` | IN-01 | `tests/conftest.py`, `tests/test_judge_fpr.py` |
| 2 | `48e5e5f` | IN-02 | `tests/conftest.py`, `tests/test_judge_fpr.py` |
| 2 | `035ffe3` | IN-03 | `scripts/run_judge_fpr.py` |

---

_Fixed: 2026-05-04T01:30:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 2_
