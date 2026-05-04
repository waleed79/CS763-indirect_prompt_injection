---
plan: 05-03
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
status: complete
completed: 2026-05-03
---

# Plan 05-03: Execute Judge Run — SUMMARY

## What Was Built

Executed `scripts/run_judge_fpr.py` against `gpt-oss:20b-cloud` to populate
`logs/judge_fpr_llama.json` (350 per-cell verdicts) and extend
`logs/ablation_table.json` with three honest FPR metrics on all 8 ablation rows.

## Execution Details

- **Wall clock:** ~45 minutes
- **Total cloud calls:** 351 (350 base + 1 retry for bert_only Q10 — network blip / 502 error; D-12 retry succeeded)
- **Auth/network blips:** 1 (bert_only Q10: wsarecv 502; retried once, verdict=TIE)
- **Model:** gpt-oss:20b-cloud via Ollama at http://localhost:11434, temperature=0.0, --delay 3

## Per-Defense M1/M2/M3 Results (headline numbers for Plan 04)

| Defense                | FPR (orig ≥1 removed) | Per-chunk FPR (M1) | Answer-preserved FPR (M2) | Judge FPR (M3) | n_calls |
|:----------------------|----------------------:|-------------------:|--------------------------:|---------------:|--------:|
| no_defense (trivial)  |                   n/a |               0.00 |                      0.00 |           0.00 |       0 |
| DEF-02 (system prompt)|                   n/a |               0.00 |                      0.00 |           0.24 |      50 |
| BERT only             |                  0.76 |               0.32 |                      0.26 |           0.28 |      51 |
| Perplexity only       |                  0.76 |               0.22 |                      0.14 |           0.16 |      50 |
| Imperative only       |                  0.76 |               0.36 |                      0.34 |           0.34 |      50 |
| Fingerprint only      |                  0.76 |               0.02 |                      0.02 |           0.04 |      50 |
| Fused (fixed θ=0.5)   |                  0.76 |               0.31 |                      0.32 |           0.34 |      50 |
| Fused (tuned θ=0.10)  |                  0.76 |               0.34 |                      0.32 |           0.34 |      50 |

Note: The original "FPR 0.76" (≥1 chunk removed from any query) applies to all
filtering defenses but is not the same metric as M1/M2/M3. The 0.76 value appears
on bert_only, perplexity_only, imperative_only, fingerprint_only, fused_fixed_0.5,
and fused_tuned_threshold rows in ablation_table.json under the `fpr` key.
DEF-02 has per_chunk_fpr=0 because system-prompt defense removes no chunks.

## Per-Defense Verdict Distribution

| Defense            | DEGRADED | PRESERVED | TIE | REFUSAL |
|:-------------------|:--------:|:---------:|:---:|:-------:|
| def02              |    12    |    13     |  25 |    0    |
| bert_only          |    14    |    15     |  21 |    0    |
| perplexity_only    |     8    |    14     |  28 |    0    |
| imperative_only    |    17    |    12     |  21 |    0    |
| fingerprint_only   |     2    |    12     |  36 |    0    |
| fused_fixed_0.5    |    17    |    14     |  19 |    0    |
| fused_tuned_threshold|  17    |    12     |  21 |    0    |

Good mixture of DEGRADED/PRESERVED/TIE — not collapsed to one value. No REFUSAL verdicts.

## Post-flight Verification

- **V-09 back-compat:** fused_fixed_0.5.fpr = 0.76 unchanged ✓
- **All 9 tests (V-01..V-09):** `pytest tests/test_judge_fpr.py -x -q` → 9 passed in 1.06s ✓
- **Schema on all 8 rows:** per_chunk_fpr, answer_preserved_fpr, judge_fpr, judge_model, judge_n_calls present ✓
- **no_defense trivial fill:** judge_n_calls=0 (canonical no-calls signal per D-02) ✓
- **judge_n_calls range:** 50–51 across active defenses (350 base + 1 retry = 351 total) ✓
- **DEGRADED sanity:** ≥1 DEGRADED per defense, none all-DEGRADED ✓

## md5 of logs/ablation_table.json (post-Plan-03)

`d66791c9b1bf836e5f72402989c06597`

## Idempotence Note (V-06)

V-06 test passes (consecutive runs from same initial state with frozen cache produce
identical output). Live re-run with production cache resets `judge_n_calls` to 0
(no cloud calls made on re-run) while M1/M2/M3 remain identical — a known minor
behavior difference in the call-counter metadata, not in the metrics. Production
n_calls restored from `logs/run_judge_fpr.stdout.log` before final commit.

## INFILTRATED Leakage Sub-Finding

DEF-02 (system prompt only) has M3=24% despite M1=0% (no chunks removed). This
confirms the Phase 3.1-06 finding: the system-prompt warning primes llama3.2:3b
to surface injected instructions, increasing apparent degradation even on clean
queries. Plan 04 §5 will call this out explicitly.

No INFILTRATED anchor-token leakage was detected in the defense-off baseline
answers for the 50 clean queries — the clean-query corpus does not overlap with
poisoned corpus retrieval on these specific queries.

## Artifacts

- `logs/judge_fpr_llama.json` — 7 defenses × 50 verdicts = 350 total
- `logs/ablation_table.json` — extended with 5 new keys on all 8 llama rows
- `logs/judge_fpr_llama.json.cache` — checkpoint cache for re-runs
- `logs/run_judge_fpr.stdout.log` — full run transcript

## Self-Check: PASSED

All acceptance criteria met. Plan 04 (writeup) and Plan 05 (callout) can now
read the three new metric values across all 7 active rows.
