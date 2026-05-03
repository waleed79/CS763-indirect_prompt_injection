---
phase: 4
slug: final-presentation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-02
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing project framework, see `pytest.ini`) |
| **Config file** | `pytest.ini` |
| **Quick run command** | `conda run -n rag-security python -m pytest tests/test_phase4_assets.py -x --quiet` |
| **Full suite command** | `conda run -n rag-security python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds (Phase 4 asset suite); ~60 seconds (full suite) |

---

## Sampling Rate

- **After every task commit:** Run quick command (Phase 4 asset suite only)
- **After every plan wave:** Run full suite
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

> Filled in by `gsd-planner` when generating plans. Each task in PLAN.md must point at a row here OR justify why it is manual-only (e.g. Google Slides composition, human dry-run for talk timing).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 0 | PRES-02/03 | — | Wave-0 stubs created | unit | `conda run -n rag-security python -m pytest tests/test_phase4_assets.py -x --quiet` | ❌ W0 | ⬜ pending |
| (additional rows added by planner) | | | | | | | | | |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase4_assets.py` — stubs for PRES-02 (figures+diagrams+QR), PRES-03 (demo GIF)
- [ ] `pip install qrcode[pil]==8.2` (only new package required per RESEARCH §Standard Stack)
- [ ] Verify `figures/fig1..fig5_*.png` all present (already produced in Phase 3.4)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Talk fits 10-12 minute window with intelligible pacing | PRES-01 | Slide narration is human performance — no programmatic timer for delivery | Run a stopwatch dry-run; record actual minutes; revise per-slide budget if outside [10, 12] |
| Slides explain RAG and indirect prompt injection in terms a CS 763 student without RAG background can follow | PRES-04 | Pedagogical clarity is qualitative; checking for "RAG"/"prompt injection" strings does not prove the explanation works | Two-person review (Musa + Waleed) against D-11 outline slides 3 (What is RAG?) and 4 (Threat model); ask "would a peer who has never seen RAG follow this?" |
| Google Slides poster (36×48") renders correctly on export and at print resolution | PRES-02 | Google Slides PDF export quality + print preview is browser-side; no Python check covers it | Export to PDF, open in Acrobat at 100% zoom, confirm: (a) no text smaller than 24 pt body / 36 pt headers, (b) all 5 figures + 2 diagrams visible without pixelation, (c) QR scans from phone at arm's length |
| Demo GIF (Tier-2 instruction smuggling on mistral:7b) plays in Google Slides preview | PRES-03 (optional) | Slide insertion + preview rendering is UI-side | Insert into talk deck, click Slideshow, confirm GIF loops within slide and is readable at projector resolution |
| Talk dry-run hits all D-11 outline slides in order | PRES-01 | Outline conformance is a checklist, not a programmatic test | After deck is composed, walk through slides 1-14 against `04-CONTEXT.md` D-11 numbered list; flag missing/reordered slides |

---

## Validation Sign-Off

- [ ] All tasks have automated verify command OR a row in Manual-Only table with stated rationale
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (relax for the manual Google Slides composition tasks — they are inherently human)
- [ ] Wave 0 covers all MISSING references (`test_phase4_assets.py`, `qrcode` install)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter once planner finalizes the per-task map

**Approval:** pending
