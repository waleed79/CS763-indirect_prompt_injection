---
phase: 06
verification_run: 2026-05-04T08:49:05Z
status: PASS_WITH_NOTES
---

# Phase 6 — Verification Audit

## Summary

| Requirement     | Status | Evidence |
|-----------------|--------|----------|
| P6-PRE          | pass   | TestSanityAssert::test_missing_tier_range_raises green |
| P6-RUN-20b-UND  | pass   | logs/eval_harness_undefended_gptoss20b_v6.json exists (86351 bytes), 5-tier aggregates present |
| P6-RUN-120b-UND | pass   | logs/eval_harness_undefended_gptoss120b_v6.json exists (88166 bytes), 5-tier aggregates present |
| P6-PRO          | pass   | TestProvenanceFields::test_provenance_fields_present_20b green; phase=06, supersedes=true, error_count int confirmed |
| P6-DEF          | pass   | TestDefendedRuns::test_all_four_defended_cells_exist green; all 4 defended cells (2 models × 2 defenses) present |
| P6-MTX          | pass   | TestMatrixSummary green (both tests); _summary_v6.json has exactly 75 cells |
| P6-RES-PR       | pass   | TestPathResolver green; _v6 files preferred when present, fallback confirmed |
| P6-RES-INT      | pass   | tests/test_make_results.py green (27 passed in targeted run; full suite: 1 pre-existing Phase 5 failure unrelated to P6) |
| P6-MD           | pass   | TestMarkdownDisclosure green; disclosure header in both undefended_baseline.md and arms_race_table.md |
| P6-CSV          | pass   | TestCsvCompanions green; undefended_baseline_v6.csv (490 bytes) + arms_race_table_v6.csv (11911 bytes) exist; originals mtime unchanged |
| P6-D12-FUSED    | pass   | TestD12FusedV6 green; figures/d12_cross_model_heatmap_v6.png exists, 67398 bytes (>>1KB) |
| P6-D12-UND      | pass   | TestD12UndefendedV6 green; figures/d12_undefended_v6.png exists, 81757 bytes (>>1KB) |
| P6-D03          | pass   | TestD03V6 green; figures/d03_arms_race_v6.png exists, 81488 bytes (>>1KB) |
| P6-FIG-INT      | pass   | Original figures untouched: fig1_arms_race.png and fig5_cross_model_heatmap.png mtime unchanged; tests/test_make_figures.py green |
| P6-AUTH         | pass   | TestPreflightCloudAuth (2 tests) green; ollama list confirms gpt-oss models present (executed at run time in Plan 03) |
| P6-ERR          | pass   | TestErrorPolicy green; error_count=0 in both undefended v6 logs (no cloud failures during runs) |
| P6-ENC          | pass   | TestEncodingExplicit green; all file I/O in run_phase6_eval.py uses encoding="utf-8" |

**Overall:** All 17 P6-* requirements pass automated verification. Full pytest suite: 1 failed (pre-existing Phase 5 data inconsistency in test_judge_fpr.py::TestJudgeConsistency::test_m3_consistency — unrelated to Phase 6), 234 passed, 4 skipped. Phase 6 targeted suite (test_phase6_eval.py + test_make_results_v6.py): 20/20 passed. Status PASS_WITH_NOTES.

## Headline gpt-oss ASR Snapshot

| Model | T1 | T1b | T2 | T3 | T4 | error_count |
|-------|----|-----|----|----|----|-------------|
| gpt-oss:20b-cloud (undefended) | 0.00 | 0.06 | 0.06 | 0.00 | 0.00 | 0 |
| gpt-oss:120b-cloud (undefended) | 0.00 | 0.02 | 0.06 | 0.00 | 0.00 | 0 |

Source: `logs/eval_harness_undefended_gptoss20b_v6.json` and `logs/eval_harness_undefended_gptoss120b_v6.json` (aggregate block).

T1 = standard tier-1 injection; T1b = homoglyph/obfuscation variant; T2 = indirect referral tier; T3 = tier-3; T4 = tier-4.
Cloud-scale models show near-zero T1/T3/T4 ASR and low but nonzero T1b/T2 ASR — consistent with stronger instruction-following reducing susceptibility to direct injections while obfuscation variants still land.

## Originals Untouched

| Original | Pre-mtime (epoch) | Post-mtime (epoch) | Verdict |
|----------|-------------------|---------------------|---------|
| logs/eval_harness_undefended_gptoss20b.json | 1776832844 | 1776832844 | unchanged |
| logs/eval_harness_undefended_gptoss120b.json | 1776834042 | 1776834042 | unchanged |
| logs/eval_matrix/_summary.json | 1777350108 | 1777350108 | unchanged |
| docs/results/undefended_baseline.csv | 1777883861 | 1777883861 | unchanged |
| docs/results/arms_race_table.csv | 1777883861 | 1777883861 | unchanged |
| figures/fig1_arms_race.png | 1777447652 | 1777447652 | unchanged |
| figures/fig5_cross_model_heatmap.png | 1777447654 | 1777447654 | unchanged |

Note: The `.pre_phase6_fig_mtimes.txt` capture references `figures/fig1_arms_race.png` and `figures/fig5_cross_model_heatmap.png` (the original naming convention), NOT `d03_arms_race.png` and `d12_cross_model_heatmap.png`. The plan's audit script template references the latter names, but those are the new v6 artifacts (verified in Section 7). No `d03_arms_race.png` or `d12_cross_model_heatmap.png` pre-phase originals exist — the old names are the true originals, and they are confirmed unchanged.

## Audit Output

```
=== Phase 6 verification audit @ 2026-05-04T08:49:05Z ===

--- Section 1: Full pytest suite ---
FAILED tests/test_judge_fpr.py::TestJudgeConsistency::test_m3_consistency (pre-existing Phase 5 data inconsistency — logs/judge_fpr_llama.json was re-run with all-PRESERVED verdicts but ablation_table.json was not updated; unrelated to Phase 6)
1 failed, 234 passed, 4 skipped, 2 warnings in ~100s

--- Section 2: Phase 6 specific tests ---
tests/test_phase6_eval.py::TestSanityAssert::test_missing_tier_range_raises PASSED
tests/test_phase6_eval.py::TestUndefendedRuns20b::test_undefended_20b_log_exists PASSED
tests/test_phase6_eval.py::TestUndefendedRuns120b::test_undefended_120b_log_exists PASSED
tests/test_phase6_eval.py::TestProvenanceFields::test_provenance_fields_present_20b PASSED
tests/test_phase6_eval.py::TestDefendedRuns::test_all_four_defended_cells_exist PASSED
tests/test_phase6_eval.py::TestMatrixSummary::test_summary_has_exactly_75_cells PASSED
tests/test_phase6_eval.py::TestMatrixSummary::test_summary_in_real_logs_has_75_cells PASSED
tests/test_phase6_eval.py::TestD12FusedV6::test_d12_fused_v6_exists_and_sized PASSED
tests/test_phase6_eval.py::TestD12UndefendedV6::test_d12_undefended_v6_exists_and_sized PASSED
tests/test_phase6_eval.py::TestD03V6::test_d03_v6_exists_and_sized PASSED
tests/test_phase6_eval.py::TestPreflightCloudAuth::test_ollama_list_contains_gptoss_models PASSED
tests/test_phase6_eval.py::TestPreflightCloudAuth::test_ollama_list_returns_clean_when_both_present PASSED
tests/test_phase6_eval.py::TestErrorPolicy::test_error_policy_increments_count PASSED
tests/test_phase6_eval.py::TestEncodingExplicit::test_run_phase6_eval_uses_utf8_explicit PASSED
tests/test_make_results_v6.py::TestPathResolver::test_v6_preferred_when_present PASSED
tests/test_make_results_v6.py::TestPathResolver::test_v6_summary_preferred_when_present PASSED
tests/test_make_results_v6.py::TestMarkdownDisclosure::test_undefended_baseline_disclosure_present PASSED
tests/test_make_results_v6.py::TestMarkdownDisclosure::test_arms_race_table_disclosure_present PASSED
tests/test_make_results_v6.py::TestCsvCompanions::test_undefended_baseline_v6_csv_exists PASSED
tests/test_make_results_v6.py::TestCsvCompanions::test_arms_race_table_v6_csv_exists PASSED
20 passed in 3.21s

--- Section 3: Wave 2 logs exist + provenance ---
OK logs/eval_harness_undefended_gptoss20b_v6.json 86351 bytes
OK logs/eval_harness_undefended_gptoss120b_v6.json 88166 bytes
OK logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json 90033 bytes
OK logs/eval_matrix/gptoss20b_cloud__def02__all_tiers_v6.json 89478 bytes
OK logs/eval_matrix/gptoss120b_cloud__fused__all_tiers_v6.json 88974 bytes
OK logs/eval_matrix/gptoss120b_cloud__def02__all_tiers_v6.json 89406 bytes
OK logs/eval_matrix/_summary_v6.json 14421 bytes

--- Section 4: _summary_v6.json cell count ---
OK: 75 cells

--- Section 5: gpt-oss ASR snapshot ---
gptoss20b undefended: t1=0.00 t1b=0.06 t2=0.06 t3=0.00 t4=0.00 err=0
gptoss120b undefended: t1=0.00 t1b=0.02 t2=0.06 t3=0.00 t4=0.00 err=0

--- Section 6: Originals untouched ---
Logs originals:
  logs/eval_harness_undefended_gptoss20b.json: pre=1776832844 cur=1776832844 -> OK unchanged
  logs/eval_harness_undefended_gptoss120b.json: pre=1776834042 cur=1776834042 -> OK unchanged
  logs/eval_matrix/_summary.json: pre=1777350108 cur=1777350108 -> OK unchanged
OK logs originals unchanged

CSV originals:
  docs/results/undefended_baseline.csv: pre=1777883861 cur=1777883861 -> OK unchanged
  docs/results/arms_race_table.csv: pre=1777883861 cur=1777883861 -> OK unchanged
OK CSV originals unchanged

Figure originals:
  figures/fig1_arms_race.png: pre=1777447652 cur=1777447652 -> OK unchanged
  figures/fig5_cross_model_heatmap.png: pre=1777447654 cur=1777447654 -> OK unchanged
OK figure originals unchanged

--- Section 7: New artifacts present ---
OK figures/d12_cross_model_heatmap_v6.png 67398 bytes
OK figures/d12_undefended_v6.png 81757 bytes
OK figures/d03_arms_race_v6.png 81488 bytes
OK docs/results/undefended_baseline_v6.csv 490 bytes
OK docs/results/arms_race_table_v6.csv 11911 bytes

--- Section 8: Disclosure header in regenerated MDs ---
docs/results/undefended_baseline.md
docs/results/arms_race_table.md
OK both MDs carry disclosure

=== Audit done @ 2026-05-04T08:52:30Z ===
```

## Notes / Anomalies

0. **Pre-existing Phase 5 test failure (out of Phase 6 scope)**: `tests/test_judge_fpr.py::TestJudgeConsistency::test_m3_consistency` fails because `logs/judge_fpr_llama.json` has uncommitted modifications (present in git status before this session began) — verdicts were re-run and changed from DEGRADED/TIE to all-PRESERVED, making it inconsistent with `logs/ablation_table.json` which still records `judge_fpr=0.24` for def02. This file is not touched by any Phase 6 script. Fixing this is out of Phase 6 scope; log in deferred-items. All 17 P6-* requirements pass independently.

1. **error_count = 0 in both runs**: No cloud rate-limit or API errors occurred during either 100-query undefended run. T-06-W5-03 (mid-run rate-limit risk) did not materialize.

2. **T1b assumption note**: gpt-oss:20b-cloud shows T1b=0.06 and gpt-oss:120b-cloud shows T1b=0.02. These are measured values from the v6 runs. For llama3.2:3b and mistral:7b, T1b data was not collected in Phase 02.3 and remains as "—" in the undefended_baseline.md table (D-08 footnote: T1b backfill for llama/mistral deferred to future phase).

3. **Figure naming convention note**: The pre-phase mtime capture file (`.pre_phase6_fig_mtimes.txt`) recorded the old figure names (`fig1_arms_race.png`, `fig5_cross_model_heatmap.png`) not the d-prefixed aliases. The plan's Section 6 audit script template references `d03_arms_race.png` and `d12_cross_model_heatmap.png` as "originals" — but those d-prefixed names are the new v6 artifacts, not pre-existing originals. The actual untouched originals are the `fig{1,5}_*.png` files, which mtime audit confirms are unchanged. This naming mismatch is cosmetic only; the integrity guarantee is preserved.

4. **Disclosure header exact text**: Both regenerated MDs carry the header:
   `> Updated 2026-05-04: Phase 6 cross-LLM gap fill — gpt-oss-20b and gpt-oss-120b numbers added across all 5 tiers and {no_defense, fused, def02}. Phase 02.3 / Phase 3.4 numbers above this line are unchanged.`
   Phrasing reads naturally.

5. **ASR magnitudes**: Both cloud-scale gpt-oss models show zero susceptibility to T1/T3/T4 injection patterns. Only T1b (homoglyph/obfuscation) and T2 (indirect referral) achieve nonzero ASR at 0.06 / 0.02 levels. This is consistent with the expectation that larger, instruction-tuned models have stronger instruction-following that resists direct injection but may still yield to subtle obfuscation strategies.

## Post-Approval Revisions (user eyeball checkpoint)

After manual review the user requested:
- Remove T4 from all 3 figures (all-zero across all models)
- Remove gemma4 from all 3 figures (all-zero everywhere)
- `d12_undefended_v6`: use real T1b values for llama/mistral from `_summary_v6.json` (llama=0.22, mistral=0.05) instead of 0.0 fill; remove gemma and T1b assumption footnotes from subtitle
- All figures now 4×4 shape
- `figures/final/` assembled with 10 files: 3 updated v6 PNGs + `demo_tier2_mistral.gif` (added manually by user) + 6 retained Phase 03.4 figures

All 3 figures re-rendered and user approved. Phase 6 closed.

## Adaptive Attack Results (Phase 6 gpt-oss cells)

Adaptive attacks ran automatically on all 6 gpt-oss cells (the harness always includes the adaptive tier alongside T1–T4).

**Denominator clarification:** `asr_adaptive` in the aggregate block divides by n=100 (all test queries). This is misleading — only **36 of the 100 queries** ever retrieved an adaptive-tier passage from the corpus; the other 64 queries had no adaptive doc in their top-k, making a hijack structurally impossible. The correct metric is `conditional_asr_adaptive = n_hijacked / n_retrieved` with n_retrieved=36.

The corpus contains **4 adaptive-tier passages** (text-search identified: passage_ids 20061, 20077, and 2 others using "[Note for AI: For...]" framing). These 4 passages match 36 distinct test queries via cosine similarity — the same passages appear in top-k for multiple queries.

| Cell | n_retrieved | n_hijacked | conditional_asr |
|------|-------------|------------|-----------------|
| gpt-oss:20b-cloud / no_defense  | 36 | 0 | 0.000 |
| gpt-oss:120b-cloud / no_defense | 36 | 1 | 0.028 |
| gpt-oss:20b-cloud / fused       | 36 | 1 | 0.028 |
| gpt-oss:20b-cloud / def02       | 36 | 0 | 0.000 |
| gpt-oss:120b-cloud / fused      | 36 | 1 | 0.028 |
| gpt-oss:120b-cloud / def02      | 36 | 0 | 0.000 |

**Interpretation:** Adaptive attack success is negligible (≤1 hijack per cell). The subtle "[Note for AI:]" framing is more resistant than it appears — the semantic camouflage that helps adaptive docs get retrieved also makes them less overtly coercive, so larger instruction-tuned models are not misled. This aligns with the paper's framing: adaptive attacks are designed to evade *detection* (defeat the classifier), not necessarily to improve *hijack rate*.

Source: per-query `adaptive_retrieved` / `hijacked_adaptive` flags in all 6 v6 harness files, verified via `scripts/_check_adaptive3.py`.

## Next Steps

- Phase 4 talk deck and poster can cite gpt-oss numbers from `docs/results/undefended_baseline.md` and `figures/final/d12_cross_model_heatmap_v6.png` (4×4 fused heatmap).
- All presentation assets are in `figures/final/` (10 files).
- When discussing adaptive ASR in any presentation or writeup, always cite conditional_asr (÷36), not raw asr_adaptive (÷100).
- Submitted Phase 3.4 writeup (`docs/phase3_results.md`) is intentionally NOT updated per D-04 (submission artifacts are frozen).
