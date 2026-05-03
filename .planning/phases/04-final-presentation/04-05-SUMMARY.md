---
phase: 04-final-presentation
plan: 05
status: COMPLETE
completed: 2026-05-03
---

# Plan 04-05 Summary: Academic Poster

## What Was Built

Academic poster for CS 763 Final Presentation, composed as `poster_cs763.pptx`:
- **Canvas:** 48"×36" landscape (pptxgenjs `defineLayout`, 48×36)
- **Generator:** `scripts/make_poster.js` (Node.js, pptxgenjs 4.0.1)
- **Output:** `poster_cs763.pptx` (~200 KB pptxgenjs output)

## Google Slides

Direct Google Workspace access was unavailable. Poster built as .pptx for user to upload to Google Slides (File → Open → Upload). A 48"×36" canvas is set in the pptxgenjs layout definition, matching CONTEXT D-14.

## Per-Section Completion

All 9 CONTEXT D-15 sections present:
1. ✓ Header — title (80pt), authors (40pt), CS 763, UW-Madison, hook question (32pt)
2. ✓ Problem & Motivation — 3-paragraph block, "Corpus Poisoning" in red
3. ✓ System Overview — diagram_a_rag_pipeline.png + diagram_b_defense_pipeline.png at full col width
4. ✓ Attack Taxonomy — 5 colored tier boxes (T1/T1b/T2/T3/ATK-08) with ASR numbers
5. ✓ Defense — 4-signal grid + meta-classifier + result "0%/0%/0%" + DEF-02 negative result
6. ✓ Results Panels — fig1_arms_race.png (hero) + fig5_cross_model_heatmap.png
7. ✓ Key Findings — 5 bullets with all canonical numbers
8. ✓ Limitations & Future Work — 5 bullets (T4 0%, LOO AUC, 76% FPR, single-seed, future)
9. ✓ QR Code — qr_github.png at 4.8"×4.8", GitHub URL label

## Cited Numbers (all verbatim from docs/phase3_results.md)

| Number | Location in Poster |
|--------|--------------------|
| 32% T2 mistral paired ASR | §4 T2 box, §6 caption, §7 Finding 1 |
| 4.7% ATK-08 vs fused (std=3.3%) | §4 ATK-08 box, §6 caption, §7 Finding 3 |
| 2%→8% / 12%→38% DEF-02 | §5 DEF-02 box, §7 Finding 4 |
| 76% FPR fused on clean queries | §7 Finding 3, §8 Limitations |
| 0% T1/T2/T3 fused llama3.2:3b | §5 result line |
| 0% gemma4 all 5 tiers × 3 defenses | §6 fig5 caption + header |
| 0.37/0.41 LOO AUC | §8 Limitations |
| 4%→16% ratio sweep | §7 Finding 5 |

## Font Sizes

- Title 80pt, authors 40pt, hook question 32pt (poster-readable at distance)
- Section headers 32pt
- Body text 24pt, tier descriptions 20pt, captions 21pt
- All meet the ≥20pt minimum for 3-4 foot viewing distance

## QR Scan

Status: PENDING USER SCAN — QR encodes `https://github.com/waleed79/CS763-indirect_prompt_injection`

## Print / Deadline

Poster file ready as of 2026-05-03. May 4 deadline is achievable: open in PowerPoint or Google Slides → export PDF → submit to print service or course portal.

## Audit Record

Full sign-off at `.planning/phases/04-final-presentation/04-POSTER-AUDIT.md`
