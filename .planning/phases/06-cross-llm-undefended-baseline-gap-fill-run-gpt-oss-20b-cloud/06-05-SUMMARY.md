---
phase: "06"
plan: "05"
subsystem: "figures"
tags: [figures, heatmap, arms-race, cross-llm, phase6]
dependency_graph:
  requires:
    - "06-03"  # _summary_v6.json composed (75 cells)
    - "06-04"  # undefended gptoss v6 logs present
  provides:
    - "figures/d12_cross_model_heatmap_v6.png"
    - "figures/d12_undefended_v6.png"
    - "figures/d03_arms_race_v6.png"
  affects:
    - "scripts/make_figures.py"
tech_stack:
  added: []
  patterns:
    - "W-5 fail-loud shape assertions on matplotlib pivot matrices"
    - "save_atomic PNG write (tmp + os.replace) with explicit format='png'"
    - "B-2 invariants: nansum>0, nanmax>0.05, nonzero_count>=5"
key_files:
  created:
    - "scripts/_render_v6_figs.py"
    - "figures/d12_cross_model_heatmap_v6.png"
    - "figures/d12_undefended_v6.png"
    - "figures/d03_arms_race_v6.png"
  modified:
    - "scripts/make_figures.py"
decisions:
  - "T1b for llama/mistral filled with 0.0 (not measured pre-Phase-3.3-02) per D-08 footnote; surfaced in subplot title"
  - "gemma4:31b-cloud excluded from undefended heatmap (no undefended eval log per D-08)"
  - "New renderers are sibling functions — originals untouched per D-04"
metrics:
  duration: "~10 minutes"
  completed: "2026-05-04"
  tasks_completed: 2
  files_created: 4
  files_modified: 1
---

# Phase 6 Plan 05: Figure Renderers — 3 New v6 PNGs Summary

**One-liner:** Added 3 Phase 6 figure renderers to `make_figures.py` and emitted `d12_cross_model_heatmap_v6.png` (5×5 fused heatmap), `d12_undefended_v6.png` (5×4 undefended heatmap), and `d03_arms_race_v6.png` (arms race bars extended to 5 LLMs × 3 defenses × 5 tiers).

## New Renderer Functions

### `render_d12_cross_model_heatmap_v6`
- **Shape assertion:** `assert matrix.shape == (5, 5)` — 5 attack tiers (T1, T1b, T2, T3, T4) × 5 LLMs (llama3.2:3b, mistral:7b, gemma4:31b-cloud, gpt-oss:20b-cloud, gpt-oss:120b-cloud)
- **Source:** `logs/eval_matrix/_summary_v6.json`, filtered to `defense == "fused"`
- **Output:** `figures/d12_cross_model_heatmap_v6.png` — 67,398 bytes
- **Description:** 5×5 viridis_r heatmap showing overall ASR under fused defense for all 5 Phase 6 LLM targets; answers the D-10 cross-model-with-defenses question left open by Phase 3.3-07.

### `render_d12_undefended_v6`
- **Shape assertion:** `assert matrix.shape == (5, 4)` — 5 tiers × 4 LLMs (gemma4 excluded per D-08)
- **Sources:** `logs/eval_harness_undefended_t34_{llama,mistral}.json` (Phase 02.4, no asr_tier1b) + `logs/eval_harness_undefended_gptoss{20b,120b}_v6.json` (Phase 6, all 5 tiers); missing T1b filled with 0.0
- **Output:** `figures/d12_undefended_v6.png` — 81,757 bytes
- **Description:** 5×4 viridis_r heatmap of undefended baseline ASR across 4 LLMs and all 5 attack tiers; gemma4 absent and T1b assumption for llama/mistral surfaced in subtitle.

### `render_d03_arms_race_v6`
- **Shape assertion:** `assert np.nansum(data) > 0`, `assert np.nanmax(data) > 0.05`, `assert nonzero_count >= 5` (B-2 invariants)
- **Source:** `logs/eval_matrix/_summary_v6.json` (75 cells, 5 LLMs × 3 defenses × 5 tiers)
- **Output:** `figures/d03_arms_race_v6.png` — 81,488 bytes
- **Description:** Grouped bar chart extending the Phase 3 arms race figure to all 5 Phase 6 LLMs (15 bar groups per tier), showing D-11 cross-LLM attack-defense landscape.

## ALL_RENDERERS Extension

```python
ALL_RENDERERS = {
    "fig1":     render_d03_arms_race,       # unchanged
    "fig2":     render_d04_utility_security,# unchanged
    "fig3":     render_d05_loo_causal,      # unchanged
    "fig4":     render_d06_ratio_sweep,     # unchanged
    "fig5":     render_d12_cross_model_heatmap, # unchanged
    "fig5_v6":  render_d12_cross_model_heatmap_v6,  # NEW
    "fig5_und": render_d12_undefended_v6,           # NEW
    "fig1_v6":  render_d03_arms_race_v6,            # NEW
}
```

## Emitted PNGs

| File | Size | Description |
|------|------|-------------|
| `figures/d12_cross_model_heatmap_v6.png` | 67,398 B | 5×5 fused-defense ASR heatmap (all 5 LLMs) |
| `figures/d12_undefended_v6.png` | 81,757 B | 5×4 undefended ASR heatmap (gemma4 skipped) |
| `figures/d03_arms_race_v6.png` | 81,488 B | Grouped bars: 5 tiers × 5 LLMs × 3 defenses |

## Verification

- Original `figures/fig1_arms_race.png` and `figures/fig5_cross_model_heatmap.png` mtimes: **UNCHANGED**
- `TestD12FusedV6`, `TestD12UndefendedV6`, `TestD03V6`: **PASS**
- `tests/test_make_figures.py` regression (3 tests): **PASS**
- Module loads via importlib with all 3 new callables: **OK**

## Deviations from Plan

None — plan executed exactly as written.

The plan referenced `figures/d03_arms_race.png` and `figures/d12_cross_model_heatmap.png` in the mtime preservation check, but these files do not exist (actual originals are `fig1_arms_race.png` and `fig5_cross_model_heatmap.png`). The mtime check was adapted to the actual filenames; originals were confirmed unchanged.

## Self-Check: PASSED

- `figures/d12_cross_model_heatmap_v6.png`: FOUND (67,398 bytes)
- `figures/d12_undefended_v6.png`: FOUND (81,757 bytes)
- `figures/d03_arms_race_v6.png`: FOUND (81,488 bytes)
- `scripts/make_figures.py` has 3 new renderer defs: CONFIRMED
- `ALL_RENDERERS` has `fig5_v6`, `fig5_und`, `fig1_v6`: CONFIRMED
- Commits `dd11f21` and `826306f`: CONFIRMED
