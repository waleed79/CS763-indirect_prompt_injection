---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
plan: "02"
subsystem: evaluation
tags: [judge, fpr, cloud-llm, ablation, phase5]
dependency_graph:
  requires:
    - logs/defense_off_llama.json
    - logs/defense_def02_llama.json
    - logs/defense_bert_llama.json
    - logs/defense_perplexity_llama.json
    - logs/defense_imperative_llama.json
    - logs/defense_fingerprint_llama.json
    - logs/defense_fused_llama.json
    - logs/defense_fused_tuned_llama.json
    - logs/ablation_table.json
  provides:
    - scripts/run_judge_fpr.py
    - logs/judge_fpr_llama.json
  affects:
    - logs/ablation_table.json
tech_stack:
  added: []
  patterns:
    - ollama.Client pairwise-judge with temperature=0.0 and auth-bail
    - atomic write (tmp + replace) for JSON corruption resistance
    - random.Random(42) instance for cross-version RNG determinism
    - importlib spec_from_file_location test pattern
key_files:
  created:
    - scripts/run_judge_fpr.py
    - logs/judge_fpr_llama.json
  modified:
    - logs/ablation_table.json
decisions:
  - "Guarded ollama import (_OLLAMA_AVAILABLE flag) so module loads cleanly under importlib without sys.exit(1) when ollama package absent (needed for pytest collect-only)"
  - "random.Random(42) instance (not module-level random.seed) per RESEARCH §A5 override — stricter cross-version determinism for V-06 idempotency"
  - "Dry-run sets n_calls=N_CLEAN (50) instead of 0 so caller can see nominal call budget without confusing the no_defense judge_n_calls=0 canonical signal"
metrics:
  duration: "~8 minutes"
  completed: "2026-05-04T03:26:46Z"
  tasks_completed: 1
  files_created: 2
  files_modified: 1
---

# Phase 05 Plan 02: judge-fpr-script Summary

Phase 5 honest-FPR entry-point script `scripts/run_judge_fpr.py` implemented and committed. The script computes three utility-cost metrics (per-chunk FPR, answer-preserved FPR, LLM-as-judge FPR) for 7 llama defense rows using pairwise A/B judge calls against `gpt-oss:20b-cloud`, with atomic writes, checkpoint cache, and `--dry-run` support.

## What Was Built

`scripts/run_judge_fpr.py` — 467 lines, single self-contained file.

### Module-Level Exports (test contract)

All Plan 01 test imports resolve via importlib:

| Export | Value |
|--------|-------|
| `main(argv=None) -> int` | CLI entry point |
| `DEFENSE_LOG_MAP` | 7 keys per D-01 |
| `TOP_K` | 5 |
| `N_CLEAN` | 50 |
| `JUDGE_SYSTEM_PROMPT` | D-10 verbatim |
| `JUDGE_USER_TEMPLATE` | D-10 verbatim |
| `parse_verdict` | 3-way + None |

### DEFENSE_LOG_MAP (exactly 7 keys per D-01)

```
['def02', 'bert_only', 'perplexity_only', 'imperative_only',
 'fingerprint_only', 'fused_fixed_0.5', 'fused_tuned_threshold']
```

### Dry-Run Smoke Test

```
conda run -n rag-security python scripts/run_judge_fpr.py --dry-run --cache /tmp/cache_test.json
```

Exit code: **0**. Duration: ~3 seconds (7 × 50 records, no cloud calls). All 7 defense M1 values computed from existing logs:
- def02: M1=0.0000 (no removals)
- bert_only: M1=0.3200
- perplexity_only: M1=0.2200
- imperative_only: M1=0.3640
- fingerprint_only: M1=0.0200
- fused_fixed_0.5: M1=0.3080
- fused_tuned_threshold: M1=0.3400

### Verbatim Copy from scripts/run_judge.py:173-233

| Source element | Source line | Destination line |
|----------------|-------------|------------------|
| `Client(host="http://localhost:11434")` | 173 | line 380 (in `main()`) |
| `options={"temperature": 0.0}` + comment | 193 | line 169 (in `judge_one()`) |
| auth bail `"login" in msg.lower() or "auth" in msg.lower()` | 197-199 | lines 173-175 |
| `"FATAL: Judge model requires auth. Run: ollama login"` | 198 | line 174 |
| `msg_obj = resp.message if hasattr(resp, "message") else resp["message"]` | 212 | line 181 |
| `content = msg_obj.content if hasattr(msg_obj, "content") else msg_obj["content"]` | 213 | line 182 |
| sleep on success: `if args.delay > 0: time.sleep(args.delay)` | 232-233 | lines 184-185 |
| sleep on failure branch | 208-209 | lines 177-178 |

### no_defense Provenance Comment

Present at the assignment in `main()` step 6 (line 437):
```python
"judge_model":  args.model,  # Schema-shape consistency only; judge_n_calls=0 is the canonical "no calls" signal (D-02).
```

### Line Count

`scripts/run_judge_fpr.py`: **467 lines** (requirement: >=200).

### pytest --collect-only Before vs After

- **Before Plan 02:** `9 skipped` (skip guard fired — module not present)
- **After Plan 02:** `9 collected in 0.67s` (skip guard lifted — module importable)

Output:
```
collected 9 items
  TestSchemaExtension::test_schema_extension
  TestSchemaExtension::test_back_compat_fpr_unchanged
  TestMetricBounds::test_no_defense_zero
  TestMetricBounds::test_m1_in_range
  TestMetricBounds::test_m1_numerator_bounded
  TestMetricBounds::test_m2_le_m1
  TestJudgeConsistency::test_judge_n_calls_min
  TestJudgeConsistency::test_m3_consistency
  TestJudgeConsistency::test_idempotent_with_cache
```

## Deviations from Plan

### Planned Override (not a deviation)

**RESEARCH §5.4 `random.seed(42)` overridden by §A5 `random.Random(42)` instance** — this is the explicitly documented planned override in the plan's `<read_first>` note. `random.Random(42)` was implemented as specified.

### Auto-fix: Guarded ollama Import

**Found during:** Task 1 (initial verification)

**Issue:** The analog `scripts/run_judge.py` uses `sys.exit(1)` inside the `except ImportError` block at module level. When loaded via `importlib.util.spec_from_file_location` (the test pattern), this causes the process to exit immediately if `ollama` is not installed in the active Python, preventing `_AVAILABLE = True` from being set and crashing `pytest --collect-only`.

**Fix:** Replaced the `sys.exit(1)` import guard with `_OLLAMA_AVAILABLE = False` flag + `Client = None` assignment. Added a runtime check in `main()` that exits with error message if `--dry-run` is not set and ollama is unavailable. This matches the test contract without breaking the runtime contract.

**Files modified:** `scripts/run_judge_fpr.py`
**Commit:** c9322e3

## Threat Flags

None — this script reads local JSON logs and writes local JSON files. No new network endpoints, no new auth paths, no schema changes at trust boundaries beyond the planned additive `ablation_table.json` extension.

## Self-Check: PASSED

- `scripts/run_judge_fpr.py` exists: FOUND
- `logs/judge_fpr_llama.json` exists: FOUND (created by dry-run)
- Commit c9322e3 exists: FOUND
- All 9 pytest tests collected: VERIFIED
- `--dry-run` exits 0: VERIFIED
- `len(DEFENSE_LOG_MAP) == 7`: VERIFIED
- `random.Random(42)` present: VERIFIED
