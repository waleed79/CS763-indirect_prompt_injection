---
phase: 07-honest-fpr-metrics-gpt-oss-extension
plan: "04"
subsystem: eval
tags: [cloud-judge, fpr-metrics, gpt-oss, phase7]
key-files:
  created:
    - logs/ablation_table_gptoss_v7.json
    - logs/judge_fpr_gptoss_v7.json
    - logs/judge_fpr_gptoss_v7.json.cache
    - logs/run_judge_fpr_gptoss_v7_runlog.txt
    - docs/results/honest_fpr_gptoss_v7.md
    - docs/results/honest_fpr_gptoss_v7.csv
  modified: []
metrics:
  verdicts_collected: 200
  cells: 4
  retry_count_nonzero: 0
---

## Summary

Executed the live cloud M3 judge run for Phase 7: 200 judge calls (4 cells × 50 queries) using `gpt-oss:20b-cloud` as judge. Produced the three canonical Phase 7 artifacts and the auto-companion table.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Tasks 1–4 | 14139d0 | feat(07-04): run M3 cloud judge — 200 verdicts, 4-cell ablation table + companion docs |

## M1 / M2 / M3 Results

| Cell | M1 (per-chunk FPR) | M2 (ans-preserved FPR) | M3 (judge FPR) | n_calls |
|------|--------------------|------------------------|----------------|---------|
| gpt-oss:20b-cloud × fused  | 0.0920 | 0.0200 | 0.1600 | 50 |
| gpt-oss:20b-cloud × def02  | 0.0000 | 0.0000 | 0.0600 | 50 |
| gpt-oss:120b-cloud × fused | 0.0920 | 0.0400 | 0.1600 | 50 |
| gpt-oss:120b-cloud × def02 | 0.0000 | 0.0000 | 0.1000 | 50 |

**M2 ≤ M1 invariant: holds for all 4 rows.**

Key findings:
- `fused` removes ~9.2% of clean chunks (M1 = 0.092); this degrades 2–4% of answers (M2) and 16% of judge comparisons (M3).
- `def02` (system-prompt only, no chunk filtering) removes 0 chunks (M1 = 0.000) but still causes 6–10% judge-rated degradation — consistent with the Phase 5 DEF-02 priming effect.
- The 120b model shows slightly higher M2 under fused (4% vs 2%), suggesting its answers are more sensitive to chunk removal.
- All `retry_count` values are 0 — no TIE/refusal retries needed; cloud was stable throughout.

## git status (new files only)

```
14139d0 feat(07-04): run M3 cloud judge — 200 verdicts, 4-cell ablation table + companion docs
 6 files created: docs/results/honest_fpr_gptoss_v7.{md,csv}, logs/ablation_table_gptoss_v7.json,
                  logs/judge_fpr_gptoss_v7.json, logs/judge_fpr_gptoss_v7.json.cache,
                  logs/run_judge_fpr_gptoss_v7_runlog.txt
```

## Test Results (post-run)

| Test | Status |
|------|--------|
| TestAblationV7Shape (P7-OUT-J-SHAPE) | PASS |
| TestNoTrivialRow (P7-OUT-J-NOROW) | PASS |
| TestVerdictsV7Shape (P7-OUT-V-SHAPE) | PASS |
| TestVerdictCount200 (P7-OUT-V-COUNT) | PASS |
| TestVerdictRecordFields (P7-OUT-V-FIELDS) | PASS |
| TestCacheResume (P7-CACHE) | PASS |
| TestV7Emit (P7-RESV-EMIT) | PASS |

P7-DOC-* tests still SKIP — Plan 05's responsibility.

## Deviations

None. Script ran cleanly to completion; no JudgeAuthError; no retries; all 200 verdicts collected on first attempt.

## Self-Check: PASSED
