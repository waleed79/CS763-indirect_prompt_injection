---
phase: "06"
plan: "02"
subsystem: phase6-driver
tags: [wave-1, driver, subprocess, chromadb, preflight, provenance, p6-pre, p6-pro, p6-auth, p6-err, p6-enc, p6-mtx, tdd]
dependency_graph:
  requires:
    - tests/test_phase6_eval.py (Wave 0 stubs from 06-01)
    - rag/constants.py (TIER*_ID_START SSOT)
    - scripts/run_eval.py (subprocess target)
    - logs/eval_matrix/_summary.json (45-cell baseline)
  provides:
    - scripts/run_phase6_eval.py (Phase 6 driver with main(argv) + 6 helpers)
  affects:
    - tests/test_phase6_eval.py (Wave 0 stubs activated — 6 tests now PASS)
    - logs/eval_matrix/_summary_v6.json (composed by driver post-run)
tech_stack:
  added: []
  patterns:
    - TDD RED/GREEN — stub tests first, production code second
    - subprocess.run(list_argv, shell=False) for T-3.3-01 command-injection mitigation
    - atomic JSON write via .tmp + os.replace (save_atomic pattern from make_figures.py)
    - chromadb.PersistentClient read-only get() for D-01a pre-flight tier probe
    - monkeypatch.setattr on module-level chromadb / subprocess for unit isolation
key_files:
  created:
    - scripts/run_phase6_eval.py
  modified:
    - tests/test_phase6_eval.py
decisions:
  - "TDD approach: replaced 5 pytest.skip() stubs with real bodies before writing production code; RED commit 8af61ef precedes GREEN commit 7eb6790"
  - "chromadb is only available under the rag-security conda env (Python 3.11); C:\\Python313\\python.exe lacks it; all pytest invocations must use conda run -n rag-security"
  - "PHASE_6_DEFENSES has 3 entries matching grep -cE count of 4 (off/fused/def02/fused appears twice due to list format) — the 4-count is correct and expected"
  - "assert_collection_has_all_tiers uses $and chromadb filter with passage_id $gte/$lt; T1b range [20150,20200) probed last so stale T1b triggers the most meaningful error message"
  - "compose_summary_v6 warns (not fails) when cell count != 75 to allow partial runs; Plan 03 will produce exactly 6 outputs for 75 total"
metrics:
  duration: "3m 58s"
  completed: "2026-05-04T07:14:53Z"
  tasks_completed: 1
  files_created: 1
  files_modified: 1
---

# Phase 06 Plan 02: Phase 6 Driver Implementation Summary

Phase 6 driver `scripts/run_phase6_eval.py` — 6-cell subprocess orchestrator wrapping `gpt-oss:{20b,120b}-cloud x {off,fused,def02}` run_eval.py invocations with D-01a pre-flight tier probe, P6-AUTH ollama list check, D-02a provenance mutation, and D-09c 75-cell summary composition.

## What Was Built

### `scripts/run_phase6_eval.py`

Single-file driver (294 lines) with these helpers:

| Function | Requirement | Contract |
|---|---|---|
| `assert_collection_has_all_tiers(name)` | D-01a / P6-PRE | Probes 5 tier ranges in chromadb; raises AssertionError with tier name in message if any empty |
| `preflight_ollama_list()` | P6-AUTH | `subprocess.run(["ollama","list"], shell=False)`; raises RuntimeError if either gpt-oss model absent |
| `undefended_output_path(model_key)` | D-02 | `logs/eval_harness_undefended_{key}_v6.json` |
| `defended_output_path(model_key, defense)` | D-09b | `logs/eval_matrix/{key}_cloud__{defense}__all_tiers_v6.json` |
| `build_run_command(model_id, flag, path)` | T-3.3-01 / D-09a | `list[str]` argv; no `--tier-filter`; `shell=False` |
| `run_one(model_id, flag, path)` | P6-RUN | Single-cell `subprocess.run(check=False, shell=False)`; returns returncode |
| `add_provenance(path)` | D-02a / D-03a | Atomic rewrite: sets `phase="06"`, `supersedes_phase_02_3=True`, counts `[ERROR:` answers into `aggregate.error_count` |
| `compose_summary_v6(run_outputs)` | D-09c | Loads 45-cell `_summary.json` + 30 new cells (2 models x 3 defenses x 5 tiers) = 75; atomic write to `_summary_v6.json` |
| `main(argv)` | — | `--dry-run`, `--skip-preflight`, `--filter-model`, `--filter-defense`; returns 0/1/2 |

### Module-level constants

```python
PHASE_6_MODELS = [("gpt-oss:20b-cloud", "gptoss20b"), ("gpt-oss:120b-cloud", "gptoss120b")]
PHASE_6_DEFENSES = [("off", "no_defense"), ("fused", "fused"), ("def02", "def02")]
COLLECTION = "nq_poisoned_v4"
```

### `tests/test_phase6_eval.py` — Wave 0 stubs activated

Five `pytest.skip()` bodies replaced with real test logic:

| Test | What it verifies |
|---|---|
| `TestSanityAssert::test_missing_tier_range_raises` | monkeypatched chromadb returns `{"ids":[]}` for T1b range; asserts `AssertionError` with `"T1b range"` |
| `TestErrorPolicy::test_error_policy_increments_count` | fixture JSON with 1 `[ERROR:` answer; asserts `error_count==1` after `add_provenance()` |
| `TestEncodingExplicit::test_run_phase6_eval_uses_utf8_explicit` | static grep: every `read_text(` / `write_text(` call includes `encoding="utf-8"` |
| `TestPreflightCloudAuth::test_ollama_list_contains_gptoss_models` | mocked stdout missing 120b; asserts `RuntimeError` with `"gpt-oss:120b-cloud"` |
| `TestPreflightCloudAuth::test_ollama_list_returns_clean_when_both_present` | mocked stdout has both; asserts no exception |
| `TestMatrixSummary::test_summary_has_exactly_75_cells` | builds 45-cell stub + 6 run stubs in `tmp_path`; monkeypatches `EXISTING_SUMMARY`/`SUMMARY_V6`; asserts 75 cells |

## Verification Results

```
pytest tests/test_phase6_eval.py::TestSanityAssert
      tests/test_phase6_eval.py::TestErrorPolicy
      tests/test_phase6_eval.py::TestEncodingExplicit
      tests/test_phase6_eval.py::TestPreflightCloudAuth
      tests/test_phase6_eval.py::TestMatrixSummary::test_summary_has_exactly_75_cells -v
=> 6 passed in 1.27s
```

```
python scripts/run_phase6_eval.py --dry-run
=> [phase6] dry-run: 6 planned cells
=> 6 lines containing "scripts/run_eval.py"; 0 lines containing "--tier-filter"
```

```
python scripts/run_phase6_eval.py --dry-run --filter-model gptoss20b --filter-defense fused
=> 1 line containing "scripts/run_eval.py"
```

Regression: `pytest tests/test_make_results.py -x` — 4 passed.

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

### Environmental Notes

- chromadb 1.5.7 is only available in the `rag-security` conda environment (Python 3.11). The system default `python.exe` (Python 3.13) lacks it. All `pytest` and `python scripts/run_phase6_eval.py` invocations must use `conda run -n rag-security`. The test module gracefully handles this via `try/except (AttributeError, FileNotFoundError)` — tests skip instead of error when chromadb unavailable.

## TDD Gate Compliance

- RED gate: commit `8af61ef` — `test(06-02): replace Wave 0 pytest.skip stubs with real test bodies`
- GREEN gate: commit `7eb6790` — `feat(06-02): implement scripts/run_phase6_eval.py Phase 6 driver`
- REFACTOR gate: not needed — code is clean on first pass.

## Known Stubs

None. All logic in `run_phase6_eval.py` is complete and unit-tested. The driver will perform actual cloud calls only when invoked from Plan 03 (Wave 2).

## Threat Surface Scan

| Flag | File | Description |
|------|------|-------------|
| threat_flag: subprocess | scripts/run_phase6_eval.py | New subprocess.run calls — mitigated: list[str] argv, shell=False, PHASE_6_MODELS hardcoded (no user input flows into argv) per T-06-W1-01 |
| threat_flag: file-write | scripts/run_phase6_eval.py | JSON writes in add_provenance and compose_summary_v6 — mitigated: atomic .tmp + os.replace per T-06-W1-02 |

## Self-Check: PASSED

```
[ -f "scripts/run_phase6_eval.py" ] => FOUND
[ -f "tests/test_phase6_eval.py" ] => FOUND
git log --oneline includes 8af61ef => FOUND (test RED commit)
git log --oneline includes 7eb6790 => FOUND (feat GREEN commit)
```
