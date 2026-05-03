# Phase 4: Final Presentation - Research

**Researched:** 2026-05-02
**Domain:** Academic poster + slide deck production (CS 763 course delivery)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 — Opening:** Attack-first hook. Open with the result: "We poisoned a RAG corpus and hijacked an LLM's answer." Show before/after hijacked output within the first minute. Same lead on the poster.
- **D-02 — Arc:** Problem → Solution. All attacks first (5 tiers), then defense (fused), then adaptive attack. Not chronological.
- **D-03 — Punchline:** "Per-chunk detection — even a fine-tuned BERT classifier — is insufficient against adaptive attacks. Multi-signal fusion and chunk-interaction awareness are required."
- **D-04 — Hero slide:** `figures/fig1_arms_race.png` gets a full slide (~90 s). Primary panel on poster.
- **D-05 — Full slide:** DEF-02 counter-productive finding (T1 2%→8%, T2 12%→38% on llama3.2:3b). Honest negative.
- **D-06 — Full slide:** ATK-08 BERT memorization gap — 4.7% mean ASR (3-seed, std 3.3%) against fused defense. Arms race climax.
- **D-07 — One bullet:** T4 cross-chunk 0% ASR (co-retrieval never achieved at top-k=3) → limitations.
- **D-08 — One bullet:** ATK-02 ratio sweep (4%→16% at 0.5%→10%) and EVAL-06 retriever transferability — generalizability one-liner.
- **D-09 — One bullet:** 76% FPR utility cost (`fig2_utility_security.png`) as caveat.
- **D-10 — Limitations only:** LOO ROC AUC 0.372/0.410 (below random) — failed-hypothesis explanation, not a standalone slide.
- **D-11 — Slide budget:** ~12-15 slides, ~1 min each. Outline locked (title / hook / RAG / threat model / 5 tiers / demo GIF / defense / arms race table / DEF-02 / adaptive / cross-model / limitations / conclusion / future + Q&A).
- **D-12 — Demo:** Pre-recorded 30-45 s GIF. Tier-2 instruction smuggling on `mistral:7b` (32% paired ASR). Clean query → clean answer; poisoned query → hijacked output echoing attacker.com URL. No live demo.
- **D-13 — Talk tooling:** Google Slides. Real-time collab Musa+Waleed. Shareable link for submission.
- **D-14 — Poster tooling:** Google Slides, custom 36" × 48" canvas. Export PDF/high-res PNG. QR code → GitHub repo.
- **D-15 — Poster layout:** Standard academic layout — header / problem / system overview (with NEW diagrams) / attacks / defense / results panels / takeaways / limitations / QR.
- **D-16 — Two NEW diagrams (do not exist yet):**
  - **Diagram A (RAG pipeline):** Query → Retriever → [Vector store with poisoned doc highlighted red] → LLM → output.
  - **Diagram B (Defense pipeline):** 4 signals (BERT, perplexity, imperative ratio, retrieval z-score) → meta-classifier → filter → LLM.
  Style: clean vector-style; reusable in talk's defense slide.

### Claude's Discretion

1. Visual style + tooling for the 2 new diagrams (matplotlib vs graphviz vs Google Slides shapes vs Excalidraw).
2. GIF recording toolchain on Windows 11.
3. Whether `gemma4:31b-cloud` 0% finding gets its own talk slide or folds into a cross-model section.
4. QR code generation method.
5. Google Slides 36"×48" custom-size setup details (Page Setup path, recommended font sizes, layout grid).

### Deferred Ideas (OUT OF SCOPE)

- Human stealthiness study (EVAL-07) — already deferred to Future Work in Phase 3.4.
- Minimax `minimax-m2.5:cloud` hard-target test — already Future Work.
- Final Musa/Waleed work split — planner suggests; user assigns later.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRES-01 | 10-12 minute presentation covering problem, approach, results, conclusions | D-11 slide outline + 5 existing PNG figures + arms race narrative locked. All numbers sourced from `docs/phase3_results.md`. |
| PRES-02 | At least 2 plots/visualizations (e.g., ASR bar chart + architecture diagram) | 5 PNGs already exist (`fig1`–`fig5`). Architecture diagrams A+B to be produced (this phase). Easily exceeds the 2-plot minimum. |
| PRES-03 *(optional)* | Live or recorded demo of the attack pipeline | D-12: pre-recorded GIF chosen (Tier-2 on mistral:7b). Tooling research for Windows 11 capture below. |
| PRES-04 | Presentation accessible to fellow students (define RAG and prompt injection clearly) | D-11 outline includes "What is RAG?" slide (slide 3) and "Threat model" slide (slide 4) — both before any attack details. |

</phase_requirements>

## Project Constraints (from CLAUDE.md)

The Phase 4 deliverables themselves don't run code, but any helper scripts (figure regen, QR generation, GIF post-processing) must comply:

- **Python execution:** `conda run -n rag-security python scripts/...` for any script that imports project modules.
- **No LangChain / LlamaIndex:** Custom RAG pipeline only — already in place; demo GIF runs the existing `scripts/run_eval.py`, no new framework dependencies.
- **Reproducible setup:** Any new script (e.g., `scripts/make_diagrams.py`, `scripts/make_qr.py`) follows the established pattern of `scripts/make_figures.py` — module-top Agg backend, deterministic seeds, atomic writes.
- **GSD workflow:** Diagram/poster artifact creation goes through `/gsd:execute-phase`; no direct file edits outside the GSD flow except for ephemeral GIF capture.

## Summary

Phase 4 is a pure-delivery phase: zero new experiments, zero new measurements. Every number cited has already been produced and is in `docs/phase3_results.md`, `logs/ablation_table.json`, `logs/eval_matrix/_summary.json`, and the 5 existing PNGs in `figures/`. Phase 4 work is **artifact composition** — assembling slides, a poster, two new architecture diagrams, a 30-45 s GIF, and a QR code.

The poster ships in 1 day (May 4); the talk has 3-5 days (May 5-7). Research therefore prioritizes **the fastest reproducible path per area** with one robust fallback documented per choice.

**Primary recommendation:** Build diagrams A & B in **matplotlib** (extends `scripts/make_figures.py` pattern, deterministic, scriptable, conda env already set up), generate the QR code with the **`qrcode` Python package** (one `pip install`, 5 lines of code, deterministic PNG), record the GIF with **Windows Game Bar (Win+G) → ffmpeg post-process** (Game Bar already installed on Windows 11, ffmpeg already installed at `C:\Users\muham\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe`, no new tooling), and lay out the poster as a **36"×48" Google Slides custom canvas** (decision D-14 locked). Allocate the gemma4 finding **its own slide** in the talk (slide 11 in D-11 outline already accommodates it) — the 0%-everywhere result is visually stark and supports the cross-architecture generalizability claim cleanly.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Slide deck (talk) | Google Slides (cloud doc) | — | D-13 locked. Real-time collab + shareable link satisfies submission. |
| Poster canvas (36×48") | Google Slides (cloud doc, custom size) | PDF export tier (Adobe Reader / browser) | D-14 locked. PDF export = printable, embeddable. |
| Reused figures (5 PNGs) | `figures/` directory (already on disk) | — | Embedded directly into Slides via Insert → Image → Upload. |
| New diagrams (A: RAG pipeline, B: Defense pipeline) | matplotlib script (`scripts/make_diagrams.py`) | Google Slides shapes (manual fallback) | Scriptable + deterministic + matches `scripts/make_figures.py` pattern. Manual fallback if matplotlib polish proves slow. |
| Demo GIF | Windows Game Bar (capture) → ffmpeg (mp4→gif) | OBS Studio (if Game Bar quality insufficient) | Game Bar pre-installed; no setup time; fastest path. |
| QR code | `qrcode` Python lib (`scripts/make_qr.py`) | qr-code-generator.com (online) | Deterministic, scriptable, offline. Online tool is one-click fallback. |
| Print/export | Google Slides → File → Download → PDF | Google Slides → File → Download → PNG (high-res) | Both supported natively. |

## Standard Stack

### Core (already installed in `rag-security` conda env — verified 2026-05-02)

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| matplotlib | 3.10.9 | Diagram A + Diagram B rendering | [VERIFIED: `conda run -n rag-security python -c "import matplotlib; print(matplotlib.__version__)"`]. Already used by `scripts/make_figures.py`. Native shape/arrow/box support via `matplotlib.patches`. Reproducible PNG output at 300 DPI for poster printing. |
| Pillow (PIL) | 12.2.0 | Image post-processing (crop, resize, composite) | [VERIFIED: `pip index versions pillow` returns 12.2.0 INSTALLED, LATEST]. Already in env. Useful for cropping the GIF, resizing screenshots, or compositing the QR onto the poster if Slides export looks off. |
| Google Slides | (web) | Slide deck + poster canvas | D-13/D-14 locked. Web app, no install. Custom slide dimensions supported via File → Page setup → Custom (max ≈ 200" per side). [CITED: support.google.com/docs/answer/97447] |
| ffmpeg | (winget-installed) | mp4 → gif conversion + GIF optimization | [VERIFIED: `where ffmpeg` returns `C:\Users\muham\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe`]. Standard tool for video→gif conversion with palette optimization (best quality / file-size tradeoff). |
| Windows Game Bar | (built-in Win11) | Screen recording for the demo GIF | Built into Windows 11, no install. `Win+G` opens overlay; records active window only (clean for terminal capture). Output is mp4 → ffmpeg-converted to GIF. |

### Supporting (need install — verified versions on PyPI)

| Library | Version | Purpose | Install Command |
|---------|---------|---------|-----------------|
| qrcode[pil] | 8.2 | QR code PNG generation | [VERIFIED: `pip index versions qrcode` → 8.2 latest, 2026-05-02]. `conda run -n rag-security pip install "qrcode[pil]==8.2"` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| matplotlib for diagrams | graphviz (Python binding) | Graphviz produces cleaner DAGs automatically but requires installing the Graphviz binary system-wide on Windows (extra step), and the visual style is more rigid. Matplotlib gives full control and is already installed. **Use matplotlib.** |
| matplotlib for diagrams | Excalidraw (web app, manual) | Excalidraw produces beautiful hand-drawn-style diagrams but is not scriptable/reproducible. Manual edit cycle. Acceptable as fallback but loses determinism. |
| matplotlib for diagrams | Google Slides shapes (manual) | Native to the poster file. Acceptable but not reusable in the talk's defense slide as a standalone PNG without screenshot kludge. **Use matplotlib + insert PNG into Slides.** |
| qrcode Python lib | qr-code-generator.com or similar online | One-click but introduces a network dependency at build time and produces non-deterministic styling. **Use qrcode lib for reproducibility.** |
| Windows Game Bar | OBS Studio | OBS is more powerful (scene composition, overlays) but requires download + first-time setup. Overkill for a 30-45 s terminal capture. |
| Windows Game Bar | terminalizer / asciinema | Both produce GIF/SVG directly from terminal. Asciinema is Linux/macOS-first; terminalizer requires Node.js install. Either works but Game Bar avoids any install. Asciinema produces text-replay (lighter) but requires a player or conversion to gif. |
| Windows Game Bar | ScreenToGif (Windows) | Free, well-regarded Windows tool that captures directly to GIF. Better than Game Bar for GIFs specifically (no mp4→gif conversion needed). Requires download + install (≈10 min). **Acceptable upgrade if Game Bar quality is poor.** [CITED: screentogif.com] |
| Google Slides for poster | LaTeX (beamerposter / tikzposter) | Industry-standard for academic posters but steep setup, debugging cycle, and fights with custom shapes. **Slides is correct for 1-day deadline.** |
| Google Slides for poster | PowerPoint .pptx | Already exists in repo (`Final Project Details.pptx`) but D-14 locked Google Slides for collaboration. |
| Google Slides for poster | Inkscape (SVG, manual) | Beautiful output, full vector control, but solo-edit only and no real-time collab. |

**Installation:**
```bash
# Only one new package needed
conda run -n rag-security pip install "qrcode[pil]==8.2"
```

**Version verification (2026-05-02):**

```
matplotlib 3.10.9     # already installed, verified
Pillow 12.2.0         # already installed, verified
qrcode 8.2            # PyPI latest, verified via pip index versions
ffmpeg (winget)       # already installed, verified via `where ffmpeg`
Windows Game Bar      # built-in Win11
```

## Architecture Patterns

### System Architecture Diagram (Phase 4 build flow)

```
                              Phase 3 deliverables (DONE — read-only inputs)
   ┌────────────────────────────────────────────────────────────────────────────┐
   │  docs/phase3_results.md   logs/ablation_table.json   logs/eval_matrix/    │
   │  figures/fig1..fig5.png   docs/results/*.md          logs/loo_results_*  │
   └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
   ┌──────────────── PHASE 4 BUILD ─────────────────┐    ┌──── PHASE 4 BUILD ────┐
   │                                                │    │                       │
   │ scripts/make_diagrams.py  (NEW, matplotlib)    │    │ Demo recording        │
   │   ├─ Diagram A: RAG pipeline → diagA.png       │    │   conda run python    │
   │   └─ Diagram B: Defense fusion → diagB.png     │    │     scripts/run_eval  │
   │                                                │    │     --tier tier2      │
   │ scripts/make_qr.py  (NEW, qrcode)              │    │     --model mistral:7b│
   │   └─ GitHub repo URL → qr.png                  │    │   on screen, capture  │
   │                                                │    │   via Win+G → mp4     │
   └────────────────────────────────────────────────┘    │   ffmpeg → demo.gif   │
                          │                              └───────────┬───────────┘
                          │                                          │
                          ▼                                          ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │   Composition layer (Google Slides — manual)                             │
   │                                                                          │
   │   ┌──────────── Talk deck ────────────┐  ┌──────── Poster canvas ──────┐│
   │   │ 12-15 slides, 16:9 standard       │  │ 36"×48" custom Page setup   ││
   │   │ Embed: fig1..fig5, diagA, diagB,  │  │ Embed: same set + qr.png    ││
   │   │        demo.gif (or screenshots)  │  │ Layout: header / problem /  ││
   │   │ Outline: D-11                     │  │ system / attacks / defense /││
   │   │                                   │  │ results / takeaways / Q&A   ││
   │   └───────────────┬───────────────────┘  └───────────────┬─────────────┘│
   │                   │                                      │              │
   │                   ▼                                      ▼              │
   │     File→Download→PDF (talk)             File→Download→PDF (poster)     │
   │     File→Share→link (talk)               File→Download→PNG (poster)     │
   └──────────────────────────────────────────────────────────────────────────┘
                          │                                      │
                          ▼                                      ▼
                Submit talk link                          Submit poster PDF +
                (course form)                             print at university press
```

Component responsibilities:

| Component | File / Tool | Owner |
|-----------|-------------|-------|
| `scripts/make_diagrams.py` | NEW Python script (matplotlib) | This phase |
| `scripts/make_qr.py` | NEW Python script (qrcode) | This phase |
| `figures/diagA_rag_pipeline.png` | NEW asset, output of make_diagrams | This phase |
| `figures/diagB_defense_pipeline.png` | NEW asset, output of make_diagrams | This phase |
| `figures/qr_github.png` | NEW asset, output of make_qr | This phase |
| `figures/demo_tier2_mistral.gif` | NEW asset, manual capture + ffmpeg | This phase |
| Talk deck (Google Slides URL) | Cloud doc | This phase |
| Poster canvas (Google Slides URL) | Cloud doc | This phase |
| `figures/fig1..fig5.png` | EXISTING (Phase 3.4) | Read-only |
| `docs/phase3_results.md` numbers | EXISTING (Phase 3.4) | Read-only |

### Recommended Project Structure

```
.planning/phases/04-final-presentation/
├── 04-CONTEXT.md            (exists)
├── 04-DISCUSSION-LOG.md     (exists)
├── 04-RESEARCH.md           (this file)
├── 04-NN-PLAN.md            (per-plan files, created by planner)
└── 04-NN-SUMMARY.md         (per-plan completion summaries)

scripts/
├── make_figures.py          (existing — 5 PNGs)
├── make_diagrams.py         (NEW — Diagrams A + B)
├── make_qr.py               (NEW — QR code PNG)
└── make_demo_gif.md         (NEW — manual recording recipe doc, since GIF capture is interactive)

figures/
├── fig1_arms_race.png       (existing)
├── fig2_utility_security.png (existing)
├── fig3_loo_causal.png      (existing)
├── fig4_ratio_sweep.png     (existing)
├── fig5_cross_model_heatmap.png (existing)
├── diagA_rag_pipeline.png   (NEW)
├── diagB_defense_pipeline.png (NEW)
├── qr_github.png            (NEW)
└── demo_tier2_mistral.gif   (NEW)

docs/
├── phase3_results.md        (existing — canonical source of truth)
├── poster_text.md           (NEW — narrative blocks for poster panels, optional helper)
└── slides_outline.md        (NEW — speaker notes per slide, optional helper)
```

### Pattern 1: matplotlib diagram script (extends existing `scripts/make_figures.py` style)

**What:** Diagrams A and B are built as matplotlib figures using `matplotlib.patches.FancyBboxPatch` for boxes and `matplotlib.patches.FancyArrowPatch` for arrows. No external graphviz binary required.

**When to use:** Both new diagrams, since they are simple flowchart-style box-and-arrow figures with ≤8 nodes each.

**Example skeleton (Diagram A — RAG pipeline):**

```python
# Source: extends pattern from scripts/make_figures.py (Phase 3.4-03)
import os
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["savefig.dpi"] = 300  # 300 DPI for poster print
plt.rcParams["figure.dpi"]  = 150
plt.rcParams["savefig.bbox"] = "tight"

def box(ax, xy, w, h, text, color="#FFFFFF", edge="black"):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.05",
                                facecolor=color, edgecolor=edge, linewidth=1.5))
    ax.text(xy[0]+w/2, xy[1]+h/2, text, ha="center", va="center", fontsize=11)

def arrow(ax, x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                 arrowstyle="-|>", mutation_scale=18, linewidth=1.4))

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")

box(ax, (0.2, 1.5), 1.6, 1, "User\nQuery")
box(ax, (2.4, 1.5), 1.8, 1, "Embedder\n(MiniLM-L6-v2)")
box(ax, (4.8, 1.5), 2.2, 1, "Vector Store\n(ChromaDB, 1000 docs)",
    color="#FFE5E5")  # tinted to highlight poisoned chunks
box(ax, (7.6, 1.5), 1.6, 1, "LLM\n(llama3.2:3b)")
# Highlight one chunk inside vector store as red
ax.add_patch(FancyBboxPatch((6.6, 1.6), 0.3, 0.3, boxstyle="round,pad=0.02",
                            facecolor="#D62728", edgecolor="black"))
ax.text(7.5, 1.75, "← poisoned chunk", fontsize=8, color="#D62728")

arrow(ax, 1.8, 2.0, 2.4, 2.0)
arrow(ax, 4.2, 2.0, 4.8, 2.0)
arrow(ax, 7.0, 2.0, 7.6, 2.0)

# Save atomically (mirrors make_figures.py pattern)
out = "figures/diagA_rag_pipeline.png"
fig.savefig(out + ".tmp", format="png")
os.replace(out + ".tmp", out)
plt.close(fig)
```

**Anti-Patterns to Avoid**

- **Hand-drawing diagrams in PowerPoint and screenshotting them.** Loses determinism; cannot regenerate if a label changes. Use the script pattern above.
- **Embedding the GIF directly into Google Slides without testing playback.** Google Slides supports animated GIFs via Insert → Image, but very large GIFs (>2 MB) can stall the editor. Compress with `ffmpeg -filter_complex "[0:v]palettegen[p];[0:v][p]paletteuse" -r 10 out.gif` to ≤1 MB.
- **Generating the QR with a vendor's online tool that injects branding.** Use `qrcode` Python lib for clean output.
- **Running the demo live during the talk.** D-12 explicitly chose pre-recorded. Live demos fail.
- **Using `\\` (Markdown) line breaks in slide text.** Google Slides reads them as literal characters.
- **Citing numbers from memory.** Every statistic on the poster/slides MUST trace to `docs/phase3_results.md`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| QR code generation | Custom QR-encoding routine | `qrcode[pil]` 8.2 | QR encoding requires Reed-Solomon error correction + masking — non-trivial, well-solved. |
| Video → GIF conversion | Custom frame-extraction loop | `ffmpeg -filter_complex palettegen/paletteuse` | Quality vs file-size tradeoff is a known recipe; ffmpeg's two-pass palette optimization is the standard. [CITED: ffmpeg.org/ffmpeg-filters.html#palettegen, CITED: trac.ffmpeg.org/wiki/Slideshow] |
| Screen recording on Windows | Custom GDI capture | Win+G (Game Bar) or ScreenToGif | OS-provided + battle-tested. |
| Poster layout grid | LaTeX template hand-port | Google Slides custom 36×48" canvas (D-14) | Course deadline is 1 day. LaTeX setup time > poster time saved. |
| Diagram layout (auto-flow) | Custom DAG layout algorithm | Hand-position in matplotlib (only 4-8 nodes per diagram) | Graphs this small don't need an auto-layout engine. |
| Image conversion (PNG→PDF, GIF compression) | Custom Pillow scripts | `ffmpeg` for video, Google Slides built-in PDF export, Pillow only if absolutely needed | Slides handles export natively. |

**Key insight:** Phase 4 is composition, not implementation. Every "hard problem" (QR encoding, GIF compression, vector graphics) has a one-import solution. Resist the urge to write anything custom beyond the two diagram scripts.

## Runtime State Inventory

> Phase 4 is a delivery phase with NO renames, refactors, or string replacements in code. This section is included only to confirm explicit awareness — there is no runtime state to migrate.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — Phase 4 produces new artifact files only (PNGs, GIF, QR), does not modify or migrate existing data. ChromaDB collections, model checkpoints, log files all read-only. | none |
| Live service config | None — no n8n / Datadog / external service involvement. The demo capture invokes `ollama serve` (already running) but does not change its config. | none |
| OS-registered state | None — no scheduled tasks, no daemons. | none |
| Secrets / env vars | None — no API keys needed. Ollama runs locally; QR code encodes the public GitHub URL. | none |
| Build artifacts / installed packages | One new package (`qrcode[pil]==8.2`) added to `rag-security` env. Update `requirements.txt` to reflect this so reproducibility is preserved per RAG-05. | Add `qrcode[pil]==8.2` to `requirements.txt`. |

## Common Pitfalls

### Pitfall 1: Google Slides custom-size canvas exceeds export limits

**What goes wrong:** A 36"×48" canvas at native resolution exports to a multi-hundred-MB PNG that strains print services or fails to upload.
**Why it happens:** Google Slides exports at 100 PPI by default — at 36×48" that's 3600×4800 pixels (≈17 MP). PDF export is much more compact than PNG.
**How to avoid:** Always export to **PDF** for printing (vector text + embedded raster images). Export PNG only as a backup preview at reduced res. Most academic print services prefer PDF/A.
**Warning signs:** PNG export >50 MB; print preview shows pixelation on text.
[CITED: support.google.com/docs/answer/97447 — custom slide dimensions]

### Pitfall 2: Animated GIF doesn't loop or doesn't play in Google Slides

**What goes wrong:** Demo GIF appears as a static first frame in presentation mode.
**Why it happens:** Google Slides plays GIFs only in Present mode, not Edit mode (this looks broken during composition). Some GIFs encoded with single-pass conversion lose loop metadata.
**How to avoid:** Test in Present mode (not Edit). Encode with `ffmpeg ... -loop 0` to set infinite loop. Verify with `ffprobe demo.gif` that frames > 1.
**Warning signs:** "GIF" file is <50 KB (likely a single frame); Present mode shows no animation.

### Pitfall 3: Number drift between poster, slides, and `docs/phase3_results.md`

**What goes wrong:** Poster says "76% FPR" but slides say "75% FPR" (someone rounded differently); reviewer flags inconsistency.
**Why it happens:** Manual transcription. Two people composing in parallel.
**How to avoid:** Single source of truth = `docs/phase3_results.md`. Every number on poster/slides must be quotable verbatim from there. Reference table:
- ATK-08 adaptive ASR: **4.7% mean (3-seed, std 3.3%)** vs fused.
- DEF-02 counter-productive: **T1 2%→8%, T2 12%→38%** on llama3.2:3b.
- T2 mistral:7b undefended paired ASR: **32%**.
- Fused defense T1/T2/T3 ASR (llama3.2:3b): **0%**.
- LOO ROC AUC: **0.372 (llama)** / **0.410 (mistral)** — both below random.
- FPR fused: **76%** clean queries.
- gemma4:31b-cloud: **0% across all 5 tiers × 3 defenses**.
- Ratio sweep: **4% at 0.5% poisoning → 16% at 10% poisoning** (Tier-1).
[VERIFIED: docs/phase3_results.md — read 2026-05-02]

### Pitfall 4: Poster font sizes too small to read at 4-6 ft

**What goes wrong:** Reviewer can't read body text from poster session viewing distance.
**Why it happens:** Designing on a 13" laptop screen at 100% zoom misleads the eye about absolute physical size.
**How to avoid:** Standard academic poster font sizing for 36×48":
- **Title:** 80-120 pt
- **Authors / affiliation:** 48-60 pt
- **Section headers:** 36-48 pt
- **Body text:** 24-32 pt
- **Caption / fine print:** 18-24 pt
Use a sans-serif font (Arial, Helvetica, Roboto). Test by zooming Google Slides view to ~25% — that approximates 4-6 ft viewing distance. [CITED: posterpresentations.com/free-poster-templates.html — common academic poster sizing guidance, MEDIUM confidence — verify with course's poster instructions if any.]

### Pitfall 5: QR code points to wrong URL (private repo, redirected URL, or pre-rebrand URL)

**What goes wrong:** Reviewer scans QR → 404 or wrong project.
**Why it happens:** GitHub URL changes (rename, transfer to org); printed poster cannot be re-encoded.
**How to avoid:** Verify URL with `git remote get-url origin` immediately before generating QR. Make the repo **public** before printing. Test the QR by scanning with a phone after generation. [VERIFIED: `git remote get-url origin` returns `https://github.com/waleed79/CS763-indirect_prompt_injection.git` (.git suffix can be stripped for the URL the user visits — encode `https://github.com/waleed79/CS763-indirect_prompt_injection`).]

### Pitfall 6: Game Bar refuses to record File Explorer / Desktop / system UI

**What goes wrong:** Win+G overlay says "This doesn't appear to be a game" or refuses to record.
**Why it happens:** Game Bar requires an "active app" window in foreground; it cannot record the desktop, File Explorer, or some system UIs.
**How to avoid:** Open Windows Terminal / PowerShell / Command Prompt as the foreground window before pressing Win+G. The terminal IS recordable. Alternative: ScreenToGif handles desktop+File Explorer correctly. [CITED: support.microsoft.com/windows/record-a-clip-with-xbox-game-bar-7c3e4f6a — Game Bar app limitations]

### Pitfall 7: Diagram visual style clashes between A and B (or with the 5 existing PNGs)

**What goes wrong:** Poster looks like 7 different people made the figures.
**Why it happens:** No shared style guide between scripts.
**How to avoid:** `scripts/make_diagrams.py` should mirror `scripts/make_figures.py` rcParams (already documented in Pattern 1 above): same DPI, same `tableau-colorblind10` palette family, same constrained_layout, same Agg backend. For Diagram A's "poisoned chunk" highlight, use `#D62728` (matplotlib's default red, also used in `tableau-colorblind10`).

## Code Examples

Verified patterns from existing project code and standard library docs:

### QR code generation (Python qrcode lib)

```python
# Source: pypi.org/project/qrcode/  (qrcode==8.2 README)
import qrcode

repo_url = "https://github.com/waleed79/CS763-indirect_prompt_injection"
qr = qrcode.QRCode(
    version=None,                               # auto-size
    error_correction=qrcode.constants.ERROR_CORRECT_M,  # 15% recovery
    box_size=12,                                # pixels per module — 12 → ~ 600 px image
    border=4,                                   # quiet zone modules
)
qr.add_data(repo_url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("figures/qr_github.png")
```

### Demo GIF post-process (mp4 → palette-optimized GIF)

```bash
# Source: trac.ffmpeg.org/wiki/Slideshow + ffmpeg-filters palettegen/paletteuse
# Step 1: capture with Win+G (saves to %USERPROFILE%\Videos\Captures\*.mp4)
# Step 2: trim and convert
INPUT="$USERPROFILE/Videos/Captures/demo.mp4"
PALETTE="figures/_palette.png"
OUT="figures/demo_tier2_mistral.gif"

# Generate optimal palette from the source
ffmpeg -y -i "$INPUT" -vf "fps=10,scale=960:-1:flags=lanczos,palettegen" "$PALETTE"

# Apply palette (smaller file, better colors)
ffmpeg -y -i "$INPUT" -i "$PALETTE" -lavfi "fps=10,scale=960:-1:flags=lanczos [x]; [x][1:v] paletteuse" -loop 0 "$OUT"

rm "$PALETTE"
```

Target: 30-45 s at 10 fps, ≤1 MB final GIF. If file >1 MB, drop to `fps=8` or `scale=720:-1`.

### Demo recording recipe (run before/during capture)

```bash
# In Windows Terminal (foreground), run this single command sequence; record from Win+G start to end of output
conda run -n rag-security python scripts/run_eval.py \
    --model mistral:7b \
    --tier-filter tier2 \
    --collection nq_poisoned_v4 \
    --defense off \
    --max-queries 2 \
    --verbose
```

This produces a clean before/after on Tier-2: clean query → clean answer; poisoned query → hijacked output echoing `attacker.com` URL. Reference: `docs/phase3_results.md` Section 8 reports T2 paired ASR = 32% on mistral:7b, so on 2 paired queries the demo has ≈54% chance of hitting a hijack on the first try; rerun until visually compelling.

### Google Slides custom canvas setup (manual click path, MEDIUM confidence — UI subject to change)

```
1. Open new Google Slides deck
2. File → Page setup
3. Click dropdown → Custom
4. Set unit to "Inches"
5. Width: 48   Height: 36   (landscape)  OR  Width: 36   Height: 48 (portrait)
6. Apply
```

Result: a single slide canvas at the requested dimensions. Subsequent inserted shapes/text/images are positioned in physical inches.

[CITED: support.google.com/docs/answer/97447 "Change the size of your slides"]
[ASSUMED: maximum custom dimension in Google Slides — believed to be ≈228 cm (≈90 in); 48 in is well within range.]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| LaTeX beamerposter | PowerPoint / Google Slides custom canvas | Mid-2010s onward | Faster iteration; collaborators don't need TeX. LaTeX is still industry-standard at ML conferences but the iteration cycle is wrong for a 1-day deadline. |
| Static screenshots in slides | Embedded animated GIFs | 2018+ | GIFs play in Present mode in both Google Slides and PowerPoint; no plugin needed. Better than video for short demo loops. |
| Hand-rendered architecture diagrams | Scripted diagrams (matplotlib, mermaid, graphviz) | 2020+ | Reproducibility — one source-of-truth script regenerates the diagram if a label or arrow changes. Mirrors `scripts/make_figures.py` discipline already in the project. |
| `pyqrcode` Python lib | `qrcode` (segno is also modern) | post-2020 | `pyqrcode` is unmaintained (last release 2016). `qrcode` is actively maintained, last release 2025. [VERIFIED: pip index versions qrcode → 8.2] |

**Deprecated/outdated:**

- **pyqrcode:** unmaintained since 2016. Do not use.
- **Win+R + snippingtool /clip:** old Snipping Tool is being replaced by the new Snip & Sketch / Snipping Tool app on Win11. Either works for screenshots, but for video/GIF use Game Bar.
- **Built-in PowerPoint screen recorder:** works but produces large WMV files. ffmpeg conversion to GIF is more reliable.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Google Slides supports a 36×48" custom canvas without distortion or export issues | Standard Stack / Pitfall 1 | LOW — Slides documents support up to ≈228 cm. If 48" exceeds limit, drop to 24×36" half-poster (acceptable for course). |
| A2 | Animated GIFs play in Google Slides Present mode | Code Examples / Pitfall 2 | LOW — well-documented behavior since 2017. Fallback: embed as MP4 video (Insert → Video). |
| A3 | Recommended poster font sizes (80pt title / 24-32pt body) are the convention for academic 36×48" posters at typical conference viewing distance | Pitfall 4 | MEDIUM — these are common but not standardized. Course may have specific guidance not yet read; planner should confirm if a course poster template exists. |
| A4 | Windows Game Bar can record Windows Terminal cleanly without a foreground-app issue | Pitfall 6 | LOW — verified anecdotally many times in dev workflows. ScreenToGif fallback documented if Game Bar refuses. |
| A5 | The course allows the GitHub repo to be the linked artifact (no separate code-archive submission required) | QR code | LOW — repo + Google Doc are the two named deliverables in CLAUDE.md. Verify if any course submission portal needs a different link. |
| A6 | `mistral:7b` Tier-2 hijacks are visually obvious in terminal output (the LLM literally prints `attacker.com`) | Demo recording | LOW — Phase 2.3/3.1 logs confirm this; the hijack string is the observable output. |
| A7 | The user has access to a printer/print service for a 36×48" poster (e.g., UW-Madison's DoIT print services or similar) | Poster delivery | OUT OF SCOPE for this research — physical printing logistics are user-side. Planner should add a task: "verify print service deadline and submission format". |

If the planner / discuss-phase needs to confirm any of these before execution, A3 and A7 are the highest-leverage to verify (A3 to get the poster looking professional; A7 to ensure the print queue meets the May 4 deadline).

## Open Questions

1. **Does the course have a specific poster template (font, colors, header layout)?**
   - What we know: CS 763 is a UW-Madison course. Many UW departments provide branded poster templates.
   - What's unclear: Whether one exists / is recommended for this class.
   - Recommendation: Planner adds a 5-minute task at the start: ask the user to check Canvas/course materials for a template. If yes, use it; if no, use the standard layout described in this RESEARCH.

2. **Does Phase 4 commit the new artifacts (PNG/GIF) to git?**
   - What we know: Existing figures are committed. `commit_docs` setting from project config not checked here.
   - What's unclear: Whether large GIFs (~1 MB) and the QR PNG should be committed or live only in `figures/` locally.
   - Recommendation: Commit them. They're <2 MB each, and reproducibility (RAG-05) benefits from anyone being able to regenerate the slides without re-running capture.

3. **Single-deck-for-both vs. separate Google Slides files for talk and poster?**
   - What we know: D-13 (talk) and D-14 (poster) both lock Google Slides but say nothing about file count.
   - What's unclear: Whether one deck with two slide sizes (talk slides 16:9, poster slide 36×48) is preferable to two separate files.
   - Recommendation: **Two separate files.** Custom canvas dimensions in Slides apply to all slides in that deck. Mixing 16:9 talk slides with a 36×48" poster slide in one file is not supported.

4. **Demo GIF: how many frames / fps target before quality vs. file-size becomes painful?**
   - What we know: ffmpeg palette-optimized 30-45 s at 10 fps + 960px width usually lands ≤1 MB.
   - What's unclear: Whether Google Slides specifically has a per-image upload limit (mentioned anecdotally as 50 MB; we did not verify).
   - Recommendation: Target ≤1 MB. Documented degradation path: 10 fps → 8 fps → 720 px → trim duration.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 (rag-security env) | Diagram script, QR script | ✓ | conda env active | — |
| matplotlib | Diagram script | ✓ | 3.10.9 | — |
| Pillow | QR (qrcode[pil] dep), GIF post-proc | ✓ | 12.2.0 | — |
| qrcode[pil] | QR PNG generation | ✗ | (PyPI 8.2) | online QR generator (qr-code-generator.com) |
| ffmpeg | mp4 → gif conversion | ✓ | winget-installed at `C:\Users\muham\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe` | ScreenToGif (records directly to gif) |
| Windows Game Bar | Screen recording | ✓ | built-in Win11 | ScreenToGif (download); OBS Studio (download) |
| Ollama server + `mistral:7b` model | Demo recording | ✓ | mistral:7b 4.4 GB pulled (verified `ollama list`) | — |
| ChromaDB collection `nq_poisoned_v4` | Demo recording (Tier-2 query) | ✓ (assumed — Phase 2.4 produced it) | — | regenerate via `scripts/generate_poisoned_corpus.py` if missing |
| Google Slides (browser) | Talk + poster | ✓ | web app | PowerPoint .pptx fallback |
| Internet access | Google Slides, ffmpeg first-run | ✓ | (assumed) | — |
| graphviz | (alternative diagram tool — not chosen) | ✗ | — | matplotlib (chosen) |
| OBS Studio | (alternative recorder — not chosen) | ✗ | — | Game Bar (chosen) |
| ScreenToGif | (alternative recorder — not chosen) | ✗ | — | Game Bar (chosen) |

**Missing dependencies with no fallback:** None — every required input is available or trivially installable.

**Missing dependencies with fallback:**
- `qrcode[pil]` not installed. Single `pip install`. Fallback: online generator (acceptable but loses determinism).

## Validation Architecture

> Skipping per `.planning/config.json` if `workflow.nyquist_validation` is false. Including by default.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing project framework, see pytest.ini) |
| Config file | `pytest.ini` |
| Quick run command | `conda run -n rag-security python -m pytest tests/ -x --quiet` |
| Full suite command | `conda run -n rag-security python -m pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRES-01 | Talk deck covers problem/approach/results/conclusions, fits 10-12 min | manual-only | (human dry-run with timer) | ❌ Wave 0 (manual) — no programmatic test possible |
| PRES-02 | At least 2 visualizations exist | unit | `pytest tests/test_phase4_assets.py::test_minimum_two_figures_present -x` | ❌ Wave 0 |
| PRES-02 | New diagrams A and B render without exception | unit | `pytest tests/test_phase4_assets.py::test_make_diagrams_runs -x` | ❌ Wave 0 |
| PRES-02 | QR code encodes the verified GitHub URL | unit | `pytest tests/test_phase4_assets.py::test_qr_decodes_to_repo_url -x` | ❌ Wave 0 |
| PRES-03 *(opt)* | Demo GIF exists, plays, < 2 MB | unit | `pytest tests/test_phase4_assets.py::test_demo_gif_present_and_animated -x` | ❌ Wave 0 |
| PRES-04 | Slides include "What is RAG?" and "Threat model" content (D-11 outline slides 3-4) | manual-only | (human review of deck against D-11 outline) | ❌ no programmatic test |

Recommended Wave 0 file (`tests/test_phase4_assets.py`) — small, self-contained:

```python
# tests/test_phase4_assets.py
from pathlib import Path

FIG = Path("figures")

def test_minimum_two_figures_present():
    pngs = list(FIG.glob("*.png"))
    assert len(pngs) >= 2, f"PRES-02 requires >=2 visualizations, found {len(pngs)}"

def test_diagram_a_present():
    assert (FIG / "diagA_rag_pipeline.png").exists(), "Diagram A (RAG pipeline) missing"

def test_diagram_b_present():
    assert (FIG / "diagB_defense_pipeline.png").exists(), "Diagram B (defense) missing"

def test_qr_present():
    p = FIG / "qr_github.png"
    assert p.exists() and p.stat().st_size > 0, "QR PNG missing or empty"

def test_qr_decodes_to_repo_url():
    # optional dep: pyzbar; skip if unavailable
    pytest = __import__("pytest")
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
    except ImportError:
        pytest.skip("pyzbar not installed; manual QR scan-test required instead")
    img = Image.open(FIG / "qr_github.png")
    decoded = decode(img)
    assert decoded, "QR did not decode"
    url = decoded[0].data.decode()
    assert "github.com/waleed79/CS763-indirect_prompt_injection" in url, f"QR URL wrong: {url}"

def test_demo_gif_present_and_animated():
    p = FIG / "demo_tier2_mistral.gif"
    assert p.exists(), "Demo GIF missing"
    assert p.stat().st_size > 50_000, "Demo GIF too small (likely a single frame)"
    assert p.stat().st_size < 2_000_000, "Demo GIF too large for slide embedding (>2 MB)"
    from PIL import Image
    img = Image.open(p)
    assert getattr(img, "n_frames", 1) > 1, "GIF has only 1 frame (not animated)"
```

### Sampling Rate

- **Per task commit:** `pytest tests/test_phase4_assets.py -x --quiet`
- **Per wave merge:** `pytest tests/ -x --quiet` (full suite — must remain green; Phase 4 changes should not regress earlier tests)
- **Phase gate:** Full suite green before `/gsd-verify-work` + manual dry-run of talk timing

### Wave 0 Gaps

- [ ] `tests/test_phase4_assets.py` — covers PRES-02 + PRES-03 (the testable parts)
- [ ] Optional: `pip install pyzbar` for QR decode validation (not strictly required; manual scan-test acceptable)
- [ ] Manual checklist file `docs/phase4_dryrun_checklist.md` — covers PRES-01 (timing) and PRES-04 (RAG explanation present)

*(PRES-01 and PRES-04 cannot be programmatically tested — they are quality judgments on slide content. Manual checklist is the substitute.)*

## Security Domain

> Phase 4 is a presentation/poster delivery phase with no code execution surface, no input handling, no auth, no network endpoints. Security domain is largely N/A but verified.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — (no auth in delivered artifacts) |
| V3 Session Management | no | — |
| V4 Access Control | yes — minimal | Make GitHub repo PUBLIC before printing QR (verifies anyone can reach the linked repo) |
| V5 Input Validation | no | — (artifacts are static) |
| V6 Cryptography | no | — (QR error correction is not cryptographic) |

### Known Threat Patterns for {presentation/poster delivery}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Sensitive data leakage in screenshots/GIF (paths exposing usernames, API keys in env) | Information Disclosure | Review GIF before publishing; the demo terminal MUST NOT show `OPENAI_API_KEY`, `OLLAMA_HOST` with auth, or any user-identifying paths. Crop or redact. The chosen demo (Tier-2 on `mistral:7b` local) does not require any keys, so risk is low — but verify. |
| Malicious QR substitution (someone replaces the printed QR with their own) | Tampering | Out of project scope; physical poster security is a print-room concern. |
| Live demo failure on stage | Repudiation/availability of result | D-12 already mitigates by pre-recording. |
| Repo content rewrite after printing | Tampering | Tag a release (`git tag v1.0-presentation`) before printing so the URL/QR can point to a frozen ref if desired (`https://github.com/waleed79/CS763-indirect_prompt_injection/tree/v1.0-presentation`). [Recommended add to plan.] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/04-final-presentation/04-CONTEXT.md` — full set of D-01..D-16 locked decisions (read 2026-05-02).
- `.planning/REQUIREMENTS.md` — PRES-01..PRES-04 definitions and traceability (read 2026-05-02).
- `.planning/STATE.md` — session continuity, prior-phase completion records (read 2026-05-02).
- `.planning/ROADMAP.md` — Phase 4 goal + success criteria (read 2026-05-02).
- `docs/phase3_results.md` — canonical source of truth for every number cited (read 2026-05-02).
- `scripts/make_figures.py` — established project pattern for matplotlib figure generation (read 2026-05-02).
- `git remote get-url origin` — verified GitHub URL `https://github.com/waleed79/CS763-indirect_prompt_injection.git` (verified 2026-05-02).
- `pip index versions qrcode` / `pillow` — verified PyPI versions 8.2 / 12.2.0 (verified 2026-05-02).
- `where ffmpeg` — verified ffmpeg installed at WinGet links path (verified 2026-05-02).
- `ollama list` — verified mistral:7b model present (verified 2026-05-02).

### Secondary (MEDIUM confidence)

- support.google.com/docs/answer/97447 — Google Slides custom Page setup (cited from training; behavior stable since 2018).
- ffmpeg.org/ffmpeg-filters.html#palettegen, trac.ffmpeg.org/wiki/Slideshow — palette-optimized GIF recipe (well-established).
- pypi.org/project/qrcode — qrcode 8.2 README + API (verified package version).
- screentogif.com — fallback recorder.
- support.microsoft.com/windows — Xbox Game Bar capture documentation.

### Tertiary (LOW confidence — flagged in Assumptions Log)

- Academic poster font-size conventions (A3) — common but not strictly standardized; verify against course poster guidance if any.
- Maximum Google Slides custom canvas dimension (A1) — believed ≈228 cm; 48" is well within plausible limits but unverified in this session.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — every package version verified live (matplotlib, Pillow, ffmpeg via shell; qrcode via `pip index versions`).
- Architecture: HIGH — locked by D-13/D-14/D-16 in CONTEXT.md; only freedom is matplotlib-vs-alternatives, where existing project pattern (`scripts/make_figures.py`) is the obvious choice.
- Pitfalls: HIGH for technical pitfalls (GIF embedding, QR encoding, Game Bar foreground-app rule); MEDIUM for design pitfalls (poster font sizes — see A3).
- Security: HIGH for "N/A" categorizations; MEDIUM for the QR-substitution / sensitive-info-in-GIF risks (real but low-probability for this delivery).

**Research date:** 2026-05-02
**Valid until:** 2026-05-09 (one week — Phase 4 is short-lived; matplotlib/qrcode versions, Slides UI all stable on this horizon).

---

*Researched 2026-05-02. Single research pass — Phase 4 is composition not implementation; ready for `/gsd-plan-phase 4`.*
