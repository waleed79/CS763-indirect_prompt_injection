# Phase 7: Honest FPR Metrics — gpt-oss extension - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 07-CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-04
**Phase:** 07-honest-fpr-metrics-gpt-oss-extension
**Areas discussed:** Script reuse strategy, Output schema & filenames, Writeup integration, Input log resolution + answer-A baseline

---

## Pre-Discussion: Roadmap Detail Section Bootstrapping

Phase 7 was registered in `.planning/ROADMAP.md`'s checklist (line 29) but lacked the detailed `### Phase 7:` section that `gsd-sdk init.phase-op` requires. The first phase-op call returned `phase_found: false`. Drafted a detail section based on the line-29 description matching Phase 5/6 voice (Goal, Depends on, Requirements, Plans TBD, Notes), inserted before the `---` separator, appended an evolution note. Re-ran phase-op — `phase_found: true`. Committed at 223f06f.

This was a procedural bootstrap, not a context decision; recorded here for traceability.

---

## Script Reuse Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Sibling script | New scripts/run_judge_fpr_gptoss.py — Phase 5 stays bit-for-bit; ~150 lines duplicated | |
| Extend with --target | Add --target {llama,gptoss20b,gptoss120b} to run_judge_fpr.py; single source of truth; touches verified Phase 5 deliverable | |
| Refactor into shared module | Move shared logic to rag/judge_fpr.py; both Phase 5 and Phase 7 become thin entry scripts; doubles plan effort | |
| You decide | Planner picks based on actual coupling complexity at plan-time | ✓ |

**User's choice:** You decide
**Notes:** Recorded as Claude's discretion in CONTEXT D-01 with default lean toward sibling script (lowest risk to Phase 5 commit 8e6942b and its 05-VERIFICATION.md). Planner picks alternative shapes only if duplication exceeds ~200 lines or a forthcoming Phase 8 is on the visible horizon.

---

## Output Schema & Filenames

### Sub-question 1: Ablation table shape

| Option | Description | Selected |
|--------|-------------|----------|
| Flat composite-key dict | Keys 'gptoss20b_cloud__fused', 'gptoss20b_cloud__def02', etc. Each value carries model, defense_mode, M1/M2/M3, judge_model, judge_n_calls. Mirrors Phase 5 flat structure. | ✓ |
| Nested by model | {'gpt-oss:20b-cloud': {'fused': {...}, 'def02': {...}}, ...}. Cleaner for humans, not parallel to Phase 5. | |
| List of cell records | [{model, defense, ...}, ...]. Most flexible for filtering; least like Phase 5's dict. | |

**User's choice:** Flat composite-key dict
**Notes:** Locked as CONTEXT D-02. Schema example included verbatim with 4 keys.

### Sub-question 2: Verdicts file layout

| Option | Description | Selected |
|--------|-------------|----------|
| Single combined file | logs/judge_fpr_gptoss_v7.json with nested verdicts.{model}.{defense}.{query_index}; mirrors Phase 5 scaled by one level | ✓ |
| Two per-model files | logs/judge_fpr_gptoss20b.json + logs/judge_fpr_gptoss120b.json; parallel to Phase 5 single-model-per-file naming | |

**User's choice:** Single combined file
**Notes:** Locked as CONTEXT D-04. 200 verdicts in one artifact for grader reproducibility.

### Sub-question 3: Downstream rendering

| Option | Description | Selected |
|--------|-------------|----------|
| No — standalone artifact only | Phase 7 emits JSON + writeup; downstream rendering out of scope | |
| Yes — add v7 path-resolver branch | Mirror Phase 6 D-02b/D-13 pattern; teach make_results.py to read v7 file; emit docs/results/honest_fpr_gptoss_v7.md | ✓ |
| You decide | Planner picks based on Phase 4 talk needs | |

**User's choice:** Yes — add v7 path-resolver branch
**Notes:** Locked as CONTEXT D-05. ~30-line delta to make_results.py. D-06 carries an optional figure renderer at Claude's discretion.

---

## Writeup Integration

### Sub-question 1: Where the addendum lives

| Option | Description | Selected |
|--------|-------------|----------|
| Append to phase5_honest_fpr.md | In-place section at end; original prose untouched; matches ROADMAP "extended Phase 5 writeup" wording; mirrors Phase 6 D-04 in-place markdown precedent | ✓ |
| Separate docs/phase7_honest_fpr_gptoss.md | Phase 5 stays bit-for-bit; cleanest per-phase separation; duplicates methodology section | |
| Both | Phase 5 callout + Phase 7 detail; most cross-linking; largest doc surface and risk of staleness | |

**User's choice:** Append addendum section to phase5_honest_fpr.md
**Notes:** Locked as CONTEXT D-07/D-08. Section header: "## Phase 7 addendum: gpt-oss extension (2026-05-04)". 10-row M1/M2/M3 table covering all 3 RAG targets.

### Sub-question 2: Addendum prose depth

| Option | Description | Selected |
|--------|-------------|----------|
| 1-2 paragraph cross-LLM analysis | Discussion paragraph examining whether M1/M2/M3 patterns generalize across model scales; aligns with arms-race / cross-LLM narrative | ✓ |
| Numbers + minimal framing only | Just the table + 2-sentence intro; lower-effort | |

**User's choice:** 1-2 paragraph cross-LLM analysis
**Notes:** Locked as CONTEXT D-07. Discussion paragraph examines per-chunk FPR scaling, answer-preserved FPR vs llama, and user-visible cost across model scales.

---

## Input Log Resolution + Answer-A Baseline

### Pre-question verification

Verified per-record schema of `logs/eval_harness_undefended_gptoss20b_v6.json` matches `logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json`:
- Both carry `query`, `paired`, `answer`, `chunks_removed` per record
- 100 records each (50 paired + 50 clean)
- Top-level keys differ slightly but per-record schema is identical

This collapsed the schema-gap question from "real" to "tiny adapter".

### Sub-question 1: Path resolution approach

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded path map | Module-level CELL_LOG_MAP + OFF_LOG_MAP mirroring Phase 5's DEFENSE_LOG_MAP idiom; loud-fail at startup if any path missing; trivially auditable | ✓ |
| Glob discovery + assertion | Glob logs/eval_matrix/gptoss*_cloud__{fused,def02}__all_tiers_v6.json; assert exactly 4 + 2 matched; more flexible if naming evolves | |
| CLI flags for input paths | --cell + --off-baseline (repeatable); pure argparse; most flexible; longer command lines | |

**User's choice:** Hardcoded path map mirroring Phase 5
**Notes:** Locked as CONTEXT D-09. Code constants included verbatim.

### Sub-question 2: Schema gap handling

| Option | Description | Selected |
|--------|-------------|----------|
| Tiny adapter in load_clean_records | Generalize the helper to accept either top-level shape; ~5-line change; localized | |
| Pre-flight 'normalize' pass | Read each v6 cell, emit temp normalized files matching Phase 5 shape; cleanest separation; muddies provenance | |
| You decide | Planner picks based on chosen script architecture | ✓ |

**User's choice:** You decide
**Notes:** Recorded as Claude's discretion in CONTEXT D-10 with default lean toward tiny adapter (5-line change to load_clean_records). Planner can substitute pre-flight normalization if it composes better with the chosen script architecture from D-01.

---

## Wrap-Up Question

| Option | Description | Selected |
|--------|-------------|----------|
| I'm ready for context | Lock decisions; default the two implicits (no trivial no_defense rows; bootstrap CIs nice-to-have) | ✓ |
| Confirm the two implicits explicitly | Ask 2 quick questions about no_defense rows and CI requirements | |
| Explore more gray areas | Surface 2-4 more decisions (M3 fast-path, one-vs-two scripts, judge_n_calls accounting) | |

**User's choice:** I'm ready for context
**Notes:** Implicits captured in CONTEXT.md as D-03 (no trivial no_defense rows) and Claude's Discretion (bootstrap CIs).

---

## Claude's Discretion

Items where the user said "you decide" or deferred to Claude:
- D-01: Script reuse strategy (sibling vs. extend vs. refactor) — planner picks at plan-time
- D-10: Schema adapter approach — planner picks based on D-01 outcome
- D-06: Whether to render a v7 figure beyond the 10-row table
- Bootstrap CIs (1000 resamples) on M1/M2/M3 — planner decides scope
- Plan wave structure (split M1/M2 from M3 vs. combined invocation)
- Test stub structure (Wave 0 importlib.util pattern from prior phases)
- Exact prose wording of the addendum's cross-LLM discussion
- Per-cell logging verbosity

## Deferred Ideas

Captured in 07-CONTEXT.md `<deferred>` section. Highlights:
- Cross-LLM extension to mistral:7b and gemma4:31b-cloud (Future Phase 8 candidate)
- Multi-seed judge calls (3-seed majority vote)
- Cross-judge sanity check (gemma4 on a 20-query subset)
- Bootstrap CIs on M1/M2/M3
- Trivial no_defense rows in ablation_table_gptoss_v7.json (excluded per D-03)
- In-place rewrite of Phase 5's logs/ablation_table.json (rejected — separate file)
- Refactoring run_judge_fpr.py into shared library
- Hand-annotated ground-truth M2 path
- Updating docs/phase3_results.md with Phase 7 numbers (out of scope — submitted artifact)

No scope-creep redirects were issued during this session.
