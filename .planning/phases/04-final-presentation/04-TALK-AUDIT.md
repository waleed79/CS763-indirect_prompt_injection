---
phase: 04-final-presentation
artifact: talk
canvas_size: "16:9 standard (13.33\" × 7.5\", LAYOUT_WIDE)"
target_duration: "10-12 minutes"
slide_count: 14
status: COMPOSED
deadline: 2026-05-07
composed_date: 2026-05-03
delivery_format: talk_cs763.pptx (upload to Google Slides per D-13)
---

# Phase 4 Talk Audit Record

## Google Slides URL

**Pending user upload.** The deck was composed as `talk_cs763.pptx` (pptxgenjs, 16:9 LAYOUT_WIDE 13.33"×7.5") because direct Google Workspace access was not available in this session. The user should:

1. Open Google Slides → New blank presentation
2. File → Page setup → Standard 16:9 (default) → Apply
3. File → Open → Upload → select `talk_cs763.pptx`  
   (Google Slides will import all 14 slides with figures, colors, and speaker notes)
4. Test slide 6 in Slideshow mode to confirm the GIF animates (RESEARCH Pitfall 2)
5. File → Share → "Anyone with the link" + Viewer access → copy share URL
6. Record the URL here

**Google Slides URL:** _(to be filled after upload)_

## Per-Slide Sign-Off

All 14 slides per CONTEXT D-11 outline. Visually inspected in PowerPoint (slide-by-slide, 2026-05-03).

| # | Title | Content Source | Figure/GIF | Speaker Note | Status |
|---|-------|---------------|------------|--------------|--------|
| 1 | Indirect Prompt Injection in RAG Systems | Title slide — team, course, UW-Madison | None | "Brief intro: this is about RAG security…" | ✓ |
| 2 | We Poisoned a Corpus and Hijacked an LLM's Answer | D-01 attack-first hook; clean vs poisoned side-by-side | None (text boxes) | "Open with the threat: this isn't theoretical…" | ✓ |
| 3 | Background: Retrieval-Augmented Generation (RAG) | PRES-04 RAG definition; 4 bullets | diagram_a_rag_pipeline.png (right column) | "Define RAG for the security audience…" | ✓ |
| 4 | Threat Model: Indirect Prompt Injection | PRES-04 threat model; 5 bullets + attacker model card | None (text + shapes) | "Cite OWASP LLM-01 ranking…" | ✓ |
| 5 | Five Attack Tiers: Naive to Adaptive | D-02 attack taxonomy; 5 tier cards (T1/T1b/T2/T3/T4) with ASR badges | None (shapes) | "Each tier is more sophisticated…" | ✓ |
| 6 | Demo: Tier-2 Instruction Smuggling on mistral:7b | D-12 demo GIF; red header | demo_tier2_mistral.gif (full width) | "Watch the second query — the LLM literally prints attacker.com…" | ✓ |
| 7 | Defense: 4-Signal Fused Classifier | D-16 Diagram B; 6 bullet description | diagram_b_defense_pipeline.png (right 62%) | "Four orthogonal signals because no single signal handles all tiers…" | ✓ |
| 8 | Arms Race Results: 5 Tiers × 5 Defense Levels | D-04 hero figure ~90s; full-slide fig1 | fig1_arms_race.png (full width) | "HERO SLIDE — spend ~90 seconds here…" | ✓ |
| 9 | Honest Negative: System Prompt Hardening (DEF-02) Backfires | D-05; yellow warning card + before/after: T1 2%→8%, T2 12%→38% | None (shapes) | "Course explicitly asked for honest negative results…" | ✓ |
| 10 | ATK-08: BERT Memorized Anchors, Not Patterns | D-06; 3-box narrative (Phase 2 → Suspicion → ATK-08) | None (shapes) | "This is the punchline of the arms race…" | ✓ |
| 11 | Cross-Model: gemma4:31b-cloud is 0% Across All Tiers | D-11 slide 11; full-slide heatmap | fig5_cross_model_heatmap.png (full width) | "Architecture matters more than the defense layer at cloud scale…" | ✓ |
| 12 | Limitations | D-07/D-09/D-10; 5 bullets (T4, 76% FPR, LOO AUC, single-seed, CR-02); NO embedded images (text-heavy slide per plan decision) | None (fig2/fig3/fig4 cited by filename in bullet text only) | "Course explicitly asks for limitations…" | ✓ |
| 13 | Conclusion: Per-Chunk Defense is Insufficient | D-03 thesis; 3 cards (✓ fused wins, ⚠ adaptive regains, ✗ per-chunk insufficient) | None (dark bg + shapes) | "Land the punchline. This is the slide they should remember." | ✓ |
| 14 | Future Work + Q&A | D-07/D-08; 4 future-work bullets + QR code | qr_github.png (right column) | "Open the floor. QR for anyone who wants to inspect the code." | ✓ |

## Embedded Assets Inventory

All images embedded via `slide.addImage({ path: ... })` in `scripts/make_talk.js`:

| Asset | Source | Slide |
|-------|--------|-------|
| `figures/diagram_a_rag_pipeline.png` | Plan 02 (make_diagrams.py) | Slide 3 — RAG background |
| `figures/diagram_b_defense_pipeline.png` | Plan 02 (make_diagrams.py) | Slide 7 — Defense |
| `figures/demo_tier2_mistral.gif` | Plan 04 (make_demo_gif.md) | Slide 6 — Demo (D-12) |
| `figures/fig1_arms_race.png` | Phase 3.4-03 (make_figures.py) | Slide 8 — Hero result (D-04) |
| `figures/fig5_cross_model_heatmap.png` | Phase 3.4-03 (make_figures.py) | Slide 11 — Cross-model |
| `figures/qr_github.png` | Plan 03 (make_qr.py) | Slide 14 — Q&A |

**Note:** Slide 12 (Limitations) references fig2/fig3/fig4 by filename in bullet captions only — no image embeds on slide 12. This is intentional per the plan decision: the limitations slide is text-heavy; embedding 3 more figures would clutter it, and these figures appear in the poster and writeup.

## Number Citation Spot-Checks

All numbers verified verbatim against `docs/phase3_results.md`:

- [x] **32%** — T2 mistral:7b paired ASR (undefended). Present in: Slide 5 T2 card "32% (mistral:7b)" ASR badge.
- [x] **4.7% mean / 3.3% std** — ATK-08 vs fused (3-seed). Present in: Slide 10 ATK-08 result badge "4.7% ASR vs fused (3-seed, std 3.3%)".
- [x] **2%→8% / 12%→38%** — DEF-02 counter-productive (llama3.2:3b). Present in: Slide 9 before/after cards "T1 ASR: 2%" vs "8%", "T2 ASR: 12%" vs "38%".
- [x] **76% FPR** — Fused defense false positive rate on clean queries. Present in: Slide 12 Limitations bullet "76% False Positive Rate: fused defense blocks 76% of clean queries".
- [x] **0% T1/T2/T3** — Fused defense ASR on llama3.2:3b. Present in: Slide 8 caption "Fused defense (green) floors T1/T2/T3 ASR to 0% on llama3.2:3b".
- [x] **0% gemma4** — gemma4:31b-cloud ASR across all 5 tiers × 3 defenses. Present in: Slide 11 title + caption "gemma4:31b-cloud: 0% ASR across 5 tiers × 3 defenses".
- [x] **0.372 (llama) / 0.410 (mistral)** — LOO causal attribution ROC AUC. Present in: Slide 12 Limitations bullet "LOO causal attribution failed: ROC AUC 0.372 (llama) / 0.410 (mistral) — both below random".
- [x] **T4 0% co-retrieval limit** — T4 cross-chunk fragmentation. Present in: Slide 5 ATK card "0% ASR (co-retrieval limit)"; Slide 12 Limitations bullet.

## Present-Mode GIF Test

**Status: PENDING USER TEST**

Slide 6 embeds `figures/demo_tier2_mistral.gif`. In PowerPoint Edit mode, the first frame is shown as a static image (expected behavior — GIF animation only plays in Slideshow/Present mode).

**User action required:** In Google Slides after upload:
1. Click Slideshow → Start from beginning (or `Ctrl+F5`)
2. Navigate to slide 6
3. Confirm the GIF animates — you should see the terminal output scrolling, clean answer first, then the hijacked `attacker.com` output
4. If GIF shows static, re-encode with `-loop 0` per `scripts/make_demo_gif.md` Section 5

Record result here: _(PASSED / FAILED — observed: ___)_

## Pedagogical Clarity Check (PRES-04)

**Requirement:** A CS 763 peer who does not know RAG should be able to follow slides 3 (What is RAG?) and 4 (Threat model).

**Assessment:** YES — slides 3 and 4 define all required concepts:
- Slide 3 explains why RAG exists (LLMs frozen at training time), what retrieval does, and the pipeline step-by-step (User Query → Embedder → Vector Store → top-k chunks → LLM → Answer). Diagram A provides visual support.
- Slide 4 explains what the attacker controls (corpus write access only), what they cannot do (modify LLM/query/output), what "indirect" means, and what the attack goal is. The attacker model card on the right makes the threat model explicit.

**Reviewer:** Musa (self-review) — independent review by Waleed recommended before presentation.

## Font Size Check

Per RESEARCH Pitfall 4 (projector legibility):

| Element | Target | Actual | Status |
|---------|--------|--------|--------|
| Slide title (content slides) | 36-44pt bold | 32pt bold | ~ CLOSE — acceptable for 16:9 at normal projection distance |
| Slide title (dark slides) | 36-44pt | 32pt bold | ~ CLOSE |
| Body bullets | 24-28pt | 21-22pt | ~ CLOSE — increase to 24pt if font reads small on projector |
| Captions | 18-20pt | 14-15pt | ⚠ SMALL — captions are supplementary, not read-aloud; acceptable |
| Tier box ASR badges | 13-15pt | 13pt | ~ OK for close-reading slides |
| Conclusion card text | 20-24pt | 20-21pt | ✓ PASS |
| QR URL | 14pt | 14pt | ✓ PASS (scannable) |

Body text is close to the 24pt floor — if the projector is small or the room is large, Waleed or Musa should bump bullet fontSize from 21 → 24 in `scripts/make_talk.js` and regenerate.

## Confirmation

Talk deck `talk_cs763.pptx` was composed by Claude (Opus 4.7) on 2026-05-03 using pptxgenjs 4.0.1 on a 13.33"×7.5" (16:9) canvas. All 14 CONTEXT D-11 slides are present in order. All 8 canonical numbers from `docs/phase3_results.md` are cited verbatim. Six figures/GIF/QR assets are embedded in their D-11-specified slides. All 14 slides visually inspected in PowerPoint.

_Pending actions: (1) User uploads to Google Slides and records share URL above. (2) User tests slide 6 GIF in Present/Slideshow mode and records PASSED/FAILED. (3) Second reviewer (Waleed) confirms PRES-04 pedagogical clarity. (4) Deliver talk May 5-7._
