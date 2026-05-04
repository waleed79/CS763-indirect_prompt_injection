---
status: complete
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
source: 05-01-SUMMARY.md, 05-02-SUMMARY.md, 05-03-SUMMARY.md, 05-04-SUMMARY.md, 05-05-SUMMARY.md, 05-REVIEW-FIX.md, 06-VERIFICATION.md
started: 2026-05-04T09:00:00Z
updated: 2026-05-04T09:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Production md5 of logs/ablation_table.json unchanged after iteration 1+2 fixes
expected: |
  md5sum logs/ablation_table.json returns d66791c9b1bf836e5f72402989c06597 (canonical
  Phase 5 production state). All 11 code-review fixes (CR-01, WR-01..WR-07, IN-01..IN-03)
  applied; none mutated production data.
result: pass
evidence: |
  `md5sum logs/ablation_table.json` →
  `d66791c9b1bf836e5f72402989c06597 *logs/ablation_table.json` ✓

### 2. Full Phase 5 test suite passes in conda rag-security env
expected: |
  pytest tests/test_judge_fpr.py -q reports 9 passed (V-01..V-09 all green) under
  the project's rag-security conda env where ollama is installed.
result: pass
evidence: |
  `conda run -n rag-security python -m pytest tests/test_judge_fpr.py -q -o addopts=` →
  `9 passed in 0.86s` ✓

### 3. logs/judge_fpr_llama.json HEAD verdicts intact (TIE=187, DEGRADED=87, PRESERVED=76)
expected: |
  After git checkout HEAD --, the file contains 350 verdicts across 7 defenses with
  the canonical mixed distribution. M3 values in ablation_table.json are consistent
  with DEGRADED counts.
result: pass
evidence: |
  `python -c "Counter(...)"` →
  `{'TIE': 187, 'DEGRADED': 87, 'PRESERVED': 76}` ✓
  M3 cross-check: def02 DEGRADED=12, M3=12/50=0.24 (matches ablation_table.json)

### 4. V-06 regression patched — pytest no longer corrupts production verdict file
expected: |
  After applying the V-06 snapshot/restore extension (commit 594291e), running
  the full Phase 5 pytest suite leaves logs/judge_fpr_llama.json bit-identical
  to the pre-test state (no all-PRESERVED corruption).
result: pass
evidence: |
  Pre-test: TIE=187 DEGRADED=87 PRESERVED=76
  Post-test: TIE=187 DEGRADED=87 PRESERVED=76 (verified 2026-05-04) ✓

### 5. All 4 Phase 5 source files compile/import cleanly with iteration 1+2 fixes applied
expected: |
  scripts/run_judge_fpr.py, scripts/_build_ablation_table.py, tests/conftest.py,
  tests/test_judge_fpr.py all importable. _build_ablation_table.py has __main__
  guard (CR-01) so import does NOT mutate logs/ablation_table.json.
result: pass
evidence: |
  pytest collection succeeds; importlib spec_from_file_location loads
  run_judge_fpr.py without ImportError; CR-01 guard verified at line 84
  (`if __name__ == "__main__":`).

### 6. 11/11 code-review findings resolved across 4 fix commits + 1 regression fix
expected: |
  CR-01, WR-01..WR-07, IN-01..IN-03 (11 findings) resolved across:
  - 435d8a5 fix(05): __main__ guard (CR-01, WR-07)
  - 8bb606e fix(05): harden judge_one + ablation write path (WR-01..WR-04)
  - 69bf260 fix(05): use N_CLEAN constant + traceback for import errors (WR-05, WR-06)
  - 75695b5 fix(05): anchor test paths to repo root (IN-01)
  - 48e5e5f fix(05): add encoding=utf-8 to remaining file writes (IN-02)
  - 035ffe3 fix(05): remove redundant n_pairs alias (IN-03)
  - 594291e fix(05): V-06 also restores judge_fpr_llama.json (IN-01 follow-up)
  Plus 88baf3f and b28497f docs commits for the REVIEW-FIX.md report.
result: pass
evidence: |
  `git log --oneline | grep "fix(05)"` shows 7 fix commits;
  REVIEW-FIX.md frontmatter `findings_in_scope: 11, fixed: 11, status: all_fixed`.

### 7. Phase 6 cross-LLM extension feasibility check (gpt-oss-20b/120b on {fused, def02})
expected: |
  Phase 6 v6 logs (logs/eval_matrix/gptoss{20b,120b}_cloud__{fused,def02}__all_tiers_v6.json)
  contain `results` arrays with 50 clean records (paired=False) each, with both
  `chunks_removed` and `answer` keys present — the schema needed to compute
  M1 (per-chunk FPR) and M2 (answer-preserved substring drop) without cloud calls,
  plus M3 (judge-scored) with ~200 cloud calls (50 queries × 4 cells).
result: pass
evidence: |
  All 4 v6 cells have results=100 with 50 clean(paired=False); first clean
  record has all required keys including `chunks_removed: True` and `answer: True`.
  Extension scope captured as Phase 7 in ROADMAP.md (NOT a Phase 5 re-run —
  Phase 5 was scoped to llama3.2:3b only).

## Summary

total: 7
passed: 7
issues: 0
pending: 0
skipped: 0

## Gaps

None. Phase 5 fully verified after iteration 1+2 code-review fixes and the
V-06 regression patch. Production data (logs/ablation_table.json md5
d66791c9b1bf836e5f72402989c06597, logs/judge_fpr_llama.json with mixed
verdicts) preserved throughout.

## Re-execution Assessment

**Q: Did any of the iteration 1+2 fixes require Phase 5 to re-run?**
A: No. All 11 code-review fixes were correctness/hygiene improvements that did
not change the M1/M2/M3 computation logic or the judge prompt contract. The
production artifacts (ablation_table.json, judge_fpr_llama.json, judge_fpr_llama.json.cache)
remain canonical at the same md5/verdict-distribution they had post-Plan-03.

**Q: Did the V-06 regression require any production re-run?**
A: No. V-06 was corrupting the working-tree copy of logs/judge_fpr_llama.json
on every test run, but the cache file (logs/judge_fpr_llama.json.cache) and
the committed HEAD version retained the real verdicts. Patch + restore was
sufficient.

**Q: Should Phase 5 metrics be computed for the gpt-oss models added in Phase 6?**
A: Yes — captured as new Phase 7 in ROADMAP.md. Phase 5 was scoped explicitly
to llama3.2:3b (the 7 active defenses include BERT classifier trained on llama
outputs, etc.). Phase 6 added gpt-oss-20b/120b on {no_defense, fused, def02}.
The honest-FPR analysis is conceptually applicable to those models for the
{fused, def02} cells; running it requires ~200 new cloud-judge calls and a
small extension script (mirroring scripts/run_judge_fpr.py but reading the
Phase 6 v6 schema). User can invoke `/gsd-plan-phase 7` to proceed.
