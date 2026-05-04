---
phase: 04-final-presentation
plan: 06
status: COMPLETE
completed: 2026-05-03
---

# Plan 04-06 Summary: Talk Deck

## What Was Built

14-slide talk deck for the CS 763 Final Presentation, composed as `talk_cs763.pptx`:
- **Canvas:** 13.33" × 7.5" widescreen 16:9 (pptxgenjs `LAYOUT_WIDE`)
- **Generator:** `scripts/make_talk.js` (Node.js, pptxgenjs 4.0.1)
- **Output:** `talk_cs763.pptx` (~1 MB pptxgenjs output)

## Google Slides

Direct Google Workspace access was unavailable. Deck built as .pptx for user to upload to Google Slides (File → Open → Upload). 16:9 Standard layout matches Google Slides default.

**Google Slides URL:** _(pending user upload — record in 04-TALK-AUDIT.md)_

## Per-Slide Completion

All 14 CONTEXT D-11 slides present in order:

1. ✓ Title — dark navy bg, "Indirect Prompt Injection in RAG Systems: An Attack-Defense Arms Race", team / course / UW-Madison
2. ✓ Attack hook — D-01 lead with result; clean vs. poisoned side-by-side text boxes
3. ✓ RAG Background — PRES-04; 4 bullets + diagram_a_rag_pipeline.png (right column)
4. ✓ Threat Model — PRES-04; 5 bullets + attacker model card; OWASP LLM-01 cited
5. ✓ Five Attack Tiers — 5 colored cards (T1/T1b/T2/T3/T4) with ASR badges; T2 32%, T4 0%
6. ✓ Demo — D-12; demo_tier2_mistral.gif full-width; red header; caption
7. ✓ Defense — diagram_b_defense_pipeline.png full-width; 6 bullet description; 4-signal fusion
8. ✓ Arms Race Results — D-04; fig1_arms_race.png full-width; hero slide; ~90s allocation
9. ✓ DEF-02 Negative — D-05; T1 2%→8%, T2 12%→38%; yellow warning card + before/after
10. ✓ ATK-08 Adaptive — D-06; 3-box narrative (Phase 2 → Suspicion → ATK-08); 4.7% ASR
11. ✓ Cross-Model — fig5_cross_model_heatmap.png full-width; gemma4 0% everywhere
12. ✓ Limitations — D-07/D-09/D-10; 5 bullets; 76% FPR, LOO AUC 0.372/0.410; NO images (text-heavy)
13. ✓ Conclusion — D-03 thesis; dark bg + 3 color-coded outcome cards; per-chunk insufficient
14. ✓ Future Work + Q&A — 4 future work bullets; qr_github.png; github URL

## Cited Numbers (all verbatim from docs/phase3_results.md)

| Number | Location |
|--------|----------|
| 32% T2 mistral paired ASR | Slide 5 ASR badge |
| 4.7% mean / 3.3% std ATK-08 vs fused | Slide 10 result badge |
| 2%→8% T1 DEF-02 | Slide 9 before/after cards |
| 12%→38% T2 DEF-02 | Slide 9 before/after cards |
| 76% FPR fused on clean queries | Slide 12 Limitations |
| 0% T1/T2/T3 fused llama3.2:3b | Slide 8 caption |
| 0% gemma4 all tiers × all defenses | Slide 11 title + caption |
| 0.372 (llama) / 0.410 (mistral) LOO AUC | Slide 12 Limitations |
| T4 0% co-retrieval limit | Slide 5 T4 card + Slide 12 |

## Embedded Assets

| Asset | Slide |
|-------|-------|
| figures/diagram_a_rag_pipeline.png | 3 |
| figures/diagram_b_defense_pipeline.png | 7 |
| figures/demo_tier2_mistral.gif | 6 |
| figures/fig1_arms_race.png | 8 |
| figures/fig5_cross_model_heatmap.png | 11 |
| figures/qr_github.png | 14 |

## PRES-01/02/04 Conformance

- **PRES-01** (10-12 min, problem/approach/results/conclusions): ✓ 14 slides × ~1 min each; arc covers attack → defense → adaptive attack → limitations → conclusion
- **PRES-02** (≥2 visualizations): ✓ 8 embedded assets (2 diagrams + 1 GIF + 3 result figures + 1 QR)
- **PRES-04** (RAG + IPI defined): ✓ Slides 3 + 4 define retrieval-augmented generation and indirect prompt injection for a CS 763 security audience

## Pending User Actions

1. Upload `talk_cs763.pptx` to Google Slides → record share URL in `04-TALK-AUDIT.md`
2. Test slide 6 GIF in Slideshow/Present mode → record PASSED in audit
3. Second reviewer (Waleed) confirm PRES-04 pedagogical clarity
4. Deliver talk May 5-7

## Audit Record

Full sign-off at `.planning/phases/04-final-presentation/04-TALK-AUDIT.md`
