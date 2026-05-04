# Phase 6: Cross-LLM Undefended Baseline Gap Fill - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 6 fills a single, narrowly-scoped gap in the cross-LLM undefended baseline: the existing `logs/eval_harness_undefended_gptoss20b.json` and `logs/eval_harness_undefended_gptoss120b.json` are Phase 02.3 artifacts produced against the **`nq_poisoned_v3`** collection (which only contained T1 and T2 passages — T1b, T3, T4 did not yet exist). They therefore carry only `asr_tier1` / `asr_tier2` keys.

Phase 6 re-runs both cloud models — `gpt-oss:20b-cloud` and `gpt-oss:120b-cloud` — against the **`nq_poisoned_v4`** collection (the combined 5-tier poisoned corpus, already indexed at 1239 docs locally), undefended (`--defense off`), in a single `run_eval.py` invocation per model. The existing per-tier `passage_id`-range tagger in `run_eval.py` (lines ~235–247) emits T1, T1b, T2, T3, T4 retrieval flags and per-tier `asr_*` aggregates simultaneously; no eval-script changes are needed for the tagging itself.

The resulting two new JSON files (`_v6.json` suffix — see D-02) plus a small `scripts/make_results.py` path-resolver edit plus four downstream re-emissions (two markdown updates in-place, two new `_v6.png` figures) collectively close the gap. Wall-clock budget: ~26 minutes of cloud inference + ~5 min for the make_results / figure regeneration.

**In scope:** undefended (no_defense) only; gpt-oss:20b-cloud + gpt-oss:120b-cloud only; one eval run per model; reuse the canonical 100-query set; use the already-indexed nq_poisoned_v4 collection; surface T1b/T3/T4 numbers in two existing Phase 3.4 result markdowns and two figures via the auto-rerun-without-overwrite pattern (D-04).

**Out of scope:** any defense changes, any new attack tier, any additional LLMs (llama+mistral already have `eval_harness_undefended_t34_*.json` from Phase 02.4 with T3/T4 — their T1b gap is a separate concern), changes to the submitted Phase 3.4 writeup prose at `docs/phase3_results.md`, regenerating the Phase 3.4 PNGs that were submitted on Apr 30 (those stay; Phase 6 emits parallel `_v6.png` files).

</domain>

<decisions>
## Implementation Decisions

### Collection & Corpus

- **D-01 (Collection):** Evaluate against `nq_poisoned_v4` — already indexed locally at 1239 docs (= 1000 clean + 50 T1 + 50 T2 + 50 T3 + 50 T1b + 9 T4 paired-topic fragments + 30 adaptive). No `--force-reindex`; the collection is the same one used by Phase 02.4 + Phase 03.1 + Phase 03.3-07 cross-model matrix, so Phase 6 numbers compare apples-to-apples with that lineage. Provenance string `collection: "nq_poisoned_v4"` is recorded in each output JSON. **Not** `nq_poisoned_v5` (functionally identical right now but conceptually a Phase 03.2 sibling — wrong lineage), **not** a fresh `nq_poisoned_v6` (saves 5–10 min of needless re-embedding).
- **D-01a (Pre-run sanity assert):** Before queries start, the eval driver should assert that all 5 expected `passage_id` ranges are present in the collection: at least one passage in each of `[20000, 20050)`, `[20050, 20100)`, `[20100, 20150)`, `[20150, 20200)`, `[20200, 20300)`. Cheap insurance against a stale collection silently producing 0% on T1b/T3/T4. Implementation can be a small wrapper script, an assertion injected via existing `scripts/_check_collections.py` pattern, or a pre-flight check in a Phase-6-specific driver.
- **D-01b (Queries):** Use `data/test_queries.json` — the canonical 100-query set (50 paired / 50 clean). Same set every other `eval_harness_undefended_*.json` was scored against. Keeps `n_queries=100` invariant intact for `make_results.py` and lets Phase 3.4 / Phase 4 narrative tables compare across LLMs without an asterisk.

### Output Filename & Provenance

- **D-02 (Versioned filenames):** Phase 6 writes to **`logs/eval_harness_undefended_gptoss20b_v6.json`** and **`logs/eval_harness_undefended_gptoss120b_v6.json`** — the `_v6.json` suffix preserves the Phase 02.3 originals bit-for-bit. The Phase 02.3 files at the un-versioned canonical path stay untouched as historical record (collection: nq_poisoned_v3, T1/T2-only).
- **D-02a (Inside-JSON provenance fields):** Each new file records `phase: "06"`, `collection: "nq_poisoned_v4"`, `corpus: "data/corpus_poisoned.jsonl"`, `supersedes_phase_02_3: true`, plus an `error_count` integer (see D-03) so reviewers can see how many queries failed.
- **D-02b (Path-resolver edit in make_results.py):** Modify the file-path resolution at `scripts/make_results.py:247` so it prefers `eval_harness_undefended_{model_key}_v6.json` when present and falls back to the un-versioned `eval_harness_undefended_{model_key}.json` otherwise. ~4-line change. This is the *only* edit to make_results.py's logic — the DEFENSE_DISPLAY single-source-of-truth (lines 57+) and three-source aggregation contract are untouched.

### Rate-Limit Handling

- **D-03 (Delay):** `--delay 3` between queries, no retry wrapper. Matches Phase 02.3 + Phase 03.3-07 cloud model conventions exactly. Total wall-clock per model ≈ 100 × (3s sleep + ~5s generation) ≈ 13 min, so two models ≈ 26 min — aligns with the roadmap's "~26 minutes total" budget. Adding a tenacity retry was considered (Option B in discussion) and rejected: it expands `run_eval.py` scope and the failure-rate envelope on these endpoints has historically been low.
- **D-03a (Error policy):** If a single query hits an unrecoverable error (network drop, auth expired, rate-limit retry-budget exhausted, model rejects request with non-recoverable status), record `answer = "[ERROR: <error_type>]"`, set `hijacked_tier1/tier1b/tier2/tier3/tier4` and `hijacked` all to `False`, and increment `aggregate.error_count` by 1. Do **not** abort the run. Output JSON still gets written. This matches Phase 02.3 implicit behavior and keeps the run publishable with `n=99` (or whatever) clearly documented.
- **D-03b (Retry/checkpoint deferred):** A resume-from-checkpoint mechanism (persist completed query results to `.json.partial` after each query, skip on rerun) was considered and rejected as overkill for a 100-query, 26-min run. Captured in deferred ideas.

### Downstream Propagation

- **D-04 (Auto-rerun without overwrite):** Phase 6 must auto-rerun the downstream artifacts that were originally produced without gpt-oss numbers folded in. New binary outputs (PNGs, fresh JSONs, fresh CSVs) **never overwrite** existing committed files — they go to new filenames (`_v6` suffix or analogous). Existing markdowns are **updated in-place** rather than spawned as new files. The submitted Phase 3.4 writeup `docs/phase3_results.md` is **not** edited — it was submitted on Apr 30 and stays as the submission record.
- **D-05 (Markdown updates, in-place):**
  - `docs/results/undefended_baseline.md` — add T1b / T3 / T4 columns for the gpt-oss-20b and gpt-oss-120b rows. Other models' rows: leave T1b/T3/T4 blank or "—" (out of scope to backfill in this phase).
  - `docs/results/arms_race_table.md` — if currently scoped to llama only, leave structure but add new gpt-oss rows for completeness (T1, T1b, T2, T3, T4 paired ASR, undefended baseline). If gpt-oss already absent by design, surface as a new "Cross-LLM undefended baseline (gap fill)" subsection appended to the same .md file.
  - **Both markdowns get a dated disclosure line** at the top: `> Updated 2026-05-04: gpt-oss T1b/T3/T4 added (Phase 6 cross-LLM gap fill). Phase 02.3 / Phase 3.4 numbers above this line are unchanged.`
- **D-06 (CSV companions, new files):** `docs/results/undefended_baseline_v6.csv` and `docs/results/arms_race_table_v6.csv` are emitted as new files — they carry the post-Phase-6 schema (with T1b/T3/T4 columns populated for gpt-oss). The original `.csv` files stay as Phase 3.4 deliverables.
- **D-07 (Figure regeneration, new files):**
  - `figures/d03_arms_race_v6.png` — re-render of D-03 with gpt-oss bars added if the figure's domain admits cross-LLM bars; otherwise emit a new `figures/d03_arms_race_gptoss_v6.png` showing the gpt-oss-only 5-tier bars in the same visual language. Original `figures/d03_arms_race.png` stays untouched.
  - `figures/d12_cross_model_heatmap_v6.png` — extend the 5-tier × 3-LLM heatmap (llama / mistral / gemma4) to a 5-tier × 5-LLM heatmap by appending gpt-oss-20b and gpt-oss-120b columns. Original `figures/d12_cross_model_heatmap.png` stays untouched. Use viridis_r colormap and the W-5 fail-loud invariants (matrix shape, no NaN) per Phase 03.4-03 STATE.
- **D-08 (llama+mistral T1b backfill deferred):** Out of scope this phase. Their `eval_harness_undefended_t34_*.json` files have T3/T4 but no T1b. Captured in deferred ideas for a future phase.

### Claude's Discretion

- Test stub structure (Wave 0): use the established `importlib.util.spec_from_file_location` pattern from Phase 03.2/03.4 stubs. Test files likely: `tests/test_phase6_eval.py` (asserts on _v6.json structure + provenance fields + 5-tier aggregate keys), `tests/test_make_results_v6.py` (asserts path-resolver prefers _v6 when present; existing `tests/test_make_results.py` tests stay green).
- Whether to factor the eval invocation into a thin Phase 6 driver (`scripts/run_phase6_eval.py`) or just two direct `run_eval.py` CLI invocations from a plan command. Either is fine; the driver wins if D-01a sanity-assert is enforced inside it.
- Wave structure (Wave 0 stubs → Wave 1 eval runs → Wave 2 make_results edit + downstream emit → Wave 3 verification) per established Phase 03.x conventions.
- Exact placement of the dated disclosure line within each markdown (top of file vs. top of section it touches) — pick whichever reads cleaner, keep wording consistent across both files.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & precedent

- `.planning/ROADMAP.md` "Phase 6: Cross-LLM undefended baseline gap fill" — phase definition; the ~26 min budget and "single eval run per model, post-hoc per-tier tagging from passage_id" constraint come from here.
- `.planning/ROADMAP.md` "Phase 2.3" — establishes the original v3-corpus T1/T2-only runs Phase 6 supersedes; SC-3 ("Tier-2 ASR is non-zero") is the precedent for cloud-model-on-paired-queries methodology.
- `.planning/ROADMAP.md` "Phase 2.4" — establishes the 5-tier passage_id schema (T1: 20000+, T2: 20050+, T3: 20100+, T1b: 20150+, T4: 20200+) Phase 6 inherits.
- `.planning/STATE.md` — Phase 02.3 decision: "Cloud models (gpt-oss:20b/120b) resist Tier-1 naive injection (0% ASR) but succumb to Tier-2 URL smuggling — confirms scale doesn't defeat instruction smuggling." Phase 6 will refine this with T1b/T3/T4 measurements.

### Code contracts (eval pipeline)

- `scripts/run_eval.py` lines ~30–46 — the constants `TIER{1,1b,2,3,4}_ID_START` and `TIER{1,1b,2,3,4}_HIJACK_STR`; agents must NOT redefine these in any Phase 6 wrapper.
- `scripts/run_eval.py` lines ~233–276 — per-tier passage_id-range tagging logic; this is the "post-hoc per-tier tagging" the roadmap line refers to. Already complete; do not duplicate.
- `scripts/run_eval.py` lines ~339–390 — per-tier aggregate computation (`asr_tier1`, `asr_tier1b`, `asr_tier3`, `asr_tier4`, `paired_asr_*`, `conditional_asr_*`, `co_retrieval_rate_tier4`); these are the keys the new `_v6.json` files will carry.
- `scripts/run_eval.py` CLI flags (`--model`, `--collection`, `--corpus`, `--queries`, `--defense off`, `--delay`, `--output`) — Phase 6 wires through these only; no new flags required.
- `rag/constants.py` — `TIER1_ID_START`, `TIER1B_ID_START`, `TIER2_ID_START`, `TIER3_ID_START`, `TIER4_ID_START`, `ADAPTIVE_ID_START`. Single source of truth for the passage_id ranges.

### Code contracts (downstream consumers)

- `scripts/make_results.py` lines 240–263 — the `eval_harness_undefended_{model_key}.json` reader loop that Phase 6 needs to teach about `_v6.json`. The `model_key` strings (`llama`, `mistral`, `gptoss20b`, `gptoss120b`) are the canonical mapping.
- `scripts/make_results.py` lines 47–105 (DEFENSE_DISPLAY) — single source of truth for defense column labels; Phase 6 does NOT modify this. The "No Defense" / "no_defense" mapping already covers the gap-fill rows.
- `scripts/make_figures.py` D-03 (`render_d03_arms_race`) and D-12 (`render_d12_cross_model_heatmap`) — fail-loud invariants from Phase 03.4-03 (B-2: nansum>0, nanmax>0.05, ≥5 non-zero cells; W-5: matrix.shape==(5,3), no NaN). The v6 re-renders must preserve those invariants (with shape (5,5) for d12_v6).
- `scripts/make_results.py` `_normalize_matrix_model()` lines ~296–309 — model-name normalization (`llama3.2_3b` → `llama3.2:3b` etc.); Phase 6 should add gpt-oss canonical mappings here if they aren't already present.

### Existing artifacts (schema references — DO NOT modify)

- `logs/eval_harness_undefended_gptoss20b.json` — current Phase 02.3 file, T1/T2-only on nq_poisoned_v3. Stays. Read once for schema cross-check.
- `logs/eval_harness_undefended_gptoss120b.json` — same.
- `logs/eval_harness_undefended_t34_llama.json` — current Phase 02.4 file with `asr_tier1`, `asr_tier2`, `asr_tier3`, `asr_tier4`, `co_retrieval_rate_tier4` keys. **This is the schema shape Phase 6 should match.**
- `logs/eval_harness_undefended_t34_mistral.json` — same.
- `data/corpus_poisoned.jsonl` — combined poisoned corpus; do not regenerate.
- `data/test_queries.json` — 100 queries, 50 paired / 50 clean.

### Test contracts

- `tests/test_make_results.py::test_three_source_aggregation` — currently asserts "llama3.2", "mistral", "gpt-oss" model substrings appear in the arms race table. Phase 6's path-resolver edit must keep this test green.
- `tests/test_make_results.py::test_arms_race_table_emitted` — currently asserts "BERT", "Fused", "DEF-02", "No Defense" substrings; Phase 6 doesn't touch DEFENSE_DISPLAY so this stays green automatically.
- `tests/test_make_figures.py` — D-03 and D-12 invariant tests (B-2, W-5). The v6 re-renders must NOT break these — they emit *parallel* files, not replacements.

### Process precedent

- `.planning/phases/03.4-full-evaluation-and-final-report/03.4-02-PLAN.md` — the make_results.py original spec; Phase 6's path-resolver edit lives in this script's contract space.
- `.planning/phases/03.4-full-evaluation-and-final-report/03.4-03-PLAN.md` — the make_figures.py original spec; D-03/D-12 invariant doctrine.
- `.planning/phases/03.3-quick-evaluation-additions/03.3-07-PLAN.md` and SUMMARY — establishes the cross-model 45-cell matrix conventions (subprocess.run with shell=False, model-name underscore-vs-colon canonicalization, etc.) that Phase 6's downstream-propagation step inherits.
- `.planning/phases/02.3-evaluation-harness/02.3-02-PLAN.md` — the original cloud-model-eval invocation pattern; Phase 6's gpt-oss CLI is a direct lineage.

### State / decision history

- `.planning/STATE.md` Phase 02.4-01 — `gpt-oss:20b-cloud` substituted for `kimi-k2.5:cloud` (Rule 3 deviation; kimi paid-only). Phase 6 inherits gpt-oss-20b-cloud as the canonical Tier-3-attacker AND now also as a Tier-1/1b/2/3/4 *target*.
- `.planning/STATE.md` Phase 03.4-02 — `paired_asr_*` is the citable headline number; Phase 6's downstream consumers (`undefended_baseline_v6.csv`, etc.) should surface paired numbers when paired/unpaired both exist, exactly as Phase 3.4 does.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`scripts/run_eval.py`**: per-tier `passage_id`-range tagging (lines ~233–247) and aggregate computation (lines ~339–390) **already produce all 5 tier ASR numbers in one pass** — this is the keystone observation that makes Phase 6 a "single eval run per model" effort. No edits to this script are required.
- **`scripts/_check_collections.py`**: existing collection-name + count probe; pattern reusable for D-01a sanity assert (verify collection has all 5 tier ranges represented).
- **`scripts/make_results.py:247` reader loop**: already iterates over the four canonical `model_key` strings (`llama`, `mistral`, `gptoss20b`, `gptoss120b`); the path-resolver edit (D-02b) is a localized change there.
- **`scripts/make_figures.py`** D-03 + D-12 renderers: already parameterized over the input data; the v6 re-emission passes the `_v6.png` filename and an extended model list to the same renderer.
- **DEFENSE_DISPLAY (`scripts/make_results.py:57+`)**: covers `"no_defense"` → `"No Defense"` already; Phase 6's downstream tables get the right column labels for free.

### Established Patterns

- **CLI cloud-model invocation**: `python scripts/run_eval.py --corpus data/corpus_poisoned.jsonl --collection nq_poisoned_v4 --queries data/test_queries.json --defense off --model gpt-oss:20b-cloud --delay 3 --output logs/eval_harness_undefended_gptoss20b_v6.json` (lineage: Phase 02.3 plan 02; preserved in Phase 03.3-07 matrix driver).
- **5-tier aggregate-keys schema**: `asr_tier{1,1b,2,3,4}` + `paired_asr_tier{1,1b,2,3,4}` + `conditional_asr_tier{1,1b,2,3,4}` + `retrieval_rate` + `co_retrieval_rate_tier4` — established Phase 02.4-03; Phase 6 outputs match this.
- **Test stubs**: `importlib.util.spec_from_file_location` to load scripts/ modules without `__init__.py` (lineage: Phase 03.2-01, Phase 03.4-01); pytest --collect-only succeeds before production code lands.
- **Atomic-write idiom**: write to `.tmp` then `os.replace` — Phase 03.4-03 used this for figures; Phase 6's _v6.png renders should follow.
- **Provenance via in-JSON fields**: `phase`, `collection`, `corpus`, `llm_model`, `n_queries` — every existing eval log has these top-level keys; Phase 6 adds `supersedes_phase_02_3: true` and `error_count: N`.

### Integration Points

- **`scripts/run_eval.py` CLI** — entry point; no source changes.
- **`scripts/make_results.py:247`** — path-resolver edit (≈4 lines).
- **`docs/results/undefended_baseline.md`** — in-place markdown edit (D-05).
- **`docs/results/arms_race_table.md`** — in-place markdown edit or appended subsection (D-05).
- **`docs/results/undefended_baseline_v6.csv`**, **`arms_race_table_v6.csv`** — new CSV outputs (D-06).
- **`figures/d03_arms_race_v6.png`** (or `d03_arms_race_gptoss_v6.png`) — new figure (D-07).
- **`figures/d12_cross_model_heatmap_v6.png`** — new figure, 5×5 shape (D-07).
- **`tests/test_phase6_eval.py`** (new) — assert _v6.json structure + 5-tier aggregate keys + provenance fields.
- **`tests/test_make_results_v6.py`** (new) — assert path-resolver prefers _v6 when present; cross-check existing test_make_results.py stays green.

### Codebase Hazards

- **Encoding (cp1252 on Windows)**: `data/corpus_poisoned.jsonl` contains non-ASCII chars (Unicode homoglyphs in T1b passages, Cyrillic НАСКЕД). Any Python file-read must specify `encoding="utf-8"` explicitly (Phase 03.4-01 documented this in `_phase34_schema_probe.py`). Phase 6 wrappers must follow.
- **Cloud auth**: `ollama login` may have expired since Phase 03.3-07. Pre-flight check: `ollama list` + a single test query at start of Plan 1 wave before committing to the full 100-query run. If auth fails, the entire 26 min budget is wasted.
- **Rate-limit envelope unknown for sustained 100-query × 2-model load**: Phase 02.3 succeeded with `--delay 3`, but Phase 03.3-07 ran much shorter cells (15 queries × 5 tiers × 3 defenses, with restarts). Phase 6 sustained run is the longest single cloud-model invocation in project history. Watch for 429s; the error-count provenance field (D-03a) makes any failures visible.

</code_context>

<specifics>
## Specific Ideas

- The user explicitly framed Phase 6 as: **"this phase should automatically re-run any of the things (like making figures) that has already been done without gpt-oss and add its results too. I shouldn't have to go back to a phase and execute it again."** This drives D-04 — the planner must produce a self-contained phase that re-emits all dependent downstream artifacts in one go, not a thin "logs only" task that requires future cleanup.
- **"Anything new made should not overwrite existing files, whether that's reports, figures or whatever. Existing markdowns however can be updated, instead of making new ones."** This is the precise rule for D-05/D-06/D-07: binary outputs go to `_v6` filenames; markdowns get in-place edits with a dated disclosure header.
- The roadmap line names ~26 minutes total. That's a soft budget, not a hard cap — but the planner should size waves so cloud inference doesn't compete with anything else for the same 26 min.

</specifics>

<deferred>
## Deferred Ideas

### Out-of-scope nice-to-haves surfaced during discussion

- **llama3.2:3b + mistral:7b T1b backfill** — their `eval_harness_undefended_t34_*.json` carry T3/T4 but no T1b. Trivially backfillable by running `run_eval.py --tier-filter tier1b` against `nq_poisoned_v4`, ~5 min for both models. Out of scope for Phase 6 because the roadmap line scoped this phase to gpt-oss only. Candidate for a future "Phase 7 (or 6.1)" gap fill if the writeup ever needs a unified 4-LLM × 5-tier undefended table.
- **Resume-from-checkpoint mechanism for `run_eval.py`** — persist completed query results to `.json.partial` after each query, skip on rerun. Considered for Phase 6 cloud robustness; rejected as overkill (≈30 min of run_eval.py edits for a 100-query × 26-min run). Reconsider if any future phase runs >500 queries against cloud endpoints.
- **Tenacity retry-on-429 wrapper around generator.generate()** — would eliminate zero-rows from transient rate-limit spikes. Rejected because Phase 02.3 + Phase 03.3-07 ran fine without it and the error-count provenance field (D-03a) gives reviewers an honest signal if it does happen.
- **Fresh `nq_poisoned_v6` collection** — would give Phase 6 a unique provenance string, but adds 5–10 min of needless re-embedding and dilutes the apples-to-apples comparison with Phase 02.4 / 03.x runs that all used `nq_poisoned_v4`.
- **Updating `docs/phase3_results.md`** (the submitted Phase 3.4 writeup prose) with the new gpt-oss numbers — explicitly out of scope. The writeup was submitted on Apr 30 and stays as the submission record. Phase 4 presentation can cite the new numbers from `docs/results/undefended_baseline.md` in-place updates without re-opening the writeup.
- **Updating the 5×5 D-12 heatmap to also include adaptive-tier columns** — the current D-12 is base-tiers-only. Adaptive (ATK-08/09) cross-model is a different dimension; out of scope.
- **Surfacing T1b in `docs/results/arms_race_table.md` for llama too** (would require running llama against `nq_poisoned_v4` for T1b). Out of scope; same as the llama+mistral T1b backfill deferral above.

### Scope-creep guardrail (none triggered)

Discussion stayed within phase scope — no scope-creep redirects were issued during this session.

</deferred>

---

*Phase: 06-cross-llm-undefended-baseline-gap-fill-run-gpt-oss-20b-cloud*
*Context gathered: 2026-05-04*
