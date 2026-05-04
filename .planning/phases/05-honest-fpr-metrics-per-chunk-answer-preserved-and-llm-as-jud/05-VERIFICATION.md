---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
verified: 2026-05-03T00:00:00Z
status: human_needed
score: 10/11 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Restore logs/judge_fpr_llama.json from HEAD commit before any downstream consumers read it"
    expected: "git checkout HEAD -- logs/judge_fpr_llama.json restores the file with real verdicts (TIE: 187, DEGRADED: 87, PRESERVED: 76), matching ablation_table.json M3 values"
    why_human: "The working-tree judge_fpr_llama.json has been overwritten with all-PRESERVED dry-run placeholders (git status shows ' M logs/judge_fpr_llama.json'). The committed version at HEAD is correct and consistent. A human must decide whether to restore it (git checkout HEAD -- logs/judge_fpr_llama.json) and commit the restoration, or whether the discrepancy is acceptable."
---

# Phase 05: Honest FPR Metrics Verification Report

**Phase Goal:** Compute three honest FPR metrics (per-chunk, answer-preserved, LLM-as-judge) for each of 7 active defense configurations on llama3.2:3b clean queries, extend logs/ablation_table.json with the new metrics, produce a standalone writeup (docs/phase5_honest_fpr.md), and add a post-submission callout in docs/phase3_results.md.
**Verified:** 2026-05-03
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | logs/judge_fpr_llama.json exists with 7 defense keys x 50 verdict records each (350 verdicts total) | VERIFIED (committed) | HEAD commit 1dec223: TIE=187, DEGRADED=87, PRESERVED=76 — real verdicts present; working tree overwritten with dry-run placeholders (see human_verification) |
| 2 | logs/ablation_table.json has per_chunk_fpr, answer_preserved_fpr, judge_fpr, judge_model, judge_n_calls on all 8 ablation rows (7 active + no_defense trivial fill) | VERIFIED | All 8 llama rows have all 5 new keys; git status clean for ablation_table.json |
| 3 | Existing fpr key on every row is unchanged (V-09 back-compat preserved) | VERIFIED | fused_fixed_0.5.fpr=0.76, bert_only.fpr=0.76, perplexity_only.fpr=0.72, imperative_only.fpr=0.88, fingerprint_only.fpr=0.06 — all match expected pre-Phase-5 values |
| 4 | M3 judge_fpr in ablation_table.json is consistent with DEGRADED count / 50 in judge_fpr_llama.json | VERIFIED (committed HEAD) | At HEAD: def02 DEGRADED=12 M3=0.24 (match), bert_only DEGRADED=14 M3=0.28 (match), fused_fixed_0.5 DEGRADED=17 M3=0.34 (match) — all 7 defenses consistent; working tree verdict file has been overwritten (all-PRESERVED), inconsistent with ablation |
| 5 | no_defense row has trivial fill: per_chunk_fpr=0.0, answer_preserved_fpr=0.0, judge_fpr=0.0, judge_n_calls=0 | VERIFIED | Confirmed from working ablation_table.json (git-clean) |
| 6 | scripts/run_judge_fpr.py is a complete, runnable entry point with all required module-level exports | VERIFIED | 467 lines; exports main, DEFENSE_LOG_MAP (7 keys), TOP_K=5, N_CLEAN=50, JUDGE_SYSTEM_PROMPT, JUDGE_USER_TEMPLATE, parse_verdict; Client(host="http://localhost:11434"), temperature=0.0, ollama login bail, dual-shape unwrap, random.Random(42), atomic write (.tmp+replace) |
| 7 | docs/phase5_honest_fpr.md exists with all 6 numbered sections per CONTEXT D-09 | VERIFIED | 133 lines; 6 sections present (## 1. Motivation through ## 6. Limitations); all required content verified |
| 8 | docs/phase5_honest_fpr.md section 4 contains a 4-column results table with all 7 active-defense rows | VERIFIED | All 7 rows present (DEF-02, BERT only, Perplexity only, Imperative only, Fingerprint only, Fused fixed, Fused tuned); numbers read from ablation_table.json |
| 9 | docs/phase5_honest_fpr.md section 3 cites MT-Bench and includes no_defense provenance sentence | VERIFIED | Zheng et al. 2023 arXiv:2306.05685 cited; "The no_defense row reports judge_n_calls = 0 ... judge_model field is populated for schema consistency only" present verbatim |
| 10 | docs/phase3_results.md section 4 ends with a single-paragraph addendum pointing to docs/phase5_honest_fpr.md | VERIFIED | Line 211: "Post-submission addendum (Phase 5)..." present; 13 numbered sections intact |
| 11 | scripts/_build_ablation_table.py docstring has a WARNING comment about Phase 5 schema preservation | VERIFIED | WARNING block present in docstring with run_judge_fpr.py, _assemble_ablation.py, per_chunk_fpr references confirmed via AST docstring extraction |

**Score:** 10/11 truths verified (Truth #4 is verified at HEAD but has a working-tree inconsistency requiring human attention)

### Deferred Items

None.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/conftest.py` | ablation_snapshot + frozen_judge_cache fixtures | VERIFIED | 2 fixtures, importable, ablation_snapshot and frozen_judge_cache both defined |
| `tests/test_judge_fpr.py` | 9 stub tests V-01..V-09 with importlib skip-guard | VERIFIED | 9 test methods, 1 spec_from_file_location, 1 pytestmark skipif, 10 V-tag references (some tests cover multiple V-tags in docstrings) |
| `scripts/run_judge_fpr.py` | Phase 5 honest-FPR entry point >=200 lines | VERIFIED | 467 lines; all required patterns present |
| `logs/judge_fpr_llama.json` | 7 defenses x 50 verdicts, real judge run | VERIFIED (at HEAD) | Committed version has real mixed verdicts (TIE/DEGRADED/PRESERVED); working tree overwritten with all-PRESERVED dry-run placeholders — uncommitted modification |
| `logs/ablation_table.json` | Extended with 5 new keys on all 8 llama rows | VERIFIED | All 8 llama rows have per_chunk_fpr, answer_preserved_fpr, judge_fpr, judge_model, judge_n_calls; git status clean |
| `logs/judge_fpr_llama.json.cache` | Checkpoint cache for re-runs | VERIFIED | Exists (50,279 bytes); contains real verdicts (TIE: 187, DEGRADED: 87, PRESERVED: 76 — same as committed HEAD verdict file) |
| `docs/phase5_honest_fpr.md` | Standalone Phase 5 writeup >=80 lines | VERIFIED | 133 lines; all 6 sections present |
| `docs/phase3_results.md` | With addendum callout to phase5_honest_fpr.md | VERIFIED | Addendum paragraph at line 211; 13 numbered sections preserved |
| `scripts/_build_ablation_table.py` | With Phase 5 schema-preservation WARNING | VERIFIED | WARNING in docstring with all required references |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tests/test_judge_fpr.py` | `scripts/run_judge_fpr.py` | importlib spec_from_file_location | VERIFIED | Pattern present; module-level _AVAILABLE flip gate works |
| `tests/test_judge_fpr.py` | `tests/conftest.py` | pytest fixture injection | VERIFIED | ablation_snapshot and frozen_judge_cache fixture names used in test methods |
| `scripts/run_judge_fpr.py` | `logs/ablation_table.json` | atomic write (.tmp + os.replace) | VERIFIED | atomic_write_json helper used; .tmp suffix pattern confirmed |
| `scripts/run_judge_fpr.py` | `logs/defense_*_llama.json` | json.loads filter paired==False | VERIFIED | DEFENSE_LOG_MAP maps defense keys to defense log filenames |
| `scripts/run_judge_fpr.py` | `scripts/run_judge.py` | verbatim call shape | VERIFIED | Client(host=), temperature=0.0, ollama login bail, dual-shape unwrap, sleep on both branches |
| `docs/phase5_honest_fpr.md` | `logs/ablation_table.json` | Section 4 results table values | VERIFIED | Values match ablation_table.json: def02 M1=0.00, bert_only M1=0.32, fused_fixed_0.5 M1=0.31 (0.308 rounded) |
| `docs/phase5_honest_fpr.md` | `scripts/run_judge_fpr.py` | Section 3 methodology cites entry point | VERIFIED | "python scripts/run_judge_fpr.py --model gpt-oss:20b-cloud --delay 3" cited |
| `docs/phase3_results.md` | `docs/phase5_honest_fpr.md` | Single-paragraph addendum at end of section 4 | VERIFIED | Line 211 references "docs/phase5_honest_fpr.md" |
| `scripts/_build_ablation_table.py` | `scripts/run_judge_fpr.py` | Docstring WARNING referencing re-run path | VERIFIED | "run_judge_fpr.py" appears in docstring WARNING block |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| `logs/ablation_table.json` | per_chunk_fpr, answer_preserved_fpr, judge_fpr | scripts/run_judge_fpr.py M1/M2/M3 computation from defense logs | Yes — M3 validated against cache DEGRADED counts | VERIFIED |
| `logs/judge_fpr_llama.json` (HEAD) | verdicts per defense x query | gpt-oss:20b-cloud pairwise judge run | Yes — TIE/DEGRADED/PRESERVED mixture (not collapsed) | VERIFIED |
| `logs/judge_fpr_llama.json` (working tree) | verdicts | Overwritten by dry-run (all-PRESERVED placeholder) | No — all 350 records show verdict=PRESERVED, raw_response=PRESERVED | HOLLOW (uncommitted) |
| `docs/phase5_honest_fpr.md` | Section 4 table numbers | Read from ablation_table.json verbatim | Yes — values traceable to JSON keys | VERIFIED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| DEFENSE_LOG_MAP has exactly 7 keys | python importlib check on DEFENSE_LOG_MAP | ['def02', 'bert_only', 'perplexity_only', 'imperative_only', 'fingerprint_only', 'fused_fixed_0.5', 'fused_tuned_threshold'] | PASS |
| ablation_table.json has 5 new keys on active defense rows | python check all 7 rows | All 7 rows have per_chunk_fpr, answer_preserved_fpr, judge_fpr, judge_model, judge_n_calls | PASS |
| no_defense trivial fill | python check no_defense row | per_chunk_fpr=0.0, judge_n_calls=0 | PASS |
| M3 consistency at HEAD | python computed vs ablation | def02: 12/50=0.24 match; fused_fixed_0.5: 17/50=0.34 match (all 7 pass) | PASS |
| phase5_honest_fpr.md has 6 sections + 7-row table + MT-Bench | grep checks | 6 sections, 7 rows, arXiv:2306.05685 present | PASS |
| phase3_results.md addendum + 13 section count | grep checks | Addendum at line 211, 13 numbered sections | PASS |
| _build_ablation_table.py docstring has WARNING | AST docstring extraction | WARNING, run_judge_fpr.py, _assemble_ablation.py, per_chunk_fpr all present | PASS |
| M3 consistency in working tree | python computed vs ablation | all 7 defenses show DEGRADED=0 from working-tree file, vs M3=0.04-0.34 in ablation | FAIL (working tree only; HEAD is correct) |

### Requirements Coverage

No requirement IDs declared in PLAN frontmatter (all plans have `requirements: []`). The ROADMAP lists informal requirements that are verified via the must-haves above. All 5 roadmap requirements for Phase 5 are satisfied:
- Per-chunk FPR computed and in ablation_table.json: SATISFIED
- Answer-preserved FPR computed and in ablation_table.json: SATISFIED
- LLM-as-judge FPR computed and in ablation_table.json: SATISFIED
- Ablation table updated with three new columns: SATISFIED
- Writeup sections updated (phase5_honest_fpr.md + phase3_results.md callout): SATISFIED

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `logs/judge_fpr_llama.json` (working tree) | All 350 records | All verdicts=PRESERVED, raw_response=PRESERVED — dry-run placeholder | WARNING | The working tree file is hollow: a consumer reading logs/judge_fpr_llama.json from the working tree would see all-PRESERVED verdicts and compute M3=0.0 for all defenses, contradicting ablation_table.json. The committed HEAD version is correct. |
| `tests/test_judge_fpr.py` | Line 38 | `reason="scripts/run_judge_fpr.py not yet implemented (Phase 5 Plan 02)"` | INFO | Expected design artifact — the skip-guard reason string is intentionally stale after Plan 02 landed. Not a blocker; the skip is no longer active since _AVAILABLE=True. |

### Human Verification Required

### 1. Restore logs/judge_fpr_llama.json from committed version

**Test:** Run `git checkout HEAD -- logs/judge_fpr_llama.json` in the repo root and verify the file has real verdicts.
**Expected:** The file at HEAD has TIE: 187, DEGRADED: 87, PRESERVED: 76 across 350 records (7 defenses x 50 queries). After restoration, python -c "import json; d=json.load(open('logs/judge_fpr_llama.json')); from collections import Counter; all_v=[v['verdict'] for vds in d['verdicts'].values() for v in vds.values()]; print(Counter(all_v))" should print Counter({'TIE': 187, 'DEGRADED': 87, 'PRESERVED': 76}).
**Why human:** The working tree `logs/judge_fpr_llama.json` was overwritten with dry-run placeholder data (all 350 records have verdict="PRESERVED", raw_response="PRESERVED"). The committed version (HEAD commit 1dec223) contains the real judge run output with a mixed verdict distribution that is consistent with ablation_table.json M3 values. The cache file (logs/judge_fpr_llama.json.cache, not modified) also has the real verdicts, confirming the committed version was produced from a genuine cloud-LLM judge run. The restoration is a single git command but requires a human to decide and execute it, since it would be the only uncommitted change in logs/ needing a follow-up commit.

### Gaps Summary

No blocking gaps were found against the committed codebase. The phase goal is substantively achieved: three honest FPR metrics are computed, ablation_table.json is extended, docs/phase5_honest_fpr.md is complete, and docs/phase3_results.md has the addendum.

One working-tree inconsistency requires human attention: `logs/judge_fpr_llama.json` has been overwritten with all-PRESERVED dry-run placeholders since the last commit. The file is shown as modified in git status (` M logs/judge_fpr_llama.json`). The committed version at HEAD is correct and consistent with all other artifacts. A grader using git checkout would see the correct file; a grader reading the working tree would see hollow data. The cache file (logs/judge_fpr_llama.json.cache) preserves the real verdicts and is unaffected.

---

_Verified: 2026-05-03_
_Verifier: Claude (gsd-verifier)_
