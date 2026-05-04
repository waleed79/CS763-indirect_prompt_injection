---
phase: 07-honest-fpr-metrics-gpt-oss-extension
plan: "05"
subsystem: docs
tags: [writeup, honest-fpr, cross-llm, addendum, gpt-oss]
dependency-graph:
  requires:
    - 07-04 (logs/ablation_table_gptoss_v7.json — 4 gpt-oss rows)
    - 05 (docs/phase5_honest_fpr.md — Phase 5 prose, §4 llama numbers)
  provides:
    - docs/phase5_honest_fpr.md with Phase 7 addendum (10-row cross-LLM table + analysis)
  affects:
    - tests/test_make_results_v7.py (4 P7-DOC-* tests flip from SKIP to PASS)
tech-stack:
  added: []
  patterns:
    - append-only in-place edit of a live deliverable
    - 10-row composite table spanning 3 RAG targets
key-files:
  created: []
  modified:
    - docs/phase5_honest_fpr.md
decisions:
  - Blank lines before addendum heading must be zero (prefix exactly equals git HEAD) — test TestPhase5ProseUntouched splits at heading and compares prefix to HEAD verbatim
  - 6 llama rows use values as displayed in §4 table (2 decimal places), not raw JSON values; 4 gpt-oss rows use raw JSON precision (0.092, 0.000)
  - DEF-02 priming effect (M3=0.24 on llama) analyzed against gpt-oss results (M3=0.06/0.10) — framed as small-model behavioral artifact
metrics:
  duration: 206s
  completed: 2026-05-04
  tasks_completed: 1
  tasks_total: 1
  files_modified: 1
---

# Phase 7 Plan 05: Phase 7 Addendum — docs/phase5_honest_fpr.md Summary

Appended a `## Phase 7 addendum: gpt-oss extension (2026-05-04)` section to `docs/phase5_honest_fpr.md` containing a 10-row cross-LLM honest-FPR table, two substantive analysis paragraphs, a methodology inheritance note, and a pointer to the auto-companion.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | fe09ca3 | docs(07-05): append Phase 7 addendum to docs/phase5_honest_fpr.md |

## Addendum Word Count

739 words, 38 lines (38 insertions, 0 deletions in git diff).

`git diff --stat HEAD~1 HEAD`:
```
docs/phase5_honest_fpr.md | 38 ++++++++++++++++++++++++++++++++++++++
1 file changed, 38 insertions(+)
```

## The 10 Table Rows (audit against source JSONs)

Source: 6 llama rows from `logs/ablation_table.json` (as displayed in §4), 4 gpt-oss rows from `logs/ablation_table_gptoss_v7.json`.

| Model              | Defense     | Per-chunk FPR (M1) | Answer-preserved FPR (M2) | Judge FPR (M3) |
|--------------------|-------------|-------------------|--------------------------|----------------|
| llama3.2:3b        | DEF-02      | 0.00              | 0.00                     | 0.24           |
| llama3.2:3b        | BERT alone  | 0.32              | 0.26                     | 0.28           |
| llama3.2:3b        | Perplexity  | 0.22              | 0.14                     | 0.16           |
| llama3.2:3b        | Imperative  | 0.36              | 0.34                     | 0.34           |
| llama3.2:3b        | Fingerprint | 0.02              | 0.02                     | 0.04           |
| llama3.2:3b        | Fused       | 0.31              | 0.32                     | 0.34           |
| gpt-oss:20b-cloud  | Fused       | 0.092             | 0.02                     | 0.16           |
| gpt-oss:20b-cloud  | DEF-02      | 0.000             | 0.00                     | 0.06           |
| gpt-oss:120b-cloud | Fused       | 0.092             | 0.04                     | 0.16           |
| gpt-oss:120b-cloud | DEF-02      | 0.000             | 0.00                     | 0.10           |

JSON cross-check (gpt-oss rows):
- `gptoss20b_cloud__fused`: per_chunk_fpr=0.092, answer_preserved_fpr=0.02, judge_fpr=0.16 — matches table row 7.
- `gptoss20b_cloud__def02`: per_chunk_fpr=0.0, answer_preserved_fpr=0.0, judge_fpr=0.06 — matches table row 8.
- `gptoss120b_cloud__fused`: per_chunk_fpr=0.092, answer_preserved_fpr=0.04, judge_fpr=0.16 — matches table row 9.
- `gptoss120b_cloud__def02`: per_chunk_fpr=0.0, answer_preserved_fpr=0.0, judge_fpr=0.10 — matches table row 10.

## docs/phase3_results.md Confirmation

`git diff --exit-code docs/phase3_results.md` exited 0 — submitted Phase 3.4 writeup untouched (T-7-02 mitigation).

## Test Results

| Test ID | Test Name | Status |
|---------|-----------|--------|
| P7-DOC-ADDENDUM | TestAddendumPresent::test_addendum_heading_once | PASS |
| P7-DOC-TABLE-10ROW | TestAddendumTable10Rows::test_table_has_ten_data_rows | PASS |
| P7-DOC-UNTOUCHED | TestPhase5ProseUntouched::test_prose_prefix_unchanged | PASS |
| P7-DOC-PHASE3-UNTOUCHED | TestPhase34NotEdited::test_phase3_doc_unchanged | PASS |

All 4 tests flipped from SKIP to PASS. TestPhase5ProseUntouched required a deviation fix (see below).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Blank lines before addendum heading caused TestPhase5ProseUntouched to fail**

- **Found during:** Task 1 initial implementation
- **Issue:** The plan template showed `\n\n## Phase 7 addendum...` (two blank lines before heading). The test splits the document at the heading text and compares everything before it to `git show HEAD:docs/phase5_honest_fpr.md`. The original file ends with a single `\n`; adding two blank lines before the heading made the prefix end with `\n\n\n` — a mismatch.
- **Fix:** Removed the two blank lines before `## Phase 7 addendum` so the heading follows immediately after the last character of the original References section. The test now passes: `prefix == head_prefix` is True.
- **Files modified:** docs/phase5_honest_fpr.md
- **Commit:** fe09ca3 (same task commit — fixed before final commit)

## Known Stubs

None. All 4 P7-DOC-* requirements are now PASS. No placeholder text in the addendum — all numbers are sourced directly from logs files.

## Threat Flags

None. No new network endpoints, auth paths, file access patterns, or schema changes introduced. This plan is a pure documentation append to an existing file.

## Self-Check: PASSED

- [x] `docs/phase5_honest_fpr.md` exists and contains addendum heading: FOUND
- [x] Commit fe09ca3 exists: FOUND
- [x] 4 doc tests pass: CONFIRMED (pytest output above)
- [x] 10 data rows in table: CONFIRMED (python script count = 10)
- [x] 0 deletions in git diff: CONFIRMED (wc -l = 0)
- [x] `docs/phase3_results.md` unchanged: CONFIRMED (git diff --exit-code = 0)
