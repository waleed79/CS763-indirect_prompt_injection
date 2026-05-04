# Phase 7: Honest FPR Metrics — gpt-oss extension - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend Phase 5's three honest FPR metrics (M1 per-chunk, M2 answer-preserved, M3 judge-scored) from llama3.2:3b to the two cloud RAG targets (`gpt-oss:20b-cloud` and `gpt-oss:120b-cloud`) on the `{fused, def02}` defense cells produced by Phase 6, so the project's user-visible defense cost is reported across all three RAG targets rather than just the local llama baseline.

Effective scope: 4 cells × 50 clean queries = **200 judge calls** (~26 min cloud + ~5 min downstream regen).

**In scope:**
- Compute M1, M2, M3 for `{gpt-oss:20b-cloud, gpt-oss:120b-cloud} × {fused, def02}` = 4 cells.
- M1 and M2 from existing Phase 6 v6 logs (no cloud calls).
- M3 via ~200 cloud-judge calls using `gpt-oss:20b-cloud` as judge (mirrors Phase 5).
- Emit `logs/ablation_table_gptoss_v7.json` (4 rows) and `logs/judge_fpr_gptoss_v7.json` (200 verdicts).
- Add a v7 path-resolver branch to `scripts/make_results.py` and `scripts/make_figures.py`; emit `docs/results/honest_fpr_gptoss_v7.md`.
- Append a "Phase 7 addendum" section to `docs/phase5_honest_fpr.md` in-place with a 10-row M1/M2/M3 table covering all 3 RAG targets plus 1–2 paragraphs of cross-LLM analysis.

**Out of scope:**
- Any new attack tier, defense component, or eval-harness change.
- Cross-LLM extension to `mistral:7b` or `gemma4:31b-cloud` (deferred — Phase 6 only produced `{fused, def02}` cells for the two gpt-oss models).
- Modifying Phase 5's `docs/phase5_honest_fpr.md` narrative above the addendum, or its `logs/judge_fpr_llama.json` / `logs/ablation_table.json` deliverables.
- Modifying the submitted Phase 3.4 writeup `docs/phase3_results.md`.
- Trivial `no_defense` rows in `ablation_table_gptoss_v7.json` (ROADMAP scope is {fused, def02} only — 4 rows, not 6).

**Key data reuse:** All four `logs/eval_matrix/gptoss{20b,120b}_cloud__{fused,def02}__all_tiers_v6.json` files contain 100 per-query records each with `answer` + `chunks_removed` + `paired` (verified 2026-05-04). Both `logs/eval_harness_undefended_gptoss{20b,120b}_v6.json` files have identical per-record schema and provide the answer-A defense-OFF baseline. M1 and M2 require zero cloud calls.

</domain>

<decisions>
## Implementation Decisions

### Script Architecture

- **D-01:** **Script reuse strategy is Claude's discretion at plan-time.** Three viable shapes:
  (a) Sibling script `scripts/run_judge_fpr_gptoss.py` — Phase 5 deliverable stays bit-for-bit; ~150 lines of utility code duplicated.
  (b) Extend `scripts/run_judge_fpr.py` with a `--target {llama,gptoss20b,gptoss120b}` flag — single source of truth; touches a freshly-verified Phase 5 deliverable; default `--target=llama` MUST produce bit-identical output.
  (c) Refactor shared logic into `rag/judge_fpr.py` + thin entry scripts — cleanest long-term; doubles plan effort.
  Default lean: **sibling script (a)** — lowest risk to Phase 5's commit at 8e6942b and its 05-VERIFICATION.md test plane. Planner picks (b) or (c) only if the duplication count exceeds ~200 lines or a forthcoming Phase 8 (mistral/gemma4 extension) is on the visible horizon.

### Ablation Table Output

- **D-02:** **`logs/ablation_table_gptoss_v7.json` is a flat composite-key dict.** Keys: `gptoss20b_cloud__fused`, `gptoss20b_cloud__def02`, `gptoss120b_cloud__fused`, `gptoss120b_cloud__def02`. Each value is a flat record:
  ```json
  {
    "model": "gpt-oss:20b-cloud",
    "defense_mode": "fused",
    "per_chunk_fpr": <float>,
    "answer_preserved_fpr": <float>,
    "judge_fpr": <float>,
    "judge_model": "gpt-oss:20b-cloud",
    "judge_n_calls": 50
  }
  ```
  Mirrors Phase 5's flat structure with composite keys to disambiguate model. Separate file (NOT a v7 row appended to `logs/ablation_table.json`) — Phase 5's table stays untouched per ROADMAP wording.

- **D-03:** **No trivial `no_defense` rows.** ROADMAP scope is `{fused, def02}` only — emit exactly 4 rows. The v6 undefended cells serve as the answer-A baseline only; they do not get their own row in the ablation table. (Phase 5 D-02 included a trivial 0/0/0 `no_defense` row for table symmetry; Phase 7 does not — keeping the file scoped to the 4 measured cells reads more honestly.)

### Per-Cell Verdicts File

- **D-04:** **Single combined `logs/judge_fpr_gptoss_v7.json`** with nested structure:
  ```json
  {
    "judge_model": "gpt-oss:20b-cloud",
    "judge_prompt_template": "<verbatim prompt>",
    "verdicts": {
      "gpt-oss:20b-cloud": {
        "fused": {"<query_index>": {"verdict": "...", "ab_assignment": "...", "raw_response": "...", "retry_count": 0}, ...},
        "def02": { ... }
      },
      "gpt-oss:120b-cloud": { "fused": {...}, "def02": {...} }
    }
  }
  ```
  200 total verdict records. Mirrors Phase 5's `logs/judge_fpr_llama.json` scaled by one nesting level (model → defense → query). One artifact for grader reproducibility.

### Downstream Rendering

- **D-05:** **`scripts/make_results.py` gets a v7 path-resolver branch** mirroring Phase 6 D-02b/D-13 pattern. The resolver prefers `logs/ablation_table_gptoss_v7.json` when present and emits a new `docs/results/honest_fpr_gptoss_v7.md` (4-row Markdown + 4-row CSV companion). Phase 5's existing `docs/results/` outputs stay untouched. Module-level constant for the v7 file path lives near `DEFENSE_DISPLAY` (single source of truth pattern from Phase 6 D-12).

- **D-06:** **`scripts/make_figures.py` adds a Phase 7 figure renderer** if a single visualization meaningfully aids Phase 4 talk/poster (e.g., a 3-LLM × 6-defense honest-FPR heatmap stacking llama Phase 5 rows + gpt-oss-20b/120b Phase 7 rows, or a 4-bar M1/M2/M3 grouped chart). Renderer emits to `figures/honest_fpr_v7.png` (or analogous `_v7` suffix). New file only — no overwrite of existing figures. Planner decides whether the figure is necessary or whether the addendum table alone suffices.

### Writeup Integration

- **D-07:** **Append "## Phase 7 addendum: gpt-oss extension (2026-05-04)" section to `docs/phase5_honest_fpr.md` in-place.** Original Phase 5 narrative above the addendum stays bit-for-bit. The addendum contains:
  - 1-paragraph framing: what was extended, why, what's in/out of scope.
  - **10-row M1/M2/M3 table:** llama3.2:3b 6 rows (copied verbatim from the existing Phase 5 table) + gpt-oss:20b-cloud 2 rows ({fused, def02}) + gpt-oss:120b-cloud 2 rows ({fused, def02}).
  - 1-2 paragraph **cross-LLM discussion** examining whether the M1/M2/M3 patterns observed on llama generalize — e.g., does fused defense's per-chunk FPR scale with model size; does gpt-oss-120b "route around" removed chunks more robustly than 20b; how does answer-preserved FPR compare to llama's number; what does this say about user-visible cost across model scales.
  - Brief methodology note explaining the 50-query eval set, single-seed convention, and inheritance of all Phase 5 D-03/D-05/D-06/D-10/D-12 conventions.
  - Pointer to `docs/results/honest_fpr_gptoss_v7.md` for the auto-generated machine-readable companion.

- **D-08:** **No standalone Phase 7 doc.** ROADMAP says "extended Phase 5 writeup", and `docs/phase5_honest_fpr.md` is internal-only (post-presentation refinement, never submitted to the course Google Doc), so editing in-place is safe and minimizes doc surface.

### Input Resolution

- **D-09:** **Hardcoded path maps mirroring Phase 5's `DEFENSE_LOG_MAP` idiom.** Two module-level constants in the Phase 7 script:
  ```python
  CELL_LOG_MAP = {
      ("gpt-oss:20b-cloud",  "fused"): "logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json",
      ("gpt-oss:20b-cloud",  "def02"): "logs/eval_matrix/gptoss20b_cloud__def02__all_tiers_v6.json",
      ("gpt-oss:120b-cloud", "fused"): "logs/eval_matrix/gptoss120b_cloud__fused__all_tiers_v6.json",
      ("gpt-oss:120b-cloud", "def02"): "logs/eval_matrix/gptoss120b_cloud__def02__all_tiers_v6.json",
  }
  OFF_LOG_MAP = {
      "gpt-oss:20b-cloud":  "logs/eval_harness_undefended_gptoss20b_v6.json",
      "gpt-oss:120b-cloud": "logs/eval_harness_undefended_gptoss120b_v6.json",
  }
  ```
  Loud-fail at startup if any mapped path is missing on disk (sanity assert, mirrors Phase 6 D-01a). Trivially auditable in git diff; no glob magic.

- **D-10:** **Schema adapter approach is Claude's discretion at plan-time.** Per-record fields are identical between Phase 5's `defense_*_llama.json` and Phase 6's `eval_matrix/*_v6.json` and `eval_harness_undefended_*_v6.json` files (verified 2026-05-04: all carry `query`, `paired`, `answer`, `chunks_removed`). Top-level keys differ slightly. Default lean: **a small generalization in `load_clean_records()`** that accepts either top-level shape and reads the per-query record list — ~5-line change to that one helper. Planner can substitute a pre-flight normalization pass if it composes better with the chosen script architecture (D-01).

### Inherited from Phase 5 (do not re-decide)

- **D-11:** All of Phase 5's D-03, D-04, D-05, D-06, D-07, D-10, D-12 carry forward verbatim:
  - Judge model = `gpt-oss:20b-cloud` (D-03)
  - Eval set = same 50 clean queries, indices 50–99 of `data/test_queries.json` (D-04)
  - Single-seed judge calls + standing caveat in writeup §1 (D-05)
  - M2's "degraded" signal = same judge as M3, no separate ROUGE/exact-match (D-06)
  - M2 denominator = 50 (literal ROADMAP wording, D-07)
  - A/B prompt with order randomization, assignment recorded per-query (D-10)
  - TIE = PRESERVED; refusals/parse failures retry once then PRESERVED (D-12)
- **D-12:** `--delay 3` cloud convention (Phase 2.4 lineage); atomic-write + checkpoint cache pattern (Phase 5 WR-01 — single ablation write at end, not per-defense rewrites).

### Claude's Discretion

- Bootstrap CIs (1000 resamples) on the three metrics — recommended for the addendum but not blocking; planner decides scope.
- Per-cell logging verbosity — match Phase 5's `scripts/run_judge_fpr.py` conventions.
- Exact wording of the addendum's cross-LLM discussion paragraphs — Claude composes; user reviews on writeup PR.
- Whether the v7 figure (D-06) is rendered — decide based on whether the 10-row table alone reads clearly, or whether a visual makes the cross-LLM comparison sharper.
- Whether to factor M1/M2 (cloud-call-free) and M3 (cloud-call-required) into separate plan waves for incremental progress, or run all three in one script invocation as Phase 5 did. Default: combined — Phase 5 set this precedent and the script already supports `--dry-run` for a fast M1-only sanity check.
- Test stub structure (Wave 0): use `importlib.util.spec_from_file_location` pattern from Phases 03.2-01, 03.4-01, 06-01.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 5 (precedent — read first)

- `.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-CONTEXT.md` — Phase 5 D-01 through D-12 establish all metric definitions, judge config, prompt format, and edge-case handling that Phase 7 inherits. **Especially D-03, D-04, D-05, D-06, D-07, D-10, D-12 — these carry forward verbatim per Phase 7 D-11.**
- `.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-VERIFICATION.md` — Phase 5 verification artifacts; Phase 7 should not break these.
- `scripts/run_judge_fpr.py` (516 lines) — the existing Phase 5 entry point. Source of truth for judge prompt template, retry logic, A/B randomization, atomic-write idiom, and `DEFENSE_LOG_MAP` idiom.
- `logs/judge_fpr_llama.json` — Phase 5's per-cell verdicts file; reference shape for `logs/judge_fpr_gptoss_v7.json` (D-04).
- `logs/ablation_table.json` — Phase 5's flat dict layout; reference shape for `logs/ablation_table_gptoss_v7.json` (D-02).
- `docs/phase5_honest_fpr.md` — Phase 5 writeup; Phase 7 appends an in-place addendum section here (D-07/D-08).

### Phase 6 (input artifacts)

- `.planning/phases/06-cross-llm-undefended-baseline-gap-fill-run-gpt-oss-20b-cloud/06-CONTEXT.md` — Phase 6 D-09b establishes the `gptoss{20b,120b}_cloud__{fused,def02}__all_tiers_v6.json` filename pattern; Phase 6 D-13 establishes the v6 path-resolver pattern that Phase 7 D-05 mirrors.
- `logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json` — Phase 7 input cell (gpt-oss:20b × fused).
- `logs/eval_matrix/gptoss20b_cloud__def02__all_tiers_v6.json` — Phase 7 input cell (gpt-oss:20b × def02).
- `logs/eval_matrix/gptoss120b_cloud__fused__all_tiers_v6.json` — Phase 7 input cell (gpt-oss:120b × fused).
- `logs/eval_matrix/gptoss120b_cloud__def02__all_tiers_v6.json` — Phase 7 input cell (gpt-oss:120b × def02).
- `logs/eval_harness_undefended_gptoss20b_v6.json` — Phase 7 answer-A baseline (gpt-oss:20b defense-OFF).
- `logs/eval_harness_undefended_gptoss120b_v6.json` — Phase 7 answer-A baseline (gpt-oss:120b defense-OFF).

### Code contracts (must read before planning)

- `scripts/run_judge_fpr.py:70-91` — `parse_verdict()` and `load_clean_records()`; the latter is the helper Phase 7 D-10 generalizes.
- `scripts/run_judge_fpr.py:112-145` — `randomize_ab()` and `atomic_write_json()`; reused verbatim by Phase 7 (or copied if sibling script).
- `scripts/run_judge_fpr.py:147-211` — `judge_one()`; the LLM-call inner loop with retry policy. Reused verbatim.
- `scripts/run_judge_fpr.py:213-348` — `run_for_defense()`; the per-cell M1/M2/M3 computation loop. Phase 7 generalizes this to per-(model, defense) cell.
- `scripts/make_results.py:240-263` — Phase 6's path-resolver pattern; Phase 7 D-05 adds an analogous branch for the v7 ablation file.
- `scripts/make_results.py:47-105` — `DEFENSE_DISPLAY` single-source-of-truth; Phase 7 does NOT modify this (the existing "Fused" / "DEF-02" labels already cover the v7 rows).
- `scripts/make_figures.py` — D-03, D-12 fail-loud invariants from Phase 03.4-03 (B-2: nansum>0, nanmax>0.05, ≥5 non-zero cells; W-5: matrix shape + no NaN). Any v7 figure renderer (D-06) must follow the same invariant pattern.

### Project & roadmap

- `.planning/ROADMAP.md` "Phase 7: Honest FPR Metrics — gpt-oss extension" — phase definition, 4-cell scope, ~26 min cloud + ~5 min downstream budget, in-place writeup extension wording, "do not redefine" inheritance from Phase 5.
- `.planning/ROADMAP.md` "Phase 5" and "Phase 6" — upstream phase contracts.
- `.planning/PROJECT.md` — development environment (conda env `rag-security`), cloud-LLM conventions.
- `.planning/REQUIREMENTS.md` — Phase 5 entry for the three metrics (M1, M2, M3 definitions are normative there).
- `.planning/STATE.md` Phase 02.4-01 — `gpt-oss:20b-cloud` substituted for `kimi-k2.5:cloud`; this is the same model used both as Tier-3 attacker, RAG target (Phase 6 + Phase 7), AND judge (Phase 5 + Phase 7).
- `data/test_queries.json` — 100 queries; clean subset is indices 50–99.

### Cloud inference convention

- All cloud LLM calls use `--delay 3` (Phase 2.4 lineage). Phase 7 inherits without question.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`scripts/run_judge_fpr.py` (516 lines)** — Phase 5's entry point. Functions reusable verbatim: `parse_verdict()`, `randomize_ab()`, `atomic_write_json()`, `judge_one()`. Function generalizable: `run_for_defense()` → `run_for_cell((model, defense))`. Function tweakable: `load_clean_records()` → accept either Phase 5 or Phase 6 v6 top-level schema (D-10). Module constants reusable: `JUDGE_PROMPT_TEMPLATE`, `JUDGE_USER_TEMPLATE`, `MAX_RETRIES`. Helper to add: `CELL_LOG_MAP` + `OFF_LOG_MAP` (D-09).
- **Phase 6 v6 cells** — All four `logs/eval_matrix/gptoss{20b,120b}_cloud__{fused,def02}__all_tiers_v6.json` exist with 100 records each, per-record fields verified (`answer`, `chunks_removed`, `paired` all present). M1 + M2 require zero cloud calls; the data is already on disk.
- **Phase 6 v6 undefended baselines** — Both `logs/eval_harness_undefended_gptoss{20b,120b}_v6.json` exist with identical per-record schema. Provide answer-A defense-OFF source for the judge prompt.
- **`scripts/make_results.py:240-263` path-resolver pattern** — Phase 6 D-02b/D-13 idiom; Phase 7 D-05 mirrors it for `ablation_table_gptoss_v7.json`.
- **`scripts/make_results.py` `DEFENSE_DISPLAY`** — covers `"fused"` → `"Fused"` and `"def02"` → `"DEF-02"` already; Phase 7 row labels are free.
- **`tests/test_make_results.py` + `tests/test_make_results_v6.py`** — Phase 6's test patterns establish how to add `tests/test_make_results_v7.py` for the new resolver branch.

### Established Patterns

- **Output logs in `logs/` with descriptive names** (Phase 2.3 convention). Phase 7 follows: `logs/ablation_table_gptoss_v7.json`, `logs/judge_fpr_gptoss_v7.json`, `logs/judge_fpr_gptoss_v7.json.cache`.
- **Atomic write idiom**: write to `.tmp` then `os.replace()` — Phase 03.4-03 / Phase 5 WR-01. Phase 7 reuses verbatim.
- **Single read-modify-write of ablation table** at end of run (Phase 5 WR-01) — minimizes Windows non-atomic-replace corruption window. Phase 7 inherits.
- **Module constant placement**: single-source-of-truth dicts (e.g., `DEFENSE_DISPLAY`, `CELL_LOG_MAP`) live near top of file with comment pointer; tests import via `importlib.util.spec_from_file_location`.
- **`scripts/run_*.py` for grader-facing entry points** vs. `scripts/_*.py` for internal/build scripts. Phase 7's entry script (sibling or extended) keeps the `run_` prefix.
- **Test stubs (Wave 0)**: skip-guards with `pytest.importorskip` or try/except ImportError module-level guards (Phase 03.1-01 / 03.4-01 lineage); pytest --collect-only succeeds before production code lands.
- **Aggregated tables include `model`, `defense_mode`, `n_queries`, `judge_model`, `judge_n_calls`** for provenance — Phase 5 D-11; Phase 7 D-02 schema preserves all of these per row.

### Integration Points

- **NEW:** `scripts/run_judge_fpr_gptoss.py` (default sibling shape per D-01 lean) — entry point. Reads CELL_LOG_MAP + OFF_LOG_MAP, runs judge over 200 cells, writes per-verdict log + `ablation_table_gptoss_v7.json`.
- **NEW:** `logs/ablation_table_gptoss_v7.json` — 4 cells, flat composite-key dict (D-02).
- **NEW:** `logs/judge_fpr_gptoss_v7.json` — 200 verdicts, nested model→defense→query (D-04).
- **NEW:** `logs/judge_fpr_gptoss_v7.json.cache` — checkpoint cache for resume support.
- **NEW:** `docs/results/honest_fpr_gptoss_v7.md` — auto-generated 4-row Markdown + CSV companion (D-05).
- **MODIFIED (light touch):** `scripts/make_results.py` — add v7 path-resolver branch + `emit_honest_fpr_gptoss_v7()` emission, mirroring Phase 6 D-13. ~30-line delta.
- **MODIFIED (light touch):** `scripts/make_figures.py` — optional v7 figure renderer (D-06); planner decides whether necessary.
- **MODIFIED (in-place edit):** `docs/phase5_honest_fpr.md` — append "## Phase 7 addendum" section (D-07).
- **NEW:** `tests/test_phase7_judge_fpr.py` — assert ablation_table_gptoss_v7.json structure, verdicts file shape, schema invariants.
- **NEW:** `tests/test_make_results_v7.py` — assert v7 path-resolver prefers v7 file when present; existing test_make_results.py and test_make_results_v6.py stay green.
- **NO CHANGE:** `scripts/run_judge_fpr.py` (if D-01 sibling path chosen), `logs/judge_fpr_llama.json`, `logs/ablation_table.json`, `docs/results/` Phase 5 outputs, Phase 5's prose above the addendum in `docs/phase5_honest_fpr.md`.

### Codebase Hazards

- **Encoding (cp1252 on Windows)**: `data/corpus_poisoned.jsonl` and several v6 cell JSONs may contain non-ASCII chars. Any Python file-read must specify `encoding="utf-8"` explicitly (Phase 03.4-01 + Phase 6 hazard list).
- **Cloud auth (`ollama login`)**: may have expired since Phase 6 — pre-flight check (`ollama list` + a single test judge query) at start of M3 wave before committing to the 200-call run. If auth fails, the entire ~26 min budget is wasted.
- **Rate-limit envelope for sustained 200-query × single-judge load**: Phase 5's 300-call run on the same `gpt-oss:20b-cloud` judge endpoint succeeded with `--delay 3`, so envelope is well-characterized. The error-count provenance field (Phase 6 D-03a pattern) makes any failures visible.
- **Atomic write on Windows**: `os.replace()` is non-atomic on Windows; Phase 5 WR-01 minimizes this by single-write-at-end. Phase 7 inherits the same exposure window.
- **Schema-drift between Phase 5's `defense_*_llama.json` and Phase 6's v6 cells**: top-level keys differ; per-record fields identical. The `load_clean_records()` adapter (D-10) is the localized fix; do NOT scatter schema-fork branches throughout the script.

</code_context>

<specifics>
## Specific Ideas

- The user explicitly chose **"Yes — add a v7 path-resolver branch"** for downstream rendering, mirroring Phase 6's auto-rerun-without-overwrite precedent. Phase 7 must be self-contained: running the entry script + `make_results.py` should produce all artifacts (ablation JSON, verdicts JSON, addendum table in `docs/results/`) without manual cleanup.
- The user explicitly chose **"Append addendum to phase5_honest_fpr.md"** + **"1-2 paragraph cross-LLM analysis"** — the addendum is not just a numbers dump; it must situate the gpt-oss numbers against the llama Phase 5 numbers and offer at least one substantive interpretation (e.g., does fused defense's per-chunk FPR scale with model size; does answer-preserved FPR cluster differently across model scales; what does this say about user-visible cost when the RAG target is a frontier-scale cloud LLM vs. a small local model).
- The user explicitly chose **"Hardcoded path map mirroring Phase 5"** for input resolution — explicit and auditable beats glob magic for a 4-cell phase.
- The 4 v6 cells and 2 v6 undefended baselines all live on disk RIGHT NOW (verified 2026-05-04). The phase can begin immediately; no upstream phase needs to complete first.
- ROADMAP wall-clock budget is **~26 min cloud + ~5 min downstream regen** — the planner should size waves accordingly (not split M3 into multiple cloud sessions).

</specifics>

<deferred>
## Deferred Ideas

### Out-of-scope nice-to-haves surfaced during discussion

- **Cross-LLM extension to mistral:7b and gemma4:31b-cloud** — Phase 6 only produced `{fused, def02}` cells for the two gpt-oss models. Extending honest FPR to mistral and gemma4 would require either (a) re-running Phase 6 against those models for the {fused, def02} defenses, or (b) reading from the existing `logs/eval_matrix/_summary.json` 45-cell matrix (which has fused/def02 cells for llama, mistral, gemma4 but uses a slightly different schema). Captured as Future Work for a hypothetical Phase 8.
- **Multi-seed judge calls (3-seed majority vote)** — would tighten M3 numbers at 3× cost; deferred under the standing single-seed convention (Phase 5 D-05).
- **Cross-judge sanity check (gemma4 on a 20-query subset)** — strongest methodological move but doubles plan complexity; deferred (Phase 5 deferred too).
- **Bootstrap CIs (1000 resamples) on M1/M2/M3** — recommended for the addendum but listed as Claude's discretion; not blocking.
- **Trivial `no_defense` rows in `ablation_table_gptoss_v7.json`** — Phase 5 included them for table symmetry; Phase 7 explicitly excludes them per D-03 to keep the file scoped to the 4 measured cells.
- **In-place rewrite of Phase 5's `logs/ablation_table.json`** to also carry gpt-oss rows — would mutate a freshly-verified Phase 5 deliverable; rejected in favor of a separate `_gptoss_v7.json` file.
- **Refactoring `scripts/run_judge_fpr.py` into a library + thin entry scripts** (D-01 option c) — cleanest long-term but doubles plan effort. Reconsider if a Phase 8 cross-LLM extension materializes.
- **A v7 figure** (D-06) — optional. Recommended only if the 10-row table doesn't read clearly on its own.
- **Hand-annotated ground-truth Metric 2 path** (sharper signal on a 10-20 query subset) — deferred under the inherited Phase 5 D-06 judge-only convention.
- **Updating `docs/phase3_results.md`** (the submitted Phase 3.4 writeup) with Phase 7 numbers — explicitly out of scope. Submitted artifact stays.

### Scope-creep guardrail

Discussion stayed within phase scope — no scope-creep redirects were issued during this session.

</deferred>

---

*Phase: 07-honest-fpr-metrics-gpt-oss-extension*
*Context gathered: 2026-05-04*
