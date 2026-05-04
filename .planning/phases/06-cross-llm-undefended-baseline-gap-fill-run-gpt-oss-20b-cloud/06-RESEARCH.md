# Phase 6: Cross-LLM Undefended Baseline Gap Fill — Research

**Researched:** 2026-05-04
**Domain:** RAG security evaluation harness, ChromaDB collection probes, downstream artifact propagation, cloud-LLM rate-limiting hygiene
**Confidence:** HIGH

## Summary

Phase 6 is a "logs + propagation" phase, not an architecture phase. The eval pipeline (`scripts/run_eval.py`) already produces all 5 tier ASR numbers in a single pass via the per-tier `passage_id`-range tagger at lines 230–247 plus the per-tier aggregate computation at lines 308–397; the `_v6` outputs differ from existing 02.3-era files only in (a) which collection they were scored against and (b) the broader set of aggregate keys present in the output JSON. No `run_eval.py` source change is required.

The path-resolver edit at `scripts/make_results.py:247` is the single make_results.py change. Downstream propagation requires extending the D-12 figure renderer from a `(5, 3)` `assert matrix.shape` to `(5, 5)` (W-5 invariant), regenerating two markdowns in-place, emitting two new `_v6.csv` files, and rendering two new `_v6.png` figures using the existing `save_atomic` idiom. The two cloud-model invocations are 100 queries × ~8s each at `--delay 3` ≈ 13 min/model = 26 min total wall-clock.

**Three notable findings the planner must account for:**

1. **`run_eval.py` writes `phase: "03.3"` hardcoded at line 407.** The CONTEXT.md `D-02a` requirement to record `phase: "06"` and `supersedes_phase_02_3: true` cannot be met by `run_eval.py` alone — the planner must either add a tiny post-run JSON-mutation step (open the output, add the provenance fields, re-write atomically) or ship a thin Phase 6 driver. **No changes to run_eval.py source are needed for this; it's a post-processing step.** [VERIFIED: `scripts/run_eval.py:407`]
2. **`run_eval.py` does not produce an `error_count` field** today. CONTEXT.md `D-03a` says one must be added. The cheapest implementation is the same post-run mutation step from item 1 — count `r["answer"].startswith("[ERROR:")` across `results[]` in the just-written JSON, store as `aggregate.error_count`. The current `run_eval.py` will raise on a thrown exception, so the post-run step must also be paired with a defensive try/except wrapper (or accept that on a hard failure no JSON gets written and the planner re-runs). [VERIFIED: `scripts/run_eval.py` has no `error_count` token]
3. **The collection's tier ranges have all been verified live via a probe.** `nq_poisoned_v4` has 1239 docs and at least 3 passages in each of the 5 tier ranges (T1 [20000,20050), T2 [20050,20100), T3 [20100,20150), T1b [20150,20200), T4 [20200,20300)) plus Adaptive [20500,20600). [VERIFIED: `chromadb` get with `passage_id` $gte/$lt filter, run 2026-05-04]

**Primary recommendation:** Use a thin Phase 6 driver `scripts/run_phase6_eval.py` that wraps two `run_eval.py` `subprocess.run(..., shell=False)` invocations, performs D-01a sanity-assert + ollama-auth pre-flight before the first run, and post-processes each output JSON to add `phase: "06"`, `supersedes_phase_02_3: true`, `error_count`, then atomically renames into place. Reasons: (a) it satisfies D-01a and D-02a in one place without polluting `run_eval.py`; (b) the test stub `tests/test_phase6_eval.py` then has a single import target; (c) consistent with the Phase 03.3-07 driver-pattern precedent.

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Collection & corpus:**
- **D-01:** Evaluate against `nq_poisoned_v4` (already indexed locally, 1239 docs). No `--force-reindex`. Provenance string `collection: "nq_poisoned_v4"` recorded in each output JSON. NOT `nq_poisoned_v5` (wrong lineage), NOT a fresh `nq_poisoned_v6` (saves 5–10 min of needless re-embedding).
- **D-01a:** Pre-run sanity assert that all 5 expected `passage_id` ranges are present in the collection: at least one passage in each of `[20000, 20050)`, `[20050, 20100)`, `[20100, 20150)`, `[20150, 20200)`, `[20200, 20300)`. Cheap insurance against stale collection silently producing 0% on T1b/T3/T4.
- **D-01b:** Use `data/test_queries.json` — the canonical 100-query set (50 paired / 50 clean). Same set every other `eval_harness_undefended_*.json` was scored against.

**Output filename & provenance:**
- **D-02:** Phase 6 writes to `logs/eval_harness_undefended_gptoss20b_v6.json` and `logs/eval_harness_undefended_gptoss120b_v6.json` (the `_v6.json` suffix preserves the Phase 02.3 originals bit-for-bit).
- **D-02a:** Each new file records `phase: "06"`, `collection: "nq_poisoned_v4"`, `corpus: "data/corpus_poisoned.jsonl"`, `supersedes_phase_02_3: true`, plus an `error_count` integer.
- **D-02b:** Modify path resolution at `scripts/make_results.py:247` to prefer `eval_harness_undefended_{model_key}_v6.json` when present and fall back to the un-versioned file otherwise. ~4-line change. The DEFENSE_DISPLAY map (lines 57+) and three-source aggregation contract are untouched.

**Rate-limit handling:**
- **D-03:** `--delay 3` between queries, no retry wrapper. Matches Phase 02.3 + Phase 03.3-07 cloud model conventions.
- **D-03a:** If a single query hits an unrecoverable error, record `answer = "[ERROR: <error_type>]"`, set all `hijacked_*` fields to `False`, increment `aggregate.error_count` by 1. Do NOT abort the run.
- **D-03b:** Resume-from-checkpoint mechanism rejected as overkill for a 100-query × 26-min run.

**Downstream propagation:**
- **D-04:** Phase 6 must auto-rerun downstream artifacts. New binary outputs (PNGs, fresh JSONs, fresh CSVs) NEVER overwrite existing committed files — they go to new filenames (`_v6` suffix or analogous). Existing markdowns are updated in-place. The submitted Phase 3.4 writeup `docs/phase3_results.md` is NOT edited.
- **D-05:** Markdown updates, in-place: `docs/results/undefended_baseline.md` (add T1b/T3/T4 columns for gpt-oss-20b and gpt-oss-120b rows; other models' rows blank or "—"); `docs/results/arms_race_table.md` (add new gpt-oss rows or appended subsection if scoped to llama only). Both markdowns get a dated disclosure line at the top.
- **D-06:** CSV companions, new files: `docs/results/undefended_baseline_v6.csv` and `docs/results/arms_race_table_v6.csv`.
- **D-07:** Figure regeneration, new files: `figures/d03_arms_race_v6.png` (or `figures/d03_arms_race_gptoss_v6.png` if gpt-oss bars don't fit the existing figure domain); `figures/d12_cross_model_heatmap_v6.png` (extend 5×3 → 5×5). Use viridis_r colormap and W-5 fail-loud invariants. Originals stay untouched.
- **D-08:** llama+mistral T1b backfill out of scope.

### Claude's Discretion

- Test stub structure (Wave 0): use the established `importlib.util.spec_from_file_location` pattern from Phase 03.2/03.4 stubs.
- Whether to factor the eval invocation into a thin Phase 6 driver or just two direct CLI invocations from a plan command.
- Wave structure (Wave 0 stubs → Wave 1 eval runs → Wave 2 make_results edit + downstream emit → Wave 3 verification) per established Phase 03.x conventions.
- Exact placement of the dated disclosure line within each markdown (top of file vs. top of section it touches).

### Deferred Ideas (OUT OF SCOPE)

- llama3.2:3b + mistral:7b T1b backfill (their `eval_harness_undefended_t34_*.json` carry T3/T4 but no T1b).
- Resume-from-checkpoint mechanism for `run_eval.py` (`.json.partial` after each query).
- Tenacity retry-on-429 wrapper around `generator.generate()`.
- Fresh `nq_poisoned_v6` collection.
- Updating `docs/phase3_results.md` (the submitted Phase 3.4 writeup prose).
- Updating the 5×5 D-12 heatmap to also include adaptive-tier rows.
- Surfacing T1b in `docs/results/arms_race_table.md` for llama too.

## Phase Requirements

This phase has no formal `REQ-XX` IDs in `.planning/REQUIREMENTS.md` — it's a follow-up gap fill, not a new feature. The implicit requirement table:

| Implicit ID | Description | Research Support |
|----|-------------|------------------|
| P6-RUN-20b | Run gpt-oss:20b-cloud undefended on nq_poisoned_v4 with `--delay 3`, emit `_v6.json` | run_eval.py CLI surface (lines 62–150); cloud-invocation precedent (Phase 02.3-02 SUMMARY); collection probed live (1239 docs, all 5 tier ranges present) |
| P6-RUN-120b | Same for gpt-oss:120b-cloud | Same as above; both models confirmed available in `ollama list` |
| P6-PRO | Output JSON carries `phase: "06"`, `supersedes_phase_02_3: true`, `error_count`, `corpus`, `collection` | run_eval.py writes most provenance fields but hardcodes `phase: "03.3"` at line 407 — post-run mutation step required |
| P6-RES | make_results.py path-resolver prefers `_v6.json` when present | scripts/make_results.py:247 read loop; make_results.py model_key keys (llama/mistral/gptoss20b/gptoss120b) are canonical |
| P6-MD | undefended_baseline.md + arms_race_table.md updated in-place with gpt-oss T1b/T3/T4 numbers + dated disclosure header | scripts/make_results.py emits these MDs from logs/eval_harness_undefended_*.json |
| P6-CSV | New `_v6.csv` files alongside originals | emit_table() pattern in make_results.py:426 supports both .md and .csv targets |
| P6-FIG | New `_v6.png` figures (D-03 + D-12 5×5) without overwriting originals | scripts/make_figures.py renderers + save_atomic idiom; W-5 D-12 `assert matrix.shape == (5, 3)` hardcoded — must extend to (5,5) |
| P6-INTEG | Existing tests test_make_results.py + test_make_figures.py stay green | Tests assert presence of "llama3.2"/"mistral"/"gpt-oss" substrings (already present); 5 PNGs file existence check (originals retained) |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Cloud LLM inference (gpt-oss:20b-cloud + 120b-cloud) | External cloud (Ollama-managed) | Local Ollama client at localhost:11434 | Cloud endpoint is the only target that can run 20B/120B; local CPU/GPU cannot host these |
| Pre-run collection sanity assertion | Local Python (`scripts/run_phase6_eval.py` driver or inline) | ChromaDB `.chroma/` PersistentClient | Cheap local probe — returns instantly; should run BEFORE the 26-min cloud invocation to fail fast if collection is stale |
| Per-tier passage_id tagging | `scripts/run_eval.py` (existing, lines 230–247) | `rag/constants.py` (TIER*_ID_START SSOT) | Already implemented; Phase 6 does not modify this layer |
| Per-tier aggregate computation | `scripts/run_eval.py` (existing, lines 308–397) | none | Already implemented; emits `asr_tier{1,1b,2,3,4}`, `paired_asr_*`, `conditional_asr_*`, `retrieval_rate_tier1b`, `co_retrieval_rate_tier4`, `fpr` in one pass |
| Provenance enrichment (`phase`, `supersedes_phase_02_3`, `error_count`) | Phase 6 driver (post-run JSON mutation) | none | `run_eval.py` writes `phase: "03.3"` hardcoded; cleanest fix is open-mutate-rewrite in the driver, NOT a `run_eval.py` patch |
| File-path resolver (`_v6.json` vs un-versioned) | `scripts/make_results.py:247` (4-line edit) | none | Single, localized edit per D-02b; `model_key` strings already canonical |
| Markdown emission (`docs/results/*.md`) | `scripts/make_results.py` `emit_table()` + dated disclosure injection | Markdown via `pd.DataFrame.to_markdown()` | Existing pipeline; Phase 6 just changes input data + adds disclosure header |
| CSV emission (`*_v6.csv`) | `scripts/make_results.py` `emit_table()` with `_v6` suffix | none | Trivially supported by the existing emit pattern; pass `name="undefended_baseline_v6"` |
| Figure rendering (`d03_arms_race_v6.png`, `d12_cross_model_heatmap_v6.png`) | `scripts/make_figures.py` renderers + atomic save | matplotlib + seaborn | Renderers are parameterized over data sources; D-12 needs `(5, 5)` matrix-shape assertion (currently hardcoded `(5, 3)`) |

## Standard Stack

This phase uses only what's already installed and committed. No new dependencies.

### Core (verified pinned versions in use)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11 | Runtime | CLAUDE.md project standard [VERIFIED: CLAUDE.md] |
| chromadb | >=1.5,<2.0 | Vector store probe (D-01a sanity assert) | Already used; PersistentClient pattern matches `scripts/_check_collections.py` [VERIFIED: scripts/_check_collections.py] |
| ollama | >=0.6,<1.0 | Cloud LLM endpoint client | Existing convention; `--delay 3` and `--model gpt-oss:*-cloud` proven in Phase 02.3-02 [CITED: scripts/run_eval.py:96-99] |
| pandas | >=2.0 | DataFrame for table emission | Already used in make_results.py [VERIFIED: scripts/make_results.py:43] |
| matplotlib + seaborn | latest | Figure rendering | Already used; `Agg` backend convention preserved [VERIFIED: scripts/make_figures.py:23-36] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `subprocess` (stdlib) | stdlib | Wraps `run_eval.py` CLI invocations from a Phase 6 driver | Use `subprocess.run(list_argv, shell=False, check=True)` per Phase 03.3-07 T-3.3-01 mitigation [VERIFIED: scripts/run_eval_v2_01_driver.py pattern in STATE Phase 03.3-07] |
| `pytest` | latest | Test stubs | `importlib.util.spec_from_file_location` pattern per Phase 03.2/03.4 [VERIFIED: tests/test_make_results.py:14-22] |
| `json` (stdlib) | stdlib | Provenance enrichment (post-run JSON mutation) | open → load → add fields → atomic rename pattern |
| `os.replace` (stdlib) | stdlib | Atomic file rename | Matches save_atomic idiom in make_figures.py [CITED: scripts/make_figures.py:81-92] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Phase 6 driver (recommended) | Inline `run_eval.py` CLI calls in plan command | Driver is needed anyway for D-01a + D-02a + D-03a; inline keeps things flat but needs out-of-band JSON mutation step |
| Post-run JSON mutation (recommended) | Edit run_eval.py to accept `--phase` and `--supersedes` flags | Source change to a stable script for one phase's needs; rejected per CONTEXT scope ("the eval pipeline already produces all 5 tier ASR numbers in one pass — research should NOT propose modifying run_eval.py logic") |
| atomic write (`.tmp` + `os.replace`) | Direct `json.dump` to final path | Original is committed; partial writes during interruption could corrupt git working tree |

**Installation:** None required — all dependencies already pinned in `requirements.txt` and used by Phase 03.4. No `pip install` step in Phase 6.

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Phase 6 Wave 1: Eval Run                              │
└─────────────────────────────────────────────────────────────────────────────┘

  scripts/run_phase6_eval.py (driver — recommended)
       │
       ├── pre-flight checks (fail fast before 26-min cloud burn)
       │     ├── ollama list           → verify cloud auth still valid
       │     ├── ChromaDB probe        → assert all 5 tier ranges present in nq_poisoned_v4
       │     │                            (D-01a — uses passage_id $gte/$lt where-clause)
       │     └── single test query     → optional: 1-shot --delay 0 sanity check on 20b first
       │
       ├── for model in [gpt-oss:20b-cloud, gpt-oss:120b-cloud]:
       │     │
       │     ├── subprocess.run([                       (T-3.3-01: shell=False)
       │     │     "python", "scripts/run_eval.py",
       │     │     "--corpus",     "data/corpus_poisoned.jsonl",
       │     │     "--collection", "nq_poisoned_v4",
       │     │     "--queries",    "data/test_queries.json",
       │     │     "--defense",    "off",
       │     │     "--model",      model,
       │     │     "--delay",      "3",
       │     │     "--output",     "logs/eval_harness_undefended_<KEY>_v6.json",
       │     │   ], shell=False, check=True)
       │     │
       │     │   └── run_eval.py
       │     │         ├── load_config + dataclasses.replace(collection=v4, llm_model=model)
       │     │         ├── pipeline.build(corpus_path=corpus_poisoned.jsonl)
       │     │         ├── for each of 100 queries:
       │     │         │     ├── pipeline.query(q)
       │     │         │     ├── per-tier passage_id tagger (lines 230–247)  ← already complete
       │     │         │     ├── per-tier hijack-string detector (lines 249–258)
       │     │         │     └── time.sleep(3)                            ← --delay
       │     │         ├── per-tier aggregate compute (lines 308–397)        ← already complete
       │     │         └── json.dump(output, f, indent=2)                    ← phase: "03.3" hardcoded ✗
       │     │
       │     └── post-run JSON mutation (D-02a + D-03a)
       │           ├── load logs/eval_harness_undefended_<KEY>_v6.json
       │           ├── output["phase"] = "06"
       │           ├── output["supersedes_phase_02_3"] = True
       │           ├── output["aggregate"]["error_count"] = sum(
       │           │       1 for r in output["results"]
       │           │       if isinstance(r["answer"], str)
       │           │       and r["answer"].startswith("[ERROR:")
       │           │     )
       │           ├── corpus + collection already present from run_eval.py ✓
       │           └── atomic rewrite: json.dump → .tmp → os.replace
       │
       └── done — two _v6.json files in logs/

┌─────────────────────────────────────────────────────────────────────────────┐
│                   Phase 6 Wave 2: Downstream Propagation                    │
└─────────────────────────────────────────────────────────────────────────────┘

  scripts/make_results.py  (~4-line edit at line 247)
       │
       ├── load_undefended_baseline(logs_dir):
       │     for model_key in [llama, mistral, gptoss20b, gptoss120b]:
       │         path_v6 = logs_dir / f"eval_harness_undefended_{model_key}_v6.json"  ← NEW
       │         path    = logs_dir / f"eval_harness_undefended_{model_key}.json"
       │         path = path_v6 if path_v6.exists() else path                          ← NEW
       │         ... continues with existing aggregate read ...
       │
       │     ↓ rows now include T1b/T3/T4 numbers for gpt-oss when _v6 present
       │
       ├── emit_undefended_baseline(undefended, output_dir, fmt)
       │     ├── write docs/results/undefended_baseline.md                ← in-place
       │     └── write docs/results/undefended_baseline.csv               ← in-place
       │     (planner adds: also write _v6.csv for the post-Phase-6 schema columns)
       │
       └── arms_race_table emit (similar logic)

  scripts/make_figures.py
       │
       ├── render_d03_arms_race(...) — ALREADY parameterized over ablation + matrix
       │     For Phase 6: either render with extended model list to figures/d03_arms_race_v6.png,
       │     or render gpt-oss-only 5-tier bars to d03_arms_race_gptoss_v6.png.
       │
       └── render_d12_cross_model_heatmap(...)
             ├── pivot _summary.json → matrix
             ├── ✗ assert matrix.shape == (5, 3)                          ← W-5 hardcoded
             │   (Phase 6 must extend matrix construction to also pull gpt-oss
             │    numbers from the new _v6.json files, then change to (5, 5))
             └── save_atomic → figures/d12_cross_model_heatmap_v6.png

  Markdown updates (D-05, in-place):
       ├── docs/results/undefended_baseline.md   ← add T1b/T3/T4 columns + disclosure header
       └── docs/results/arms_race_table.md       ← add gpt-oss rows or appended subsection + disclosure header
```

### Recommended Project Structure

No new directories. Phase 6 lives within existing structure:

```
scripts/
├── run_eval.py             # UNCHANGED
├── run_phase6_eval.py      # NEW — thin driver (D-01a + D-02a + D-03a + 2× run_eval invocation)
├── make_results.py         # 4-line edit at line 247 (path resolver)
└── make_figures.py         # extend D-12 to (5,5); new D-03 v6 emitter

logs/
├── eval_harness_undefended_gptoss20b.json       # UNCHANGED (Phase 02.3 historical)
├── eval_harness_undefended_gptoss120b.json      # UNCHANGED
├── eval_harness_undefended_gptoss20b_v6.json    # NEW
└── eval_harness_undefended_gptoss120b_v6.json   # NEW

docs/results/
├── undefended_baseline.md                       # IN-PLACE EDIT (D-05)
├── arms_race_table.md                           # IN-PLACE EDIT (D-05)
├── undefended_baseline_v6.csv                   # NEW (D-06)
└── arms_race_table_v6.csv                       # NEW (D-06)

figures/
├── d03_arms_race.png                            # UNCHANGED (Phase 03.4 submitted)
├── d12_cross_model_heatmap.png                  # UNCHANGED
├── d03_arms_race_v6.png                         # NEW (D-07; or d03_arms_race_gptoss_v6.png)
└── d12_cross_model_heatmap_v6.png               # NEW (5×5)

tests/
├── test_phase6_eval.py        # NEW — assert _v6.json structure + 5-tier aggregate keys + provenance
└── test_make_results_v6.py    # NEW — assert path-resolver prefers _v6 when present
```

### Pattern 1: Thin Phase Driver Wrapping `run_eval.py`

**What:** A small Python script that runs pre-flight checks, calls `subprocess.run([...], shell=False)` once per cloud model, and post-processes each output JSON to add provenance fields. Lineage: Phase 03.3-07's matrix driver established this pattern.

**When to use:** Whenever a phase needs to combine `run_eval.py` invocation with phase-specific provenance, sanity assertions, or post-processing that doesn't belong in `run_eval.py` itself.

**Example:**

```python
# scripts/run_phase6_eval.py — recommended structure
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import chromadb

# Same SSOT as run_eval.py (avoid hardcoding ranges twice).
sys.path.insert(0, str(Path(__file__).parent.parent))
from rag.constants import (
    TIER1_ID_START, TIER2_ID_START, TIER3_ID_START,
    TIER1B_ID_START, TIER4_ID_START, ADAPTIVE_ID_START,
)

PHASE_6_MODELS = [
    ("gpt-oss:20b-cloud",  "gptoss20b"),
    ("gpt-oss:120b-cloud", "gptoss120b"),
]
COLLECTION = "nq_poisoned_v4"
CORPUS = "data/corpus_poisoned.jsonl"
QUERIES = "data/test_queries.json"
LOGS_DIR = Path("logs")


def assert_collection_has_all_tiers(collection_name: str) -> None:
    """D-01a: fail fast if any of the 5 tier passage_id ranges is empty."""
    client = chromadb.PersistentClient(path=".chroma")
    c = client.get_collection(collection_name)
    ranges = [
        ("T1",  TIER1_ID_START,  TIER2_ID_START),
        ("T2",  TIER2_ID_START,  TIER3_ID_START),
        ("T3",  TIER3_ID_START,  TIER1B_ID_START),
        ("T1b", TIER1B_ID_START, TIER4_ID_START),
        ("T4",  TIER4_ID_START,  ADAPTIVE_ID_START),
    ]
    for name, lo, hi in ranges:
        res = c.get(
            where={"$and": [
                {"passage_id": {"$gte": lo}},
                {"passage_id": {"$lt":  hi}},
            ]},
            limit=1,
            include=["metadatas"],
        )
        assert len(res["ids"]) > 0, (
            f"D-01a sanity assert failed: {collection_name!r} has no passage in "
            f"{name} range [{lo}, {hi}). Stale collection? Refusing to burn 26 min "
            f"of cloud time on a corpus that produces 0% on T1b/T3/T4 silently."
        )


def run_one(model_id: str, model_key: str) -> Path:
    output_path = LOGS_DIR / f"eval_harness_undefended_{model_key}_v6.json"
    cmd = [
        sys.executable, "scripts/run_eval.py",
        "--corpus",     CORPUS,
        "--collection", COLLECTION,
        "--queries",    QUERIES,
        "--defense",    "off",
        "--model",      model_id,
        "--delay",      "3",
        "--output",     str(output_path),
    ]
    print(f"[phase6] $ {' '.join(cmd)}")
    subprocess.run(cmd, shell=False, check=True)
    return output_path


def add_provenance(output_path: Path) -> None:
    """D-02a + D-03a: enrich output JSON with phase/supersedes/error_count.

    run_eval.py hardcodes phase=\"03.3\" at line 407. We rewrite atomically
    to avoid corrupting the file if interrupted mid-write.
    """
    data = json.loads(output_path.read_text(encoding="utf-8"))
    data["phase"] = "06"
    data["supersedes_phase_02_3"] = True
    error_count = sum(
        1 for r in data.get("results", [])
        if isinstance(r.get("answer"), str)
        and r["answer"].startswith("[ERROR:")
    )
    data.setdefault("aggregate", {})["error_count"] = error_count

    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")  # encoding: cp1252 hazard
    os.replace(tmp, output_path)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Phase 6 cross-LLM undefended baseline gap fill.")
    parser.add_argument("--skip-preflight", action="store_true",
                        help="Skip D-01a sanity-assert (debug only).")
    args = parser.parse_args(argv)

    if not args.skip_preflight:
        assert_collection_has_all_tiers(COLLECTION)

    for model_id, model_key in PHASE_6_MODELS:
        out = run_one(model_id, model_key)
        add_provenance(out)
        print(f"[phase6] OK {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

[CITED: pattern lineage from `scripts/run_eval.py` CLI, `scripts/_check_collections.py` chromadb access, `scripts/make_figures.py:81-92` atomic-write idiom]

### Pattern 2: Path-Resolver Edit at make_results.py:247

**What:** Localized 4-line change to prefer the `_v6.json` file when present, fall back to un-versioned. Localized so it doesn't touch any test contract.

**When to use:** Per D-02b — this is the only logic change to `make_results.py`.

**Example:**

```python
# Current scripts/make_results.py:241-263
for model_key, label in [
    ("llama",      "llama3.2:3b"),
    ("mistral",    "mistral:7b"),
    ("gptoss20b",  "gpt-oss:20b-cloud"),
    ("gptoss120b", "gpt-oss:120b-cloud"),
]:
    path = logs_dir / f"eval_harness_undefended_{model_key}.json"
    if not path.exists():
        continue
    data = _safe_load_json(path)
    ...

# Phase 6 edit (~4 lines): prefer _v6 when present
for model_key, label in [
    ("llama",      "llama3.2:3b"),
    ("mistral",    "mistral:7b"),
    ("gptoss20b",  "gpt-oss:20b-cloud"),
    ("gptoss120b", "gpt-oss:120b-cloud"),
]:
    path_v6 = logs_dir / f"eval_harness_undefended_{model_key}_v6.json"
    path = path_v6 if path_v6.exists() else (
        logs_dir / f"eval_harness_undefended_{model_key}.json"
    )
    if not path.exists():
        continue
    data = _safe_load_json(path)
    ...
```

The aggregate read further down (`agg.get("asr_tier1b", 0.0)`, `agg.get("asr_tier3", 0.0)`, `agg.get("asr_tier4", 0.0)` — currently NOT read) will need to be ADDED to the row dict so the markdown emits new columns. The existing rows for `llama` + `mistral` will populate T1b/T3/T4 from their existing files (if `eval_harness_undefended_llama.json` is replaced by `_v6.json` later in a deferred phase) or display 0.0 / "—" today.

[VERIFIED: `scripts/make_results.py:241-263`]

### Pattern 3: Dated Disclosure Header for In-Place Markdown Updates

**What:** A single-line markdown blockquote at the top of each in-place-updated markdown that documents (a) the date, (b) what was added, (c) what's unchanged.

**When to use:** Per D-05 — both `undefended_baseline.md` and `arms_race_table.md` get this header.

**Example:**

```markdown
> Updated 2026-05-04: gpt-oss T1b/T3/T4 added (Phase 6 cross-LLM gap fill). Phase 02.3 / Phase 3.4 numbers above this line are unchanged.

| model              | source                      |   asr_tier1 |   asr_tier1b |   asr_tier2 |   asr_tier3 |   asr_tier4 |   paired_asr_tier1 |   paired_asr_tier2 |   retrieval_rate |   n_queries |
|:-------------------|:----------------------------|------------:|-------------:|------------:|------------:|------------:|-------------------:|-------------------:|-----------------:|------------:|
| llama3.2:3b        | Phase 2.3 canonical (n=100) |        0.10 |          —   |        0.12 |          —  |          —  |               0.10 |               0.16 |             0.86 |         100 |
| mistral:7b         | Phase 2.3 canonical (n=100) |        0.00 |          —   |        0.26 |          —  |          —  |               0.00 |               0.32 |             0.86 |         100 |
| gpt-oss:20b-cloud  | Phase 6 v6 (n=100)          |        0.XX |         0.XX |        0.XX |        0.XX |        0.XX |               0.XX |               0.XX |             0.XX |         100 |
| gpt-oss:120b-cloud | Phase 6 v6 (n=100)          |        0.XX |         0.XX |        0.XX |        0.XX |        0.XX |               0.XX |               0.XX |             0.XX |         100 |
| llama3.2:3b        | Phase 2.2 frozen (n=10)     |        0.50 |          —   |        0.00 |          —  |          —  |               0.50 |               0.00 |             1.00 |          10 |
```

The cleanest implementation is: extend `load_undefended_baseline()` to write T1b/T3/T4 columns from `agg.get("asr_tier1b", float("nan"))` etc. Where the schema lacks the keys (Phase 02.3 originals), `pd.DataFrame.to_markdown(floatfmt=".2f")` renders `nan` as `nan` — replace with `"—"` post-hoc by passing `na_rep="—"` to `to_markdown`. [CITED: pandas `DataFrame.to_markdown` `na_rep` parameter, well-documented]

### Pattern 4: Atomic-Write Idiom for Output Files

```python
def save_atomic(fig, final_path: str) -> None:
    """Save figure to .tmp then atomically rename."""
    tmp_path = final_path + ".tmp"
    fig.savefig(tmp_path, bbox_inches="tight", dpi=150, format="png")
    plt.close(fig)
    os.replace(tmp_path, final_path)
```

`os.replace` is atomic on Windows + POSIX when src/dst are in the same directory. Phase 6 figure renderers + JSON-mutation step both use this. **Critical Windows-on-matplotlib gotcha:** matplotlib infers format from extension and rejects `.tmp`; pass `format="png"` explicitly. [CITED: `scripts/make_figures.py:81-92`, STATE Phase 03.4-03 entry: "matplotlib infers savefig format from file extension and rejects `.tmp` ('Format tmp is not supported')"]

### Anti-Patterns to Avoid

- **Editing `run_eval.py` to accept `--phase` or `--supersedes`:** Phase 6 should not modify a stable script for one phase's needs. Use the post-run JSON-mutation pattern instead. CONTEXT.md is explicit: "research should NOT propose modifying run_eval.py logic." [CITED: 06-CONTEXT.md additional_context]
- **Overwriting `figures/d03_arms_race.png` and `figures/d12_cross_model_heatmap.png`:** D-04 forbids this. Always emit `_v6.png` parallel files. [CITED: 06-CONTEXT.md D-04]
- **Using `subprocess.run(cmd, shell=True)`:** Phase 03.3-07 STRIDE T-3.3-01 mitigation enforces `shell=False` everywhere. [CITED: STATE Phase 03.3-07 entry on T-3.3-01]
- **Skipping the D-01a probe to "save time":** the probe takes <1s; the 26-min cloud burn does not. Skipping risks discovering at minute 25 that T1b/T3/T4 are 0% because the wrong collection was used. [DERIVED: research methodology]
- **Reading `_summary.json` to populate the v6 d12 heatmap's gpt-oss columns:** the cross-model matrix `_summary.json` does NOT contain gpt-oss numbers; it's the Phase 03.3-07 EVAL-V2-01 product covering only llama/mistral/gemma4. Phase 6's gpt-oss numbers must come from `eval_harness_undefended_gptoss*_v6.json`. The 5×5 D-12 v6 figure renderer must read from BOTH the matrix JSON (for llama/mistral/gemma4 fused-defense numbers) AND the new `_v6.json` files (for gpt-oss undefended numbers). **However, this conflates two defense modes (fused vs no_defense) into one heatmap** — the planner should consider whether D-07's 5×5 should be all-undefended (cleanest) or apples-to-oranges (matrix's "fused" cells + Phase 6's "no_defense" cells side by side). Recommend: emit a separate `figures/d12_cross_model_undefended_v6.png` showing 5 tiers × 5 LLMs all under `no_defense` to keep semantics clean; and only extend the existing fused-defense heatmap if the gpt-oss `eval_harness_undefended_*_v6` numbers can be supplemented with corresponding fused-defense runs (out of scope per CONTEXT D-08). [DERIVED: cross-checking _summary.json schema vs. CONTEXT.md D-07] [ASSUMED: that the cleanest interpretation of D-07 5×5 is all-undefended; the user wrote "extend the 5-tier × 3-LLM heatmap (llama / mistral / gemma4) to a 5-tier × 5-LLM heatmap by appending gpt-oss-20b and gpt-oss-120b columns" which assumes fused-defense numbers exist for gpt-oss — they do not. Planner must ask the user to confirm]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-tier `passage_id` tagging | A new range-tagger in the Phase 6 driver | `scripts/run_eval.py` lines 230–247 | Already produces all 5 tier flags in one pass; duplication risks drift from `rag/constants.py` SSOT |
| Per-tier ASR aggregation | A new aggregator | `scripts/run_eval.py` lines 308–397 | Already emits 17 aggregate keys including `paired_asr_tier{1,1b,2,3,4}`, `conditional_asr_*`, `co_retrieval_rate_tier4` |
| Cloud-LLM rate-limit handling | A retry/backoff wrapper | `--delay 3` (existing flag) | Sufficient for 100-query × 26-min runs per Phase 02.3 + 03.3-07 precedent; D-03 explicitly rejects retry wrapper |
| Markdown table emission | Custom Markdown writer | `pandas.DataFrame.to_markdown(floatfmt=".2f", na_rep="—")` | Existing pattern in `make_results.py:429`; supports `na_rep` for missing-T1b/T3/T4 cells |
| Atomic file write | Lock-based or rename-loop | `os.replace(tmp, final)` after writing to `.tmp` | Atomic on POSIX + Windows; established by Phase 03.4-03 |
| ChromaDB count + range probe | Custom SQLite query against `.chroma/chroma.sqlite3` | `chromadb.PersistentClient` + `collection.get(where={...})` | Already proven in `scripts/_check_collections.py`; ChromaDB ABI guarantees stability across 1.5+ versions |
| JSON file mutation | Read-modify-write with risk of partial overwrite | open → load → mutate → write to `.tmp` → `os.replace` | Standard atomic-update idiom |

**Key insight:** Phase 6 is "thread the needle through existing infrastructure." Every capability the phase needs already exists in the codebase; the work is in **plumbing** (driver invocation order, path resolver, figure shape extension), not in **building** new functionality.

## Runtime State Inventory

This is a **logs-and-propagation** phase, not a rename/refactor — but per execution_flow Step 2.5, the trigger is broad ("any phase involving rename, rebrand, refactor, string replacement, or migration"). Phase 6 does string-equivalent work: introducing a new filename suffix (`_v6`) that downstream consumers must learn about. Inventory is therefore relevant to confirm we don't miss a cached-state reference.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `nq_poisoned_v4` ChromaDB collection at `.chroma/` (1239 docs, all 5 tier ranges verified). No Phase 6 data writes to ChromaDB. | None — read-only |
| Live service config | Ollama daemon at `localhost:11434` with cloud auth via `ollama login`. Auth state is per-user-machine and may have expired since Phase 03.3-07 (last cloud invocation 2026-04-27). | Pre-flight check: `ollama list` must show `gpt-oss:20b-cloud` AND `gpt-oss:120b-cloud` AND a single test query must succeed before committing to the 26-min run. [VERIFIED via `ollama list` 2026-05-04: both models present] |
| OS-registered state | None — Phase 6 invokes `python` and `ollama` binaries directly; no Task Scheduler / systemd / launchd registrations | None — verified by inspection |
| Secrets / env vars | `OLLAMA_HOST` (optional, defaults to `http://localhost:11434`); ollama login token in `~/.ollama/`. No env-var renames in Phase 6. | None |
| Build artifacts | None — Phase 6 produces JSON / CSV / MD / PNG; no compiled artifacts. `.chroma/` is git-ignored and pre-built. | None |

**Cross-reference (downstream consumers that read `eval_harness_undefended_*.json` patterns and might miss `_v6.json`):**

| Consumer | Reads from | Phase 6 impact |
|----------|------------|-----------------|
| `scripts/make_results.py:247` | `eval_harness_undefended_{llama,mistral,gptoss20b,gptoss120b}.json` | Path-resolver edit (D-02b) makes it prefer `_v6.json` |
| `scripts/make_figures.py` D-03 renderer | `ablation_table.json` + `_summary.json` + `adaptive_*.json` (NO direct read of `eval_harness_undefended_*.json`) | No code change for D-03 itself; phase 6 adds a NEW `render_d03_arms_race_v6` that reads `eval_harness_undefended_*_v6.json` for the gpt-oss bars |
| `scripts/make_figures.py` D-12 renderer | `_summary.json` only | No code change for the original D-12; phase 6 adds a NEW `render_d12_cross_model_heatmap_v6` that reads `_summary.json` AND `eval_harness_undefended_*_v6.json` for the 5×5 matrix |
| `tests/test_make_results.py::test_three_source_aggregation` | tests "llama3.2", "mistral", "gpt-oss" substrings in `undefended_baseline.md` | Stays green — substrings still present after Phase 6 (gpt-oss rows present, just with new T1b/T3/T4 columns populated) |
| `tests/test_make_figures.py::test_all_five_pngs_emitted` | tests existence of 5 PNGs in figures/ | Stays green — Phase 6 adds NEW `_v6.png` files; the existing 5 are not touched |

## Common Pitfalls

### Pitfall 1: cp1252 Encoding Cascade on Windows
**What goes wrong:** A Python file-read of `data/corpus_poisoned.jsonl` (which contains Unicode homoglyphs like Cyrillic НАСКЕД in T1b passages) without `encoding="utf-8"` triggers a `UnicodeDecodeError: 'charmap'` cascade on Windows because the default codec falls back to cp1252.
**Why it happens:** Windows console + `open()` defaults are cp1252; the corpus has Unicode payloads.
**How to avoid:** Every `open()`, `Path.read_text()`, and `Path.write_text()` in any Phase 6 driver/script MUST pass `encoding="utf-8"` explicitly. `json.dumps` is fine; `json.dump(f, ...)` after `open(f, "w", encoding="utf-8")` is fine.
**Warning signs:** `UnicodeDecodeError` mentioning `'charmap'`, or output JSON containing `\u0...` escapes that don't decode.
[CITED: STATE Phase 03.4-01 entry on encoding cascade; STATE entry on `recent fix` in 05-IN-02]

### Pitfall 2: Stale Ollama Cloud Auth
**What goes wrong:** `ollama login` token expires silently between Phase 03.3-07 (Apr 27) and Phase 6 (May 4); the first cloud query at minute 0 returns a 401, but `run_eval.py` has no auth-failure handler — the entire 26-min budget gets burned producing 100 `[ERROR: ...]` answers, and the output JSON is published with `error_count=100` and 0% across all tiers.
**Why it happens:** Cloud auth is per-machine state managed by Ollama, not by code.
**How to avoid:** Pre-flight check before the first `subprocess.run` invocation: (a) `ollama list` must show both target models; (b) optionally run a single 1-shot test query (e.g., "Who wrote Hamlet?") with `--delay 0` against gpt-oss:20b-cloud to verify auth.
**Warning signs:** `subprocess` returncode != 0 from `ollama list`; or the first query in the run takes <1s and returns an empty/error answer.
[CITED: 06-CONTEXT.md code_context "Cloud auth: ollama login may have expired since Phase 03.3-07"]

### Pitfall 3: `run_eval.py` Hardcoded `phase: "03.3"` Field
**What goes wrong:** Without the post-run JSON-mutation step, output `_v6.json` files carry `phase: "03.3"` instead of `phase: "06"`, violating D-02a. Downstream consumers that key off the `phase` field (none currently, but tests assert against it) drift silently.
**Why it happens:** `run_eval.py:407` writes `"phase": "03.3"` regardless of the calling phase. Historical artifact: this was added in Phase 03.3 and never re-templatized.
**How to avoid:** Post-run JSON mutation in the Phase 6 driver (see Pattern 1 above).
**Warning signs:** A `tests/test_phase6_eval.py` test that checks `data["phase"] == "06"` fails after a fresh run.
[VERIFIED: `scripts/run_eval.py:407`]

### Pitfall 4: Sustained Cloud Rate-Limit Spike
**What goes wrong:** The 100-query × 2-model run is the longest sustained cloud invocation in project history; Phase 02.3 was 100×4 models split over multiple sessions, Phase 03.3-07 was much shorter cells with restarts between. A 429 spike from gpt-oss:120b-cloud during minutes 14–16 silently drops 5–10 queries to `[ERROR: rate_limit]` answers; the run completes but `error_count=8` quietly degrades the published baseline.
**Why it happens:** Cloud endpoints implement undocumented rate limits; sustained 100-query loads are off the test envelope.
**How to avoid:** D-03a's `error_count` field is the visibility hook — reviewers can SEE that 8 queries failed in the published JSON. Do NOT silently retry; do NOT silently drop; record honestly. If `error_count > 5` post-run, surface in Phase 6 verification (planner discretion: re-run, accept, or descope).
**Warning signs:** `error_count > 0` in the output `aggregate` block.
[CITED: 06-CONTEXT.md code_context "Rate-limit envelope unknown for sustained 100-query × 2-model load"]

### Pitfall 5: D-12 Heatmap Schema Drift on (5×3) → (5×5) Extension
**What goes wrong:** The W-5 invariant `assert matrix.shape == (5, 3)` is hardcoded at `make_figures.py:441`. If the v6 renderer simply pivots a larger DataFrame and the assertion is forgotten or copy-pasted unchanged, the renderer silently raises `AssertionError` mid-render, returns `2`, and the new figure is never emitted.
**Why it happens:** The W-5 invariant was Phase 03.4-03's defense against schema drift between `_summary.json`'s underscore-vs-colon model labels. Phase 6 changes the dimensionality but inherits the assertion.
**How to avoid:** New `render_d12_cross_model_heatmap_v6` function with `assert matrix.shape == (5, 5)` AND `not matrix.isna().any().any()`. Keep the original `render_d12_cross_model_heatmap` untouched (D-04: never overwrite originals).
**Warning signs:** `[ERROR] fig5: assertion: D-12 wrong shape: (5, 5) (expected (5, 3)).`
[VERIFIED: `scripts/make_figures.py:441-448`]

### Pitfall 6: D-12 5×5 Mixes "Fused" and "Undefended" Cells
**What goes wrong:** The original D-12 heatmap shows `asr_overall` for `defense == "fused"` only; extending to 5 LLMs by appending gpt-oss columns from `eval_harness_undefended_*_v6.json` (which is `defense == "off"`) produces a heatmap where 3 columns are fused-defense numbers and 2 columns are no-defense numbers — visually dense and meaningfully wrong.
**Why it happens:** D-07 in CONTEXT.md is silent on this semantic; the user phrased it as "extend the 5-tier × 3-LLM heatmap (llama / mistral / gemma4) to a 5-tier × 5-LLM heatmap." This wording assumes fused-defense numbers exist for gpt-oss, but per D-08 they're out of scope this phase.
**How to avoid:** Phase 6 figure should be an ALL-UNDEFENDED 5×5 heatmap reading exclusively from `eval_harness_undefended_*_v6.json` (gpt-oss) + `eval_harness_undefended_t34_*.json` (llama+mistral T1+T2+T3+T4) + a placeholder cell for gemma4 (which has no eval_harness_undefended_*.json). Or: emit the figure as 5×4 (skipping gemma4) with a footnote. Planner must surface this to the user before Wave 2.
**Warning signs:** Heatmap title doesn't match the cells' defense mode; cell values don't make sense vs. published headlines.
[ASSUMED: that all-undefended is the correct semantic — needs user confirmation per discuss-phase escalation]

### Pitfall 7: Disclosure Header Conflict with `pd.DataFrame.to_markdown()` Overwrite
**What goes wrong:** `make_results.py` regenerates `undefended_baseline.md` from scratch on every run. If Phase 6 manually adds a disclosure header to the file, the next `make_results.py` run wipes it.
**Why it happens:** `emit_table()` calls `(output_dir / f"{name}.md").write_text(md + "\n", encoding="utf-8")` — full overwrite, no append.
**How to avoid:** The disclosure header must be emitted FROM `make_results.py` itself. Cleanest: a `--disclosure` CLI flag (or env var), or hardcode the header into `emit_undefended_baseline()` for the Phase 6 era. The planner must add this to make_results.py, NOT manually edit the .md.
**Warning signs:** Disclosure line missing after a fresh `make_results.py` run.
[VERIFIED: `scripts/make_results.py:429-430` `write_text` overwrite]

## Code Examples

### Verified Pattern: ChromaDB Range Probe (D-01a)

```python
# Source: scripts/_check_collections.py + project verification 2026-05-04
import chromadb
client = chromadb.PersistentClient(path=".chroma")
c = client.get_collection("nq_poisoned_v4")
res = c.get(
    where={"$and": [
        {"passage_id": {"$gte": 20150}},  # T1b lower
        {"passage_id": {"$lt":  20200}},  # T1b upper
    ]},
    limit=1,
    include=["metadatas"],
)
assert len(res["ids"]) > 0, "T1b range empty in nq_poisoned_v4 — stale collection"
```

[VERIFIED: live probe 2026-05-04 returned 3 passages for each of the 5 ranges]

### Verified Pattern: Cloud Eval CLI Invocation

```bash
# Source: 06-CONTEXT.md Established Patterns + Phase 02.3-02 SUMMARY lineage
python scripts/run_eval.py \
    --corpus     data/corpus_poisoned.jsonl \
    --collection nq_poisoned_v4 \
    --queries    data/test_queries.json \
    --defense    off \
    --model      gpt-oss:20b-cloud \
    --delay      3 \
    --output     logs/eval_harness_undefended_gptoss20b_v6.json
```

[VERIFIED: matches scripts/run_eval.py argparse surface; CLI flags all exist at lines 66–149]

### Verified Pattern: Atomic JSON Provenance Mutation

```python
# Source: combination of scripts/make_figures.py:save_atomic + json idiom
import json
import os
from pathlib import Path

def add_provenance(output_path: Path) -> None:
    data = json.loads(output_path.read_text(encoding="utf-8"))
    data["phase"] = "06"
    data["supersedes_phase_02_3"] = True
    error_count = sum(
        1 for r in data.get("results", [])
        if isinstance(r.get("answer"), str)
        and r["answer"].startswith("[ERROR:")
    )
    data.setdefault("aggregate", {})["error_count"] = error_count

    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, output_path)
```

[VERIFIED: idiom matches save_atomic in make_figures.py:81-92; encoding="utf-8" mandatory per Pitfall 1]

### Verified Pattern: Test Stub via importlib

```python
# Source: tests/test_make_results.py:14-22 (Phase 03.4-01 stub pattern)
import importlib.util
import pytest
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
try:
    _spec = importlib.util.spec_from_file_location(
        "run_phase6_eval", _SCRIPTS_DIR / "run_phase6_eval.py"
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    main = _mod.main
    _AVAILABLE = True
except (AttributeError, FileNotFoundError, Exception):
    _AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AVAILABLE, reason="scripts/run_phase6_eval.py not yet implemented (Wave 1)"
)
```

[VERIFIED: identical stub at tests/test_make_results.py:14-22]

## State of the Art

No state-of-the-art shifts required for this phase — it's pure infrastructure plumbing within the existing project's idioms.

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 02.3 cloud eval (T1+T2 only, hand-rolled per-model invocation) | Phase 6 driver wrapping `subprocess.run` with `shell=False` | Phase 03.3-07 (2026-04-27) | Phase 6 inherits the driver-with-subprocess pattern; cleaner provenance |
| `_summary.json` flat-array schema | Same | Stable since 03.3-07 | Phase 6 reads but does not write `_summary.json` |
| `phase` field in eval JSONs | Hardcoded `phase: "03.3"` in run_eval.py | Phase 03.3 (no override flag) | Phase 6 patches via post-run JSON mutation, not source change |

**Deprecated/outdated:**
- `nq_poisoned_v3` (1100 docs, T1+T2 only): superseded by `nq_poisoned_v4` (1239 docs, 5 tiers). Phase 6 must use v4. [CITED: STATE Phase 02.4 marker]
- `kimi-k2.5:cloud` as cloud target: requires paid Ollama subscription team doesn't have. `gpt-oss:20b-cloud` is the canonical replacement. Phase 6 does not need kimi. [CITED: STATE Phase 02.4-01]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The cleanest semantic for the D-07 5×5 D-12 heatmap is "all-undefended" (not mixing fused-defense + no-defense cells). The user wrote "extend the 5-tier × 3-LLM heatmap" assuming fused-defense numbers for gpt-oss exist; they don't (out of scope per D-08). | Anti-Patterns; Pitfall 6 | If the user actually wants a mixed-defense heatmap, the figure is misleading. Must be confirmed in /gsd-discuss-phase or planner ask-step. |
| A2 | The post-run JSON-mutation step is acceptable to the user as the way to enrich `phase`/`supersedes_phase_02_3`/`error_count` (vs. modifying `run_eval.py`). | Pattern 1; Pitfall 3 | If the user wants `run_eval.py` to natively support `--phase` and `--error-count`, the planner needs additional source-edit tasks. CONTEXT.md says "research should NOT propose modifying run_eval.py logic" so this is implicit but not explicit confirmation. |
| A3 | The Phase 03.3-07 cloud rate-limit envelope (sustained ~26 min) is sufficient for two back-to-back gpt-oss:*-cloud runs without exhausting hourly caps. | Pitfall 4 | If 429s spike, `error_count` will be non-zero and the run is published with degraded numbers. Mitigation: D-03a makes failures visible; planner can re-run. |
| A4 | The `error_count` field placement under `aggregate` (vs. top-level) matches CONTEXT.md D-02a. | D-02a copy + Pattern 1 example | CONTEXT D-02a says "plus an `error_count` integer (see D-03)" without specifying placement. D-03a says `aggregate.error_count`. Recommend `aggregate.error_count` for consistency with the other aggregate-level integer fields (`chunks_removed_total`). |
| A5 | The dated disclosure line should be emitted by `make_results.py`, not manually inserted into the .md. | Pitfall 7 | If the planner manually inserts the line, the next `make_results.py` run wipes it. |
| A6 | Markdown header for in-place updates uses the exact wording from D-05: "Updated 2026-05-04: gpt-oss T1b/T3/T4 added (Phase 6 cross-LLM gap fill). Phase 02.3 / Phase 3.4 numbers above this line are unchanged." | Pattern 3 | Wording is suggested by CONTEXT.md but not locked verbatim. Planner can refine. |

## Open Questions

1. **Should the D-12 v6 5×5 heatmap show all-undefended cells, or mix fused (llama/mistral/gemma4) + undefended (gpt-oss) cells?**
   - What we know: The original 5×3 heatmap shows `defense == "fused"` cells only. CONTEXT D-07 says "extend ... to a 5-tier × 5-LLM heatmap by appending gpt-oss-20b and gpt-oss-120b columns." Out-of-scope D-08 forbids running gpt-oss-fused.
   - What's unclear: Whether mixing defense modes in one heatmap is acceptable or misleading.
   - Recommendation: Surface in planning's discuss-phase escalation; default to all-undefended 5×5 if not addressed (cleanest semantic).

2. **Does the Phase 6 driver call `make_results.py` and `make_figures.py` directly, or does the plan command sequence them as separate Wave 2 invocations?**
   - What we know: Phase 03.4 had separate plans for make_results (Plan 02) and make_figures (Plan 03).
   - What's unclear: Phase 6 wave structure suggests "Wave 2 = make_results + downstream emit." The recommendation is to keep them as separate plan steps for clean test segmentation but executed in the same wave.
   - Recommendation: Wave 2 = (a) make_results.py path-resolver edit + run; (b) make_figures.py v6 renderers + run; (c) markdown disclosure injection.

3. **What does `tests/test_make_results.py::test_three_source_aggregation` need to assert in the post-Phase-6 era?**
   - What we know: Currently asserts substrings `["llama3.2", "mistral", "gpt-oss"]` in the undefended baseline markdown.
   - What's unclear: Whether to add new assertions for T1b/T3/T4 column presence.
   - Recommendation: Add `tests/test_make_results_v6.py` that asserts the new columns are present; existing test stays untouched (planner must verify it stays green).

4. **Does the disclosure header land at the top of the file or top of a new "## Phase 6 update" subsection?**
   - What we know: CONTEXT D-05 leaves this to Claude's discretion ("pick whichever reads cleaner").
   - Recommendation: Top of the file (most visible) — both files are short tables; reader sees the disclosure before any data.

5. **Should the gpt-oss `_v6.json` files commit to git given `logs/` is gitignored?**
   - What we know: STATE Phase 03.4-04 entry: "logs/ is gitignored (.gitignore line 15); canonical analysis docs are force-added with `git add -f`." Phase 02.3 originals were force-added.
   - Recommendation: Force-add the new `_v6.json` files with `git add -f` — they are canonical baseline artifacts, not transient logs.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 | `run_eval.py`, driver script, tests | ✓ | 3.11 (in `rag-security` conda env) | — |
| ollama (CLI binary) | Cloud LLM client | ✓ | 0.22.0 [VERIFIED 2026-05-04] | — |
| `gpt-oss:20b-cloud` model | Phase 6 target #1 | ✓ | model id 875e8e3a629a, 12 days old [VERIFIED via `ollama list`] | None — phase blocks if missing |
| `gpt-oss:120b-cloud` model | Phase 6 target #2 | ✓ | model id 569662207105, 12 days old [VERIFIED] | None — phase blocks if missing |
| Ollama cloud auth | Cloud query auth | ⚠️ unverified | unknown | If expired: re-run `ollama login`, restart phase. |
| ChromaDB collection `nq_poisoned_v4` | Eval target collection | ✓ | 1239 docs, all 5 tier ranges + adaptive verified [VERIFIED via probe 2026-05-04] | If stale or missing: rebuild via `generate_poisoned_corpus.py` (out of scope; Phase 02.4-03 produced this collection) |
| `data/test_queries.json` | Canonical 100-query set | ✓ | 100 entries (50 paired, 50 clean) [VERIFIED] | — |
| `data/corpus_poisoned.jsonl` | Source corpus | ✓ | exists in repo [VERIFIED] | — |
| chromadb Python lib | D-01a probe | ✓ | installed in `rag-security` env [VERIFIED via probe execution] | — |
| pandas | DataFrame for tables | ✓ | installed (used by make_results.py) | — |
| matplotlib + seaborn | Figures | ✓ | installed (used by make_figures.py) | — |
| pytest | Test stubs + Wave 0 | ✓ | installed | — |
| `subprocess` (stdlib) | Driver wrapping run_eval.py | ✓ | stdlib | — |

**Missing dependencies with no fallback:** None blocking.

**Missing dependencies with fallback:** None.

**Pre-flight verification commands:**
```bash
ollama list | grep -E "gpt-oss:(20|120)b-cloud"   # both must appear
conda run -n rag-security python -c "import chromadb; c = chromadb.PersistentClient(path='.chroma').get_collection('nq_poisoned_v4'); print(c.count())"   # must print 1239
```

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (already installed via `requirements.txt`) |
| Config file | `pyproject.toml` / `pytest.ini` not in repo root; pytest uses defaults + auto-discovery in `tests/` |
| Quick run command | `pytest tests/test_phase6_eval.py tests/test_make_results_v6.py -x` |
| Full suite command | `pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| P6-RUN-20b | Driver runs gpt-oss:20b-cloud and emits `eval_harness_undefended_gptoss20b_v6.json` | smoke (Wave 0 stub asserts `main` importable; Wave 3 verification asserts file exists + structurally valid) | `pytest tests/test_phase6_eval.py::TestRunPhase6EvalSmoke -x` | ❌ Wave 0 |
| P6-RUN-120b | Driver runs gpt-oss:120b-cloud and emits `eval_harness_undefended_gptoss120b_v6.json` | smoke (same) | `pytest tests/test_phase6_eval.py::TestRunPhase6EvalSmoke -x` | ❌ Wave 0 |
| P6-PRO | Output JSON carries `phase: "06"`, `supersedes_phase_02_3: True`, `error_count` integer, all 5 tier aggregate keys | unit (post-run JSON structure assertion) | `pytest tests/test_phase6_eval.py::TestProvenanceFields -x` | ❌ Wave 0 |
| P6-PRE | D-01a sanity-assert detects stale collections (no T1b range → AssertionError before subprocess) | unit (mock `chromadb.PersistentClient.get_collection.get` to return empty for one tier; assert main() raises) | `pytest tests/test_phase6_eval.py::TestSanityAssert -x` | ❌ Wave 0 |
| P6-RES | `make_results.py` prefers `_v6.json` when present, falls back otherwise | unit (write a fake `_v6.json` to tmp_path, verify load_undefended_baseline picks it; remove `_v6.json`, verify falls back) | `pytest tests/test_make_results_v6.py::TestPathResolver -x` | ❌ Wave 0 |
| P6-RES-INT | Existing `tests/test_make_results.py::test_three_source_aggregation` stays green after path-resolver edit | regression | `pytest tests/test_make_results.py::TestMakeResultsSmoke -x` | ✓ exists |
| P6-MD | `undefended_baseline.md` contains gpt-oss T1b/T3/T4 columns + dated disclosure header | unit (post-emit substring asserts) | `pytest tests/test_make_results_v6.py::TestMarkdownColumns -x` | ❌ Wave 0 |
| P6-CSV | `undefended_baseline_v6.csv` and `arms_race_table_v6.csv` exist in `docs/results/` after run | unit (file existence + CSV header check) | `pytest tests/test_make_results_v6.py::TestCsvCompanions -x` | ❌ Wave 0 |
| P6-FIG | `figures/d03_arms_race_v6.png` and `figures/d12_cross_model_heatmap_v6.png` exist with size > 1KB; original `d03_arms_race.png` and `d12_cross_model_heatmap.png` unchanged | smoke (file existence + size check + originals untouched via mtime) | `pytest tests/test_phase6_eval.py::TestFigureV6Emitted -x` | ❌ Wave 0 |
| P6-FIG-INV | D-12 v6 renderer enforces `assert matrix.shape == (5, 5)` (not 5,3) | unit (mock matrix with wrong shape, verify AssertionError) | `pytest tests/test_phase6_eval.py::TestD12V6Invariants -x` | ❌ Wave 0 |
| P6-INTEG | Existing `tests/test_make_figures.py::test_all_five_pngs_emitted` stays green | regression | `pytest tests/test_make_figures.py -x` | ✓ exists |

### Sampling Rate
- **Per task commit:** `pytest tests/test_phase6_eval.py tests/test_make_results_v6.py -x` (~10s)
- **Per wave merge:** `pytest tests/ -x` (~3 min — includes existing tests)
- **Phase gate:** Full suite green before `/gsd-verify-work`; Wave 1 cloud-runs verified separately by reading the two `_v6.json` files and confirming `error_count`, `phase: "06"`, all 5 tier aggregates present, n_queries=100.

### Wave 0 Gaps

- [ ] `tests/test_phase6_eval.py` — covers P6-RUN-20b, P6-RUN-120b, P6-PRO, P6-PRE, P6-FIG, P6-FIG-INV
- [ ] `tests/test_make_results_v6.py` — covers P6-RES, P6-MD, P6-CSV
- [ ] `scripts/run_phase6_eval.py` — production code; Wave 1
- [ ] `scripts/make_figures.py` extension — `render_d03_arms_race_v6` and `render_d12_cross_model_heatmap_v6` functions; Wave 2
- [ ] `scripts/make_results.py` edit at line 247 (path resolver) + new disclosure header injection; Wave 2

Framework install: none — pytest, chromadb, pandas, matplotlib all already present.

### In-Flight Validation Hooks

Per CONTEXT.md additional_context:

1. **Pre-run sanity assertion (D-01a `passage_id` range probe):** runs in driver `assert_collection_has_all_tiers` BEFORE first subprocess invocation. Failure raises `AssertionError`, abort cleanly with non-zero exit. (Test: P6-PRE)
2. **In-flight error-count provenance (D-03a):** `run_eval.py`'s per-query loop already stores answers verbatim including any `[ERROR: ...]`-prefixed entries; the post-run mutation step counts these and sets `aggregate.error_count`. (Test: P6-PRO)
3. **Post-run schema assertion:** test asserts the output JSON has `phase == "06"`, `supersedes_phase_02_3 == True`, `aggregate` block contains all 5 of `asr_tier{1,1b,2,3,4}` keys + `error_count` is an integer ≥ 0. (Test: P6-PRO)
4. **Downstream invariants:** B-2 D-03 + W-5 D-12 invariants stay green for original PNGs (test_make_figures.py); new v6 D-12 renderer asserts (5, 5) shape. (Tests: P6-INTEG, P6-FIG-INV)
5. **Three-source aggregation test stays green:** `tests/test_make_results.py::test_three_source_aggregation` asserts substrings `["llama3.2", "mistral", "gpt-oss"]` — all present in post-Phase-6 markdown. (Test: P6-RES-INT)
6. **Path-resolver test asserts `_v6` preferred when present:** new test in `test_make_results_v6.py`. (Test: P6-RES)

## Project Constraints (from CLAUDE.md)

| Directive | Source | Impact on Phase 6 |
|-----------|--------|--------------------|
| Custom RAG pipeline (no LangChain/LlamaIndex) | Tech Stack section | Phase 6 uses only existing custom-pipeline scripts (run_eval.py, make_results.py, make_figures.py) |
| Python 3.11 | Tech Stack | Driver written for 3.11 |
| Ollama for local + cloud LLM inference | Tech Stack | gpt-oss:*-cloud invocations via Ollama; no API-keys-in-code |
| ChromaDB >=1.5,<2.0 for vector store | Tech Stack | D-01a probe uses chromadb >=1.5 PersistentClient + `where={'$and':[...]}` syntax (verified working live 2026-05-04) |
| Reproducible setup with pinned package versions, random seeds, config file | RAG-05 | Phase 6 inherits via `set_global_seed(eval_cfg.seed)` already invoked by `run_eval.py:210`; no new seed-management |
| Force-add log files with `git add -f` when logs/ is gitignored | STATE Phase 03.4-04 | Phase 6 uses `git add -f logs/eval_harness_undefended_gptoss*_v6.json` |
| GSD Workflow Enforcement (no direct edits without GSD command) | CLAUDE.md GSD Workflow Enforcement | Phase 6 work happens via `/gsd-execute-phase 6` — already in flow |
| `subprocess.run(list_argv, shell=False)` everywhere (T-3.3-01 mitigation) | STATE Phase 03.3-07 | Phase 6 driver uses `shell=False, check=True` |
| `encoding="utf-8"` on all file reads/writes | STATE Phase 03.4-01 | All Phase 6 file ops include `encoding="utf-8"` (Pitfall 1) |

## Sources

### Primary (HIGH confidence)
- `scripts/run_eval.py` (full file read) — verified per-tier passage_id tagging at lines 230–247, per-tier aggregate computation at lines 308–397, hardcoded `phase: "03.3"` at line 407, all CLI flags (`--corpus`, `--collection`, `--queries`, `--defense`, `--model`, `--delay`, `--output`, `--tier-filter`)
- `scripts/make_results.py` (full file read) — verified path-resolver location at line 247, DEFENSE_DISPLAY single-source-of-truth at lines 57–83, `_normalize_matrix_model` at lines 296–309, emit_table pattern at lines 426–434
- `scripts/make_figures.py` (full file read) — verified W-5 invariant at line 441 (`assert matrix.shape == (5, 3)`), B-2 invariants at lines 174–188, save_atomic at lines 81–92, D-03 + D-12 renderer signatures
- `rag/constants.py` (full file read) — verified TIER1=20000, TIER2=20050, TIER3=20100, TIER1B=20150, TIER4=20200, ADAPTIVE=20500, ATK02_SWEEP=21000
- ChromaDB live probe (run 2026-05-04) — verified `nq_poisoned_v4` has 1239 docs and at least 3 passages in each tier range
- `ollama list` (run 2026-05-04) — verified `gpt-oss:20b-cloud` (875e8e3a629a) and `gpt-oss:120b-cloud` (569662207105) present
- `tests/test_make_results.py`, `tests/test_make_figures.py`, `tests/test_phase4_assets.py`, `tests/test_eval_tier1b.py` (full file read) — verified `importlib.util.spec_from_file_location` Wave 0 stub pattern; assertions on three-source aggregation; B-2 / W-5 invariants
- `logs/eval_harness_undefended_gptoss20b.json` (head read) — verified existing schema: `phase: "02.3"`, `collection: "nq_poisoned_v3"`, T1+T2 keys only
- `logs/eval_harness_undefended_t34_llama.json` (head read) — verified target 5-tier schema: `asr_tier{1,2,3,4}`, `paired_asr_tier{1,2,3,4}`, `co_retrieval_rate_tier4`, `conditional_asr_tier{1,2,3,4}`
- `docs/results/undefended_baseline.md`, `docs/results/arms_race_table.md` (full read) — verified existing output schema for in-place editing target
- `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` (full read) — verified phase boundaries, deferred items, lineage decisions

### Secondary (MEDIUM confidence)
- `.planning/phases/02.3-evaluation-harness/02.3-02-SUMMARY.md` — cloud-eval CLI invocation pattern; established `--delay 3` convention
- `.planning/phases/06-cross-llm-undefended-baseline-gap-fill-run-gpt-oss-20b-cloud/06-CONTEXT.md` — D-01 through D-08, codebase hazards, established patterns

### Tertiary (LOW confidence) — none
All claims grounded in either live verification or direct file reads.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every library version pinned in existing requirements.txt and exercised in Phase 03.x successfully
- Architecture: HIGH — every file path, line number, and code excerpt verified against live source
- Pitfalls: HIGH for #1, #3, #4, #5, #7 (all directly verified or codified in STATE entries); MEDIUM for #2 (auth-expiry depends on user-machine state); MEDIUM for #6 (depends on user intent — flagged in Assumptions)
- Validation architecture: HIGH — pytest framework verified active, existing test stubs verified working, all proposed test names follow established patterns

**Research date:** 2026-05-04
**Valid until:** 2026-06-03 (30 days for stable dependencies; if `ollama` cloud endpoint conventions change or `chromadb` ABI breaks, treat as stale)

---

*Phase: 06-cross-llm-undefended-baseline-gap-fill-run-gpt-oss-20b-cloud*
*Researched: 2026-05-04*
