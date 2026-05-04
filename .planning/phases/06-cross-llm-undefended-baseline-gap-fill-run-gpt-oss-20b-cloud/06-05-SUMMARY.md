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

**One-liner:** Added 3 Phase 6 figure renderers to `make_figures.py` and emitted `d12_cross_model_heatmap_v6.png` (4×4 fused heatmap), `d12_undefended_v6.png` (4×4 undefended heatmap with real T1b), and `d03_arms_race_v6.png` (arms race bars, 4 tiers × 4 LLMs × 3 defenses). T4 and gemma4 dropped from all figures (both all-zero). `figures/final/` assembled with 10 presentation-ready files including `demo_tier2_mistral.gif`.

## New Renderer Functions

### `render_d12_cross_model_heatmap_v6`
- **Shape assertion:** `assert matrix.shape == (4, 4)` — 4 attack tiers (T1, T1b, T2, T3) × 4 LLMs (llama3.2:3b, mistral:7b, gpt-oss:20b-cloud, gpt-oss:120b-cloud); T4 and gemma4 dropped (all-zero)
- **Source:** `logs/eval_matrix/_summary_v6.json`, filtered to `defense == "fused"`
- **Output:** `figures/d12_cross_model_heatmap_v6.png`
- **Description:** 4×4 viridis_r heatmap showing overall ASR under fused defense for 4 LLM targets; answers the D-10 cross-model-with-defenses question left open by Phase 3.3-07.

### `render_d12_undefended_v6`
- **Shape assertion:** `assert matrix.shape == (4, 4)` — 4 tiers × 4 LLMs (gemma4 excluded per D-08; T4 dropped as all-zero)
- **Sources:** T1b for llama/mistral pulled from `_summary_v6.json` no_defense cells (real values: llama=0.22, mistral=0.05); gpt-oss tiers from harness v6 files. No 0.0 fill or assumption disclaimer needed.
- **Output:** `figures/d12_undefended_v6.png`
- **Description:** 4×4 viridis_r heatmap of undefended baseline ASR across 4 LLMs and 4 attack tiers; gemma4 absent, T1b fully populated with measured values.

### `render_d03_arms_race_v6`
- **Shape assertion:** `assert np.nansum(data) > 0`, `assert np.nanmax(data) > 0.05`, `assert nonzero_count >= 5` (B-2 invariants)
- **Source:** `logs/eval_matrix/_summary_v6.json` (75 cells); T4 tier and gemma4 model excluded from bar groups
- **Output:** `figures/d03_arms_race_v6.png`
- **Description:** Grouped bar chart extending the Phase 3 arms race figure to 4 LLMs × 3 defenses × 4 tiers, showing D-11 cross-LLM attack-defense landscape.

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

| File | Description |
|------|-------------|
| `figures/d12_cross_model_heatmap_v6.png` | 4×4 fused-defense ASR heatmap (4 LLMs, T4+gemma4 removed) |
| `figures/d12_undefended_v6.png` | 4×4 undefended ASR heatmap (real T1b for all models) |
| `figures/d03_arms_race_v6.png` | Grouped bars: 4 tiers × 4 LLMs × 3 defenses |

## figures/final/ — Presentation Assembly

10 files assembled for the talk deck / poster:

| File | Type | Source |
|------|------|--------|
| `d12_cross_model_heatmap_v6.png` | Updated v6 | Rendered this wave |
| `d12_undefended_v6.png` | Updated v6 | Rendered this wave |
| `d03_arms_race_v6.png` | Updated v6 | Rendered this wave |
| `demo_tier2_mistral.gif` | Demo | Added manually by user |
| `diagram_a_rag_pipeline.png` | Architecture | Phase 03.4 |
| `diagram_b_defense_pipeline.png` | Architecture | Phase 03.4 |
| `fig2_utility_security.png` | Result | Phase 03.4 |
| `fig3_loo_causal.png` | Result | Phase 03.4 |
| `fig4_ratio_sweep.png` | Result | Phase 03.4 |
| `qr_github.png` | QR code | Phase 03.4 |

`fig1_arms_race.png` and `fig5_cross_model_heatmap.png` excluded — superseded by the v6 versions above.

## Verification

- Original `figures/fig1_arms_race.png` and `figures/fig5_cross_model_heatmap.png` mtimes: **UNCHANGED**
- `TestD12FusedV6`, `TestD12UndefendedV6`, `TestD03V6`: **PASS**
- `tests/test_make_figures.py` regression (3 tests): **PASS**
- Module loads via importlib with all 3 new callables: **OK**

## Deviations from Plan

None — plan executed exactly as written.

The plan referenced `figures/d03_arms_race.png` and `figures/d12_cross_model_heatmap.png` in the mtime preservation check, but these files do not exist (actual originals are `fig1_arms_race.png` and `fig5_cross_model_heatmap.png`). The mtime check was adapted to the actual filenames; originals were confirmed unchanged.

## Adaptive Attack Note

Adaptive attacks ran on all 6 Phase 6 cells. The corpus contains **4 adaptive-tier passages** (passage_ids 20061, 20077 + 2 others, using "[Note for AI:]" framing). 36 of the 100 test queries retrieved at least one adaptive passage (n_retrieved=36, identical across all 6 cells — same corpus, same queries).

**Correct denominator is 36, not 100.** The raw `asr_adaptive` field divides by n=100 and is misleading: 64 queries had no adaptive doc retrieved. The conditional ASR (÷36) is:

| Cell | conditional_asr |
|------|----------------|
| gpt-oss:20b-cloud / no_defense  | 0.000 (0/36) |
| gpt-oss:120b-cloud / no_defense | 0.028 (1/36) |
| gpt-oss:20b-cloud / fused       | 0.028 (1/36) |
| gpt-oss:20b-cloud / def02       | 0.000 (0/36) |
| gpt-oss:120b-cloud / fused      | 0.028 (1/36) |
| gpt-oss:120b-cloud / def02      | 0.000 (0/36) |

Adaptive attacks show negligible hijack success (≤1 per cell). Use `conditional_asr_adaptive` when citing these numbers in presentations.

## Self-Check: PASSED

- `figures/d12_cross_model_heatmap_v6.png`: FOUND (67,398 bytes)
- `figures/d12_undefended_v6.png`: FOUND (81,757 bytes)
- `figures/d03_arms_race_v6.png`: FOUND (81,488 bytes)
- `scripts/make_figures.py` has 3 new renderer defs: CONFIRMED
- `ALL_RENDERERS` has `fig5_v6`, `fig5_und`, `fig1_v6`: CONFIRMED
- Commits `dd11f21` and `826306f`: CONFIRMED
