# Phase 7: Honest FPR Metrics — gpt-oss extension - Research

**Researched:** 2026-05-04
**Domain:** Cloud-LLM judge evaluation + cross-LLM extension of an existing post-hoc FPR pipeline (Python 3.11, Ollama, single-LLM-as-judge methodology). No new attacks, no new defenses, no new corpus.
**Confidence:** HIGH

## Summary

Phase 7 is a narrowly-scoped, low-architectural-risk extension of Phase 5. Three findings dominate the research:

1. **The Phase 6 v6 cell schema is bit-for-bit compatible with Phase 5's `load_clean_records()` helper.** All four `logs/eval_matrix/gptoss{20b,120b}_cloud__{fused,def02}__all_tiers_v6.json` files and both `logs/eval_harness_undefended_gptoss{20b,120b}_v6.json` files use the same top-level `results` key and the same per-record fields (`query`, `paired`, `answer`, `chunks_removed`) as Phase 5's `defense_*_llama.json`. **CONTEXT D-10's "5-line adapter" estimate is conservative — the existing helper works as-is**; the planner can confirm by passing the v6 paths to `load_clean_records()` directly. The only schema diffs are at the top level (extra `supersedes_phase_02_3`, `n_paired` keys; extra per-record `hijacked_tier1b`, `tier1b_retrieved`, `adaptive_retrieved` fields not used by the metric pipeline) and they are additive — they cannot break a reader that uses `data["results"]` and `r.get(...)`.

2. **The path-resolver hook in `scripts/make_results.py` is already the right shape for D-05.** Phase 6 added `_resolve_matrix_path()` (lines 514–530) that tests `_v6` suffix presence and falls back to the un-versioned name. Phase 7 adds an analogous `_resolve_v7_ablation_path()` (or extends a new emit function) that prefers `logs/ablation_table_gptoss_v7.json` over the un-versioned `ablation_table.json` when emitting the gpt-oss honest-FPR markdown. **No regex fork, no architectural seam — the resolver pattern Phase 6 already established is the same shape Phase 7 needs.**

3. **The cloud rate-limit envelope is well-characterized.** Phase 5 ran 350 calls (7 defenses × 50 queries) on `gpt-oss:20b-cloud` with `--delay 3` to completion; Phase 7's 200 calls (4 cells × 50 queries) is a 43% smaller envelope on the same endpoint. The only risk is `ollama login` token expiry (separate from registry presence — `ollama list` shows `gpt-oss:20b-cloud` registered but does not prove the auth token is live). Flagged as a plan-time preflight check, not a research blocker.

**Primary recommendation:** Implement Phase 7 as a sibling script (`scripts/run_judge_fpr_gptoss.py`) per CONTEXT D-01 default lean. Reuse `parse_verdict`, `randomize_ab`, `atomic_write_json`, `judge_one`, and `load_clean_records` verbatim via `importlib.util.spec_from_file_location` (the test-stub pattern already used in Phases 03.2/03.4/06). Add two module constants (`CELL_LOG_MAP`, `OFF_LOG_MAP`) and a `run_for_cell((model, defense), cell_path, off_path, ...)` generalization of `run_for_defense`. Net plan delta: ~150 lines of new script + ~30-line `make_results.py` v7 branch + ~60 lines of tests. Wall clock: ~26 min cloud.

## Architectural Responsibility Map

Phase 7 is a single-tier (offline batch script + post-hoc analysis) phase. There is no UI, no API, no live service. The "tiers" are the data pipeline stages.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Read v6 cell logs (no cloud) | Disk I/O / log layer | — | M1 + M2 numerator inputs are already on disk; pure replay. |
| Pairwise A/B judge call | Cloud-LLM client (Ollama) | — | M3 only; ~200 calls with `--delay 3`. |
| Verdict aggregation → M1/M2/M3 | Compute / Python | — | Reuses Phase 5 reduction logic verbatim. |
| Atomic write of `ablation_table_gptoss_v7.json` | Disk I/O / log layer | — | Single-write-at-end (Phase 5 WR-01 inheritance). |
| Cache / resume support | Disk I/O / log layer | — | Per-defense cache write after each cell (Phase 5 RESEARCH §5.1). |
| Path resolution (v7 prefers, v6 falls back) | `make_results.py` reader | — | Mirrors Phase 6 D-13 resolver pattern. |
| Rendered Markdown + CSV companion | `make_results.py` emitter | — | New `emit_honest_fpr_gptoss_v7()` analogous to Phase 6 emitters. |
| Optional figure render | `make_figures.py` renderer | — | Optional per CONTEXT D-06; planner decides. |
| Writeup addendum | `docs/phase5_honest_fpr.md` (in-place append) | — | D-07/D-08; appended section, original prose untouched. |

**Key insight:** No tier crossing is invented. Phase 7 reuses every existing tier boundary that Phase 5 + Phase 6 established. The "right" tier for each new piece of work is dictated by the existing layout.

## User Constraints (from CONTEXT.md)

### Locked Decisions

The following are user-locked decisions from `07-CONTEXT.md`. Plan-time agents MUST NOT re-decide these.

- **D-02 — Ablation table shape:** Flat composite-key dict with keys `gptoss20b_cloud__fused`, `gptoss20b_cloud__def02`, `gptoss120b_cloud__fused`, `gptoss120b_cloud__def02`. Each value carries `model`, `defense_mode`, `per_chunk_fpr`, `answer_preserved_fpr`, `judge_fpr`, `judge_model`, `judge_n_calls`. Separate file (`logs/ablation_table_gptoss_v7.json`), not a row appended to Phase 5's `logs/ablation_table.json`.
- **D-03 — No trivial `no_defense` rows.** Exactly 4 measured rows in the v7 ablation file.
- **D-04 — Verdicts file shape:** Single combined `logs/judge_fpr_gptoss_v7.json` with nested structure `verdicts[model][defense][query_index] = verdict_record`.
- **D-05 — `make_results.py` v7 path-resolver branch:** prefers `logs/ablation_table_gptoss_v7.json` when present; emits new `docs/results/honest_fpr_gptoss_v7.md` (4-row Markdown + CSV companion). Phase 5 outputs untouched.
- **D-07 — Append "## Phase 7 addendum: gpt-oss extension (2026-05-04)" to `docs/phase5_honest_fpr.md` in-place.** Original Phase 5 prose above the addendum stays bit-for-bit. 10-row M1/M2/M3 table (llama 6 rows verbatim + gpt-oss 4 new rows) + 1-2 paragraphs cross-LLM analysis + methodology note + pointer to `docs/results/honest_fpr_gptoss_v7.md`.
- **D-08 — No standalone Phase 7 doc.**
- **D-09 — Hardcoded path maps mirroring Phase 5's `DEFENSE_LOG_MAP`:** `CELL_LOG_MAP` (4 entries) + `OFF_LOG_MAP` (2 entries). Loud-fail at startup if any path missing.
- **D-11 — Phase 5 inherited verbatim:**
  - Judge model = `gpt-oss:20b-cloud` (D-03)
  - Eval set = same 50 clean queries, indices 50–99 of `data/test_queries.json` (D-04)
  - Single-seed judge calls + standing caveat in writeup §1 (D-05)
  - M2 "degraded" signal = same judge as M3, no separate ROUGE/exact-match (D-06)
  - M2 denominator = 50 (D-07)
  - A/B prompt with order randomization, assignment recorded per-query (D-10)
  - TIE = PRESERVED; refusals/parse failures retry once then PRESERVED (D-12)
- **D-12 — `--delay 3` cloud convention; atomic-write + checkpoint cache pattern** (Phase 5 WR-01).

### Claude's Discretion (planner picks at plan-time)

- **D-01 — Script architecture:** sibling (`scripts/run_judge_fpr_gptoss.py`) [default lean] vs. extend `scripts/run_judge_fpr.py` with `--target` flag vs. refactor into `rag/judge_fpr.py` + thin entry scripts. Default lean is sibling — lowest risk to Phase 5's commit.
- **D-10 — Schema adapter approach:** small generalization in `load_clean_records()` accepting either top-level shape [default lean] vs. pre-flight normalization pass. **(Research finding: existing helper already works; no adapter needed — see "Code Examples" §1 below.)**
- Bootstrap CIs (1000 resamples) on M1/M2/M3 — recommended for the addendum but not blocking.
- Per-cell logging verbosity — match Phase 5's `scripts/run_judge_fpr.py` conventions.
- Exact wording of cross-LLM discussion paragraphs — Claude composes; user reviews on writeup PR.
- Whether the optional v7 figure (D-06) is rendered.
- Whether to factor M1/M2 (cloud-call-free) and M3 (cloud-call-required) into separate plan waves vs. one combined invocation. Default: combined (Phase 5 precedent; `--dry-run` already supports M1-only sanity check).
- Test stub structure (Wave 0): use `importlib.util.spec_from_file_location` from Phases 03.2-01 / 03.4-01 / 06-01.

### Deferred Ideas (OUT OF SCOPE — do not research, do not plan)

- Cross-LLM extension to `mistral:7b` and `gemma4:31b-cloud` (Phase 6 only produced `{fused, def02}` cells for gpt-oss).
- Multi-seed judge calls (3-seed majority vote).
- Cross-judge sanity check (gemma4 on a 20-query subset).
- Bootstrap CIs (Claude's discretion, not deferred — but never blocking).
- Trivial `no_defense` rows in `ablation_table_gptoss_v7.json`.
- In-place rewrite of Phase 5's `logs/ablation_table.json` to also carry gpt-oss rows.
- Refactoring `scripts/run_judge_fpr.py` into a library (D-01 option c).
- Optional v7 figure (D-06) — only if planner decides 10-row table doesn't read clearly alone.
- Hand-annotated ground-truth M2 path (Phase 5 D-06 judge-only convention inherited).
- Updating `docs/phase3_results.md` (submitted Phase 3.4 writeup) with Phase 7 numbers.

## Phase Requirements

The phase requirement IDs were not set in INIT (`phase_req_ids` was TBD). Mapping ROADMAP Phase 7 requirements to research support:

| ID (ROADMAP-implicit) | Description | Research Support |
|-----------------------|-------------|------------------|
| P7-M1 | Per-chunk FPR computed for `{gpt-oss:20b-cloud, gpt-oss:120b-cloud} × {fused, def02}` from existing v6 logs (no cloud calls) | Verified `chunks_removed` field present in all 4 v6 cells (Code Examples §1); reuses Phase 5 numerator/denominator formula verbatim |
| P7-M2 | Answer-preserved FPR computed for the same 4 cells from existing v6 logs | M2 numerator subset is non-strictly contained in M1 ∩ M3 sets — exact same computation as Phase 5; reuses `degraded_with_removal_count / N_CLEAN` |
| P7-M3 | LLM-as-judge FPR via ~200 cloud-judge calls using `gpt-oss:20b-cloud` | Judge endpoint registered in `ollama list`; Phase 5 ran 350 calls successfully on same endpoint; rate-limit envelope characterized |
| P7-OUT-J | Emit `logs/ablation_table_gptoss_v7.json` with M1/M2/M3 × 4 cells (D-02 schema) | Schema definition in CONTEXT D-02; sample row shape verified against Phase 5's existing `judge_fpr` row |
| P7-OUT-V | Emit `logs/judge_fpr_gptoss_v7.json` with 200 verdicts (D-04 nested schema) | Phase 5's `judge_fpr_llama.json` shape verified; D-04 adds one nesting level (model → defense → query) |
| P7-RESV | `make_results.py` v7 path-resolver branch + `docs/results/honest_fpr_gptoss_v7.md` | Phase 6's `_resolve_matrix_path` at `make_results.py:514–530` is the exact pattern to mirror |
| P7-DOC | Append "## Phase 7 addendum" section to `docs/phase5_honest_fpr.md` in-place | Phase 5 writeup section structure verified: §1–§6 + References (lines 12, 22, 69, 87, 105, 117, 128) |
| P7-INHERIT | Inherit Phase 5 D-03/04/05/06/07/10/12 verbatim (judge model, eval set, single-seed, M2 = judge, M2 denom = 50, A/B randomization, TIE=PRESERVED) | All seven decisions documented in CONTEXT D-11 and verified against `scripts/run_judge_fpr.py` source |

## Standard Stack

### Core (already installed; no new dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11 | Runtime | Project standard per `CLAUDE.md`; Phase 5 uses 3.11 [VERIFIED: project CLAUDE.md] |
| `ollama` (python client) | ≥0.6,<1.0 | Cloud LLM client | Already used by `scripts/run_judge_fpr.py:27` (try/except ImportError pattern); same Client invocation [VERIFIED: scripts/run_judge_fpr.py L26-31, L170-181] |
| `pytest` | 9.0.3 | Test framework | Project standard; verified installed in current env [VERIFIED: `pytest --version`] |
| `pandas` | ≥2.0 | DataFrame for `make_results.py` | Already used by `scripts/make_results.py:43` for table emission [VERIFIED: scripts/make_results.py L43] |
| stdlib (`json`, `pathlib`, `argparse`, `random`, `time`, `importlib.util`) | stdlib | Script plumbing | All used by Phase 5 script verbatim [VERIFIED: scripts/run_judge_fpr.py imports] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `tabulate` (transitive via pandas) | as installed | `to_markdown()` in emitters | Required by `emit_table()` in `make_results.py`; the `fillna("—")` workaround is already documented (Phase 06-04 STATE entry) [VERIFIED: scripts/make_results.py L466] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Sibling script (D-01a) | Extend `run_judge_fpr.py` with `--target` flag | Single source of truth, but touches a freshly-verified Phase 5 deliverable (commit 8e6942b) and risks drift in default behavior. Reject unless Phase 8 (mistral/gemma4) is on the visible horizon. |
| Sibling script | Refactor into `rag/judge_fpr.py` library + thin entry scripts | Cleanest long-term but doubles plan effort. Reject for a 4-cell phase. |
| `importlib.util.spec_from_file_location` for code reuse | Direct `from scripts.run_judge_fpr import ...` | Project has no `scripts/__init__.py`; importlib spec pattern already established in Phases 03.2-01, 03.4-01, 06-01 test stubs [VERIFIED: STATE.md Phase 03.4-01 entry, Phase 06-01 test conventions]. |

**Installation:** None — all dependencies already in the conda env `rag-security`.

**Version verification:** No new packages, so no version churn risk. Existing pinned versions in the env are already known-good for Phase 5's `scripts/run_judge_fpr.py`.

## Architecture Patterns

### System Architecture Diagram

```
                     ┌────────────────────────────────────────────┐
                     │  Inputs (already on disk; verified present) │
                     │                                              │
                     │  logs/eval_matrix/                           │
                     │    gptoss20b_cloud__fused__all_tiers_v6.json │
                     │    gptoss20b_cloud__def02__all_tiers_v6.json │
                     │    gptoss120b_cloud__fused__all_tiers_v6.json│
                     │    gptoss120b_cloud__def02__all_tiers_v6.json│
                     │                                              │
                     │  logs/eval_harness_undefended_                │
                     │    gptoss20b_v6.json     (answer-A baseline) │
                     │    gptoss120b_v6.json    (answer-A baseline) │
                     └────────────────────────────────────────────┘
                                          │
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │  scripts/run_judge_fpr_gptoss.py             │
                  │  (NEW — sibling script per D-01 default lean) │
                  │                                                │
                  │   1. assert all 6 input paths exist (D-09)    │
                  │   2. ollama_login_preflight (1 test call)     │
                  │   3. for each (model, defense) cell:          │
                  │        load_clean_records(off_path)           │ ← reuse Phase 5
                  │        load_clean_records(cell_path)          │ ← reuse Phase 5
                  │        for q in 50 clean queries:             │
                  │          M1 → chunks_removed[q]               │
                  │          M3 → judge_one(off, cell, A/B)       │ ← reuse Phase 5
                  │          M2 → M1[q]>0 ∧ M3[q]==DEGRADED       │
                  │        atomic_write cache                     │ ← reuse Phase 5
                  │   4. atomic_write logs/ablation_table_         │
                  │        gptoss_v7.json (single write at end)   │
                  │   5. atomic_write logs/judge_fpr_gptoss_v7    │
                  │        .json (D-04 nested verdicts)           │
                  └──────────────────────────────────────────────┘
                                          │
                  ┌───────────────────────┴────────────────────────┐
                  ▼                                                ▼
   ┌──────────────────────────────────┐         ┌──────────────────────────────────┐
   │  scripts/make_results.py          │         │  scripts/make_figures.py         │
   │  (LIGHT-TOUCH MODIFICATION)       │         │  (OPTIONAL per D-06)              │
   │                                    │         │                                    │
   │   _resolve_v7_ablation_path()    │         │   render_honest_fpr_v7_heatmap()  │
   │   load_honest_fpr_v7()           │         │     OR render_honest_fpr_v7_bars  │
   │   emit_honest_fpr_gptoss_v7()    │         │   → figures/honest_fpr_v7.png      │
   │   → docs/results/                 │         │   (NEW file; never overwrites      │
   │     honest_fpr_gptoss_v7.md       │         │    Phase 3.4/6 PNGs)              │
   │     honest_fpr_gptoss_v7.csv      │         └──────────────────────────────────┘
   └──────────────────────────────────┘
                  │
                  ▼
  ┌────────────────────────────────────────────┐
  │  docs/phase5_honest_fpr.md                  │
  │  (IN-PLACE EDIT; original prose untouched)  │
  │                                              │
  │  ## 1. Motivation        (verbatim)         │
  │  ## 2. The Three Metrics (verbatim)         │
  │  ## 3. Methodology       (verbatim)         │
  │  ## 4. Results           (verbatim)         │
  │  ## 5. Discussion        (verbatim)         │
  │  ## 6. Limitations       (verbatim)         │
  │  ## References           (verbatim)         │
  │  ## Phase 7 addendum: gpt-oss extension     │ ← APPEND HERE (D-07)
  │      • framing paragraph                     │
  │      • 10-row M1/M2/M3 table                 │
  │      • cross-LLM discussion (1-2 paras)     │
  │      • methodology note                      │
  │      • pointer to honest_fpr_gptoss_v7.md   │
  └────────────────────────────────────────────┘
```

**Key flow property:** The script is "M1/M2 = pure log replay, M3 = cloud calls." `--dry-run` (already supported by Phase 5's `parse_args`) lets the planner verify M1/M2 are correct before committing to the ~26 min cloud spend.

### Recommended Project Structure (additive only)

```
scripts/
├── run_judge_fpr.py              # (UNCHANGED) Phase 5 entry — sibling-script default
├── run_judge_fpr_gptoss.py       # NEW — Phase 7 entry, ~150 lines
├── make_results.py               # MODIFIED — add v7 path-resolver + emit_honest_fpr_gptoss_v7 (~30 lines)
├── make_figures.py               # OPTIONAL — Phase 7 figure renderer (~50 lines, D-06)
└── ...

logs/
├── ablation_table.json           # (UNCHANGED) Phase 5 deliverable
├── judge_fpr_llama.json          # (UNCHANGED) Phase 5 deliverable
├── ablation_table_gptoss_v7.json # NEW — D-02 flat composite-key dict, 4 entries
├── judge_fpr_gptoss_v7.json      # NEW — D-04 nested verdicts, 200 records
└── judge_fpr_gptoss_v7.json.cache # NEW — checkpoint cache for resume

docs/
├── phase5_honest_fpr.md          # MODIFIED (in-place append) — D-07 addendum section
└── results/
    ├── honest_fpr_gptoss_v7.md   # NEW — D-05 emit (4-row MD)
    └── honest_fpr_gptoss_v7.csv  # NEW — D-05 emit (4-row CSV companion)

tests/
├── test_phase7_judge_fpr.py      # NEW — assert ablation+verdicts file structure
└── test_make_results_v7.py       # NEW — assert v7 path-resolver prefers v7 file
```

### Pattern 1: importlib.util.spec_from_file_location for code reuse

**What:** Load a `scripts/` module without `scripts/__init__.py`. The project has no package layout, so this is the canonical reuse path.
**When to use:** Test stubs (Wave 0) referencing functions from `scripts/run_judge_fpr.py`; or when `scripts/run_judge_fpr_gptoss.py` wants to import `parse_verdict`, `randomize_ab`, `judge_one`, `atomic_write_json`, `load_clean_records`, `JUDGE_SYSTEM_PROMPT`, `JUDGE_USER_TEMPLATE` from the Phase 5 script without copying them.
**Example:**
```python
# Source: scripts/run_judge_fpr_gptoss.py (proposed)
import importlib.util
from pathlib import Path

_phase5_path = Path(__file__).parent / "run_judge_fpr.py"
_spec = importlib.util.spec_from_file_location("run_judge_fpr", _phase5_path)
_phase5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_phase5)

# Reuse Phase 5 helpers verbatim
parse_verdict = _phase5.parse_verdict
randomize_ab  = _phase5.randomize_ab
judge_one     = _phase5.judge_one
atomic_write_json = _phase5.atomic_write_json
load_clean_records = _phase5.load_clean_records
JUDGE_SYSTEM_PROMPT = _phase5.JUDGE_SYSTEM_PROMPT
JUDGE_USER_TEMPLATE = _phase5.JUDGE_USER_TEMPLATE
JudgeAuthError = _phase5.JudgeAuthError
```
This pattern eliminates the "duplicated ~150 lines" cost listed in CONTEXT D-01a's sibling-script tradeoff.

**Source:** Verified by `STATE.md` Phase 03.4-01 (`importlib.util.spec_from_file_location used to load scripts/ modules in tests — avoids sys.path mutation`) and Phase 06-01 test conventions. [VERIFIED]

### Pattern 2: Hardcoded path map with loud-fail startup assert

**What:** Module-level `dict` mapping (model, defense) tuples → log paths. Loud-fail at startup if any path is missing.
**When to use:** Any phase that reads from a known-fixed set of input artifacts. D-09 explicitly chooses this idiom.
**Example:**
```python
# Source: proposed scripts/run_judge_fpr_gptoss.py
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

# At startup:
for path in list(CELL_LOG_MAP.values()) + list(OFF_LOG_MAP.values()):
    assert Path(path).exists(), f"Phase 7 input missing: {path}"
```

### Pattern 3: Path-resolver fallback in make_results.py

**What:** Resolver function that prefers a versioned filename when present, falls back to the un-versioned name. Localizes the version-bump to a single read.
**When to use:** Whenever a downstream emitter must read either a Phase N artifact or a Phase N+1 supersession of it without forking the reader logic.
**Example:**
```python
# Source: scripts/make_results.py:514-530 (Phase 6 D-13 idiom)
def _resolve_matrix_path(default_path: str, logs_dir: Path | None = None) -> Path:
    p = Path(default_path)
    if logs_dir is not None and not p.is_absolute():
        try:
            rel = p.relative_to("logs")
            p = logs_dir / rel
        except ValueError:
            pass
    p_v6 = p.with_name(p.stem + "_v6" + p.suffix)
    return p_v6 if p_v6.exists() else p
```
**Phase 7 analog (proposed):** A new `_resolve_v7_ablation_path()` (or inline `Path("logs/ablation_table_gptoss_v7.json")` existence check inside a new `emit_honest_fpr_gptoss_v7()` function). The Phase 7 ablation file is *separate* from Phase 5's, so a fallback path isn't strictly needed — emission can skip cleanly if the v7 file is absent. **Cleaner pattern: gate emission on v7-file existence** (no fallback to a "v6 honest-FPR file" because there isn't one).

### Pattern 4: Atomic-write idiom (single-write-at-end for production files)

**What:** Write to `path.tmp` then `os.replace`. Phase 5 WR-01 minimizes the Windows non-atomic-replace window by accumulating per-cell metrics in memory and writing the production ablation file once at the end.
**When to use:** Any production JSON file where partial corruption from interrupted writes would cause downstream tool breakage.
**Example:**
```python
# Source: scripts/run_judge_fpr.py:132-136
def atomic_write_json(path: Path, obj: object) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    tmp.replace(path)
```
Phase 7 reuses this verbatim. Cache file writes can be per-cell (cache is a derived/recoverable artifact); production ablation file writes once at the end.

### Anti-Patterns to Avoid

- **Schema-fork branches scattered through the loop body.** D-10 explicitly mandates the schema diff fix is localized to one helper. Anti-pattern: `if "results" in data: ... elif "per_query" in data: ...` scattered through metric computation. Correct: localize to a single helper or skip entirely (the existing helper already works — see Code Examples §1).
- **Glob-pattern input discovery.** D-09 mandates explicit hardcoded path maps. Anti-pattern: `glob.glob("logs/eval_matrix/*v6.json")` — fragile to new files appearing.
- **Per-cell ablation-file rewrites.** Inflates Windows non-atomic-write window 4×. Use single-write-at-end (Phase 5 WR-01).
- **Implicit cp1252 file reads on Windows.** Always pass `encoding="utf-8"`. The v6 cell `answer` strings contain non-ASCII (smart quotes; verified — see Codebase Hazards).
- **`from scripts.run_judge_fpr import ...`** without a `scripts/__init__.py`. Use `importlib.util.spec_from_file_location` instead.
- **Mutating `logs/ablation_table.json` to add gpt-oss rows.** Explicitly forbidden by D-02. Phase 5's deliverable stays bit-for-bit.
- **Editing `docs/phase5_honest_fpr.md` above the addendum.** D-07 mandates original prose stays bit-for-bit; only an appended `## Phase 7 addendum:` section is allowed.
- **Editing `docs/phase3_results.md`.** D-08 + Phase 6 D-04 + 03.4-06 submission record — explicitly forbidden.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pairwise-judge prompt template + retry/parse | A new `run_judge_fpr_gptoss`-specific prompt | `JUDGE_SYSTEM_PROMPT` + `JUDGE_USER_TEMPLATE` from Phase 5 script (lines 36–47) | D-11 inherits Phase 5 D-10 verbatim — drift here breaks the cross-LLM comparability claim of the addendum. |
| Verdict parsing | New regex/branching | `parse_verdict()` from Phase 5 (lines 70–88) | Already handles the 4 cases (DEGRADED / PRESERVED / TIE / parse failure) per D-12. |
| A/B order randomization | New flip logic | `randomize_ab()` from Phase 5 (lines 112–129) | Same Random instance idiom (RESEARCH §A5) — instantiating `random.Random(42)` once before the loop, not `random.seed()`. |
| Atomic JSON write | New tmp-then-replace dance | `atomic_write_json()` from Phase 5 (lines 132–136) | Already handles Windows non-atomic-replace caveat. |
| Auth-error escalation | sys.exit() inside a helper | `JudgeAuthError` exception (Phase 5 lines 139–144) — caller catches and returns rc=1 | Keeps `judge_one` testable per WR-02. |
| Bootstrap CIs | scipy.stats.bootstrap (or hand-rolled resample loop) | Either `numpy.random.choice` resample loop OR skip CIs entirely | Discretionary per D-13; if added, follow Phase 5's note in §6 Limitations rather than inventing a new convention. |
| Markdown table rendering | hand-rolled pipe formatter | `df.fillna("—").to_markdown(index=False, floatfmt=".2f")` | Already used by `emit_table()` (`make_results.py:466`); honors the older-tabulate-version workaround documented in Phase 06-04 STATE. |
| CSV escape/quoting | hand-rolled | `df.to_csv(index=False)` (`make_results.py:469`) | Already used by every Phase 3.4/6 emitter. |
| LLM-as-judge calibration / agreement studies | A 5-judge ensemble or human-annotated subset | Single-seed convention (D-05 inherited; deferred to Future Work) | Out of scope per CONTEXT deferred ideas. |

**Key insight:** Phase 7 is almost entirely **reuse**. The plan's net new code budget should be `~150 LOC script + ~30 LOC make_results.py + ~50 LOC tests + writeup prose`. If a plan lands at >300 LOC of new Python, the planner is hand-rolling something already in `run_judge_fpr.py`.

## Common Pitfalls

### Pitfall 1: cp1252 encoding cascade on Windows
**What goes wrong:** Default `Path.read_text()` on Windows uses cp1252 codec, which fails on the smart quotes (`'` U+2019) and other non-ASCII chars present in v6 cell `answer` strings.
**Why it happens:** `gpt-oss:20b-cloud` and `gpt-oss:120b-cloud` answers contain typographic apostrophes (e.g., `"I'm sorry, but the provided context..."`) that fail cp1252 decode.
**How to avoid:** Always pass `encoding="utf-8"` to every `read_text()` and `write_text()`. Phase 5's `atomic_write_json` already does this (line 135). The new script's `load_clean_records` reuses Phase 5's helper, which uses `Path(...).read_text()` *without* an explicit encoding — **THIS IS A BUG INHERITED FROM PHASE 5** that did not bite Phase 5 because llama answers are pure ASCII. Phase 7 will hit this on the very first cell.
**Warning signs:** `UnicodeDecodeError: 'charmap' codec can't decode byte 0x... in position N` during `load_clean_records()`.
**Mitigation:** The planner should either (a) extend Phase 5's `load_clean_records` to pass `encoding="utf-8"` (1-line patch, backward-compatible), or (b) write a Phase 7-local `load_clean_records_utf8` that wraps the call. Option (a) is cleaner; option (b) honors D-01's "default sibling, don't touch Phase 5" lean. Test stub MUST cover this: read a v6 cell file via the helper and assert no UnicodeDecodeError.
[VERIFIED: live test of cp1252 decoding showed `'` rendered as `?` placeholder, confirming non-ASCII presence.]

### Pitfall 2: `ollama login` token expiry (separate from registry presence)
**What goes wrong:** `ollama list` shows `gpt-oss:20b-cloud` as registered (verified — present in this environment). But cloud models require a separate `ollama login` token that can expire silently. If expired, the *first* judge call returns an auth error.
**Why it happens:** Cloud-LLM auth state is not introspectable from `ollama list`. The token TTL is undocumented; Phase 6 hit this scenario at planning time (`Codebase Hazards: ollama login may have expired since Phase 6`).
**How to avoid:** Pre-flight check at script start: issue ONE judge call with a known query/answer pair before entering the cell loop. If it raises `JudgeAuthError` (Phase 5 lines 139–144), abort with rc=1 and a clear message. Phase 5's main() already escalates `JudgeAuthError` cleanly — Phase 7 inherits this for free.
**Warning signs:** `ollama._types.ResponseError: model requires login` or `403` from the cloud endpoint on the first call. Without preflight, this wastes ~2 sec; with preflight, it wastes <5 sec total.

### Pitfall 3: Per-cell ablation-file rewrites widen the corruption window
**What goes wrong:** If `run_for_cell` writes to `ablation_table_gptoss_v7.json` after each cell completes, the file gets rewritten 4 times. `Path.replace` is non-atomic on Windows; an interrupt during any of the 4 windows leaves a corrupted file.
**Why it happens:** A naive translation of Phase 5's `run_for_defense` flow would do per-iteration writes.
**How to avoid:** Phase 5 WR-01 explicitly addresses this: accumulate per-cell metrics in memory in an `accumulated_metrics: dict` (lines 425–445), do a single `atomic_write_json` at the end (lines 458–496). The cache file (`.cache`) can be written per-cell because it's a recoverable derived artifact. Phase 7 inherits this two-tier write strategy.
**Warning signs:** `json.JSONDecodeError` when re-reading the production file after an interrupted run.

### Pitfall 4: Schema-fork branches in the M1/M2 numerator code
**What goes wrong:** The CONTEXT D-10 wording ("5-line load_clean_records adapter") implies the v6 schema differs from Phase 5's. **In fact, it does not differ at the level the helper reads from.** Both have `data["results"]`, both have per-record `query`/`paired`/`answer`/`chunks_removed`. Adding a schema-fork branch where there is no schema fork creates dead code and makes the script harder to read.
**Why it happens:** The CONTEXT was written before the v6 cell schema was probed end-to-end. Research-time probing showed the schemas are identical at the read-points the helper uses.
**How to avoid:** Don't add schema-fork branches. Pass the v6 cell path to `load_clean_records` and let the existing assertions (`len(clean) == N_CLEAN`, `"answer" in r`, `"chunks_removed" in r`) pass on the v6 data. If they don't, fix the helper at the point of failure — don't pre-emptively branch.
**Warning signs:** Multiple `if/elif` cascades on top-level keys in helper code where research already showed only one branch is reachable.

### Pitfall 5: Forgetting that `make_figures.py` invariants extend to v7 figures
**What goes wrong:** If the optional v7 figure (D-06) is rendered, it must follow Phase 03.4-03 fail-loud invariants (B-2: nansum>0, nanmax>0.05, ≥5 non-zero cells; W-5: matrix shape + no NaN). Phase 6 added new renderers that inherit these (D-10 5×5, 5×4 invariants). A v7 renderer that skips these silently degrades to all-zero placeholders.
**Why it happens:** Easy to forget when adding "just one more chart."
**How to avoid:** If the v7 figure is rendered, add an `assert matrix.shape == (3, 6)` (or whatever the canonical shape is) AND `assert np.nansum(data) > 0` BEFORE `save_atomic`.
**Warning signs:** Silent all-zero output PNG. (Better: `AssertionError` from the invariant check.)

### Pitfall 6: M2 conditional logic depends on the M3 verdict; cache must capture the join, not just the M3 verdict
**What goes wrong:** M2 = `count(chunks_removed > 0 AND verdict == DEGRADED) / 50`. If the cache stores only the M3 verdict and re-derives M2 by re-reading the cell file, an interrupted run + resume might compute M2 against a different cell file (e.g., user re-pointed CELL_LOG_MAP). The result is silent M2 drift.
**Why it happens:** Cache invalidation is only about the verdict; the join with `chunks_removed` is recomputed at aggregation time.
**How to avoid:** Phase 5 already handles this correctly: the cache is keyed on `(defense, qid)` and stores only the verdict; `chunks_removed` is read from the cell file at aggregation time inside the same cell-loop iteration that consumes the cache. As long as Phase 7 follows Phase 5's loop structure exactly, M2 stays consistent.
**Warning signs:** M2 numbers shift between two consecutive runs even though no cloud calls were made (suggests cache + cell file desync).

## Code Examples

### Example 1: load_clean_records works on Phase 6 v6 cells AS-IS (verified live)

```python
# Source: scripts/run_judge_fpr.py:91-109 — works on v6 cells WITHOUT modification
# VERIFIED: probed all 4 v6 cells + both undefended baselines on 2026-05-04;
# every file has top-level "results" key, exactly 50 paired=False records,
# and per-record "answer"/"chunks_removed" keys.
def load_clean_records(log_path: "str | Path") -> list:
    data = json.loads(Path(log_path).read_text())  # ← BUG: missing encoding="utf-8"
    clean = [r for r in data["results"] if not r.get("paired", False)]
    assert len(clean) == N_CLEAN, ...
    for i, r in enumerate(clean):
        assert "answer" in r, ...
        assert "chunks_removed" in r, ...
    return clean
```

**Verified probe output (2026-05-04):**
```
logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json
  top_keys: ['phase', 'corpus', 'collection', 'llm_model', 'defense_mode',
             'n_queries', 'n_paired', 'aggregate', 'results', 'supersedes_phase_02_3']
  n_results: 100 | paired=True: 50 | paired=False: 50
  record_keys: ['adaptive_retrieved', 'answer', 'chunks_removed', 'hijacked',
                'hijacked_adaptive', 'hijacked_tier1', 'hijacked_tier1b',
                'hijacked_tier2', 'hijacked_tier3', 'hijacked_tier4',
                'paired', 'query', 'retrieved_poisoned', 'tier1_retrieved',
                'tier1b_retrieved', 'tier2_retrieved', 'tier3_retrieved',
                'tier4_retrieved']
```
The Phase 5 fields (`answer`, `chunks_removed`, `paired`, `query`) are all present. **The "5-line adapter" in CONTEXT D-10 is not needed**; the only required change is adding `encoding="utf-8"` to the `read_text()` call (Pitfall 1). [VERIFIED]

### Example 2: Generalized run_for_cell signature (proposed)

```python
# Source: proposed scripts/run_judge_fpr_gptoss.py
# Generalizes scripts/run_judge_fpr.py:213-343 (run_for_defense)
# from per-defense to per-(model, defense)

def run_for_cell(
    client,
    args,
    model_name: str,
    defense_key: str,
    cell_path: Path,
    off_path: Path,
    cache_for_cell: dict,
    rng: random.Random,
) -> tuple[dict, float, float, float, int]:
    """Run judge evaluation for one (model, defense) cell against 50 clean queries.

    Returns:
        (verdicts_dict, m1, m2, m3, n_calls)
        verdicts_dict: {qid_str: verdict_record}
        m1: per_chunk_fpr        (chunks_removed sum / TOP_K * N_CLEAN)
        m2: answer_preserved_fpr (count(chunks_removed>0 AND DEGRADED) / N_CLEAN)
        m3: judge_fpr            (count(DEGRADED) / N_CLEAN)
        n_calls: total judge calls (>= N_CLEAN unless cache hits or dry-run)
    """
    off_records = load_clean_records(off_path)   # 50 clean records from cell's matching off file
    cell_records = load_clean_records(cell_path) # 50 clean records from this cell

    # RESEARCH §A2 mitigation (Phase 5): assert query strings align by position.
    for i, (off_r, cell_r) in enumerate(zip(off_records, cell_records)):
        assert off_r["query"] == cell_r["query"], (
            f"{model_name}/{defense_key} record {i}: query mismatch"
        )

    # ... (body identical to run_for_defense, just substitute defense_key with f"{model_name}__{defense_key}")
```

### Example 3: D-02 ablation row shape (proposed write-out)

```python
# Source: proposed scripts/run_judge_fpr_gptoss.py — Step 6 (single write at end)
ablation_v7 = {}
for (model_name, defense_key), (m1, m2, m3, n_calls) in accumulated_metrics.items():
    composite_key = f"{model_name.replace(':', '').replace('-', '')}_cloud__{defense_key}"
    # WAIT: composite key naming — see PROVENANCE NOTE below
    ablation_v7[composite_key] = {
        "model":                model_name,         # "gpt-oss:20b-cloud"
        "defense_mode":         defense_key,        # "fused" or "def02"
        "per_chunk_fpr":        m1,
        "answer_preserved_fpr": m2,
        "judge_fpr":            m3,
        "judge_model":          args.model,         # "gpt-oss:20b-cloud"
        "judge_n_calls":        n_calls,
    }

atomic_write_json(Path("logs/ablation_table_gptoss_v7.json"), ablation_v7)
```

**Composite-key normalization note:** CONTEXT D-02 specifies the keys as `gptoss20b_cloud__fused`, `gptoss20b_cloud__def02`, `gptoss120b_cloud__fused`, `gptoss120b_cloud__def02`. The naming pattern matches existing `logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json` filename roots. Use a lookup dict (not a string-mutation function) for clarity:
```python
COMPOSITE_KEY_MAP = {
    ("gpt-oss:20b-cloud",  "fused"): "gptoss20b_cloud__fused",
    ("gpt-oss:20b-cloud",  "def02"): "gptoss20b_cloud__def02",
    ("gpt-oss:120b-cloud", "fused"): "gptoss120b_cloud__fused",
    ("gpt-oss:120b-cloud", "def02"): "gptoss120b_cloud__def02",
}
```

### Example 4: D-04 verdicts file shape (proposed write-out)

```python
# Source: proposed scripts/run_judge_fpr_gptoss.py — Step 7 (single write at end)
verdicts_v7 = {
    "phase": "07",
    "judge_model": args.model,
    "judge_prompt_template": JUDGE_USER_TEMPLATE,  # reused from Phase 5
    "verdicts": {
        "gpt-oss:20b-cloud": {
            "fused": {qid: verdict_record, ...},   # 50 entries
            "def02": {qid: verdict_record, ...},   # 50 entries
        },
        "gpt-oss:120b-cloud": {
            "fused": {qid: verdict_record, ...},   # 50 entries
            "def02": {qid: verdict_record, ...},   # 50 entries
        },
    },
}
atomic_write_json(Path("logs/judge_fpr_gptoss_v7.json"), verdicts_v7)
```

Total: 200 verdict records. Mirrors Phase 5's `judge_fpr_llama.json` (verified shape: `{phase, judge_model, judge_prompt_template, verdicts: {defense: {qid: ...}}}`) with one nesting level added.

### Example 5: make_results.py v7 path-resolver branch (proposed)

```python
# Source: proposed scripts/make_results.py addition near _resolve_matrix_path

def _resolve_v7_ablation_path(
    default_path: str = "logs/ablation_table_gptoss_v7.json",
    logs_dir: Path | None = None,
) -> Path | None:
    """D-05 resolver: return v7 ablation path if present, else None.

    Unlike _resolve_matrix_path (Phase 6 D-13), there is no v6/un-versioned
    fallback for v7 — it's a separate file from Phase 5's ablation_table.json.
    Returning None means 'no v7 data; skip emit' rather than 'fall back to Phase 5'.
    """
    p = Path(default_path)
    if logs_dir is not None and not p.is_absolute():
        try:
            rel = p.relative_to("logs")
            p = logs_dir / rel
        except ValueError:
            pass
    return p if p.exists() else None


def emit_honest_fpr_gptoss_v7(
    v7_path: Path,
    output_dir: Path,
    fmt: str,
) -> None:
    """D-05 emitter: load v7 ablation file, render 4-row Markdown + CSV companion."""
    raw = _safe_load_json(v7_path)
    if raw is None:
        raise RuntimeError(f"Could not load v7 ablation table from {v7_path}")
    rows = []
    for composite_key, entry in raw.items():
        rows.append({
            "Composite Key":          composite_key,
            "Model":                  entry.get("model", "unknown"),
            "Defense":                _display_defense(entry.get("defense_mode", "")),
            "Per-Chunk FPR":          entry.get("per_chunk_fpr", float("nan")),
            "Answer-Preserved FPR":   entry.get("answer_preserved_fpr", float("nan")),
            "Judge FPR":              entry.get("judge_fpr", float("nan")),
            "Judge Model":            entry.get("judge_model", "—"),
            "Judge N Calls":          entry.get("judge_n_calls", 0),
        })
    df = pd.DataFrame(rows)
    emit_table(df, "honest_fpr_gptoss_v7", output_dir, fmt)


# In main(), after existing emits:
v7_path = _resolve_v7_ablation_path(logs_dir=logs_dir)
if v7_path is not None:
    emit_honest_fpr_gptoss_v7(v7_path, output_dir, args.format)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Coarse query-level FPR ("any chunk removed = FPR") | Three honest metrics: per-chunk, answer-preserved, judge-scored | Phase 5 (2026-05-03) | The "76%" headline number is now reframed as a loose upper bound; the per-chunk number is far lower. Phase 7 carries this to two more LLM targets. |
| Single-LLM (llama3.2:3b) honest FPR | Cross-LLM (llama + gpt-oss-20b + gpt-oss-120b) honest FPR | Phase 7 (this phase) | Lets the addendum address whether honest-FPR pattern generalizes across model scales and lineages. |
| Per-tier matrix-driver invocations (5× redundant runs per cell) | Single-pass `run_eval.py` for all-tier ASR aggregates | Phase 6 D-09a (2026-05-04) | Phase 7 inherits this for free — no eval re-runs needed. |
| `--tier-filter` flag | Single-pass per cell (no `--tier-filter`) | Phase 6 D-09a | n/a — Phase 7 doesn't run `run_eval.py` at all. |

**Deprecated/outdated:**
- The path `logs/eval_matrix/_summary.json` (Phase 03.3-07 45-row) is superseded for cross-model purposes by `_summary_v6.json` (Phase 6 75-row). Phase 7 does NOT need to read either; it reads the per-cell v6 files directly.
- The schema in Phase 02.3's `logs/eval_harness_undefended_gptoss{20b,120b}.json` (T1/T2-only on `nq_poisoned_v3`) is superseded by the `_v6.json` files (5-tier on `nq_poisoned_v4`). Phase 7 reads only the `_v6.json` files via D-09's hardcoded path map.

## Assumptions Log

> All factual claims in this research were either VERIFIED by direct probing of the codebase or CITED from CONTEXT.md / STATE.md / ROADMAP.md / source files. No claims marked `[ASSUMED]`.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | (none) | — | — |

**This table is empty:** All claims in this research were verified or cited — no user confirmation needed beyond the locked decisions already in CONTEXT.md.

## Open Questions

1. **Should the Phase 5 `load_clean_records` UTF-8 bug be fixed in Phase 5 or worked around in Phase 7?**
   - What we know: Phase 5's helper at line 101 (`Path(log_path).read_text()`) lacks `encoding="utf-8"`. Phase 5 doesn't trigger the bug because llama answers are ASCII; Phase 7 will trigger on cell answers containing smart quotes.
   - What's unclear: D-01's "default sibling, don't touch Phase 5" lean implies Phase 7 should work around (option b). But the fix is a 1-character change that benefits any future caller — touching Phase 5 is principled.
   - Recommendation: **Plan-time choice.** Either (a) one-line patch to Phase 5's helper (cleanest; preserves bit-for-bit deliverable test by adding `encoding="utf-8"` only — no behavior change for ASCII inputs), or (b) Phase 7 wraps with a local helper that reads via `Path.read_text(encoding="utf-8")` then passes a StringIO/dict to a refactored Phase 5 helper. Default lean: **option (a)** — the 1-char addition is provably backward-compatible.

2. **Is the optional v7 figure (D-06) worth rendering?**
   - What we know: D-06 is explicitly Claude's discretion. The 10-row table covers 3 LLMs × 2 defenses × 3 metrics = 18 numbers, which a reader can scan unaided.
   - What's unclear: Whether a heatmap/grouped-bar adds enough cross-LLM signal to justify the renderer + invariant tests + plan task.
   - Recommendation: **Skip the figure unless the planner is already adding multiple Phase 7 figure-type plans**, in which case bundle it. The addendum prose can carry the cross-LLM observations without a chart.

3. **Should bootstrap CIs (1000 resamples) on M1/M2/M3 be included?**
   - What we know: D-13 lists this as Claude's discretion; Phase 5's writeup §6 acknowledges wide CIs (~±7pp at 95%) but does not compute them.
   - What's unclear: Whether the addendum's "cross-LLM analysis" paragraph reads more honestly with CIs included.
   - Recommendation: **Add CIs.** A 50-query bootstrap is cheap (<1 sec for 1000 resamples × 4 cells), the formula is canonical, and the addendum's substantive interpretation paragraph is more credible if the bands are visible. If the planner agrees, follow numpy.random.choice resampling; persist to ablation file under per-row `per_chunk_fpr_ci_lo`/`_ci_hi` etc. (additive schema; doesn't break D-02's flat-record structure).

4. **Composite-key naming choice — `gptoss20b_cloud__fused` vs. `gpt-oss-20b-cloud__fused`?**
   - What we know: D-02 specifies exactly `gptoss20b_cloud__fused`, `gptoss120b_cloud__fused`, etc. — no hyphens, no colons in the model token. This matches existing `logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json` filename root.
   - What's unclear: Nothing — D-02 is explicit.
   - Recommendation: **No question; D-02 is explicit.** Use a lookup dict (`COMPOSITE_KEY_MAP` per Code Examples §3) to avoid string-mutation bugs.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 | Runtime | ✓ | (assume conda env `rag-security`) | — |
| `ollama` python client | judge calls | ✓ | already used by Phase 5 | dry-run mode (`--dry-run` skips cloud calls) |
| Ollama server (`localhost:11434`) | judge calls | unknown — verify at plan time | — | `--dry-run` for M1+M2 only |
| `gpt-oss:20b-cloud` registered | judge calls | ✓ (verified `ollama list` 2026-05-04) | — | none (judge-LLM is locked by D-11) |
| `ollama login` (cloud auth token) | judge calls | unknown — separate from registry | — | abort with rc=1 via JudgeAuthError |
| Python `pytest` 9.0.3 | tests | ✓ (verified) | 9.0.3 | — |
| Python `pandas` ≥2.0 | `make_results.py` emit | ✓ (already imported) | as installed | — |
| `tabulate` (transitive) | `to_markdown()` | ✓ (already used) | as installed | — |
| Phase 6 v6 cell files (4) | M1, M2, M3 inputs | ✓ (verified all 4 paths, 100 records each) | — | none — phase blocked if missing |
| Phase 6 v6 undefended baselines (2) | judge prompt answer-A | ✓ (verified both paths, 100 records each) | — | none — phase blocked if missing |
| Phase 5 `scripts/run_judge_fpr.py` | code reuse via importlib | ✓ (516 lines, verified at commit 8e6942b) | — | none — sibling-script architecture depends on it |
| Disk writeable for `logs/`, `docs/results/`, `docs/phase5_honest_fpr.md` | output | assumed ✓ | — | — |

**Missing dependencies with no fallback:**
- None at this time — all 6 v6 input files exist on disk; all script reuse points exist.

**Missing dependencies with fallback:**
- Cloud auth state (`ollama login`) — preflight check at script start; abort cleanly via `JudgeAuthError` if expired.

## Validation Architecture

> nyquist_validation = true (verified `.planning/config.json:workflow.nyquist_validation`). This section is REQUIRED. VALIDATION.md will be derived from the contents below.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | (project uses default pytest discovery — `tests/` directory with `test_*.py` filenames) |
| Quick run command | `pytest tests/test_phase7_judge_fpr.py tests/test_make_results_v7.py -x` |
| Full suite command | `pytest tests/ -x` |

### Phase Requirements → Test Map

Test IDs use the V-N convention from Phase 5 (e.g., `tests/test_judge_fpr.py::TestM1` style classes).

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| P7-M1 | M1 = sum(chunks_removed) / (TOP_K × N_CLEAN) for each of 4 cells | unit | `pytest tests/test_phase7_judge_fpr.py::TestM1Numerator -x` | ❌ Wave 0 stub needed |
| P7-M2 | M2 = count(chunks_removed > 0 AND DEGRADED) / N_CLEAN | unit | `pytest tests/test_phase7_judge_fpr.py::TestM2Aggregation -x` | ❌ Wave 0 stub needed |
| P7-M3 | M3 = count(DEGRADED) / N_CLEAN; TIE and refusal collapse to PRESERVED | unit | `pytest tests/test_phase7_judge_fpr.py::TestM3Aggregation -x` | ❌ Wave 0 stub needed |
| P7-LCR | `load_clean_records(v6_cell_path)` returns exactly 50 records (no schema-fork branch needed) | unit | `pytest tests/test_phase7_judge_fpr.py::TestLoadCleanRecordsV6 -x` | ❌ Wave 0 stub needed |
| P7-UTF | `load_clean_records` reads v6 cell with non-ASCII answer chars without UnicodeDecodeError | unit | `pytest tests/test_phase7_judge_fpr.py::TestUtf8Encoding -x` | ❌ Wave 0 stub needed |
| P7-PATH | `CELL_LOG_MAP` and `OFF_LOG_MAP` paths all resolve to existing files at startup | unit | `pytest tests/test_phase7_judge_fpr.py::TestPathMapsLoudFail -x` | ❌ Wave 0 stub needed |
| P7-CKEY | Composite key map yields exactly 4 keys: `gptoss20b_cloud__{fused,def02}` and `gptoss120b_cloud__{fused,def02}` | unit | `pytest tests/test_phase7_judge_fpr.py::TestCompositeKeys -x` | ❌ Wave 0 stub needed |
| P7-OUT-J-SHAPE | `logs/ablation_table_gptoss_v7.json` is a flat dict with exactly 4 entries; each entry has D-02 fields | unit | `pytest tests/test_phase7_judge_fpr.py::TestAblationV7Shape -x` | ❌ Wave 0 stub needed |
| P7-OUT-J-NOROW | `logs/ablation_table_gptoss_v7.json` does NOT contain a trivial `no_defense` row (D-03) | unit | `pytest tests/test_phase7_judge_fpr.py::TestNoTrivialRow -x` | ❌ Wave 0 stub needed |
| P7-OUT-V-SHAPE | `logs/judge_fpr_gptoss_v7.json` matches D-04 nested structure: `verdicts[model][defense][qid]` | unit | `pytest tests/test_phase7_judge_fpr.py::TestVerdictsV7Shape -x` | ❌ Wave 0 stub needed |
| P7-OUT-V-COUNT | `logs/judge_fpr_gptoss_v7.json` contains exactly 200 verdict records (4 cells × 50 queries) | unit | `pytest tests/test_phase7_judge_fpr.py::TestVerdictCount200 -x` | ❌ Wave 0 stub needed |
| P7-OUT-V-FIELDS | Each verdict record has `verdict`, `ab_assignment`, `raw_response`, `retry_count` fields (D-04 + Phase 5 D-12) | unit | `pytest tests/test_phase7_judge_fpr.py::TestVerdictRecordFields -x` | ❌ Wave 0 stub needed |
| P7-RESV | `make_results.py` v7 resolver returns Path when `ablation_table_gptoss_v7.json` exists, None otherwise | unit | `pytest tests/test_make_results_v7.py::TestV7Resolver -x` | ❌ Wave 0 stub needed |
| P7-RESV-EMIT | When v7 file present, `docs/results/honest_fpr_gptoss_v7.{md,csv}` are produced; when absent, no v7 emit happens | unit | `pytest tests/test_make_results_v7.py::TestV7Emit -x` | ❌ Wave 0 stub needed |
| P7-RESV-COMPAT | Existing `tests/test_make_results.py` and `tests/test_make_results_v6.py` stay green after v7 branch is added | regression | `pytest tests/test_make_results.py tests/test_make_results_v6.py -x` | ✓ existing tests |
| P7-DOC-UNTOUCHED | Original Phase 5 prose in `docs/phase5_honest_fpr.md` (lines 1 through start-of-addendum) is bit-for-bit unchanged | unit | `pytest tests/test_make_results_v7.py::TestPhase5ProseUntouched -x` | ❌ Wave 0 stub needed |
| P7-DOC-ADDENDUM | `docs/phase5_honest_fpr.md` contains a `## Phase 7 addendum: gpt-oss extension` heading exactly once after the Phase 5 sections | unit | `pytest tests/test_make_results_v7.py::TestAddendumPresent -x` | ❌ Wave 0 stub needed |
| P7-DOC-TABLE-10ROW | The addendum's M1/M2/M3 table has exactly 10 data rows (6 llama + 2 gpt-oss-20b + 2 gpt-oss-120b) | unit | `pytest tests/test_make_results_v7.py::TestAddendumTable10Rows -x` | ❌ Wave 0 stub needed |
| P7-DOC-PHASE3-UNTOUCHED | `docs/phase3_results.md` is bit-for-bit unchanged compared to git HEAD before Phase 7 (defensive — D-08 inheritance) | unit | `pytest tests/test_make_results_v7.py::TestPhase34NotEdited -x` | ❌ Wave 0 stub needed |
| P7-INHERIT-PROMPT | The Phase 7 script imports `JUDGE_SYSTEM_PROMPT` and `JUDGE_USER_TEMPLATE` from `scripts/run_judge_fpr.py` (no redefinition) | unit | `pytest tests/test_phase7_judge_fpr.py::TestPromptInherited -x` | ❌ Wave 0 stub needed |
| P7-INHERIT-PARSE | The Phase 7 script reuses `parse_verdict()` from Phase 5 (no copy-pasted parser) | unit | `pytest tests/test_phase7_judge_fpr.py::TestParserInherited -x` | ❌ Wave 0 stub needed |
| P7-CACHE | A second invocation with `.cache` file present skips judge calls (cache hits) | integration | `pytest tests/test_phase7_judge_fpr.py::TestCacheResume -x` | ❌ Wave 0 stub needed |
| P7-DRYRUN | `--dry-run` flag computes M1 only, makes zero cloud calls | integration | `pytest tests/test_phase7_judge_fpr.py::TestDryRunNoCloud -x` | ❌ Wave 0 stub needed |
| P7-AUTH | `JudgeAuthError` from a mocked failing client returns rc=1 cleanly without aborting mid-cell | integration | `pytest tests/test_phase7_judge_fpr.py::TestAuthEscalation -x` | ❌ Wave 0 stub needed |

**What FAILS if M1/M2/M3 are computed wrong?**
- M1 wrong: `TestM1Numerator` fails (synthetic 5-record fixture with known `chunks_removed` total).
- M2 wrong: `TestM2Aggregation` fails (synthetic fixture: 3 records with `chunks_removed > 0` of which 1 is DEGRADED → M2 = 1/50 = 0.02).
- M3 wrong: `TestM3Aggregation` fails (synthetic: 2 DEGRADED of 50 → M3 = 0.04; TIE and refusal collapse to PRESERVED).

**What FAILS if v7 path-resolver mis-routes?**
- v7 file present but resolver returns None → `TestV7Emit` fails (asserts `honest_fpr_gptoss_v7.md` produced).
- v7 file absent but resolver returns a path → `TestV7Resolver::test_returns_none_when_absent` fails.

**What FAILS if the addendum table omits a row?**
- `TestAddendumTable10Rows` fails (regex/parser counts pipe-table data rows; expects exactly 10).

### Sampling Rate

- **Per task commit:** `pytest tests/test_phase7_judge_fpr.py tests/test_make_results_v7.py -x` (~5 sec; pure unit tests, no cloud).
- **Per wave merge:** `pytest tests/ -x` (~30-60 sec; full suite including Phase 3/4/5/6 regressions).
- **Phase gate:** Full suite green AND a manual `--dry-run` of `scripts/run_judge_fpr_gptoss.py` showing M1 numbers without cloud calls, before `/gsd-verify-work`.
- **Single-seed convention inherited (D-11):** No per-call sampling beyond Phase 5's single judge call per (cell, query). The 200-call run is treated as one observation per cell-query pair. This caveat is already in the addendum's methodology note.

### Wave 0 Gaps

- [ ] `tests/test_phase7_judge_fpr.py` — covers all P7-M*, P7-LCR, P7-UTF, P7-PATH, P7-CKEY, P7-OUT-*, P7-INHERIT-*, P7-CACHE, P7-DRYRUN, P7-AUTH.
- [ ] `tests/test_make_results_v7.py` — covers P7-RESV, P7-RESV-EMIT, P7-DOC-*, plus regression-stays-green check for `test_make_results.py` and `test_make_results_v6.py`.
- [ ] No new framework install needed (pytest 9.0.3 already present).
- [ ] Test stubs MUST use `importlib.util.spec_from_file_location` to load `scripts/run_judge_fpr.py` and `scripts/run_judge_fpr_gptoss.py` — Phase 03.4-01 / 06-01 lineage. Skip-guards for `_OLLAMA_AVAILABLE` and for the v7 file's existence let `pytest --collect-only` succeed before production code lands.

## Project Constraints (from CLAUDE.md)

| Directive | Source | Phase 7 Compliance |
|-----------|--------|-------------------|
| Python 3.11 | CLAUDE.md "Recommended Stack" | ✓ — phase 7 uses existing conda env |
| Custom RAG pipeline (no LangChain/LlamaIndex) | CLAUDE.md "What NOT to Use" | ✓ — no new RAG-pipeline code; phase 7 is post-hoc analysis only |
| ChromaDB / Ollama / sentence-transformers stack | CLAUDE.md "Core Technologies" | ✓ — phase 7 reuses existing Ollama client; no new stack changes |
| Local-first reproducibility | CLAUDE.md "Constraints" | ✓ — judge runs use cloud `gpt-oss:20b-cloud` (already in stack), all input artifacts on disk |
| GSD workflow gating for edits | CLAUDE.md "GSD Workflow Enforcement" | ✓ — this research file is generated under `/gsd-research-phase` |
| utf-8 encoding on Windows | (project hazard, Phase 03.4-01 + 06 STATE) | ⚠ MUST fix in Phase 5 helper or wrap in Phase 7 — see Open Question 1 |
| Atomic-write idiom on production JSON | Phase 5 WR-01 + Phase 03.4-03 | ✓ — reuse `atomic_write_json` |

## Sources

### Primary (HIGH confidence)

- **`scripts/run_judge_fpr.py`** (516 lines) — Phase 5 entry script; verified line ranges 70–88 (parse_verdict), 91–109 (load_clean_records), 112–129 (randomize_ab), 132–136 (atomic_write_json), 139–144 (JudgeAuthError), 147–210 (judge_one), 213–343 (run_for_defense), 350–375 (parse_args), 382–512 (main). [VERIFIED: read in full + cross-checked CONTEXT line range claims]
- **`scripts/make_results.py`** (lines 1–620 read) — Phase 6 D-13 path-resolver pattern at lines 514–530; PHASE6_DISCLOSURE_HEADER + DEFENSE_DISPLAY at lines 47–93; emit_table at 455–471; load_undefended_baseline at 236–315 (already prefers `_v6.json`). [VERIFIED]
- **Phase 6 v6 cell files** — all 4 verified present and probed end-to-end on 2026-05-04: top-level keys + per-record keys + 100/50/50 paired/clean split + first-record content. [VERIFIED via Bash probe]
- **Phase 6 undefended baselines** — both `eval_harness_undefended_gptoss{20b,120b}_v6.json` verified present, same schema as cells. [VERIFIED]
- **Phase 5 deliverables** — `logs/ablation_table.json` (15 keys verified, sample row schema printed), `logs/judge_fpr_llama.json` (top-level keys + verdicts shape verified), `docs/phase5_honest_fpr.md` (section structure verified: ##1 Motivation, ##2 The Three Metrics, ##3 Methodology, ##4 Results, ##5 Discussion, ##6 Limitations, ##References). [VERIFIED]
- **`.planning/phases/07-honest-fpr-metrics-gpt-oss-extension/07-CONTEXT.md`** — D-01 through D-12 + canonical refs + code context + specifics + deferred. [READ IN FULL]
- **`.planning/phases/05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud/05-CONTEXT.md`** — Phase 5 D-01 through D-12. [READ IN FULL]
- **`.planning/phases/06-cross-llm-undefended-baseline-gap-fill-run-gpt-oss-20b-cloud/06-CONTEXT.md`** — Phase 6 D-01 through D-14. [READ IN FULL]
- **`.planning/REQUIREMENTS.md`** — Phase 5/6 requirement IDs + traceability table. [READ IN FULL]
- **`.planning/STATE.md`** — Phase decisions log; especially Phase 03.4-01 (importlib pattern), Phase 06 post-close (encoding hazards). [READ IN FULL]
- **`.planning/ROADMAP.md`** — Phase 5/6/7 detail sections. [READ IN FULL]
- **`.planning/config.json`** — `nyquist_validation: true` confirmed. [VERIFIED]
- **Live environment probe** — `ollama list` confirms `gpt-oss:20b-cloud` and `gpt-oss:120b-cloud` are registered locally; `pytest --version` confirms 9.0.3. [VERIFIED]

### Secondary (MEDIUM confidence)

- Inferred composite-key naming from `logs/eval_matrix/*_v6.json` filename roots → matches CONTEXT D-02 exactly. [INFERRED + VERIFIED against D-02 wording]

### Tertiary (LOW confidence)

- (none)

## Metadata

**Confidence breakdown:**

- **Standard stack:** HIGH — every dependency is already installed and used by Phase 5; no version churn risk.
- **Architecture:** HIGH — every tier boundary inherited from Phase 5/6; no new architectural seams.
- **Pitfalls:** HIGH — the cp1252 encoding pitfall is observable in live data (probed and confirmed); the auth-state pitfall is documented in Phase 6 STATE; the atomic-write pitfall is documented in Phase 5 WR-01 + Phase 03.4-03.
- **Validation Architecture:** HIGH — every requirement has a unit-test mapping; sampling rates inherited from Phase 5 single-seed convention.
- **Code reuse paths:** HIGH — every helper proposed for reuse was read in full; line ranges verified to match CONTEXT claims (with one note: `run_for_defense` ends near line 343, not 348 — close enough that CONTEXT's "213-348" range is fine).

**Research date:** 2026-05-04
**Valid until:** 2026-05-11 (7 days — fast-moving project; Phase 4 active in parallel).
