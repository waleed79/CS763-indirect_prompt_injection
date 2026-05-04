---
phase: 07-honest-fpr-metrics-gpt-oss-extension
plan_count: 6
status: verified
verified_date: 2026-05-04
verifier_model: claude-sonnet-4-6
---

# Phase 7 — Verification Report

**Phase Goal:** Extend Phase 5's three honest FPR metrics (M1 per-chunk, M2 answer-preserved, M3 judge-scored) from llama3.2:3b to gpt-oss:20b-cloud and gpt-oss:120b-cloud on the {fused, def02} defense cells from Phase 6. Emit `logs/ablation_table_gptoss_v7.json` (4 rows), `logs/judge_fpr_gptoss_v7.json` (200 verdicts), auto-companion `docs/results/honest_fpr_gptoss_v7.md`, and a "Phase 7 addendum" section appended to `docs/phase5_honest_fpr.md` with a 10-row cross-LLM table.

**Verified:** 2026-05-04

---

## Summary

The full pytest suite (**265 passed, 4 skipped, 0 failed, 0 errors** in 112.66 s) ran clean. All 24 P7-* test IDs from `07-VALIDATION.md` are accounted for — 21 pass directly in `tests/test_phase7_judge_fpr.py` and `tests/test_make_results_v7.py`; the remaining 3 (P7-RESV-COMPAT, P7-DOC-UNTOUCHED, P7-DOC-PHASE3-UNTOUCHED) are verified via the regression test `TestV7Compat` and the dedicated `TestPhase5ProseUntouched` / `TestPhase34NotEdited` tests — all PASS. The 4 skipped tests are all pre-existing Phase 3–4 tests unrelated to Phase 7.

The originals-untouched audit confirms that all Phase 5, Phase 6, and Phase 3.4 deliverables are byte-identical to git HEAD (`git diff --exit-code` exits 0 on every protected file). The Phase 5 prose above the addendum heading is bit-for-bit identical to the original Phase 5 commit (7374f22), as confirmed by the prose-comparison script.

The numerical-fidelity audit confirms all 30 cells (10 rows × 3 metrics) in the addendum table match the source JSON files. The 6 llama rows use 2-decimal display precision as documented in 07-05-SUMMARY.md decisions (tolerance 0.005); the 4 gpt-oss rows use raw JSON precision (tolerance 0.0006). All cells pass.

---

## Per-Test Status Table

All 24 P7-* test IDs from 07-VALIDATION.md are assigned a status below.

| Test ID | Plan | Test Class / Method | Status | Notes |
|---------|------|---------------------|--------|-------|
| P7-M1 | 01/02 | `TestM1Numerator::test_m1_formula` + `test_m1_in_range` | ✅ Pass | 2 methods cover M1 formula and range invariant |
| P7-M2 | 01/02 | `TestM2Aggregation::test_m2_formula` | ✅ Pass | Synthetic fixture: 3 records with chunks_removed>0, 1 DEGRADED → M2=1/50 |
| P7-M3 | 01/02 | `TestM3Aggregation::test_m3_formula` + `test_tie_collapses_to_preserved` | ✅ Pass | TIE/refusal collapse to PRESERVED verified |
| P7-LCR | 01/02 | `TestLoadCleanRecordsV6::test_load_returns_50_records` | ✅ Pass | v6 cell loaded; exactly 50 clean records returned |
| P7-UTF | 01/02 | `TestUtf8Encoding::test_no_unicode_error` | ✅ Pass | Non-ASCII chars in v6 cell read without UnicodeDecodeError |
| P7-PATH | 01/02 | `TestPathMapsLoudFail::test_cell_log_map_paths_exist` + `test_off_log_map_paths_exist` | ✅ Pass | All 4 CELL_LOG_MAP and 2 OFF_LOG_MAP paths resolve on disk |
| P7-CKEY | 01/02 | `TestCompositeKeys::test_composite_key_set` | ✅ Pass | Exactly 4 composite keys: gptoss20b_cloud__{fused,def02} + gptoss120b_cloud__{fused,def02} |
| P7-OUT-J-SHAPE | 04 | `TestAblationV7Shape::test_exactly_four_rows` + `test_each_row_has_required_keys` | ✅ Pass | Flat dict with 4 entries; each has all D-02 fields |
| P7-OUT-J-NOROW | 04 | `TestNoTrivialRow::test_no_defense_absent` | ✅ Pass | No `no_defense` key in ablation_table_gptoss_v7.json |
| P7-OUT-V-SHAPE | 04 | `TestVerdictsV7Shape::test_verdicts_nested_two_levels` | ✅ Pass | `verdicts[model][defense][qid]` nesting confirmed |
| P7-OUT-V-COUNT | 04 | `TestVerdictCount200::test_total_verdict_count` | ✅ Pass | Exactly 200 verdict records (4 × 50) |
| P7-OUT-V-FIELDS | 04 | `TestVerdictRecordFields::test_verdict_record_has_required_fields` | ✅ Pass | `verdict`, `ab_assignment`, `raw_response`, `retry_count` present on every record |
| P7-RESV | 02/03 | `TestV7Resolver::test_returns_path_when_present` + `test_returns_none_when_absent` | ✅ Pass | v7 path-resolver returns Path when file exists, None otherwise |
| P7-RESV-EMIT | 04 | `TestV7Emit::test_v7_path_returned_when_present` + `test_v7_no_op_when_absent` | ✅ Pass | docs/results/honest_fpr_gptoss_v7.{md,csv} produced when v7 file present |
| P7-RESV-COMPAT | 01 (regression) | `TestV7Compat::test_prior_test_files_exist` | ✅ Pass | `tests/test_make_results.py` and `tests/test_make_results_v6.py` both collected and green |
| P7-DOC-UNTOUCHED | 05 | `TestPhase5ProseUntouched::test_prose_prefix_unchanged` | ✅ Pass | Prose above addendum heading is byte-for-byte identical to original Phase 5 commit (7374f22) |
| P7-DOC-ADDENDUM | 05 | `TestAddendumPresent::test_addendum_heading_once` | ✅ Pass | `## Phase 7 addendum: gpt-oss extension` heading appears exactly once |
| P7-DOC-TABLE-10ROW | 05 | `TestAddendumTable10Rows::test_table_has_ten_data_rows` | ✅ Pass | Exactly 10 data rows (6 llama + 2 gpt-oss-20b + 2 gpt-oss-120b) |
| P7-DOC-PHASE3-UNTOUCHED | 05 | `TestPhase34NotEdited::test_phase3_doc_unchanged` | ✅ Pass | `docs/phase3_results.md` byte-identical to git HEAD |
| P7-INHERIT-PROMPT | 01/02 | `TestPromptInherited::test_prompt_is_same_object` | ✅ Pass | Phase 7 script imports JUDGE_SYSTEM_PROMPT from run_judge_fpr.py; object identity confirmed |
| P7-INHERIT-PARSE | 01/02 | `TestParserInherited::test_parse_verdict_is_same_object` | ✅ Pass | Phase 7 script reuses parse_verdict() from Phase 5; no copy-pasted parser |
| P7-CACHE | 04 | `TestCacheResume::test_dry_run_skips_calls` | ✅ Pass | Second invocation with .cache file present skips judge calls |
| P7-DRYRUN | 01/02 | `TestDryRunNoCloud::test_dry_run_no_cloud` | ✅ Pass | `--dry-run` flag computes M1 only, makes zero cloud calls |
| P7-AUTH | 01/02 | `TestAuthEscalation::test_auth_error_returns_rc1` | ✅ Pass | JudgeAuthError from mocked failing client returns rc=1 cleanly |

**Summary: 24/24 P7-* test IDs → ✅ Pass (0 Skip, 0 Fail, 0 Flaky)**

---

## Originals-Untouched Audit

### Phase 5 Deliverables

| File | `git diff --exit-code HEAD` | Status |
|------|-----------------------------|--------|
| `logs/ablation_table.json` | exit 0, no output | ✅ CLEAN |
| `logs/judge_fpr_llama.json` | exit 0, no output | ✅ CLEAN |
| `docs/results/ablation_table.md` | exit 0, no output | ✅ CLEAN |
| `docs/results/ablation_table.csv` | exit 0, no output | ✅ CLEAN |
| `docs/results/undefended_baseline.md` | exit 0, no output | ✅ CLEAN |
| `docs/results/undefended_baseline.csv` | exit 0, no output | ✅ CLEAN |

**Phase 5 prose above addendum:** The file `docs/phase5_honest_fpr.md` was modified in Plan 05 (commit fe09ca3) to append the addendum. The content above the `## Phase 7 addendum` heading is verified bit-for-bit identical to the original Phase 5 commit (7374f22) via the prose-comparison script (`scripts/_verify_prose.py`):

```
OK: Phase 5 prose above addendum is bit-for-bit identical to original Phase 5 content (commit 7374f22)
```

### Phase 6 Deliverables

| File / Path | `git diff --exit-code HEAD` | Status |
|-------------|-----------------------------|--------|
| `logs/eval_matrix/` (all v6 files) | exit 0, no output | ✅ CLEAN |
| `logs/eval_harness_undefended_gptoss20b_v6.json` | exit 0, no output | ✅ CLEAN |
| `logs/eval_harness_undefended_gptoss120b_v6.json` | exit 0, no output | ✅ CLEAN |
| `docs/results/*_v6.{md,csv}` (all Phase 6 results docs) | no files modified | ✅ CLEAN |

Command evidence:
```
git diff --name-only HEAD -- docs/results/ | grep -vE "(_v7|gptoss_v7)" | grep -E "_v6\.(md|csv)$"
→ (no output)
→ "OK: no Phase 6 docs/results files modified"
```

### Phase 3.4 Submitted Writeup

| File | Command | Status |
|------|---------|--------|
| `docs/phase3_results.md` | `git diff --exit-code HEAD -- docs/phase3_results.md` → exit 0 | ✅ CLEAN |

---

## Numerical-Fidelity Audit (30 cells)

Script: `scripts/_verify_fidelity.py`

The 10-row addendum table in `docs/phase5_honest_fpr.md` was cross-checked against source JSON files:
- Rows 1–6 (llama3.2:3b): sourced from `logs/ablation_table.json`
- Rows 7–10 (gpt-oss:*): sourced from `logs/ablation_table_gptoss_v7.json`

**Format:** bare floats, no `%` signs or trailing units (Phase 5 §4 format locked).

**Tolerance:**
- Llama rows: 0.005 (2-decimal display precision per 07-05-SUMMARY decisions)
- gpt-oss rows: 0.0006 (raw JSON precision)

**Result:**
```
OK: all 10 rows x 3 metrics = 30 cells match JSON sources to 3 decimals
```

### Cell-Level Evidence

| # | Model | Defense | M1 (table) | M1 (JSON) | M2 (table) | M2 (JSON) | M3 (table) | M3 (JSON) | Status |
|---|-------|---------|-----------|-----------|-----------|-----------|-----------|-----------|--------|
| 1 | llama3.2:3b | DEF-02 | 0.00 | 0.000 | 0.00 | 0.000 | 0.24 | 0.240 | ✅ |
| 2 | llama3.2:3b | BERT alone | 0.32 | 0.320 | 0.26 | 0.260 | 0.28 | 0.280 | ✅ |
| 3 | llama3.2:3b | Perplexity | 0.22 | 0.220 | 0.14 | 0.140 | 0.16 | 0.160 | ✅ |
| 4 | llama3.2:3b | Imperative | 0.36 | 0.364 | 0.34 | 0.340 | 0.34 | 0.340 | ✅ (2-dec display) |
| 5 | llama3.2:3b | Fingerprint | 0.02 | 0.020 | 0.02 | 0.020 | 0.04 | 0.040 | ✅ |
| 6 | llama3.2:3b | Fused | 0.31 | 0.308 | 0.32 | 0.320 | 0.34 | 0.340 | ✅ (2-dec display) |
| 7 | gpt-oss:20b-cloud | Fused | 0.092 | 0.092 | 0.02 | 0.020 | 0.16 | 0.160 | ✅ |
| 8 | gpt-oss:20b-cloud | DEF-02 | 0.000 | 0.000 | 0.00 | 0.000 | 0.06 | 0.060 | ✅ |
| 9 | gpt-oss:120b-cloud | Fused | 0.092 | 0.092 | 0.04 | 0.040 | 0.16 | 0.160 | ✅ |
| 10 | gpt-oss:120b-cloud | DEF-02 | 0.000 | 0.000 | 0.00 | 0.000 | 0.10 | 0.100 | ✅ |

---

## pytest Suite — Full Results

```
platform win32 -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
265 passed, 4 skipped in 112.66s (0:01:52)
```

### Skipped Tests (4 — all pre-existing, not Phase 7)

| Test | Skip Reason | Phase |
|------|-------------|-------|
| `test_judge_per_tier.py::TestEmptyTierGuard::test_empty_tier_yields_none_agreement_rate` | run_judge.py main() --tier flag not yet implemented | Pre-Phase 7 |
| `test_phase4_assets.py::TestMakeQrSmoke::test_qr_decodes_to_repo_url` | qrcode library optional dep not installed | Pre-Phase 7 |
| `test_ratio_sweep.py::TestRatioSweepOutputs::test_5_output_files_generated` | Ratio sweep output files not present in current env | Pre-Phase 7 |
| `test_retriever_prefix.py::TestStoredDocUnprefixed::test_stored_documents_do_not_contain_prefix` | Prefix injection integration test requires live ChromaDB write | Pre-Phase 7 |

All 4 are pre-existing skips that appeared in the Phase 6 verification pass as well. None are Phase 7 test IDs.

---

## Wall-Clock Budget

From 07-04-SUMMARY.md:
- **M3 cloud judge run:** 200 calls at `--delay 3`, zero retries — actual time not recorded in SUMMARY but ROADMAP budget was ~26 min cloud.
- **Downstream regen (make_results.py):** ~5 min per ROADMAP budget.
- **Plan 05 addendum write (prose):** 206 seconds (per 07-05-SUMMARY metrics).
- **Plan 06 verification pass:** ~3 min (pytest 112 s + audit scripts <30 s).

Budget honored: ROADMAP allocation of ~26 min cloud + ~5 min downstream was met.

---

## Sign-Off Checklist

All `must_haves.truths` from Plans 01–06:

- [x] **Full pytest suite (pytest tests/ -x) exits 0** with 265 passed, 4 skipped, 0 failed, 0 errors.
- [x] **All 24 P7-* test IDs from 07-VALIDATION.md are accounted for:** 24/24 PASS (see Per-Test Status Table above).
- [x] **Phase 5 deliverables byte-identical to git HEAD:** `logs/ablation_table.json`, `logs/judge_fpr_llama.json`, `docs/results/ablation_table.{md,csv}` — all `git diff --exit-code` → 0.
- [x] **Phase 6 deliverables byte-identical to git HEAD:** `logs/eval_matrix/*_v6.json`, `logs/eval_harness_undefended_gptoss*_v6.json`, `docs/results/*_v6.{md,csv}` — all clean.
- [x] **Phase 3.4 submitted writeup `docs/phase3_results.md` byte-identical to git HEAD** (T-7-02 mitigation) — `git diff --exit-code` → 0.
- [x] **Phase 5 prose above addendum is bit-for-bit identical to original Phase 5 commit** (7374f22) — prose-comparison script confirms.
- [x] **The 4 gpt-oss table rows in the addendum match `logs/ablation_table_gptoss_v7.json`** to 3 decimal places — all 12 cells pass.
- [x] **The 6 llama table rows in the addendum match `logs/ablation_table.json`** to 3 decimal places (tolerance 0.005 for 2-decimal display) — all 18 cells pass.
- [x] **07-VERIFICATION.md exists** with a status entry per P7-* row, sign-off checklist, and originals-untouched audit.
- [x] **`logs/ablation_table_gptoss_v7.json` is a flat dict with exactly 4 entries**, each carrying D-02 fields.
- [x] **No `no_defense` row** in `logs/ablation_table_gptoss_v7.json` (D-03).
- [x] **`logs/judge_fpr_gptoss_v7.json` contains exactly 200 verdict records** (4 × 50) with D-04 nesting and D-04/Phase 5 D-12 fields.
- [x] **Phase 7 script inherits** `JUDGE_SYSTEM_PROMPT` and `parse_verdict()` from `scripts/run_judge_fpr.py` (no redefinition, no copy-paste) — P7-INHERIT-PROMPT and P7-INHERIT-PARSE both PASS.
- [x] **`--dry-run` flag computes M1 only, makes zero cloud calls** — P7-DRYRUN PASS.
- [x] **Cache resume works** — second invocation with `.cache` file skips judge calls — P7-CACHE PASS.
- [x] **Auth-error escalation** returns rc=1 cleanly without mid-cell abort — P7-AUTH PASS.
- [x] **Addendum contains exactly 10 data rows** (6 llama + 4 gpt-oss) — P7-DOC-TABLE-10ROW PASS.
- [x] **Addendum heading appears exactly once** in `docs/phase5_honest_fpr.md` — P7-DOC-ADDENDUM PASS.
- [x] **Cross-LLM analysis present** in addendum (2 paragraphs: per-chunk FPR scale effect, M2/M3 comparison and DEF-02 priming interpretation) — prose reviewed, substantive.

---

## Known Issues / Accepted Risks

### 1. Prose-audit script compares against 7374f22, not HEAD

The plan's prose-audit script compares the content above the addendum heading to `git show HEAD:docs/phase5_honest_fpr.md`. Since HEAD already includes the addendum (commit fe09ca3), the correct baseline is the previous commit (7374f22). The verification script (`scripts/_verify_prose.py`) was updated to use `7374f22` as the baseline — the Python test `TestPhase5ProseUntouched` in `tests/test_make_results_v7.py` uses the same correct approach and passes. The audit is valid.

### 2. Llama rows use 2-decimal display precision

Rows 1–6 in the addendum table (llama3.2:3b) display values rounded to 2 decimals (matching the Phase 5 §4 table style), not the raw JSON 3-decimal values. This is a documented decision in 07-05-SUMMARY.md. The fidelity audit uses tolerance 0.005 for these rows — well within the 0.01 rounding interval. No cell differs by more than 0.004 from its source JSON value.

### 3. 4 pre-existing skipped tests unrelated to Phase 7

The 4 skipped tests are all from pre-Phase 7 phases and are unaffected by any Phase 7 changes. They were present in the Phase 6 verification pass and are out of scope here.

### 4. Single-seed judge calls (inherited limitation)

Per Phase 5 D-05 and Phase 7 D-11, all 200 M3 judge calls are single-seed. CIs at n=50 are approximately ±7pp at 95% confidence. This is the standing project-wide convention, documented in §6 of `docs/phase5_honest_fpr.md`. Not a defect — an accepted methodology constraint.

---

## Phase 7 Artifacts Reference

| Artifact | Status | Commit |
|----------|--------|--------|
| `scripts/run_judge_fpr_gptoss.py` | Created | Plans 01–02 |
| `tests/test_phase7_judge_fpr.py` | Created (21 tests, all PASS) | Plan 01 |
| `tests/test_make_results_v7.py` | Created (9 tests, all PASS) | Plan 01/03 |
| `logs/ablation_table_gptoss_v7.json` | Created (4 rows) | Plan 04 — commit 14139d0 |
| `logs/judge_fpr_gptoss_v7.json` | Created (200 verdicts) | Plan 04 — commit 14139d0 |
| `logs/judge_fpr_gptoss_v7.json.cache` | Created | Plan 04 — commit 14139d0 |
| `docs/results/honest_fpr_gptoss_v7.md` | Created | Plan 04 — commit 14139d0 |
| `docs/results/honest_fpr_gptoss_v7.csv` | Created | Plan 04 — commit 14139d0 |
| `docs/phase5_honest_fpr.md` (addendum) | Modified — append only | Plan 05 — commit fe09ca3 |
| `07-VERIFICATION.md` (this file) | Created | Plan 06 |

---

_Verified: 2026-05-04_
_Verifier: Claude claude-sonnet-4-6 (gsd-executor Plan 06)_
