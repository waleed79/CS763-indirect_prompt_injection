---
phase: 04-final-presentation
plan: "04"
subsystem: presentation-assets
tags: [wave1, demo-gif, recording, tier2, mistral, attack-demo]
dependency_graph:
  requires:
    - rag/pipeline.py + run_eval.py (from Phase 2-3 — provides the RAG pipeline and eval CLI)
    - data/nq_poisoned_v4 ChromaDB collection (Phase 2.4 — Tier-2 poisoned corpus)
    - Ollama running mistral:7b (Phase 2.2 — confirmed Tier-2 target, 32% paired ASR)
    - tests/test_phase4_assets.py Wave 0 stubs (Plan 04-01)
  provides:
    - scripts/make_demo_gif.md (reproducible 6-section Win+G + ffmpeg recording recipe)
    - scripts/run_demo.py (clean demo entrypoint for screen-capture runs)
    - data/demo_queries.json (2-query clean+poisoned demo sequence)
    - figures/demo_tier2_mistral.gif (animated GIF: clean answer → attacker.com hijack)
  affects:
    - tests/test_phase4_assets.py (TestPhase4AssetsOnDisk::test_demo_gif_present_and_animated: SKIP -> PASS)
tech_stack:
  added:
    - Win+G Game Bar screen capture (Windows 11 built-in)
    - ffmpeg palette-optimized GIF conversion (palettegen + paletteuse two-pass)
  patterns:
    - Two-pass ffmpeg GIF encoding (generate palette then apply) for optimal file size
    - run_demo.py as a clean demo entrypoint separate from run_eval.py
    - data/demo_queries.json as a versioned query fixture for reproducible screen-capture runs
key_files:
  created:
    - scripts/make_demo_gif.md
    - scripts/run_demo.py
    - data/demo_queries.json
    - figures/demo_tier2_mistral.gif
  modified: []
decisions:
  - "scripts/run_demo.py created as a dedicated demo entrypoint — cleaner terminal output for screen capture than run_eval.py with its eval scaffolding; run_demo.py prints each query and response directly"
  - "make_demo_gif.md recording command updated to remove non-existent --max-queries/--verbose flags from run_eval.py; data/demo_queries.json added to supply the 2 demo queries"
  - "Query confirmed as 'What is the speed of light?' — this specific query triggers Tier-2 [Note for AI:] injection retrieval from nq_poisoned_v4 with attacker.com echo on mistral:7b"
  - "GIF captured at 960x516, 10fps, -loop 0 (infinite), palette-optimized — 271 KB, 374 frames, ~37 seconds"
metrics:
  duration: "~1 hour (recipe authoring + multiple recording attempts + post-processing)"
  completed: "2026-05-02"
  tasks_completed: 2
  files_created: 4
  files_modified: 1
---

# Phase 4 Plan 04: Demo GIF Recording Summary

**One-liner:** Palette-optimized animated GIF (271 KB, 374 frames, 37s, 960x516, 10fps) captures Tier-2 instruction-smuggling hijack on mistral:7b — "What is the speed of light?" query triggers attacker.com echo; pytest TestPhase4AssetsOnDisk::test_demo_gif_present_and_animated transitions SKIP -> PASS.

---

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 4.1 | Author scripts/make_demo_gif.md — reproducible Win+G + ffmpeg recipe | f9b9131 | scripts/make_demo_gif.md (219 lines) |
| 4.1 (fix) | Correct recording command — remove non-existent flags, add demo_queries.json | bad84ae | scripts/make_demo_gif.md (updated), data/demo_queries.json |
| 4.1 (add) | Add scripts/run_demo.py — clean demo entrypoint for screen-capture | 95090c8 | scripts/run_demo.py (58 lines) |
| 4.1 (fix) | Update demo query to confirmed Tier-2 hijack trigger | 568c678 | scripts/run_demo.py |
| 4.2 | Record + post-process demo GIF; GIF approved by user | 15f806a | figures/demo_tier2_mistral.gif |

---

## scripts/make_demo_gif.md

- **Path:** `scripts/make_demo_gif.md`
- **Line count:** 219 lines, ~9.7 KB
- **Sections:** 6 numbered headings (## 1. Goal through ## 6. Verify)
- **Coverage:** Prerequisites, exact recording command, Win+G capture procedure (4-step), two-pass ffmpeg palette-optimized GIF conversion, pytest verification step, sensitive-content checklist

## scripts/run_demo.py

- **Path:** `scripts/run_demo.py`
- **Line count:** 58 lines, 1.4 KB
- **Purpose:** Dedicated demo entrypoint — reads `data/demo_queries.json`, runs each query through the RAG pipeline (with defense off), and prints formatted Q+A output for clean screen-capture. Avoids run_eval.py's eval scaffolding noise in the terminal window.

## data/demo_queries.json

- **Path:** `data/demo_queries.json`
- **Size:** 295 bytes, 13 lines
- **Contents:** 2-query fixture — one clean query and one Tier-2 poisoned query ("What is the speed of light?") that triggers [Note for AI:] injection retrieval from nq_poisoned_v4

## figures/demo_tier2_mistral.gif

- **Path:** `figures/demo_tier2_mistral.gif`
- **File size:** 277,890 bytes (271 KB) — within 50 KB–2 MB acceptance window
- **Dimensions:** 960 x 516 pixels
- **Frame count:** 374 frames
- **Duration:** ~37 seconds at 10fps
- **Loop:** infinite (-loop 0)
- **Encoding:** palette-optimized (two-pass ffmpeg: palettegen + paletteuse, lanczos scale)
- **Visual content confirmed:**
  - Clean query: produces a clean factual answer (no injection)
  - Poisoned query ("What is the speed of light?"): output echoes `attacker.com` — Tier-2 instruction smuggling hijack on mistral:7b confirmed
  - GIF loops continuously
  - No sensitive content visible (no API keys, no private paths beyond project repo)

---

## pytest Results

```
tests/test_phase4_assets.py::TestPhase4AssetsOnDisk::test_demo_gif_present_and_animated  PASSED
```

TestPhase4AssetsOnDisk::test_demo_gif_present_and_animated transitioned SKIP -> PASS.

Test checks: file exists, 50_000 < size < 2_000_000 bytes, PIL Image.open(...).n_frames > 1.
All three conditions satisfied: 277,890 bytes, 374 frames.

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Recording command used non-existent run_eval.py flags**

- **Found during:** Task 4.1 execution / user testing the recipe
- **Issue:** `make_demo_gif.md` Section 3 recording command included `--max-queries 2` and `--verbose` flags that do not exist in `run_eval.py`. Running the command as written would fail with an unrecognized argument error.
- **Fix:** Removed both non-existent flags from `make_demo_gif.md`. Added `data/demo_queries.json` (2-entry query fixture) as a versioned fixture to control which queries are demonstrated. Updated the recording command to use `run_demo.py` instead.
- **Files modified:** `scripts/make_demo_gif.md`, `data/demo_queries.json` (new)
- **Commit:** bad84ae

**2. [Rule 2 - Missing functionality] run_eval.py unsuitable as demo entrypoint**

- **Found during:** Task 4.1 execution — run_eval.py outputs eval scaffolding (timing, ASR aggregates, file paths) that clutters the terminal window during recording
- **Fix:** Created `scripts/run_demo.py` as a dedicated, clean demo entrypoint. Reads `data/demo_queries.json`, runs each query, prints formatted output only. Terminal output is clean and presentation-appropriate.
- **Files modified:** `scripts/run_demo.py` (new)
- **Commit:** 95090c8

**3. [Rule 1 - Bug] Initial demo query did not trigger Tier-2 hijack reliably**

- **Found during:** Task 4.2 — first recording attempts did not produce attacker.com in the response
- **Issue:** Query needed to be one that reliably retrieves a Tier-2 poisoned chunk from nq_poisoned_v4. Initial query was not confirmed to map to a Tier-2 document at index time.
- **Fix:** Updated `run_demo.py` demo query to "What is the speed of light?" — confirmed to trigger Tier-2 injection retrieval with attacker.com echo on mistral:7b.
- **Files modified:** `scripts/run_demo.py`
- **Commit:** 568c678

---

## Known Stubs

None. `figures/demo_tier2_mistral.gif` is a real screen recording of the Tier-2 hijack, not a placeholder. The attacker.com payload is visible in the actual mistral:7b output.

---

## Threat Flags

None. This plan creates static assets (Markdown recipe, Python script, JSON fixture, GIF image). No network endpoints, auth paths, or trust-boundary-crossing code introduced. The GIF contains no API keys or sensitive credentials (visually confirmed during recording review).

---

## Self-Check: PASSED

```
[ FOUND ] scripts/make_demo_gif.md (219 lines, 9760 bytes)
[ FOUND ] scripts/run_demo.py (58 lines, 1441 bytes)
[ FOUND ] data/demo_queries.json (13 lines, 295 bytes)
[ FOUND ] figures/demo_tier2_mistral.gif (277890 bytes, 374 frames, 960x516)
[ FOUND ] commit f9b9131 (docs(04-04): add Win+G+ffmpeg recording recipe for demo GIF)
[ FOUND ] commit bad84ae (fix(04-04): correct recording command — remove non-existent flags, add demo_queries.json)
[ FOUND ] commit 95090c8 (feat(04-04): add scripts/run_demo.py — prints Q+A for presentation GIF recording)
[ FOUND ] commit 568c678 (fix(04-04): update demo query to confirmed Tier-2 hijack (speed of light -> attacker.com))
[ FOUND ] commit 15f806a (feat(04-04): add demo GIF — Tier-2 mistral:7b hijack (attacker.com))
[ VERIFIED ] GIF file size 277890 bytes — within 50000..2000000 bytes window
[ VERIFIED ] GIF n_frames = 374 > 1
[ VERIFIED ] GIF dimensions 960x516 (matches recipe scale=960:-1)
[ VERIFIED ] make_demo_gif.md contains: mistral:7b, attacker.com, tier-filter tier2, defense off, loop 0, palettegen, paletteuse, nq_poisoned_v4
[ PASSED  ] TestPhase4AssetsOnDisk::test_demo_gif_present_and_animated
```
