---
phase: 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
plan: "04"
subsystem: documentation
tags: [writeup, results, fpr-metrics, llm-as-judge]
dependency_graph:
  requires: [05-03-SUMMARY.md, logs/ablation_table.json, logs/judge_fpr_llama.json]
  provides: [docs/phase5_honest_fpr.md]
  affects: [docs/phase3_results.md (Plan 05 callout)]
tech_stack:
  added: []
  patterns: [numbered-section-writeup, pipe-table, plain-numbered-references]
key_files:
  created: [docs/phase5_honest_fpr.md]
  modified: []
decisions:
  - "Used verbatim fpr values from ablation_table.json (per-defense fpr varies: 0.00/0.76/0.72/0.88/0.06/0.76/0.76)"
  - "Formatted per_chunk_fpr=0.308 as 0.31 and per_chunk_fpr=0.364 as 0.36 (2dp rounding)"
  - "No INFILTRATED leakage found in clean-query defense-off baseline per 05-03-SUMMARY; omitted optional sub-analysis sentence"
metrics:
  duration: "~15 minutes"
  completed: "2026-05-04"
  tasks_completed: 1
  files_created: 1
---

# Phase 05 Plan 04: Writeup — SUMMARY

**One-liner:** Phase 5 standalone writeup framing 76% FPR as loose upper bound, refined via per-chunk (M1), answer-preserved (M2), and LLM-as-judge (M3) metrics with full 7-defense results table.

## What Was Built

Created `docs/phase5_honest_fpr.md` (133 lines) — the Phase 5 standalone writeup deliverable following the 6-section contract from CONTEXT D-09.

## Final Line Count

`wc -l docs/phase5_honest_fpr.md` → **133 lines** (within the 80–150 target).

## Section 4 Results Table (verbatim — all 7 active-defense rows)

| Defense                      | FPR (≥1 removed) | Per-chunk FPR | Answer-preserved FPR | Judge FPR |
|:-----------------------------|----------------:|--------------:|---------------------:|----------:|
| DEF-02 (system prompt)       |            0.00 |          0.00 |                 0.00 |      0.24 |
| BERT only                    |            0.76 |          0.32 |                 0.26 |      0.28 |
| Perplexity only              |            0.72 |          0.22 |                 0.14 |      0.16 |
| Imperative only              |            0.88 |          0.36 |                 0.34 |      0.34 |
| Fingerprint only             |            0.06 |          0.02 |                 0.02 |      0.04 |
| **Fused (fixed θ=0.5)**      |        **0.76** |      **0.31** |             **0.32** |  **0.34** |
| Fused (tuned θ=0.10)         |            0.76 |          0.34 |                 0.32 |      0.34 |

Note: FPR (≥1 removed) values read verbatim from `ablation_table.json` `fpr` key per defense row. Per-defense values differ from the task-summary's uniform "0.76" because perplexity_only=0.72, imperative_only=0.88, and fingerprint_only=0.06 have different actual fpr values. Per_chunk_fpr=0.308 rounded to 0.31; imperative_only per_chunk_fpr=0.364 rounded to 0.36.

## Section 3 no_defense Provenance Sentence (D-02)

Present verbatim: "The `no_defense` row reports `judge_n_calls = 0` (no judge calls were issued — chunks_removed is 0 by construction); the `judge_model` field is populated for schema consistency only and does not imply judge invocation."

## Section 5 Discussion Narrative

The DEF-02 M3=24% priming finding is discussed explicitly in §5: DEF-02 has M3=24% despite M1=0% (no chunks removed), confirming the Phase 3.1-06 finding that the system-prompt warning primes llama3.2:3b to surface injected instructions even on clean queries. The optional INFILTRATED anchor-token sub-analysis was **omitted** — per 05-03-SUMMARY, no INFILTRATED leakage was detected in the defense-off baseline answers for the 50 clean queries. The M3 dual-interpretation bullet (removed-legitimate-content vs. removed-poisoned-content-that-leaked) is present per RESEARCH §5.5.

## Headline Framing

Confirmed: §1 frames 76% as "a loose upper bound under the strictest possible interpretation" — no retraction language. The original 76% is defended as "deliberately conservative and correct under its stated terms."

## Divergences from D-09 6-Section Structure

**No divergence.** The document follows the 6-section structure exactly:
1. Motivation
2. The three metrics
3. Methodology
4. Results
5. Discussion
6. Limitations

Plus a References section (plain numbered list, no `[^N]` footnote syntax per STATE.md Phase 03.4-05).

One minor note: the FPR column in §4 uses actual per-defense `fpr` key values from `ablation_table.json` rather than a uniform "0.76" — this is more accurate and correct. The 05-03-SUMMARY already documents that the original FPR of 0.76 applies only to the filtering defenses (bert_only, fused, fused_tuned_threshold); perplexity_only=0.72, imperative_only=0.88, fingerprint_only=0.06 per their actual `fpr` keys.

## Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Write docs/phase5_honest_fpr.md | 7374f22 | docs/phase5_honest_fpr.md (133 lines, created) |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- `docs/phase5_honest_fpr.md` exists: FOUND
- Commit 7374f22 exists: FOUND
- 6 numbered sections present: PASSED
- 7 active-defense rows in §4 table: PASSED
- MT-Bench citation with arXiv:2306.05685: PASSED
- no_defense provenance sentence (D-02): PASSED
- 76% as "loose upper bound": PASSED
- No `[^N]` footnote syntax: PASSED (count=0)
