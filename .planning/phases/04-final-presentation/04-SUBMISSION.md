---
phase: 04-final-presentation
submission_date: PENDING
poster_deadline: 2026-05-04
talk_deadline: 2026-05-07
poster_status: PENDING
talk_status: PENDING
---

# Phase 4 Final Submission Record

## Poster Submission

**Google Slides URL:** _(upload talk_cs763.pptx, record share URL here)_  
**Exported PDF path:** `poster_cs763.pptx` → export PDF via PowerPoint or Google Slides  
**Print service / portal:** _(where submitted — UW print service, Canvas portal, or in-person)_  
**Confirmation:** _(timestamp + confirmation number / receipt)_  
**Deadline hit:** _(YES / NO — submitted by 2026-05-04?)_

## Talk Submission

**Google Slides URL:** _(upload talk_cs763.pptx, record share URL here)_  
**Sharing status:** Anyone with the link, Viewer  
**Submission portal:** _(Canvas / course Google Doc / email — per course instructions)_  
**Confirmation:** _(timestamp)_  
**Deadline hit:** _(YES / NO — submitted by 2026-05-07?)_

## Dry-Run Evidence (PRES-01)

**Actual duration:** ___ minutes  
**Pass criterion:** 10.0 ≤ duration ≤ 12.0 minutes  
**Result:** _(PASS / FAIL)_  
**Presenter / Timer:** _(Musa / Waleed)_  

If too short (<10 min): expand slides 8 (hero fig1, aim ~90s) and 10 (ATK-08, aim ~75s).  
If too long (>12 min): trim slide 12 Limitations to 3 bullets; compress slide 5 to 4 tiers.

## Pedagogical Clarity Sign-Off (PRES-04)

**Slide 3 (What is RAG?) clarity:** _YES / NO_ — peer-followable in 60s without RAG background?  
**Slide 4 (Threat model) clarity:** _YES / NO_ — attacker model clear without security jargon?  
**Reviewers:** Musa + Waleed  

Both must be YES for PRES-04 to pass.

## Embedded Assets Confirmed Live (in Google Slides Slideshow mode)

- [ ] Slide 3: `figures/diagram_a_rag_pipeline.png` — loads correctly
- [ ] Slide 6: `figures/demo_tier2_mistral.gif` — **animates in Present/Slideshow mode** (RESEARCH Pitfall 2; does NOT animate in Edit mode — that is expected)
- [ ] Slide 7: `figures/diagram_b_defense_pipeline.png` — loads correctly
- [ ] Slide 8: `figures/fig1_arms_race.png` — loads correctly
- [ ] Slide 11: `figures/fig5_cross_model_heatmap.png` — loads correctly
- [ ] Slide 14: `figures/qr_github.png` — loads; scan with phone to confirm GitHub URL resolves
- [ ] Slide 12: `figures/fig2/fig3/fig4_*.png` — cited by filename in bullet text only (no embed on slide 12)

## Requirements Satisfied

- PRES-01 (10-12 min talk): _(SATISFIED — dry-run {X} min / PENDING)_
- PRES-02 (≥2 visualizations): SATISFIED — 5 result figures + 2 pipeline diagrams + 1 demo GIF embedded across poster and talk
- PRES-03 (optional demo): SATISFIED — pre-recorded GIF embedded in talk slide 6 (Tier-2 mistral:7b hijack recording)
- PRES-04 (accessible to peers): _(SATISFIED — slides 3-4 reviewed / PENDING)_

## GitHub Repo Status

**URL:** https://github.com/waleed79/CS763-indirect_prompt_injection  
**Visibility:** _(PUBLIC / PRIVATE — must be PUBLIC before QR scanning at presentation)_  
**Recommended:** `git tag v1.0-presentation && git push --tags` before the presentation date

## Phase 4 Artifacts Delivered

| Artifact | File | Status |
|----------|------|--------|
| Academic poster | `poster_cs763.pptx` | ✓ COMPOSED |
| RAG pipeline diagram | `figures/diagram_a_rag_pipeline.png` | ✓ |
| Defense pipeline diagram | `figures/diagram_b_defense_pipeline.png` | ✓ |
| QR code | `figures/qr_github.png` | ✓ |
| Demo GIF | `figures/demo_tier2_mistral.gif` | ✓ |
| Talk deck | `talk_cs763.pptx` | ✓ COMPOSED |
| Poster generator | `scripts/make_poster.js` | ✓ |
| Talk generator | `scripts/make_talk.js` | ✓ |
| Poster audit | `.planning/phases/04-final-presentation/04-POSTER-AUDIT.md` | ✓ |
| Talk audit | `.planning/phases/04-final-presentation/04-TALK-AUDIT.md` | ✓ |

## Confirmation

_(Fill in after both deadlines are hit)_

Phase 4 deliverables submitted. Poster shipped ___; talk delivered/submitted ___. All four PRES requirements satisfied. CS 763 final project complete.
