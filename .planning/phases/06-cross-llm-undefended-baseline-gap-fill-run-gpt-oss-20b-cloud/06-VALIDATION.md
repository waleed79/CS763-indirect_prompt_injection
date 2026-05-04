---
phase: 6
slug: cross-llm-undefended-baseline-gap-fill-run-gpt-oss-20b-cloud
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-04
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Source: 06-RESEARCH.md §Validation Architecture + scope-expansion D-14.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (already installed via `requirements.txt`; existing `tests/` structure) |
| **Config file** | none in repo root — pytest uses defaults + auto-discovery in `tests/` |
| **Quick run command** | `pytest tests/test_phase6_eval.py tests/test_make_results_v6.py -x` |
| **Full suite command** | `pytest tests/ -x` |
| **Estimated runtime** | ~30 seconds (quick) / ~3-5 min (full) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_phase6_eval.py tests/test_make_results_v6.py -x` (Phase 6 quick suite)
- **After every plan wave:** Run `pytest tests/ -x` (full suite — guards regressions in test_make_results.py / test_make_figures.py)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~30 seconds for the quick suite

---

## Per-Task Verification Map

> Requirement IDs are Phase-6-local (P6-*) since the project ROADMAP did not pre-assign REQ-IDs to this phase. They map 1:1 onto CONTEXT.md decisions D-01 through D-14.

| Req ID | Behavior | Test Type | Automated Command | File Exists | Status |
|--------|----------|-----------|-------------------|-------------|--------|
| P6-PRE | D-01a sanity assert detects stale collection (missing T1b/T3/T4 ranges → AssertionError before subprocess) | unit (mock chromadb collection.get to return empty for one tier; assert main() raises) | `pytest tests/test_phase6_eval.py::TestSanityAssert -x` | ❌ W0 | ⬜ pending |
| P6-RUN-20b-UND | Driver runs gpt-oss:20b-cloud undefended and emits `logs/eval_harness_undefended_gptoss20b_v6.json` with 5-tier aggregates | smoke (driver-importable + post-run JSON shape) | `pytest tests/test_phase6_eval.py::TestUndefendedRuns20b -x` | ❌ W0 | ⬜ pending |
| P6-RUN-120b-UND | Driver runs gpt-oss:120b-cloud undefended and emits `logs/eval_harness_undefended_gptoss120b_v6.json` | smoke | `pytest tests/test_phase6_eval.py::TestUndefendedRuns120b -x` | ❌ W0 | ⬜ pending |
| P6-PRO | Each undefended `_v6.json` carries `phase: "06"`, `collection: "nq_poisoned_v4"`, `corpus: "data/corpus_poisoned.jsonl"`, `supersedes_phase_02_3: true`, `error_count: int`, all 5 tier aggregate keys (`asr_tier1`, `asr_tier1b`, `asr_tier2`, `asr_tier3`, `asr_tier4`, `paired_asr_*`, `co_retrieval_rate_tier4`) | unit (post-run JSON structure assertion against fixture) | `pytest tests/test_phase6_eval.py::TestProvenanceFields -x` | ❌ W0 | ⬜ pending |
| P6-DEF | Driver runs both gpt-oss models × {fused, def02} = 4 defended runs and emits `logs/eval_matrix/gptoss{20b,120b}_cloud__{fused,def02}__all_tiers_v6.json` | smoke | `pytest tests/test_phase6_eval.py::TestDefendedRuns -x` | ❌ W0 | ⬜ pending |
| P6-MTX | `logs/eval_matrix/_summary_v6.json` is a list with **exactly 75 cells**: 45 from existing `_summary.json` (bit-for-bit) + 30 new cells = 2 gpt-oss models × 3 defenses × 5 tiers; each new cell has keys `{model, defense, tier, asr_overall, asr_tier_native, fpr, retrieval_rate}` | unit (cell count + schema assertion) | `pytest tests/test_phase6_eval.py::TestMatrixSummary -x` | ❌ W0 | ⬜ pending |
| P6-RES-PR | `make_results.py` path-resolver prefers `eval_harness_undefended_*_v6.json` over un-versioned + prefers `_summary_v6.json` over `_summary.json` when present, falls back otherwise | unit (write fake _v6 files to tmp_path, verify resolver picks them; remove, verify fallback) | `pytest tests/test_make_results_v6.py::TestPathResolver -x` | ❌ W0 | ⬜ pending |
| P6-RES-INT | Existing `tests/test_make_results.py::test_three_source_aggregation` and `test_arms_race_table_emitted` stay green after path-resolver edit | regression | `pytest tests/test_make_results.py -x` | ✓ exists | ⬜ pending |
| P6-MD | `docs/results/undefended_baseline.md` and `docs/results/arms_race_table.md` contain dated disclosure header (top of file, after H1) + gpt-oss rows with T1b/T3/T4 columns | unit (substring asserts on regenerated .md content) | `pytest tests/test_make_results_v6.py::TestMarkdownDisclosure -x` | ❌ W0 | ⬜ pending |
| P6-CSV | `docs/results/undefended_baseline_v6.csv` and `docs/results/arms_race_table_v6.csv` exist after `make_results.py` run; original .csv files unchanged (mtime ≤ phase start) | unit (file existence + CSV header check + originals untouched) | `pytest tests/test_make_results_v6.py::TestCsvCompanions -x` | ❌ W0 | ⬜ pending |
| P6-D12-FUSED | `figures/d12_cross_model_heatmap_v6.png` exists, size > 1KB; renderer enforces `assert matrix.shape == (5, 5)` (5 tiers × 5 LLMs fused-defense) | unit (mock matrix wrong shape → AssertionError; happy path → file exists) | `pytest tests/test_phase6_eval.py::TestD12FusedV6 -x` | ❌ W0 | ⬜ pending |
| P6-D12-UND | `figures/d12_undefended_v6.png` exists, size > 1KB; renderer enforces `assert matrix.shape == (5, 4)` (5 tiers × 4 LLMs undefended, gemma4 skipped) | unit | `pytest tests/test_phase6_eval.py::TestD12UndefendedV6 -x` | ❌ W0 | ⬜ pending |
| P6-D03 | `figures/d03_arms_race_v6.png` exists, size > 1KB AND ≥ 1.2× original size delta vs `figures/d03_arms_race.png` (proxy for added gpt-oss bars) | smoke | `pytest tests/test_phase6_eval.py::TestD03V6 -x` | ❌ W0 | ⬜ pending |
| P6-FIG-INT | Original `figures/d03_arms_race.png`, `figures/d12_cross_model_heatmap.png`, and existing `tests/test_make_figures.py::test_all_five_pngs_emitted` all unchanged after Phase 6 run | regression (mtime + checksum check on originals; pytest on existing test) | `pytest tests/test_make_figures.py -x && python -c "import os; assert os.path.getmtime('figures/d12_cross_model_heatmap.png') < {phase_start_ts}"` | ✓ exists | ⬜ pending |
| P6-AUTH | Pre-flight `ollama list` confirms `gpt-oss:20b-cloud` and `gpt-oss:120b-cloud` are present before any 100-query run begins | smoke (subprocess + grep) | `pytest tests/test_phase6_eval.py::TestPreflightCloudAuth -x` | ❌ W0 | ⬜ pending |
| P6-ERR | Single-query failure during a 100-query run records `answer = "[ERROR: <type>]"`, sets all `hijacked_*` to False, increments `aggregate.error_count`, does NOT abort run | unit (mock generator.generate to raise once; assert run completes with error_count=1) | `pytest tests/test_phase6_eval.py::TestErrorPolicy -x` | ❌ W0 | ⬜ pending |
| P6-ENC | All file reads/writes use `encoding="utf-8"` explicitly (cp1252 hazard on Windows) | static (grep for `open(` calls in `scripts/run_phase6_eval.py` lacking `encoding=`) | `pytest tests/test_phase6_eval.py::TestEncodingExplicit -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Test stub files to create in Wave 0 (importlib pattern from Phase 03.2/03.4 stubs — load scripts/ modules without `__init__.py`):

- [ ] `tests/test_phase6_eval.py` — stub classes for: TestSanityAssert (P6-PRE), TestUndefendedRuns20b/120b (P6-RUN-*), TestProvenanceFields (P6-PRO), TestDefendedRuns (P6-DEF), TestMatrixSummary (P6-MTX), TestD12FusedV6 (P6-D12-FUSED), TestD12UndefendedV6 (P6-D12-UND), TestD03V6 (P6-D03), TestPreflightCloudAuth (P6-AUTH), TestErrorPolicy (P6-ERR), TestEncodingExplicit (P6-ENC). All test methods initially raise `pytest.skip("Wave 0 stub — implementation pending")`.
- [ ] `tests/test_make_results_v6.py` — stub classes for: TestPathResolver (P6-RES-PR), TestMarkdownDisclosure (P6-MD), TestCsvCompanions (P6-CSV).
- [ ] `tests/conftest.py` — extend if existing fixtures don't already cover the patterns (cross-check existing conftest first; do not duplicate).
- [ ] `pytest --collect-only tests/test_phase6_eval.py tests/test_make_results_v6.py` must succeed (proves stubs are importable + discoverable) before Wave 1 begins.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Cloud auth still valid mid-run | P6-AUTH (extension) | `ollama login` token expiry can happen mid-100-query-run; simulating in unit test would require a mock that breaks halfway. Manual: glance at run logs after each ~5 min checkpoint to confirm queries are still completing. | Run `tail -f` on the active driver's stdout during the ~78 min cloud run; if errors spike past ~5/100 in any single run, abort and re-auth. |
| Heatmap visual correctness | P6-D12-FUSED, P6-D12-UND | matplotlib output size ≠ correctness. Eyeball the v6 heatmaps: viridis_r colormap, expected ASR magnitudes (gpt-oss-20b T1=0%, T2 nonzero per Phase 02.3 lineage), no swapped axes. | Open both PNGs; verify subtitle, axis labels (5 tiers vs 5/4 LLMs), colorbar range matches Phase 03.4-03 conventions. |
| Disclosure line wording readability | P6-MD | Substring assertion catches presence; doesn't catch awkward phrasing. | Read both regenerated .md files top-to-bottom; confirm header reads naturally. |

---

## Validation Sign-Off

- [ ] All 16 P6-* requirements have automated verify (or Wave 0 dependency)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (verified by planner)
- [ ] Wave 0 covers all ❌ W0 references in the test map above
- [ ] No watch-mode flags in any pytest invocation
- [ ] Feedback latency < 30s for quick suite
- [ ] `nyquist_compliant: true` set in frontmatter once all gates pass

**Approval:** pending
