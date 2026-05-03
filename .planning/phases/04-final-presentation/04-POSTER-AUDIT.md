---
phase: 04-final-presentation
artifact: poster
canvas_size: "48x36 inches landscape (pptxgenjs custom layout)"
status: COMPOSED
deadline: 2026-05-04
composed_date: 2026-05-03
delivery_format: poster_cs763.pptx (upload to Google Slides per D-14)
---

# Phase 4 Poster Audit Record

## Google Slides URL

**Pending user upload.** The poster was composed as `poster_cs763.pptx` (pptxgenjs, 48"×36" custom layout) because direct Google Workspace access was not available in this session. The user should:

1. Open Google Slides → New blank presentation
2. File → Page Setup → Custom → Inches → Width **48**, Height **36** → Apply
3. Insert → Image → Upload from computer → select each figure from `figures/`
   (The .pptx can also be uploaded directly to Google Slides via: File → Open → Upload)
4. Copy the Slides share URL here once composed.

**Google Slides URL:** _(to be filled after upload)_

## Exported PPTX / PDF

- **File:** `poster_cs763.pptx`
- **Canvas:** 48" × 36" landscape (pptxgenjs `defineLayout`)
- **Generator script:** `scripts/make_poster.js` (Node.js, pptxgenjs 4.0.1)
- **PDF export:** Open in PowerPoint → File → Save As → PDF (or Google Slides → File → Download → PDF)

## Per-Section Sign-Off

Per CONTEXT D-15 — 9-section structure. All sections present in `poster_cs763.pptx`:

- [x] §1 Header — Title "Indirect Prompt Injection in RAG Systems", Muhammad Musa · Waleed, CS 763: Computer Security Spring 2026, University of Wisconsin–Madison. Hook question in italic: "Can a poisoned document in a RAG corpus silently hijack an LLM's answer?"
- [x] §2 Problem & Motivation — 3-paragraph block: RAG attack surface intro, Corpus Poisoning definition (red bold), study scope (5 tiers × 3 defenses × 3 LLMs). Source: `docs/phase3_results.md` §1.
- [x] §3 System Overview — `figures/diagram_a_rag_pipeline.png` (RAG Attack Surface) + `figures/diagram_b_defense_pipeline.png` (Multi-Signal Fused Defense — Per-Chunk Injection Detection). Both at full column width, section headers "RAG PIPELINE & ATTACK SURFACE" and "DEFENSE: 4-SIGNAL FUSION PIPELINE".
- [x] §4 Attack Taxonomy — 5 colored tier boxes: T1 (Naive Injection), T1b (Homoglyph Obfuscation), T2 (Instruction Smuggling), T3 (LLM-Authored Injection), ATK-08 (Adaptive Attack / BERT Gap). Each box has title + description + ASR numbers.
- [x] §5 Defense — 4-signal grid (DistilBERT Classifier, GPT-2 Perplexity, Imperative Ratio, Retrieval Z-Score) + Logistic Regression Meta-Classifier arrow + Result line "0% / 0% / 0%" in green + DEF-02 negative result in red. Section header "DEFENSE: MULTI-SIGNAL FUSION".
- [x] §6 Results Panels — `figures/fig1_arms_race.png` (Hero figure, Arms Race Results, section "ARMS RACE RESULTS (HERO FIGURE)") + `figures/fig5_cross_model_heatmap.png` (Cross-Model, section "CROSS-MODEL: GEMMA4 IMMUNE TO ALL ATTACKS"). Both with caption text including key numbers.
- [x] §7 Key Findings — 5 bullet points: corpus poisoning (32% ASR), fused defense (0% T1/T2/T3), per-chunk insufficient (ATK-08 4.7%), prompt hardening counter-productive (2%→8% / 12%→38%), poisoning ratio (4%→16%). Section header "KEY FINDINGS".
- [x] §8 Limitations & Future Work — 5 bullets: T4 0% (co-retrieval limit), LOO AUC 0.37/0.41 (below chance), 76% FPR utility cost, single-seed caveat, future work (human stealthiness, minimax, chunk-interaction defense). Section header "LIMITATIONS & FUTURE WORK".
- [x] §9 QR Code — `figures/qr_github.png` at 4.8"×4.8", URL label "github.com/waleed79/CS763-indirect_prompt_injection". Section header "GITHUB REPO".

## Embedded Assets Inventory

All images embedded via `slide.addImage({ path: ... })` in `scripts/make_poster.js`:

| Asset | Source | Section |
|-------|--------|---------|
| `figures/diagram_a_rag_pipeline.png` | Plan 02 (make_diagrams.py) | §3 System Overview |
| `figures/diagram_b_defense_pipeline.png` | Plan 02 (make_diagrams.py) | §3 System Overview |
| `figures/fig1_arms_race.png` | Phase 3.4-03 (make_figures.py) | §6 Results |
| `figures/fig5_cross_model_heatmap.png` | Phase 3.4-03 (make_figures.py) | §6 Results |
| `figures/qr_github.png` | Plan 03 (make_qr.py) | §9 QR Code |

## Number Citation Spot-Checks

All numbers verified verbatim against `docs/phase3_results.md`:

- [x] **32%** — T2 mistral:7b paired ASR (undefended). Present in: §4 T2 tier box, §6 fig1 caption "Key numbers: T2 mistral undefended 32%", §7 Key Finding 1.
- [x] **4.7%** — ATK-08 mean ASR vs fused defense (3-seed). Present in: §4 ATK-08 tier box "4.7% mean ASR (std=3.3%)", §6 fig1 caption "ATK-08 adaptive 4.7% vs fused", §7 Key Finding 3.
- [x] **2%→8% / 12%→38%** — DEF-02 counter-productive T1/T2 ASR on llama3.2:3b. Present in: §5 DEF-02 negative result box, §7 Key Finding 4 "T1 ASR 2%→8%, T2 12%→38%".
- [x] **76% FPR** — Fused defense false positive rate on clean queries. Present in: §7 Key Finding 3 "ATK-08 4.7% ASR against fused defense", §8 Limitations "76% FPR on clean queries".
- [x] **0% T1/T2/T3** — Fused defense ASR on llama3.2:3b. Present in: §5 Result "0% / 0% / 0% with fused defense", §7 Key Finding 2.
- [x] **0% gemma4** — gemma4:31b-cloud ASR across all 5 tiers × 3 defenses. Present in: §6 fig5 caption "gemma4:31b-cloud: 0% ASR across all 5 tiers × 3 defenses", §6 heatmap section header.
- [x] **0.37/0.41** — LOO causal attribution ROC AUC (llama/mistral). Present in: §8 Limitations "LOO causal attribution AUC 0.37/0.41".
- [x] **4%→16%** — Poisoning ratio sweep ASR at 0.5%→10%. Present in: §7 Key Finding 5 "ASR scales 4%→16% as poisoned docs increase from 0.5%→10% of corpus (EVAL-06)".

## Font Size Check

Per RESEARCH §Pitfall 4 — recommended: title 80-120pt, section headers 36-48pt, body 24-32pt, captions 18-24pt.

| Element | Target | Actual | Status |
|---------|--------|--------|--------|
| Poster title | 80-120pt | 80pt | ✓ PASS |
| Authors/course line | 48-60pt | 40pt | ~ CLOSE (increase to 48pt if printing >48") |
| Hook question | 32-40pt | 32pt | ✓ PASS |
| Section headers | 36-48pt | 32pt | ~ CLOSE (increase if needed) |
| Problem body text | 24-32pt | 24pt | ✓ PASS |
| Tier box title | 24-32pt | 24pt | ✓ PASS |
| Tier box description | 20-24pt | 20pt | ✓ PASS |
| Signal box labels | 20-24pt | 20pt | ✓ PASS |
| Defense body text | 24-32pt | 24pt | ✓ PASS |
| Result/finding text | 22-28pt | 22pt | ✓ PASS |
| Captions | 18-24pt | 21pt | ✓ PASS |
| QR URL | 18-24pt | 22pt | ✓ PASS |

All body text meets the 20pt+ minimum for poster readability at 3-4 feet. Section headers at 32pt are slightly below the 36pt target — acceptable for a 48" wide poster viewed at course-setting distances.

## QR Scan Test

**Status: PENDING USER SCAN**

QR code encodes: `https://github.com/waleed79/CS763-indirect_prompt_injection`
Generated by `scripts/make_qr.py` using `qrcode 8.2`, error correction M.

**User action required:** Open `poster_cs763.pptx` → scan QR code with phone → confirm it resolves to the public GitHub repo. If repo is private, make it public before the May 4 deadline.

Record result here: _(PASSED / FAILED — resolved URL: ___)_

## Print Submission Path

Per CONTEXT D-14 and the May 4 deadline:

1. **Option A — Google Slides:** Upload `poster_cs763.pptx` via File → Open → Upload → export as PDF from Slides → submit PDF to print service.
2. **Option B — Direct PowerPoint:** Open in PowerPoint → File → Save As → PDF → submit PDF to print service.
3. **Option C — Digital submission:** If course accepts digital poster, submit `poster_cs763.pptx` or its PDF directly.

Print specs: 48" × 36" landscape at 150-300 DPI. At 300 DPI: 14400 × 10800 pixels.

**Deadline:** May 4, 2026. _(Record print service submission confirmation here.)_

## Confirmation

Poster `poster_cs763.pptx` was composed by Claude (Opus 4.7) on 2026-05-03 using pptxgenjs 4.0.1 on a 48"×36" custom canvas. All 9 CONTEXT D-15 sections are present. All 8 canonical numbers from `docs/phase3_results.md` are cited verbatim. All 5 figures (fig1, fig5, diagram_a, diagram_b, qr_github) are embedded from the `figures/` directory. The poster is ready for user review, QR scan test, and print/digital submission to meet the May 4 deadline.

_Pending actions: (1) User uploads to Google Slides and records share URL above. (2) User scans QR code and records result. (3) User submits PDF to print/course portal by May 4._
