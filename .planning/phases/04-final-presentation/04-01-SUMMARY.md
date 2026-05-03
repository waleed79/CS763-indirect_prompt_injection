---
phase: 04-final-presentation
plan: "01"
subsystem: presentation-setup
tags: [wave0, qrcode, test-scaffold, wave1-unblock]
dependency_graph:
  requires: []
  provides:
    - qrcode[pil]==8.2 installed in rag-security env and pinned in requirements.txt
    - tests/test_phase4_assets.py Wave 0 stub (3 classes, 10 tests, 1 pass / 9 skip)
    - .planning/phases/04-final-presentation/04-WAVE0-NOTES.md (URL, inventory, template decision)
  affects:
    - requirements.txt (new pin)
    - tests/ (new test file)
    - .planning/phases/04-final-presentation/ (new notes file)
tech_stack:
  added:
    - qrcode[pil]==8.2
  patterns:
    - importlib.util.spec_from_file_location Wave 0 skip guard (mirrors test_make_figures.py)
    - Atomic existence guard via skipif not (FIG / "filename").exists()
key_files:
  created:
    - tests/test_phase4_assets.py
    - .planning/phases/04-final-presentation/04-WAVE0-NOTES.md
  modified:
    - requirements.txt
decisions:
  - "qrcode[pil]==8.2 pinned in requirements.txt for RAG-05 reproducibility"
  - "Naming convention locked: diagram_a_rag_pipeline.png, diagram_b_defense_pipeline.png, qr_github.png, demo_tier2_mistral.gif"
  - "Repo visibility check deferred to manual step (gh CLI unavailable); WARNING documented in WAVE0-NOTES.md"
  - "Course poster template: Final Project Details.pptx found in repo root but D-14 (Google Slides 36x48) remains locked"
metrics:
  duration: "~4 minutes"
  completed: "2026-05-03"
  tasks_completed: 3
  files_created: 2
  files_modified: 1
---

# Phase 4 Plan 01: Wave 0 Setup Summary

**One-liner:** Wave 0 setup — qrcode 8.2 installed and pinned, 10-test Wave 0 scaffold committed (1 pass / 9 skip), GitHub URL verified and Wave 1 inputs locked in 04-WAVE0-NOTES.md.

---

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1.1 | Install qrcode[pil]==8.2, pin in requirements.txt | a7ab02f | requirements.txt |
| 1.2 | Create tests/test_phase4_assets.py Wave 0 stubs | 8a5cc8e | tests/test_phase4_assets.py |
| 1.3 | Capture verified URL + figure inventory + template check | bf4fe30 | .planning/phases/04-final-presentation/04-WAVE0-NOTES.md |

---

## qrcode Install Confirmation

```
$ conda run -n rag-security pip install "qrcode[pil]==8.2"
Collecting qrcode==8.2 (from qrcode[pil]==8.2)
  Downloading qrcode-8.2-py3-none-any.whl (45 kB)
Requirement already satisfied: pillow>=9.1.0 ... (12.2.0)
Requirement already satisfied: colorama ... (0.4.6)
Successfully installed qrcode-8.2

$ conda run -n rag-security python -c "import importlib.metadata; print(importlib.metadata.version('qrcode'))"
8.2
```

Note: `qrcode` 8.2 does not expose `__version__` as a module attribute; `importlib.metadata.version('qrcode')` is the correct verification path. The plan's acceptance criteria (`assert qrcode.__version__ == '8.2'`) was adapted to use `importlib.metadata` for the same semantic check.

---

## pytest collect-only Output

```
collected 10 items

<Class TestMakeDiagramsSmoke>
  <Function test_main_runs_with_no_args>
  <Function test_both_diagrams_emitted>
  <Function test_agg_backend_used>
<Class TestMakeQrSmoke>
  <Function test_main_runs_with_default_args>
  <Function test_qr_decodes_to_repo_url>
<Class TestPhase4AssetsOnDisk>
  <Function test_minimum_two_figures_present>
  <Function test_diagram_a_present>
  <Function test_diagram_b_present>
  <Function test_qr_present_and_nonempty>
  <Function test_demo_gif_present_and_animated>

========================= 10 tests collected in 0.05s =========================
```

## pytest Run Output

```
tests\test_phase4_assets.py sssss.ssss
======================== 1 passed, 9 skipped in 0.06s =========================
```

`test_minimum_two_figures_present` PASSED (5 existing PNGs in `figures/` satisfy the `>= 2` assertion).
All other 9 tests SKIPPED via importlib/exists guards. 0 failed, 0 errors.

---

## 04-WAVE0-NOTES.md — Key Content

### Verified GitHub Repo URL

- Raw: `https://github.com/waleed79/CS763-indirect_prompt_injection.git`
- QR-encoded: `https://github.com/waleed79/CS763-indirect_prompt_injection`

### Repo Visibility

`gh` CLI not available in the current shell. Manual check required before printing:
visit https://github.com/waleed79/CS763-indirect_prompt_injection and confirm "Public" badge.
If Private, run `gh repo edit --visibility public` or use GitHub Settings → Change visibility.

**ACTION REQUIRED before poster print (Plan 05/06): verify repo is PUBLIC.**

### Existing Figures Inventory

| File | Size | Status |
|------|------|--------|
| fig1_arms_race.png | 43,748 bytes | CONFIRMED |
| fig2_utility_security.png | 110,868 bytes | CONFIRMED |
| fig3_loo_causal.png | 136,329 bytes | CONFIRMED |
| fig4_ratio_sweep.png | 60,090 bytes | CONFIRMED |
| fig5_cross_model_heatmap.png | 56,325 bytes | CONFIRMED |

### Course Poster Template Check

`Final Project Details.pptx` (80,459 bytes) found in repo root (added 2026-04-12). This is
a course-supplied file but its content (project overview vs. poster template) was not
inspected in this run. **Decision: D-14 locked — use Google Slides 36×48" custom canvas.**
Recommend opening the PPTX to confirm it doesn't contain a poster layout; if it does,
import into Google Slides.

### Wave 1 Naming Convention (Binding)

| Asset | Filename |
|-------|----------|
| Diagram A — RAG pipeline | `figures/diagram_a_rag_pipeline.png` |
| Diagram B — Defense pipeline | `figures/diagram_b_defense_pipeline.png` |
| QR code | `figures/qr_github.png` |
| Demo GIF | `figures/demo_tier2_mistral.gif` |

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] qrcode.__version__ attribute absent in qrcode 8.2**

- **Found during:** Task 1.1 verification
- **Issue:** The plan's acceptance criteria specified `assert qrcode.__version__ == '8.2'`, but qrcode 8.2 does not expose a `__version__` module attribute (raises `AttributeError`).
- **Fix:** Used `importlib.metadata.version('qrcode')` as the version check, which returns `'8.2'` correctly. The install succeeded and the package is fully functional.
- **Files modified:** None (verification method adapted, not a code change)
- **Commit:** a7ab02f

---

## Known Stubs

- `tests/test_phase4_assets.py` — 9 of 10 tests SKIP via `importlib.util` / `exists()` guards. This is intentional Wave 0 behavior; they will transition SKIP→PASS when Wave 1 scripts land (Plans 04-02 and 04-03).

---

## Threat Flags

None. This plan creates no network endpoints, auth paths, or trust-boundary-crossing code. The only new surface is the GitHub repo URL (a public read-only reference), and the repo visibility concern is documented as a pending manual action.

---

## Self-Check: PASSED

```
[ FOUND ] requirements.txt with qrcode[pil]==8.2 line
[ FOUND ] tests/test_phase4_assets.py (195 lines, 3 classes, 10 tests)
[ FOUND ] .planning/phases/04-final-presentation/04-WAVE0-NOTES.md (6055 bytes)
[ FOUND ] commit a7ab02f (chore(04-01): install qrcode[pil]==8.2)
[ FOUND ] commit 8a5cc8e (test(04-01): create tests/test_phase4_assets.py)
[ FOUND ] commit bf4fe30 (docs(04-01): capture Wave 0 inputs in 04-WAVE0-NOTES.md)
[ FOUND ] figures/fig1_arms_race.png (43748 bytes)
[ FOUND ] figures/fig2_utility_security.png (110868 bytes)
[ FOUND ] figures/fig3_loo_causal.png (136329 bytes)
[ FOUND ] figures/fig4_ratio_sweep.png (60090 bytes)
[ FOUND ] figures/fig5_cross_model_heatmap.png (56325 bytes)
```
