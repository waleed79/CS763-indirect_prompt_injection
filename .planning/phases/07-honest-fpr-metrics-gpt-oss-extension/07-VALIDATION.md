---
phase: 7
slug: honest-fpr-metrics-gpt-oss-extension
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-04
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `07-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 |
| **Config file** | none — pytest default discovery on `tests/test_*.py` |
| **Quick run command** | `pytest tests/test_phase7_judge_fpr.py tests/test_make_results_v7.py -x` |
| **Full suite command** | `pytest tests/ -x` |
| **Estimated runtime** | ~5 sec quick · ~30–60 sec full suite |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_phase7_judge_fpr.py tests/test_make_results_v7.py -x` (~5 sec; pure unit tests, no cloud)
- **After every plan wave:** Run `pytest tests/ -x` (~30–60 sec; full suite incl. Phase 3/4/5/6 regressions)
- **Before `/gsd-verify-work`:** Full suite green AND a manual `--dry-run` of `scripts/run_judge_fpr_gptoss.py` showing M1 numbers without cloud calls
- **Max feedback latency:** 60 seconds
- **Single-seed convention inherited (Phase 5 D-05 / Phase 7 D-11):** No per-call resampling; the 200-call run is one observation per `(cell, query)` pair

---

## Per-Task Verification Map

| Test ID | Plan | Wave | Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|----------|-----------|-------------------|-------------|--------|
| P7-M1 | TBD | 1 | M1 numerator | M1 = sum(chunks_removed) / (TOP_K × N_CLEAN) for each of 4 cells | unit | `pytest tests/test_phase7_judge_fpr.py::TestM1Numerator -x` | ❌ W0 | ⬜ pending |
| P7-M2 | TBD | 1 | M2 aggregation | M2 = count(chunks_removed > 0 AND DEGRADED) / N_CLEAN | unit | `pytest tests/test_phase7_judge_fpr.py::TestM2Aggregation -x` | ❌ W0 | ⬜ pending |
| P7-M3 | TBD | 1 | M3 aggregation | M3 = count(DEGRADED) / N_CLEAN; TIE + refusal collapse to PRESERVED | unit | `pytest tests/test_phase7_judge_fpr.py::TestM3Aggregation -x` | ❌ W0 | ⬜ pending |
| P7-LCR | TBD | 1 | v6 schema compat | `load_clean_records(v6_cell_path)` returns exactly 50 records | unit | `pytest tests/test_phase7_judge_fpr.py::TestLoadCleanRecordsV6 -x` | ❌ W0 | ⬜ pending |
| P7-UTF | TBD | 0 | UTF-8 decode | `load_clean_records` reads v6 cell with non-ASCII answer chars without UnicodeDecodeError | unit | `pytest tests/test_phase7_judge_fpr.py::TestUtf8Encoding -x` | ❌ W0 | ⬜ pending |
| P7-PATH | TBD | 1 | path map loud-fail | `CELL_LOG_MAP` and `OFF_LOG_MAP` paths all resolve to existing files at startup | unit | `pytest tests/test_phase7_judge_fpr.py::TestPathMapsLoudFail -x` | ❌ W0 | ⬜ pending |
| P7-CKEY | TBD | 1 | composite keys | Composite key map yields exactly 4 keys: `gptoss20b_cloud__{fused,def02}` and `gptoss120b_cloud__{fused,def02}` | unit | `pytest tests/test_phase7_judge_fpr.py::TestCompositeKeys -x` | ❌ W0 | ⬜ pending |
| P7-OUT-J-SHAPE | TBD | 2 | ablation shape | `logs/ablation_table_gptoss_v7.json` is a flat dict with exactly 4 entries; each has D-02 fields | unit | `pytest tests/test_phase7_judge_fpr.py::TestAblationV7Shape -x` | ❌ W0 | ⬜ pending |
| P7-OUT-J-NOROW | TBD | 2 | no trivial row | `logs/ablation_table_gptoss_v7.json` does NOT contain a trivial `no_defense` row (D-03) | unit | `pytest tests/test_phase7_judge_fpr.py::TestNoTrivialRow -x` | ❌ W0 | ⬜ pending |
| P7-OUT-V-SHAPE | TBD | 2 | verdicts shape | `logs/judge_fpr_gptoss_v7.json` matches D-04: `verdicts[model][defense][qid]` | unit | `pytest tests/test_phase7_judge_fpr.py::TestVerdictsV7Shape -x` | ❌ W0 | ⬜ pending |
| P7-OUT-V-COUNT | TBD | 2 | verdict count | `logs/judge_fpr_gptoss_v7.json` contains exactly 200 verdict records (4 × 50) | unit | `pytest tests/test_phase7_judge_fpr.py::TestVerdictCount200 -x` | ❌ W0 | ⬜ pending |
| P7-OUT-V-FIELDS | TBD | 2 | verdict fields | Each verdict record has `verdict`, `ab_assignment`, `raw_response`, `retry_count` (D-04 + Phase 5 D-12) | unit | `pytest tests/test_phase7_judge_fpr.py::TestVerdictRecordFields -x` | ❌ W0 | ⬜ pending |
| P7-RESV | TBD | 1 | v7 resolver | `make_results.py` v7 resolver returns Path when v7 ablation exists, None otherwise | unit | `pytest tests/test_make_results_v7.py::TestV7Resolver -x` | ❌ W0 | ⬜ pending |
| P7-RESV-EMIT | TBD | 1 | v7 emit | When v7 file present, `docs/results/honest_fpr_gptoss_v7.{md,csv}` produced; when absent, no v7 emit | unit | `pytest tests/test_make_results_v7.py::TestV7Emit -x` | ❌ W0 | ⬜ pending |
| P7-RESV-COMPAT | TBD | 1 | regression | Existing `tests/test_make_results.py` and `tests/test_make_results_v6.py` stay green | regression | `pytest tests/test_make_results.py tests/test_make_results_v6.py -x` | ✅ existing | ⬜ pending |
| P7-DOC-UNTOUCHED | TBD | 3 | prose preserved | Original Phase 5 prose in `docs/phase5_honest_fpr.md` (above addendum) is bit-for-bit unchanged | unit | `pytest tests/test_make_results_v7.py::TestPhase5ProseUntouched -x` | ❌ W0 | ⬜ pending |
| P7-DOC-ADDENDUM | TBD | 3 | addendum present | `docs/phase5_honest_fpr.md` contains `## Phase 7 addendum: gpt-oss extension` heading exactly once | unit | `pytest tests/test_make_results_v7.py::TestAddendumPresent -x` | ❌ W0 | ⬜ pending |
| P7-DOC-TABLE-10ROW | TBD | 3 | 10-row table | The addendum's M1/M2/M3 table has exactly 10 data rows (6 llama + 2 gpt-oss-20b + 2 gpt-oss-120b) | unit | `pytest tests/test_make_results_v7.py::TestAddendumTable10Rows -x` | ❌ W0 | ⬜ pending |
| P7-DOC-PHASE3-UNTOUCHED | TBD | 3 | submitted artifact | `docs/phase3_results.md` is bit-for-bit unchanged compared to git HEAD | unit | `pytest tests/test_make_results_v7.py::TestPhase34NotEdited -x` | ❌ W0 | ⬜ pending |
| P7-INHERIT-PROMPT | TBD | 1 | prompt inherited | Phase 7 script imports `JUDGE_SYSTEM_PROMPT` and `JUDGE_USER_TEMPLATE` from `scripts/run_judge_fpr.py` (no redefinition) | unit | `pytest tests/test_phase7_judge_fpr.py::TestPromptInherited -x` | ❌ W0 | ⬜ pending |
| P7-INHERIT-PARSE | TBD | 1 | parser inherited | Phase 7 script reuses `parse_verdict()` from Phase 5 (no copy-pasted parser) | unit | `pytest tests/test_phase7_judge_fpr.py::TestParserInherited -x` | ❌ W0 | ⬜ pending |
| P7-CACHE | TBD | 2 | cache resume | Second invocation with `.cache` file present skips judge calls | integration | `pytest tests/test_phase7_judge_fpr.py::TestCacheResume -x` | ❌ W0 | ⬜ pending |
| P7-DRYRUN | TBD | 1 | dry-run M1 only | `--dry-run` flag computes M1 only, makes zero cloud calls | integration | `pytest tests/test_phase7_judge_fpr.py::TestDryRunNoCloud -x` | ❌ W0 | ⬜ pending |
| P7-AUTH | TBD | 2 | auth escalation | `JudgeAuthError` from a mocked failing client returns rc=1 cleanly without aborting mid-cell | integration | `pytest tests/test_phase7_judge_fpr.py::TestAuthEscalation -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Plan column = TBD until plan-phase assigns each test ID to a specific PLAN.md file.*

---

## Wave 0 Requirements

- [ ] `tests/test_phase7_judge_fpr.py` — stubs for P7-M*, P7-LCR, P7-UTF, P7-PATH, P7-CKEY, P7-OUT-*, P7-INHERIT-*, P7-CACHE, P7-DRYRUN, P7-AUTH
- [ ] `tests/test_make_results_v7.py` — stubs for P7-RESV, P7-RESV-EMIT, P7-DOC-*, plus regression-stays-green check for `test_make_results.py` and `test_make_results_v6.py`
- [ ] No new framework install needed (pytest 9.0.3 already present)
- [ ] Test stubs MUST use `importlib.util.spec_from_file_location` to load `scripts/run_judge_fpr.py` and `scripts/run_judge_fpr_gptoss.py` (Phase 03.4-01 / 06-01 lineage). Skip-guards for `_OLLAMA_AVAILABLE` and for the v7 file's existence let `pytest --collect-only` succeed before production code lands.

---

## Failure-Mode Coverage (what FAILS if X is wrong)

- **M1 wrong** → `TestM1Numerator` fails (synthetic 5-record fixture with known `chunks_removed` total)
- **M2 wrong** → `TestM2Aggregation` fails (synthetic: 3 records with `chunks_removed > 0` of which 1 DEGRADED → M2 = 1/50 = 0.02)
- **M3 wrong** → `TestM3Aggregation` fails (synthetic: 2 DEGRADED of 50 → M3 = 0.04; TIE/refusal collapse to PRESERVED)
- **v7 path-resolver mis-routes** → `TestV7Emit` (file present but None returned) OR `TestV7Resolver::test_returns_none_when_absent` (file absent but path returned) fails
- **Addendum table omits a row** → `TestAddendumTable10Rows` fails (regex/parser counts pipe-table data rows; expects exactly 10)
- **Phase 5 deliverable mutated** → `TestPhase5ProseUntouched` OR git-diff regression on `logs/ablation_table.json` / `logs/judge_fpr_llama.json` fails
- **UTF-8 decode bypassed** → `TestUtf8Encoding` fails on first cell with smart quotes

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Cross-LLM analysis paragraphs in addendum read coherently | D-07 | Quality of prose is subjective; cannot grep | Reviewer reads §7 addendum end-to-end on PR; checks ≥1 substantive interpretation present |
| Ollama cloud auth state at run-start | (Phase 6 STATE pitfall) | Auth tokens expire silently; preflight is a 1-call live check | Run preflight check before `--dry-run`; if `JudgeAuthError`, run `ollama login` |
| Wall-clock budget honored (~26 min cloud + ~5 min downstream) | ROADMAP | Wall-clock is observed, not asserted | Operator times the M3 wave; abort if >60 min |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`tests/test_phase7_judge_fpr.py`, `tests/test_make_results_v7.py`)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
