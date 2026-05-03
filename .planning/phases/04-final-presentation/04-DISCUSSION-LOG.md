# Phase 4: Final Presentation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-02
**Phase:** 04-final-presentation
**Areas discussed:** Narrative Arc, Depth Allocation, Demo, Slide Tooling

---

## Narrative Arc

| Option | Description | Selected |
|--------|-------------|----------|
| Attack-first hook | Open with hijacked output in first minute; audience sees threat is real before background | ✓ |
| Problem/OWASP context first | Lead with OWASP #1, why RAG matters, then introduce system | |
| System demo first | Open by running pipeline live/GIF | |

**User's choice:** Attack-first hook

---

| Option | Description | Selected |
|--------|-------------|----------|
| Chronological tiers | Walk through T1→T2→T3→T4→defense→adaptive in build order | |
| Problem → Solution arc | Show ALL attacks first, then defense, then adaptive | ✓ |
| Two-act: attack vs defense | Act 1 all attacks, Act 2 defense side | |

**User's choice:** Problem → Solution arc

---

| Option | Description | Selected |
|--------|-------------|----------|
| Per-chunk defense insufficient | "Per-chunk detection is insufficient — multi-signal fusion required" | ✓ |
| Defenses work but costly | "76% FPR — real utility-security tradeoff" | |
| RAG is a new injection surface | "Corpus poisoning is the analog of SQL injection for LLMs" | |
| Arms race is unresolved | "4.7% adaptive ASR — arms race ongoing, generalization gap" | |

**User's choice:** Per-chunk defense insufficient

---

## Depth Allocation

| Option | Description | Selected |
|--------|-------------|----------|
| Arms race ASR table (fig1) | Hero result — 5 tiers × defense levels | ✓ |
| Adaptive attack breakthrough | ATK-08 partially breaks fused defense (4.7% ASR) | |
| DEF-02 counter-productive | System-prompt hardening increased ASR | ✓ |
| Gemma4 0% everywhere | Cloud-scale model robust to all 5 tiers | |

**User's choice:** Arms race ASR table + DEF-02 counter-productive finding (full slides)

---

| Option | Description | Selected |
|--------|-------------|----------|
| T4 cross-chunk 0% ASR | Honest negative — co-retrieval never achieved | ✓ |
| LOO causal attribution | AUC below chance — negative result | |
| Ratio sweep / transferability | 4%→16% ASR, 3-model transferability | ✓ |
| Utility-security tradeoff | 76% FPR utility cost (fig2) | ✓ |

**User's choice:** T4, ratio sweep, 76% FPR → one bullet each

---

| Option | Description | Selected |
|--------|-------------|----------|
| Full slide for adaptive attack | Required to support "per-chunk insufficient" conclusion | ✓ |
| Roll into arms race table | Show 4.7% as one row in main table | |
| Skip adaptive | End at fused 0% ASR | |

**User's choice:** Full slide for adaptive attack (Recommended)

**Notes:** LOO causal attribution was not placed in either category; will be mentioned in
limitations only (same treatment as T4).

---

## Demo

| Option | Description | Selected |
|--------|-------------|----------|
| Recorded GIF/video clip | 30-45s pre-recorded terminal clip; zero live risk | ✓ |
| Skip demo | Use before/after text on a slide | |
| Live demo | Run Ollama during talk — high risk | |

**User's choice:** Recorded GIF/video clip

---

| Option | Description | Selected |
|--------|-------------|----------|
| Tier-2 instruction smuggling | [Note for AI: …] — most visually clear, 32% ASR on mistral | ✓ |
| Tier-1 naive injection | Anchor tokens — looks like obvious spam | |
| Tier-3 LLM-generated | Most stealthy but hard to explain in 30s | |

**User's choice:** Tier-2 on mistral:7b

---

## Slide Tooling

| Option | Description | Selected |
|--------|-------------|----------|
| Google Slides | Easy collaboration, 5 PNGs embed cleanly | ✓ |
| PowerPoint | Course PPTX template in repo | |
| Beamer / LaTeX | Clean academic, but overkill | |

**User's choice:** Google Slides

---

| Option | Description | Selected |
|--------|-------------|----------|
| Standard academic poster 36×48" | Google Slides custom size, export PDF/PNG | ✓ |
| I need to check | Confirm with TA | |
| Digital/A4 format | Single slide or A4 | |

**User's choice:** 36×48 inch standard poster

---

| Option | Description | Selected |
|--------|-------------|----------|
| 12-15 slides (~1 min/slide) | Leaves room on results table and adaptive | ✓ |
| 8-10 slides | Faster, denser | |
| You decide | Planner decides count | |

**User's choice:** 12-15 slides

---

| Option | Description | Selected |
|--------|-------------|----------|
| Same structure condensed | Reuses 5 PNGs, easier since content exists | |
| Visual-first big figures | Big panels, minimal text | |
| Mix: standard poster structure + big figures + new pipeline images | Standard poster sections but with images showing full pipeline; new diagrams if needed | ✓ |

**User's choice:** Mix — poster structure with large figures including new pipeline/defense
diagrams. "Make new images to show pipeline and other information if needed."

---

| Option | Description | Selected |
|--------|-------------|----------|
| Clean RAG + attack surface diagram (single diagram) | Pipeline + attack surface in one | |
| Two separate diagrams: RAG pipeline + defense pipeline | More detail, separate layouts | ✓ |
| You decide on new figures | Planner decides | |

**User's choice:** Two separate diagrams

---

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, QR code to GitHub | Standard academic poster practice | ✓ |
| No QR code | Skip it | |
| You decide | Planner decides | |

**User's choice:** Yes, QR code to GitHub repo

---

## Claude's Discretion

- Visual style / color scheme for the 2 new diagrams
- Time allocation per slide within the 12-15 budget
- Whether gemma4 0% gets its own slide or is folded into cross-model section
- GIF recording toolset (terminalizer, asciinema, screen record)

## Deferred Ideas

- Human stealthiness study → Future Work in talk/poster
- Minimax hard-target → Future Work in talk/poster
- Musa vs Waleed work split → left to planner to suggest but not enforce
