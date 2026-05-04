---
phase: "07"
plan: "03"
subsystem: scripts
tags: [wave-1, make-results, v7-emitter, path-resolver, phase7, honest-fpr]
dependency_graph:
  requires:
    - 07-01 (Wave 0 stubs in tests/test_make_results_v7.py)
  provides:
    - scripts/make_results.py (_resolve_v7_ablation_path, load_honest_fpr_v7, emit_honest_fpr_gptoss_v7, _V7_ABLATION_FILENAME)
  affects:
    - Wave 2 Plan 04 (cloud M3 run produces logs/ablation_table_gptoss_v7.json which this emitter consumes)
    - Wave 2 Plan 05 (writeup addendum; TestV7Compat already passes)
    - Wave 2 Plan 06 (verification; runs make_results.py to regenerate auto-companion table)
tech_stack:
  added: []
  patterns:
    - Phase 6 D-13 v6 path-resolver pattern mirrored for v7
    - schema-defensive .get(...) reads (T-3.4-W1-02)
    - no-op-when-absent additive branch (purely additive delta)
    - DEFENSE_DISPLAY single source of truth (not modified)
key_files:
  created: []
  modified:
    - scripts/make_results.py
decisions:
  - "DEFENSE_DISPLAY not modified — existing fused/def02 entries already cover Phase 7 row labels (per CONTEXT line 196)"
  - "Type annotations quoted (Path | None) for Python 3.9 compatibility — avoid runtime error on older Python"
  - "_V7_ABLATION_FILENAME constant placed before DEFENSE_DISPLAY (line 57) as module-level single source of truth per D-05"
metrics:
  duration: "2m 18s"
  completed: "2026-05-04"
  tasks: 1
  files: 1
---

# Phase 07 Plan 03: Phase 7 Path-Resolver + Emitter (make_results.py) Summary

Additive ~65-line delta to `scripts/make_results.py` adding a v7 path-resolver branch mirroring the Phase 6 D-13 pattern: `_resolve_v7_ablation_path`, `load_honest_fpr_v7`, `emit_honest_fpr_gptoss_v7`, and `_V7_ABLATION_FILENAME`. When `logs/ablation_table_gptoss_v7.json` is absent, `main()` no-ops gracefully (rc=0, no v7 files written). When present, `docs/results/honest_fpr_gptoss_v7.{md,csv}` are emitted.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add _resolve_v7_ablation_path + load_honest_fpr_v7 + emit_honest_fpr_gptoss_v7 + main() integration | d1de4c9 | scripts/make_results.py |

## git diff --stat scripts/make_results.py

```
 scripts/make_results.py | 65 +++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 65 insertions(+)
```

## Lines Added (resolver, loader, emitter, main() integration)

**Resolver** (lines 541-550):
```python
def _resolve_v7_ablation_path(logs_dir: "Path | None" = None) -> "Path | None":
    base = (logs_dir if logs_dir is not None else Path("logs"))
    p = base / _V7_ABLATION_FILENAME
    return p if p.exists() else None
```

**Loader** (lines 553-577):
```python
def load_honest_fpr_v7(path: Path) -> "pd.DataFrame":
    raw = _safe_load_json(path)
    if raw is None:
        raise RuntimeError(f"Could not load v7 ablation table from {path}")
    rows = []
    for key, entry in raw.items():
        if not isinstance(entry, dict):
            continue
        rows.append({
            "composite_key":        key,
            "model":                entry.get("model", "unknown"),
            "defense_mode":         entry.get("defense_mode", "unknown"),
            "per_chunk_fpr":        entry.get("per_chunk_fpr", 0.0),
            "answer_preserved_fpr": entry.get("answer_preserved_fpr", 0.0),
            "judge_fpr":            entry.get("judge_fpr", 0.0),
            "judge_model":          entry.get("judge_model", "unknown"),
            "judge_n_calls":        entry.get("judge_n_calls", 0),
        })
    return pd.DataFrame(rows)
```

**Emitter** (lines 580-589):
```python
def emit_honest_fpr_gptoss_v7(df: pd.DataFrame, output_dir: Path, fmt: str) -> None:
    df = df.copy()
    df.insert(1, "Defense", df["defense_mode"].map(_display_defense))
    emit_table(df, "honest_fpr_gptoss_v7", output_dir, fmt)
```

**main() integration block** (lines 672-680):
```python
# Phase 7 D-05: emit honest_fpr_gptoss_v7 if v7 ablation file present (no-op otherwise)
v7_path = _resolve_v7_ablation_path(logs_dir)
if v7_path is not None:
    try:
        df_v7 = load_honest_fpr_v7(v7_path)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    emit_honest_fpr_gptoss_v7(df_v7, output_dir, args.format)
```

## DEFENSE_DISPLAY Unchanged Confirmation

`grep -n "DEFENSE_DISPLAY" scripts/make_results.py` shows the dict at lines 61-87 is identical to git HEAD. The plan explicitly does NOT modify this block (CONTEXT line 196 confirms "fused" -> "Fused" and "def02" -> "DEF-02" already present).

Line count: `git diff scripts/make_results.py | grep -E "^\-" | grep -vE "^\-\-\-" | wc -l` = **0** (no lines deleted).

## tests/test_make_results_v7.py Pass/SKIP Table (post-plan)

| P7-ID | Class | Test | Status |
|-------|-------|------|--------|
| P7-RESV | TestV7Resolver | test_returns_path_when_present | PASS |
| P7-RESV | TestV7Resolver | test_returns_none_when_absent | PASS |
| P7-RESV-EMIT | TestV7Emit | test_v7_path_returned_when_present | PASS |
| P7-RESV-EMIT | TestV7Emit | test_v7_no_op_when_absent | PASS |
| P7-RESV-COMPAT | TestV7Compat | test_prior_test_files_exist | PASS |
| P7-DOC-UNTOUCHED | TestPhase5ProseUntouched | test_prose_prefix_unchanged | SKIP (Plan 05) |
| P7-DOC-ADDENDUM | TestAddendumPresent | test_addendum_heading_once | SKIP (Plan 05) |
| P7-DOC-TABLE-10ROW | TestAddendumTable10Rows | test_table_has_ten_data_rows | SKIP (Plan 05) |
| P7-DOC-PHASE3-UNTOUCHED | TestPhase34NotEdited | test_phase3_doc_unchanged | PASS |

**Total: 6 PASS, 3 SKIP** — all 3 SKIP are Plan 05 (addendum doc) responsibilities, correct.

## Phase 5/6 Regression Status

| Suite | Result |
|-------|--------|
| tests/test_make_results.py | 4/4 PASS |
| tests/test_make_results_v6.py | 6/6 PASS |

## Deviations from Plan

None — plan executed exactly as written. The type annotations used quoted strings (`"Path | None"`) instead of bare union syntax to maintain Python 3.9 compatibility (bare `Path | None` requires Python 3.10+), which is a safe stylistic choice consistent with the existing codebase.

## Known Stubs

None. All new functions are fully implemented. The v7 emitter correctly no-ops when the input file is absent (tested), and emits correctly when present (tested).

## Threat Flags

No new network endpoints, auth paths, or schema changes. The only new file-system writes are `docs/results/honest_fpr_gptoss_v7.{md,csv}` (gated by v7 file presence). T-7-02 (tampering of Phase 5/6 outputs) mitigated — regression tests pass, 0 lines deleted from make_results.py. T-7-02b (DEFENSE_DISPLAY drift) mitigated — 0 lines deleted from the DEFENSE_DISPLAY block. T-7-03 (malformed JSON crash) mitigated — `_safe_load_json` + RuntimeError + rc=2 pattern applied.

## Self-Check: PASSED

- [x] `scripts/make_results.py` modified with 65 insertions, 0 deletions
- [x] `_resolve_v7_ablation_path` present (grep count = 2)
- [x] `load_honest_fpr_v7` present (grep count = 2)
- [x] `emit_honest_fpr_gptoss_v7` present (grep count = 2)
- [x] `_V7_ABLATION_FILENAME == 'ablation_table_gptoss_v7.json'` (symbol check passed)
- [x] Commit d1de4c9 exists
- [x] 4/4 Phase 5 tests PASS, 6/6 Phase 6 tests PASS (regression clean)
- [x] 4/4 TestV7Resolver + TestV7Emit tests PASS (flipped from SKIP)
- [x] No docs/results/ files changed (git diff --stat docs/results/ is empty)
- [x] `python scripts/make_results.py` produces no `honest_fpr_gptoss_v7.*` (no-op confirmed)
