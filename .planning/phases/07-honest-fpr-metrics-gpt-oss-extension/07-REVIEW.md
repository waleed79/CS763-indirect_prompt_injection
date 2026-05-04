---
phase: 07-honest-fpr-metrics-gpt-oss-extension
reviewed: 2026-05-04T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - scripts/run_judge_fpr.py
  - scripts/run_judge_fpr_gptoss.py
  - scripts/make_results.py
  - scripts/_verify_fidelity.py
  - scripts/_verify_prose.py
  - tests/test_phase7_judge_fpr.py
  - tests/test_make_results_v7.py
  - docs/phase5_honest_fpr.md
findings:
  critical: 0
  warning: 5
  info: 6
  total: 11
status: issues_found
---

# Phase 07: Code Review Report

**Reviewed:** 2026-05-04T00:00:00Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed 8 files covering the Phase 7 honest-FPR gpt-oss extension: two judge-evaluation scripts, a results-table emitter, two audit scripts, two test modules, and the living-document addendum. The codebase is well-structured with good error-handling patterns — defensive JSON reads, atomic writes, and explicit exit-code contracts. No security vulnerabilities or data-loss risks were found.

Five warnings were identified: a silent `MAX_RETRIES` fallback that always evaluates to 1 regardless of Phase 5 intent; a `str(ablation_v7)` serialization check that can produce false negatives for key-name assertions; client instantiation inconsistency between Phase 5 and Phase 7 (host argument omitted); uncaught `subprocess.CalledProcessError` in `_verify_prose.py`; and leaked file handles in `_verify_fidelity.py`. Six informational items cover documentation gaps, a dead import, a missing missing-input return code in Phase 7, and a slightly fragile regex in the fidelity checker.

## Warnings

### WR-01: `MAX_RETRIES` silent fallback always evaluates to 1

**File:** `scripts/run_judge_fpr_gptoss.py:41`

**Issue:** Line 41 reads:
```python
MAX_RETRIES = _phase5.MAX_RETRIES if hasattr(_phase5, "MAX_RETRIES") else 1
```
`MAX_RETRIES` does not exist in `run_judge_fpr.py` (confirmed by grep — Phase 5 hardcodes the single-retry logic inline at lines 295-305). The `hasattr` guard always evaluates to the fallback `1`. `MAX_RETRIES` is also never consumed anywhere in `run_judge_fpr_gptoss.py` — the retry loop in `run_for_cell` (lines 175-186) independently hardcodes the same "retry once" logic. The imported name is dead code, but if Phase 5 ever adds a `MAX_RETRIES` with a different value, Phase 7 will silently start using it without a corresponding update to the loop.

**Fix:** Remove the unused `MAX_RETRIES` import entirely, or replace with an explicit constant that matches the Phase 5 inline behavior:
```python
# Phase 7 inherits Phase 5's single-retry policy. Do not import MAX_RETRIES
# (it does not exist in Phase 5); keep retry logic explicit and local.
_JUDGE_MAX_RETRIES: int = 1  # mirrors run_judge_fpr.py:295-305 inline retry
```

---

### WR-02: `str(ablation_v7)` assertion is a false-negative trap for key names

**File:** `scripts/run_judge_fpr_gptoss.py:371`

**Issue:**
```python
assert "no_defense" not in str(ablation_v7), "D-03 violation: trivial no_defense row leaked"
```
`str()` on a Python dict produces the `repr` of keys and values (e.g., `"{'gptoss20b_cloud__fused': {...}}"` ). If any *value* field happens to contain the string `"no_defense"` — for instance, if a model name or a note field ever contained that substring — the assertion would fire as a false positive. More dangerously, the check would silently pass if the key were stored under a variant spelling (e.g., `"nodefense"`, `"no_defense_row"`). The intent (D-03) is to assert that no key named exactly `"no_defense"` exists in the dict, which should use key membership testing.

**Fix:**
```python
assert "no_defense" not in ablation_v7, (
    "D-03 violation: trivial no_defense row found in ablation_v7 keys"
)
```

---

### WR-03: Phase 7 client instantiated without `host` argument; Phase 5 uses explicit host

**File:** `scripts/run_judge_fpr_gptoss.py:305`

**Issue:** Phase 7 instantiates the Ollama client as `client = Client()` (line 305, no arguments), while Phase 5 uses `client = Client(host="http://localhost:11434")` (run_judge_fpr.py:404). `Client()` falls back to the Ollama default, which is also `localhost:11434` — so functionally equivalent in the common case. However the discrepancy means that if a user has configured a non-default Ollama host (e.g., via `OLLAMA_HOST` environment variable or a custom port), Phase 5 and Phase 7 will contact different endpoints, producing inconsistent results with no warning. Since Phase 7 explicitly states it inherits all Phase 5 conventions (D-11), the client instantiation should match.

**Fix:**
```python
client = Client(host="http://localhost:11434")
```

---

### WR-04: `_verify_prose.py` — `subprocess.check_output` raises `CalledProcessError` on bad git ref; unhandled

**File:** `scripts/_verify_prose.py:12-14`

**Issue:**
```python
original = subprocess.check_output(
    ['git', 'show', f'{original_commit}:docs/phase5_honest_fpr.md']
).decode('utf-8')
```
`subprocess.check_output` raises `subprocess.CalledProcessError` if `git show` returns a non-zero exit code (e.g., if the repository does not have commit `7374f22`, a shallow clone, or a fresh checkout without full history). This is an unhandled exception that produces a raw Python traceback rather than a clear diagnostic message. The script has no `try/except` and no `sys.exit` path for this case.

**Fix:**
```python
import subprocess, sys
try:
    original = subprocess.check_output(
        ['git', 'show', f'{original_commit}:docs/phase5_honest_fpr.md'],
        stderr=subprocess.DEVNULL,
    ).decode('utf-8')
except subprocess.CalledProcessError:
    print(
        f"ERROR: Could not retrieve commit {original_commit} from git history. "
        "Ensure the repository has full depth (not a shallow clone)."
    )
    sys.exit(2)
```

---

### WR-05: `_verify_fidelity.py` — file handles opened without `with` statement (resource leak)

**File:** `scripts/_verify_fidelity.py:18-19, 46`

**Issue:** Three `open()` calls are used without a `with` statement:
```python
p5 = json.load(open('logs/ablation_table.json', encoding='utf-8'))      # line 18
p7 = json.load(open('logs/ablation_table_gptoss_v7.json', encoding='utf-8'))  # line 19
text = open('docs/phase5_honest_fpr.md', encoding='utf-8').read()        # line 46
```
In CPython these are typically closed by reference-counting GC, but this is not guaranteed (PyPy, Jython) and flake8/pylint flag it as a code quality issue. If `json.load` or `.read()` raises mid-read, the file handle leaks until the interpreter exits.

**Fix:**
```python
with open('logs/ablation_table.json', encoding='utf-8') as f:
    p5 = json.load(f)
with open('logs/ablation_table_gptoss_v7.json', encoding='utf-8') as f:
    p7 = json.load(f)
# ... and at line 46:
with open('docs/phase5_honest_fpr.md', encoding='utf-8') as f:
    text = f.read()
```

---

## Info

### IN-01: `_verify_fidelity.py` — hardcoded relative paths assume CWD is repo root

**File:** `scripts/_verify_fidelity.py:18-19, 46`

**Issue:** All three file paths (`logs/ablation_table.json`, `logs/ablation_table_gptoss_v7.json`, `docs/phase5_honest_fpr.md`) are relative and assume the script is run from the repository root. Running from another directory silently produces `FileNotFoundError` with no diagnostic. `_verify_prose.py` (line 16) has the same pattern. This is a common footgun for audit scripts that get run from within the `scripts/` directory.

**Fix:** Use `Path(__file__).parent.parent` to anchor paths, mirroring the pattern used in the test files:
```python
from pathlib import Path
_ROOT = Path(__file__).parent.parent
p5 = json.load(open(_ROOT / 'logs/ablation_table.json', encoding='utf-8'))
```

---

### IN-02: `run_judge_fpr_gptoss.py` — `main()` returns `rc=2` for missing `ollama` but `rc=1` for missing input files (undocumented asymmetry)

**File:** `scripts/run_judge_fpr_gptoss.py:277, 303`

**Issue:** The docstring documents `rc=2` for config errors (line 277: `"Returns 0 on success, 1 on auth error, 2 on config error"`), and line 303 correctly returns 2 when ollama is absent. However, the `_assert_paths_exist()` call at line 279 raises `AssertionError` (not returning a code) when input log files are missing. The test `TestDryRunNoCloud.test_dry_run_no_cloud` (test_phase7_judge_fpr.py:435) acknowledges this by asserting `rc in (0, 1)` — but per the docstring, a missing-input failure should produce `rc=2`, not an uncaught `AssertionError` traceback.

**Fix:** Wrap `_assert_paths_exist()` in a `try/except AssertionError` and return 2:
```python
try:
    _assert_paths_exist()
except AssertionError as exc:
    print(f"FATAL: {exc}")
    return 2
```

---

### IN-03: `_verify_fidelity.py` — `src_v = round(expected[metric], 3)` rounds to 3 decimals but llama tolerance is 0.005 (implies 2 decimals)

**File:** `scripts/_verify_fidelity.py:100-103`

**Issue:** For llama rows the script does:
```python
src_v = round(expected[metric], 3)
if abs(table_v - src_v) > 0.005:
```
The comment says "Llama rows displayed at 2-decimal precision ... tolerance = 0.005 (half of 0.01 rounding interval)." Rounding `src_v` to 3 decimal places before comparing against a 0.005 tolerance is a mismatch: if a value is `0.3249`, `round(0.3249, 3)` is `0.325`, and the comparison is done against `0.325` — but the table stores `0.32` (2 decimal places). The correct reference value for the 2-decimal display should be `round(expected[metric], 2)`, not `round(expected[metric], 3)`. As written, the rounding to 3 decimals introduces a spurious intermediate step that can push a valid table value outside the stated half-interval tolerance.

**Fix:**
```python
# For llama rows: table displays 2-decimal precision; compare against 2-dp reference
src_v = round(expected[metric], 2)
if abs(table_v - src_v) > 0.005:
```

---

### IN-04: `test_phase7_judge_fpr.py` — `TestCacheResume.test_dry_run_skips_calls` assertion allows `rc=1` silently

**File:** `tests/test_phase7_judge_fpr.py:420-421`

**Issue:**
```python
rc = main(["--dry-run", "--cache", str(cache_file)])
assert rc in (0, 1), f"Unexpected return code from main: {rc}"
```
The test passes whether `main()` succeeded (`rc=0`) or failed due to missing input files (`rc=1`). This means the test provides no signal when run in an environment where the v6 log files are absent — it always passes. This is a deliberately acknowledged limitation ("a full cache-resume test requires monkeypatching; that is a Wave 2 concern") but the test name `test_dry_run_skips_calls` implies it validates that calls are skipped, which it does not verify.

**Fix (minimal, without requiring monkeypatching):** Add a skip guard that mirrors what `TestPathMapsLoudFail` does, so the test clearly communicates its own pre-conditions:
```python
if not all(Path(p).exists() for p in CELL_LOG_MAP.values()):
    pytest.skip("v6 cell files absent — cache-resume test requires live inputs")
rc = main(["--dry-run", "--cache", str(cache_file)])
assert rc == 0, f"--dry-run with staged cache returned rc={rc}"
```

---

### IN-05: `make_results.py` — `load_undefended_baseline` silently produces wrong column order when `rows` is non-empty

**File:** `scripts/make_results.py:319`

**Issue:**
```python
return pd.DataFrame(rows, columns=_COLUMNS) if not rows else pd.DataFrame(rows)
```
When `rows` is non-empty, the explicit `columns=_COLUMNS` argument is omitted. `pd.DataFrame(rows)` infers columns from the dicts' key insertion order (Python 3.7+ dict ordering). This is reliable in Python 3.11, but if a future code change adds a key to some rows and not others, the column order (and presence) will silently diverge from `_COLUMNS`. The guard also has the logic inverted for readability — "if not rows … else …" is the less-obvious form.

**Fix:**
```python
return pd.DataFrame(rows, columns=_COLUMNS)
```
This is safe to always pass `columns=_COLUMNS` — `pd.DataFrame(rows, columns=_COLUMNS)` will reorder/fill-NaN columns from the dicts correctly whether or not `rows` is empty.

---

### IN-06: `docs/phase5_honest_fpr.md` — missing blank line before `## Phase 7 addendum` heading breaks some Markdown renderers

**File:** `docs/phase5_honest_fpr.md:133-134`

**Issue:** The addendum heading appears immediately after the References list item with no blank line:
```
2. Dubois et al., 2024. ...  arXiv:2404.04475.
## Phase 7 addendum: gpt-oss extension (2026-05-04)
```
CommonMark spec requires a blank line before ATX headings when they follow a paragraph or list item for the heading to be recognized. Most renderers (GitHub, VS Code) handle this, but strict CommonMark parsers will treat the `## Phase 7 addendum` line as continuation text of the preceding list item, breaking the section structure that `_verify_fidelity.py` relies on (its regex `re.search(r'## Phase 7 addendum.*?(?=^## |\Z)', ...)` would fail if the heading is not recognized as such).

**Fix:** Add a blank line between the last reference and the addendum heading:
```
2. Dubois et al., 2024. ...  arXiv:2404.04475.

## Phase 7 addendum: gpt-oss extension (2026-05-04)
```

---

_Reviewed: 2026-05-04T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
