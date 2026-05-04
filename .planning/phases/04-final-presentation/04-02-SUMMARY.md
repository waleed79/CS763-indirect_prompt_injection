---
phase: 04-final-presentation
plan: "02"
subsystem: presentation-diagrams
tags: [wave1, diagrams, matplotlib, architecture, poster, talk]
dependency_graph:
  requires:
    - scripts/make_figures.py (Pattern 1 setup, save_atomic, ALL_RENDERERS — mirrored verbatim)
    - tests/test_phase4_assets.py Wave 0 stubs (TestMakeDiagramsSmoke — 3 tests SKIP -> PASS)
    - .planning/phases/04-final-presentation/04-CONTEXT.md (D-16 diagram specs)
  provides:
    - scripts/make_diagrams.py (Phase 4 architecture-diagram generator, Diagrams A + B)
    - figures/diagram_a_rag_pipeline.png (RAG pipeline attack-surface diagram, 300 DPI)
    - figures/diagram_b_defense_pipeline.png (4-signal defense pipeline diagram, 300 DPI)
  affects:
    - tests/test_phase4_assets.py (TestMakeDiagramsSmoke: 3 SKIP -> PASS; test_diagram_a/b_present: SKIP -> PASS)
tech_stack:
  added: []
  patterns:
    - Pattern 1 matplotlib setup (Agg backend at module top, dpi=300 for poster, constrained_layout, tableau-colorblind10)
    - save_atomic helper (write to .tmp + os.replace — atomic write idiom from make_figures.py)
    - ALL_RENDERERS dict + main(argv)->int CLI scaffold (mirrors make_figures.py:467-513)
    - FancyBboxPatch + FancyArrowPatch box/arrow primitives (from RESEARCH Pattern 1)
key_files:
  created:
    - scripts/make_diagrams.py (238 lines)
    - figures/diagram_a_rag_pipeline.png (140,639 bytes, 300 DPI)
    - figures/diagram_b_defense_pipeline.png (293,150 bytes, 300 DPI)
  modified: []
decisions:
  - "Signal boxes in Diagram B widened from w=2.0 to w=2.3 after first render to prevent text truncation on 'vs models/signal4_baseline.json' label — simplified to 'vs signal4_baseline.json' for legibility"
  - "Arrow x-coordinate for signal-to-metaclassifier arrows updated from 2.3 to 2.5 to match widened signal boxes"
  - "No new pip dependencies — matplotlib 3.10.9 and FancyBboxPatch/FancyArrowPatch already in rag-security env"
metrics:
  duration: "~8 minutes"
  completed: "2026-05-03"
  tasks_completed: 1
  files_created: 3
  files_modified: 0
---

# Phase 4 Plan 02: Architecture Diagrams (make_diagrams.py) Summary

**One-liner:** Deterministic matplotlib generator for two 300-DPI architecture diagrams — Diagram A (RAG attack surface with #D62728 poisoned-chunk highlight) and Diagram B (4-signal fused defense pipeline with LR meta-classifier), mirroring the make_figures.py Pattern 1 scaffold exactly.

---

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 2.1 | Implement scripts/make_diagrams.py + emit Diagrams A and B | daedc1e | scripts/make_diagrams.py, figures/diagram_a_rag_pipeline.png, figures/diagram_b_defense_pipeline.png |

---

## scripts/make_diagrams.py — Line Count and Exports

- **Path:** `scripts/make_diagrams.py`
- **Lines:** 238 (exceeds min_lines=200 requirement)
- **Exports:** `main`, `render_diagram_a_rag_pipeline`, `render_diagram_b_defense_pipeline`, `ALL_RENDERERS`
- **Pattern compliance:**
  - `MPLBACKEND=Agg` at module top: YES (1 occurrence, per grep check)
  - `save_atomic` defined + called: YES (4 occurrences — defined once, called once per renderer = 3 total)
  - `ALL_RENDERERS` dict defined + read: YES (4 occurrences)
  - `#D62728` poisoned-chunk highlight: YES (5 occurrences — inner box facecolor, edge color, text color, comment)
  - `all-MiniLM-L6-v2` embedder name: YES (1 occurrence)
  - `mistral:7b` LLM name: YES (1 occurrence, matches D-12 demo target)
  - `BERT classifier|DistilBERT` (Signal 1): YES (1 occurrence)
  - `Logistic Regression` (meta-classifier): YES (2 occurrences — box text + docstring)

---

## PNG Artifacts

| File | Size (bytes) | DPI | Status |
|------|-------------|-----|--------|
| `figures/diagram_a_rag_pipeline.png` | 140,639 | 300 | CONFIRMED (>5120 bytes) |
| `figures/diagram_b_defense_pipeline.png` | 293,150 | 300 | CONFIRMED (>5120 bytes) |

No `.tmp` files left behind (atomic write verified). Re-running is idempotent (verified 2x).

---

## pytest Output — TestMakeDiagramsSmoke

```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\muham\...\CS763-indirect_prompt_injection
configfile: pytest.ini
collected 3 items

tests\test_phase4_assets.py ...                                          [100%]

============================== 3 passed in 1.80s ==============================
```

**3 PASSED, 0 FAILED, 0 SKIPPED** — TestMakeDiagramsSmoke fully transitioned from SKIP to PASS.

Also verified:
- `test_diagram_a_present`: PASS
- `test_diagram_b_present`: PASS
- `test_minimum_two_figures_present`: PASS (7 PNGs in figures/ now)

---

## Visual Adjustments After First Render

One round of visual iteration after the initial render:

1. **Signal boxes in Diagram B widened (w=2.0 → w=2.3):** The initial render showed text wrapping awkwardly in Signal 4 ("vs models/signal4_baseline.json" was truncated). Widened the boxes and simplified the label to "vs signal4_baseline.json" (path still unambiguous; the full key is only relevant in code).

2. **Arrow x-coordinate updated (2.3 → 2.5):** Arrow origins updated to match the widened right edges of the signal boxes.

3. **No changes to Diagram A** — first render was clean: all 5 boxes, 4 arrows, red poisoned-chunk highlight, and italic payload caption all rendered legibly.

---

## Naming Convention

| Asset | Filename | Status |
|-------|----------|--------|
| Diagram A — RAG pipeline | `figures/diagram_a_rag_pipeline.png` | APPLIED |
| Diagram B — Defense fusion pipeline | `figures/diagram_b_defense_pipeline.png` | APPLIED |

Names match the binding convention from `04-WAVE0-NOTES.md` and `tests/test_phase4_assets.py`. Stale draft names (`diagA_*`, `diagB_*`) from PATTERNS.md were NOT used.

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Signal box text truncation in Diagram B first render**

- **Found during:** Task 2.1 visual inspection step
- **Issue:** Signal box width of 2.0 caused "vs models/signal4_baseline.json" to overflow the box boundary at fontsize=11. Text was readable but wrapped awkwardly.
- **Fix:** Widened signal boxes to w=2.3 and simplified Signal 4 label to "vs signal4_baseline.json" (path is still unambiguous for the diagram context). Updated arrow x-coordinates from 2.3 → 2.5 to track the new right edge.
- **Files modified:** scripts/make_diagrams.py
- **Commit:** daedc1e (included in same task commit — adjustment made before the commit)

---

## Known Stubs

None. Both diagram functions are fully implemented and render real content. No placeholder data.

---

## Threat Flags

None. This plan creates no network endpoints, auth paths, file access patterns outside the figures/ directory, or schema changes. The only new surface is two PNG files (static, offline-generated, no executable content).

---

## Self-Check: PASSED

```
[ FOUND ] scripts/make_diagrams.py (238 lines)
[ FOUND ] figures/diagram_a_rag_pipeline.png (140,639 bytes > 5120)
[ FOUND ] figures/diagram_b_defense_pipeline.png (293,150 bytes > 5120)
[ FOUND ] commit daedc1e (feat(04-02): implement scripts/make_diagrams.py + emit Diagrams A and B)
[ FOUND ] grep -c "MPLBACKEND.*Agg" scripts/make_diagrams.py == 1
[ FOUND ] grep -c "save_atomic" scripts/make_diagrams.py == 4 (>= 3)
[ FOUND ] grep -c "ALL_RENDERERS" scripts/make_diagrams.py == 4 (>= 2)
[ FOUND ] grep -c "#D62728" scripts/make_diagrams.py == 5 (>= 1)
[ FOUND ] grep -c "all-MiniLM-L6-v2" scripts/make_diagrams.py == 1
[ FOUND ] grep -c "mistral:7b" scripts/make_diagrams.py == 1
[ FOUND ] grep -c "BERT classifier\|DistilBERT" scripts/make_diagrams.py == 1
[ FOUND ] grep -c "Logistic Regression" scripts/make_diagrams.py == 2
[ FOUND ] TestMakeDiagramsSmoke: 3 PASSED, 0 FAILED, 0 SKIPPED
[ FOUND ] test_diagram_a_present: PASSED
[ FOUND ] test_diagram_b_present: PASSED
[ FOUND ] No .tmp files in figures/
[ FOUND ] Idempotent re-run: both runs exit 0, PNGs overwritten cleanly
```
