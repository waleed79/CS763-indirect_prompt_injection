---
phase: 5
slug: honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-03
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Drives `tests/test_judge_fpr.py` (Wave 0 stubs).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 (already in env, see `tests/__pycache__/test_corpus.cpython-311-pytest-9.0.3.pyc`) |
| **Config file** | none — pytest auto-discovers `tests/test_*.py` |
| **Quick run command** | `pytest tests/test_judge_fpr.py -x -q` |
| **Full suite command** | `pytest tests/ -x` |
| **Estimated runtime** | <10 seconds for `test_judge_fpr.py`; no judge calls in tests (uses fixture cache) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_judge_fpr.py -x -q`
- **After every plan wave:** Run `pytest tests/ -x`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~10 seconds (no live LLM calls in tests)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|----------|-----------|-------------------|-------------|--------|
| V-01 | TBD | 1 | M1 numerator on `no_defense` row equals 0 (chunks_removed = 0 by construction) | unit | `pytest tests/test_judge_fpr.py::test_no_defense_zero -x` | ❌ W0 | ⬜ pending |
| V-02 | TBD | 1 | M2 numerator ≤ M1 numerator (degraded set ⊆ flagged set) | unit | `pytest tests/test_judge_fpr.py::test_m2_le_m1 -x` | ❌ W0 | ⬜ pending |
| V-03 | TBD | 1 | `judge_n_calls` ≥ 50 for each defense row (retries possible) | unit | `pytest tests/test_judge_fpr.py::test_judge_n_calls_min -x` | ❌ W0 | ⬜ pending |
| V-04 | TBD | 1 | `0.0 ≤ per_chunk_fpr ≤ 1.0` for all 6 defense rows | unit | `pytest tests/test_judge_fpr.py::test_m1_in_range -x` | ❌ W0 | ⬜ pending |
| V-05 | TBD | 1 | M1 numerator ≤ 250 (top_k * 50) for each row — sanity bound | unit | `pytest tests/test_judge_fpr.py::test_m1_numerator_bounded -x` | ❌ W0 | ⬜ pending |
| V-06 | TBD | 1 | Re-running with cached verdicts produces byte-identical `ablation_table.json` (determinism / idempotence) | unit | `pytest tests/test_judge_fpr.py::test_idempotent_with_cache -x` | ❌ W0 | ⬜ pending |
| V-07 | TBD | 1 | M3 numerator equals count of `verdict == DEGRADED` in per-cell file | unit | `pytest tests/test_judge_fpr.py::test_m3_consistency -x` | ❌ W0 | ⬜ pending |
| V-08 | TBD | 1 | Schema check: each defense row has the 5 new keys (`per_chunk_fpr`, `answer_preserved_fpr`, `judge_fpr`, `judge_model`, `judge_n_calls`) plus existing keys | unit | `pytest tests/test_judge_fpr.py::test_schema_extension -x` | ❌ W0 | ⬜ pending |
| V-09 | TBD | 1 | Existing `fpr` key value unchanged on every row (back-compat with Phase 3.4 `make_results.py`) | unit | `pytest tests/test_judge_fpr.py::test_back_compat_fpr_unchanged -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Plan IDs (`Plan` column) populated by gsd-planner during planning.*

---

## Wave 0 Requirements

- [ ] `tests/test_judge_fpr.py` — stubs for V-01..V-09 covering all three metrics + schema + idempotence
- [ ] `tests/conftest.py` — fixture providing a frozen `judge_fpr_llama.json` cache + a frozen pre/post `ablation_table.json` snapshot for V-06 / V-09
- [ ] (No new framework install — pytest 9.0.3 already in env)

Use `importlib.util.spec_from_file_location` to load `scripts/run_judge_fpr.py` (matches Phase 3.2 / 3.4 test pattern). Wave 0 stubs use `pytest.skip("module not yet implemented")` until production code lands.

---

## Manual-Only Verifications

| Behavior | Why Manual | Test Instructions |
|----------|------------|-------------------|
| Live judge run reproduces verdicts | Requires `gpt-oss:20b-cloud` cloud auth + ~15-45 min wall clock; cannot run in unit tests | `python scripts/run_judge_fpr.py --delay 3` then diff `logs/judge_fpr_llama.json` against committed snapshot |
| `docs/phase5_honest_fpr.md` table renders correctly | Markdown table layout is visual | Open in renderer, confirm 4-column FPR table × 6 defense rows |
| Phase 3.4 figures still regenerate cleanly | `make_figures.py` outputs PNGs | `python scripts/make_figures.py` → no errors, output PNGs match prior commit hashes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all V-01..V-09 stubs
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter after all tests green

**Approval:** pending
