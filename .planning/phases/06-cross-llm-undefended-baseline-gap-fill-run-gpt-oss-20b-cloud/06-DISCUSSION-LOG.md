# Phase 6: Cross-LLM Undefended Baseline Gap Fill - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-04
**Phase:** 06-cross-llm-undefended-baseline-gap-fill-run-gpt-oss-20b-cloud
**Areas discussed:** Collection & corpus combo, Output filename strategy, Rate-limit delay & retry, Downstream propagation

---

## Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Collection & corpus combo | Which Chroma collection to evaluate against. nq_poisoned_v4 vs nq_poisoned_v5 vs fresh nq_poisoned_v6. Affects whether T1b ASR is even measurable. | ✓ |
| Output filename strategy | Overwrite the existing Phase-02.3 logs vs versioned new files (_v6.json). Affects whether make_results.py code edits are needed. | ✓ |
| Rate-limit delay & retry | --delay 3 (Phase 02.3 convention) vs --delay 0 vs --delay 5 with retry. Drives the 26-min budget. | ✓ |
| Downstream propagation | After Phase 6, do we update make_results.py and re-emit Phase 3.4 tables, or stop at "logs emitted"? | ✓ |

**User's choice:** All four areas selected for discussion.

---

## Collection & Corpus Combo

### Q1: Which Chroma collection should Phase 6 evaluate against?

| Option | Description | Selected |
|--------|-------------|----------|
| nq_poisoned_v4 (Recommended) | 1239 docs, already indexed. Used by Phase 02.4 + 03.1 + 03.3-07 cross-model matrix — strongest precedent. Contains T1/T1b/T2/T3/T4/adaptive simultaneously. | ✓ |
| nq_poisoned_v5 | Also 1239 docs. Used by Phase 03.2 adaptive runs. Functionally identical to v4 right now. Conceptually a Phase 03.2 sibling — wrong lineage for the gap-fill. | |
| Fresh nq_poisoned_v6 (force-reindex) | Build a new collection. Costs ~5–10 min of embedding. Only worth it for Phase-6-specific provenance string. | |
| v4, but also assert post-load that all 5 tier ranges present | Same as option 1 + sanity-check against stale collection. | |

**User's choice:** nq_poisoned_v4 (Recommended)
**Notes:** Locked the most direct lineage. Captured the post-load tier-range sanity assert as decision D-01a even though the user picked option 1 — it's cheap insurance and the planner can decide implementation form.

### Q2: Which queries file should the eval use?

| Option | Description | Selected |
|--------|-------------|----------|
| data/test_queries.json (Recommended) | 100 queries, 50 paired/50 clean — the canonical Phase 02.3+ eval set. | ✓ |
| Larger / alternative query set | Build or load a different query set. Out of scope for a "gap fill" — would change comparability. | |

**User's choice:** data/test_queries.json (Recommended)
**Notes:** Comparability with the existing four undefended_*.json files takes priority.

---

## Output Filename Strategy

### Q1: How should Phase 6 name its output files?

| Option | Description | Selected |
|--------|-------------|----------|
| Overwrite the existing files (Recommended) | Write to canonical paths directly. Make_results.py untouched. Phase 02.3 files lost. | |
| Versioned new files: _v6.json suffix | Write logs/eval_harness_undefended_gptoss{20b,120b}_v6.json. Preserves Phase 02.3 history. Requires ~4-line make_results.py edit at line 247. | ✓ |
| Move old files to logs/archive/, write canonical name | git mv to archive dir, write fresh files at canonical path. History preserved in git + on disk. | |
| Both: write canonical + keep old as _v3.json | Rename old files to _v3.json, write new ones to canonical path. | |

**User's choice:** Versioned new files: _v6.json suffix
**Notes:** Highest fidelity to the project's "preserve historical artifacts" pattern. Cost: a small make_results.py path-resolver edit (D-02b).

---

## Rate-Limit Delay & Retry

### Q1: How should Phase 6 handle cloud rate limiting?

| Option | Description | Selected |
|--------|-------------|----------|
| --delay 3, no retry (Recommended) | Matches Phase 02.3 + Phase 03.3-07 cross-model matrix. Total wall-clock ~27 min. | ✓ |
| --delay 3 + retry-on-429 wrapper | Add tenacity-style retry around generator.generate(). Honest result quality but expands run_eval.py scope. | |
| --delay 5, no retry | Conservative — doubles safety margin. Total ~37 min, exceeds budget. | |
| --delay 0, opportunistic | Fastest (~12 min). Acceptable only if rate cap is permissive. | |

**User's choice:** --delay 3, no retry (Recommended)

### Q2: What if a single query hits an unrecoverable error?

| Option | Description | Selected |
|--------|-------------|----------|
| Record error answer, continue (Recommended) | Store answer = '[ERROR: <type>]', mark hijacked=False for all tiers, increment error_count, finish run. | ✓ |
| Hard-fail: abort the entire eval on first error | Run dies, no output written. Honest but expensive. | |
| Resume-from-checkpoint | Persist completed query results to .json.partial. Bulletproof but ≈30 min of edits. Overkill for a 100-query run. | |

**User's choice:** Record error answer, continue (Recommended)
**Notes:** Resume-from-checkpoint captured in deferred ideas for any future >500-query cloud run.

---

## Downstream Propagation

### Q1: How far should Phase 6 propagate the new T1b/T3/T4 numbers downstream?

| Option | Description | Selected |
|--------|-------------|----------|
| Logs + minimal make_results.py path edit (Recommended) | Emit _v6.json files + ~4-line make_results.py edit. Do NOT regenerate Phase 3.4 tables/figures. | |
| Full propagation: regenerate docs/results/*.md + figures/*.png | Patch make_results.py + regenerate everything. Risk: changes the submitted writeup's underlying data. | |
| Logs only, NO consumer edits | Emit _v6.json files. Make_results.py untouched. Smallest blast radius. | |
| Logs + standalone summary file | Emit _v6.json + new docs/results/cross_llm_undefended_v6.md. Self-contained. | |
| **Other (free text)** | User's freeform directive — see below | ✓ |

**User's choice (Other / freeform):**
> "so do 1, but this phase should automatically re run any of the things (like making figures) that has already been done without gpt-oss and add its results too. I shoulnd't have to go back to a phase and execute it again. Any thing new made should not overwrite exsiting files, whtehr thats reports, figures or whatever. Exisitng markdowns however can be updated, instead of makign new ones."

**Notes:** This blends option 1 (path-resolver edit) with auto-rerun of downstream artifacts under a strict no-overwrite-of-existing-files rule, with the explicit exception that existing markdowns are updated in-place. Captured as decision D-04 in CONTEXT.md.

### Q2: Should llama3.2:3b and mistral:7b also get _v6.json artifacts in this phase?

| Option | Description | Selected |
|--------|-------------|----------|
| No — phase scope is gpt-oss only (Recommended) | Roadmap line names only the two cloud models. llama+mistral T1b gap is a separate concern. | ✓ |
| Yes — also rerun llama+mistral on v4 to get unified _v6.json files | 4 models × 100 queries; adds ~10 min. Out of original "gap fill" framing. | |
| Yes for llama+mistral, but only to add T1b column | Tier-filter to T1b. Smallest yes-option blast radius. | |

**User's choice:** No — phase scope is gpt-oss only (Recommended)
**Notes:** llama+mistral T1b backfill captured in deferred ideas as a candidate future phase.

### Q3: Which downstream artifacts should Phase 6 re-emit? (multi-select)

| Option | Description | Selected |
|--------|-------------|----------|
| docs/results/undefended_baseline.{md,csv} | Phase 3.4 Plan 02 output. Most directly load-bearing for the gap fill. | ✓ |
| docs/results/arms_race_table.{md,csv} | The headline table. Adds gpt-oss rows. | ✓ |
| figures/d03_arms_race.png | 5-tier × N-defense bar chart. Adding gpt-oss bars expands the visual story. | ✓ |
| figures/d12_cross_model_heatmap.png | 5-tier × 3-LLM heatmap. Most natural visual home for the gap-fill data. | ✓ |

**User's choice:** All four selected.
**Notes:** Markdowns updated in-place per user directive; CSVs and PNGs go to new `_v6` filenames. Captured in CONTEXT D-05/D-06/D-07.

### Q4: Should the in-place markdown edits add a 'Phase 6 update note' disclosure?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — add a dated 'Updated <date>: gpt-oss T1b/T3/T4 added (Phase 6)' line at the top (Recommended) | Cheap provenance signal; preserves audit trail. | ✓ |
| No — silent in-place edit | Reads as if always present. Loses audit trail. | |

**User's choice:** Yes — dated disclosure header (Recommended)
**Notes:** Wording standardized in CONTEXT D-05.

---

## Closing Confirmation

### Q: Any more gray areas, or ready for context?

| Option | Description | Selected |
|--------|-------------|----------|
| I'm ready for context (Recommended) | Write CONTEXT.md and DISCUSSION-LOG.md now. | ✓ |
| Explore more gray areas | Surface 2–3 additional decisions (e.g., test stub scope, run_eval.py error-handling scope, success-criteria thresholds, post-run verification asserts). | |

**User's choice:** I'm ready for context (Recommended)

---

## Claude's Discretion

The following were left to Claude / planner judgment rather than asked:

- Test stub structure (Wave 0 stubs in `tests/test_phase6_eval.py` + `tests/test_make_results_v6.py` using the established `importlib.util.spec_from_file_location` pattern).
- Whether the Phase 6 eval invocation lives in a thin wrapper (`scripts/run_phase6_eval.py`) or as two direct CLI calls in plan steps.
- Wave structure (Wave 0 stubs → Wave 1 cloud eval runs → Wave 2 make_results path edit + downstream artifact re-emission → Wave 3 verification checkpoint).
- Exact placement of the dated disclosure line within each updated markdown.
- The specific docstring / commit-message wording for the make_results.py path-resolver edit.

## Deferred Ideas

- llama3.2:3b + mistral:7b T1b backfill (separate future phase).
- Resume-from-checkpoint mechanism for run_eval.py (overkill at 100 queries; reconsider if any future phase runs >500 cloud queries).
- Tenacity retry-on-429 wrapper around generator.generate() (rejected; error-count provenance field is the chosen failure-visibility signal).
- Fresh nq_poisoned_v6 collection (rejected; would dilute apples-to-apples comparison).
- Editing the submitted Phase 3.4 writeup `docs/phase3_results.md` (out of scope; submitted Apr 30).
- 5×5 D-12 heatmap with adaptive-tier columns (out of scope; different dimension).
- Surfacing T1b in arms_race_table.md for llama (would require a llama re-run; covered by the llama+mistral T1b backfill deferral).
