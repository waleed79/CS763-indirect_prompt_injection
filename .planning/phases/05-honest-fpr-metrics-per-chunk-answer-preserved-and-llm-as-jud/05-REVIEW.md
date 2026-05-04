---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
reviewed: 2026-05-03T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - tests/conftest.py
  - tests/test_judge_fpr.py
  - scripts/run_judge_fpr.py
  - scripts/_build_ablation_table.py
findings:
  critical: 1
  warning: 7
  info: 3
  total: 11
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-05-03T00:00:00Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Reviewed four files introduced in Phase 5: the pytest fixtures in `tests/conftest.py`, the nine-test suite in `tests/test_judge_fpr.py`, the main evaluation script `scripts/run_judge_fpr.py`, and the ablation table builder `scripts/_build_ablation_table.py`.

The most serious issue is that `_build_ablation_table.py` has no `if __name__ == "__main__"` guard, meaning any import of that module immediately writes `logs/ablation_table.json` and prints to stdout — a significant side-effect that makes the module unusable as a library. Additionally, there are multiple places where Windows non-atomic file replacement could silently corrupt `ablation_table.json` mid-run, and several locations use cwd-relative paths that make the test suite fragile when pytest is run from a non-root directory. A hardcoded `50` denominator in one test diverges from the `N_CLEAN` constant, creating a silent consistency risk if the constant is ever changed.

---

## Critical Issues

### CR-01: `_build_ablation_table.py` executes at import time — writes files, prints stdout

**File:** `scripts/_build_ablation_table.py:54-84`
**Issue:** The entire script body (file I/O loop, `json.dump`, `print` calls) runs unconditionally at module level. There is no `if __name__ == "__main__":` guard. Any `import _build_ablation_table` — from another script, from a test, or from an IDE code-intelligence tool — will immediately overwrite `logs/ablation_table.json` and print to stdout. This would silently destroy any Phase 5 extended keys (per_chunk_fpr, judge_fpr, etc.) that `run_judge_fpr.py` wrote, precisely the scenario warned about in the module docstring on lines 6-11.
**Fix:**
```python
def _build_table() -> dict:
    table = {}
    for name, fname in LLAMA_FILES.items():
        fpath = LOGDIR / fname
        if fpath.exists():
            table[name] = extract_row(fpath)
            print(f"  Loaded: {fname} -> {name}")
        else:
            print(f"WARNING: missing {fpath}")
    # ... rest of current module-level logic ...
    return table

if __name__ == "__main__":
    table = _build_table()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(table, f, indent=2)
```

---

## Warnings

### WR-01: Windows non-atomic file replacement may corrupt `ablation_table.json`

**File:** `scripts/run_judge_fpr.py:419-432` and `443-447`
**Issue:** The code comments advertise "Atomic write per RESEARCH §5.2 (tmp + replace to survive Ctrl-C)". On Linux/macOS, `Path.replace()` wraps POSIX `rename()`, which is atomic. On Windows (the platform confirmed in the env block), `Path.replace()` is NOT guaranteed atomic — a crash or Ctrl-C between `tmp_ab.write_text(...)` and `tmp_ab.replace(ablation_path)` can leave the `.tmp` file without completing the replace, and a subsequent `json.loads(ablation_path.read_text())` on line 421 may read a partial or stale file. The write inside the loop (lines 419-432) is also called once per defense (up to 7 times), multiplying the exposure window.
**Fix:** Accept the non-atomicity limitation on Windows and add a try/except around the read-modify-write block with an informative error message, or document the Windows caveat explicitly. As a stronger fix, accumulate all defense results in memory and do a single write at the end:
```python
# Accumulate all results first, then write once
for defense_key, log_fname in DEFENSE_LOG_MAP.items():
    ...
    all_metrics[defense_key] = (m1, m2, m3, n_calls)

# Single write at the end
ablation = json.loads(ablation_path.read_text())
for defense_key, (m1, m2, m3, n_calls) in all_metrics.items():
    ablation[defense_key].update({...})
atomic_write_json(ablation_path, ablation)
```

### WR-02: `sys.exit(1)` called inside library function `judge_one`

**File:** `scripts/run_judge_fpr.py:174-175`
**Issue:** `judge_one` calls `sys.exit(1)` on auth errors. This makes the function untestable (any test that triggers this path exits the entire pytest process), bypasses any cleanup in `main()`, and violates the principle that library functions should raise exceptions rather than terminate the process. The function's return type annotation `tuple[str | None, str, str | None]` implies it always returns — but it may not.
**Fix:** Raise a dedicated exception instead and let `main()` catch it:
```python
class JudgeAuthError(RuntimeError):
    pass

# Inside judge_one:
if "login" in msg.lower() or "auth" in msg.lower():
    raise JudgeAuthError(f"Judge model requires auth. Run: ollama login\n{exc}")

# Inside main():
try:
    verdict, raw_response, err = judge_one(...)
except JudgeAuthError as e:
    print(f"FATAL: {e}")
    return 1
```

### WR-03: `judge_one` does not catch `TypeError` from response parsing

**File:** `scripts/run_judge_fpr.py:181-183`
**Issue:** After the `except Exception` block, lines 181-183 access the response object with attribute-then-subscript fallback:
```python
msg_obj = resp.message if hasattr(resp, "message") else resp["message"]
content = msg_obj.content if hasattr(msg_obj, "content") else msg_obj["content"]
```
If `resp` is neither an object with `.message` nor a subscriptable mapping (e.g., the Ollama client changes its return type), `resp["message"]` raises `TypeError`, which is not caught by the outer `except Exception` block (that block has already exited). This `TypeError` propagates uncaught out of `judge_one`, crashes `run_for_defense`, and terminates the entire run after potentially hours of judge calls.
**Fix:** Wrap the response parsing in its own try/except:
```python
try:
    msg_obj = resp.message if hasattr(resp, "message") else resp["message"]
    content = msg_obj.content if hasattr(msg_obj, "content") else msg_obj["content"]
except (AttributeError, KeyError, TypeError) as parse_exc:
    print(f"  [ERROR] Unexpected response shape from judge model: {parse_exc}")
    if delay > 0:
        time.sleep(delay)
    return None, "", str(parse_exc)
```

### WR-04: `no_defense` key access without existence check

**File:** `scripts/run_judge_fpr.py:437`
**Issue:** `ablation["no_defense"].update(...)` raises `KeyError` with no user-friendly message if the `no_defense` key does not exist in `ablation_table.json` (e.g., if `_build_ablation_table.py` was never run, or if `defense_off_llama.json` was missing when the table was built). This crash occurs after all 7 defense evaluations have completed, losing the metrics output.
**Fix:**
```python
if "no_defense" not in ablation:
    print("WARNING: no_defense key missing from ablation_table.json — creating it.")
    ablation["no_defense"] = {}
ablation["no_defense"].update({...})
```

### WR-05: Test hardcodes `50` denominator instead of using `N_CLEAN`

**File:** `tests/test_judge_fpr.py:141`
**Issue:** `expected = degraded_count / 50` hardcodes the denominator. The module imports `N_CLEAN` from `run_judge_fpr.py` at line 27 precisely to avoid magic numbers. If `N_CLEAN` is ever changed to 100 queries (a natural extension), this test will silently compute the wrong expected value and compare it against `ablation[defense_key]["judge_fpr"]` (which was computed with the new `N_CLEAN`). The test will give a false pass or false fail depending on direction.
**Fix:**
```python
expected = degraded_count / N_CLEAN
```

### WR-06: Broad `except Exception` silently hides import errors in test module

**File:** `tests/test_judge_fpr.py:30`
**Issue:** The import block uses `except (AttributeError, FileNotFoundError, Exception)`. The final `Exception` makes the first two redundant and catches everything — including `SyntaxError`, `IndentationError`, and other hard failures in `run_judge_fpr.py`. A syntax error in the module would set `_AVAILABLE = False` and emit the misleading skip reason "scripts/run_judge_fpr.py not yet implemented (Phase 5 Plan 02)" instead of the actual traceback, making debugging very difficult.
**Fix:** Re-raise unexpected exceptions, or at minimum print the traceback before setting `_AVAILABLE = False`:
```python
import traceback
try:
    ...
    _AVAILABLE = True
except (AttributeError, FileNotFoundError):
    _AVAILABLE = False
except Exception:
    traceback.print_exc()
    _AVAILABLE = False
```

### WR-07: SC-5 verification defaults missing ASR keys to `1.0`, masking data gaps

**File:** `scripts/_build_ablation_table.py:116`
**Issue:** `min_signal_asr = min(table[s].get(tier, 1.0) for s in available_signals)` uses `1.0` (100% ASR) as a default when a signal row is missing a tier key. This silently makes `fused_asr <= min_signal_asr` more likely to be true, potentially inflating the SC-5 pass count and reporting a false "Fused better" result when data is actually missing.
**Fix:**
```python
for s in available_signals:
    val = table[s].get(tier)
    if val is None:
        print(f"  WARNING: {s} missing {tier} key — SC-5 comparison skipped for this tier")
        break
else:
    min_signal_asr = min(table[s][tier] for s in available_signals)
    # ... comparison logic
```

---

## Info

### IN-01: Relative paths in fixtures and tests are cwd-sensitive

**File:** `tests/conftest.py:35` and `tests/test_judge_fpr.py:46,50,99,149`
**Issue:** Multiple fixtures and helper functions use bare relative paths (`Path("logs/ablation_table.json")`, `Path("logs/judge_fpr_llama.json")`, `Path(f"logs/{log_fname}")`). These resolve relative to the process working directory at test time. If pytest is invoked from a subdirectory (e.g., `cd tests && pytest`), all these paths silently resolve to wrong locations, causing either `pytest.skip` or `FileNotFoundError` with no indication of what went wrong.
**Fix:** Anchor all paths to the repo root using `__file__`:
```python
# In conftest.py
_REPO_ROOT = Path(__file__).parent.parent
src = _REPO_ROOT / "logs" / "ablation_table.json"

# In test_judge_fpr.py
_LOGS_DIR = Path(__file__).parent.parent / "logs"
def _load_ablation():
    return json.loads((_LOGS_DIR / "ablation_table.json").read_text())
```

### IN-02: `open()` and `write_text()` calls missing explicit `encoding="utf-8"`

**File:** `scripts/_build_ablation_table.py:81` and `tests/conftest.py:60`
**Issue:** On Windows, `open()` without `encoding` and `Path.write_text()` without `encoding` use the system default (often `cp1252`). If any string in the JSON (model names, raw judge responses) contains non-ASCII characters, writes will either silently corrupt data or raise `UnicodeEncodeError`. The `atomic_write_json` helper in `run_judge_fpr.py` (line 135) also uses `Path.write_text()` without encoding.
**Fix:** Add `encoding="utf-8"` to all file writes:
```python
# _build_ablation_table.py line 81
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(table, f, indent=2)

# conftest.py line 60
cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")

# run_judge_fpr.py atomic_write_json (line 135)
tmp.write_text(json.dumps(obj, indent=2), encoding="utf-8")
```

### IN-03: `n_pairs` is a redundant variable in `run_for_defense`

**File:** `scripts/run_judge_fpr.py:229`
**Issue:** `n_pairs = len(off_records)` is assigned but only used in one print statement on line 235. Since `load_clean_records` already asserts exactly `N_CLEAN` records, `n_pairs` always equals `N_CLEAN`. The variable adds noise without adding information.
**Fix:** Replace with the constant directly:
```python
print(f"\n[{defense_key}] Evaluating {N_CLEAN} clean queries ...")
```

---

_Reviewed: 2026-05-03T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
