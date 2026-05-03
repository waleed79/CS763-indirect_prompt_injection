# Phase 5: Honest FPR Metrics — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-03
**Phase:** 05-honest-fpr-metrics-per-chunk-answer-preserved-and-llm-as-jud
**Areas discussed:** Scope (defenses & models), Judge model + eval set + seeds, Answer-degraded definition, Writeup integration + 76% framing, Judge prompt template, Output schema, Edge cases

---

## Scope: Defenses & Models

### Q1: How many (defense × model) cells get all three new FPR metrics?

| Option | Description | Selected |
|--------|-------------|----------|
| Headline only: fused × llama | Just the cell that produces 76%. ~50 judge calls. Fixes headline only. | |
| All 7 ablation rows × llama | Full ablation_table.json defense rows on llama. ~350 judge calls. | ✓ |
| EVAL-V2-01 grid (3 × 3) | fused/def02/no_defense × llama/mistral/gemma4. ~450 judge calls. | |

**User's choice:** All 7 ablation rows × llama (Recommended)
**Notes:** Most coherent story for the writeup; lets §4 utility-tradeoff figure be regenerated with honest numbers if planner chooses.

### Q2: What do we do with the `no_defense` row (chunks_removed = 0 by definition)?

| Option | Description | Selected |
|--------|-------------|----------|
| Skip it | Drop from Phase 5 outputs; trivially 0/0/0 by construction. | ✓ |
| Include as zero-baseline anchor | Compute and report 0/0/0 explicitly. ~50 judge calls of pure-zero output. | |

**User's choice:** Skip it (Recommended)
**Notes:** Effective scope = 6 defense rows × 50 = 300 judge calls.

---

## Judge Model + Eval Set + Seeds

### Q3: Which judge model for the LLM-as-judge FPR?

| Option | Description | Selected |
|--------|-------------|----------|
| gpt-oss:20b-cloud | Already used as Tier 3 attacker; pipeline proven. | ✓ |
| gemma4:31b-cloud | Different lineage, less self-eval bias. Slower. | |
| Both as cross-judge sanity check | gpt-oss primary, gemma4 on 20-query subset for kappa. ~120 extra calls. | |

**User's choice:** gpt-oss:20b-cloud (Recommended)
**Notes:** Proven plumbing, conda env, and `--delay 3` budget. Lineage independence accepted as good-enough.

### Q4: Eval set size for clean queries?

| Option | Description | Selected |
|--------|-------------|----------|
| Stay on existing 50 clean queries | Indices 50–99; no re-inference needed. CIs ±7pp. | ✓ |
| Expand to 200 from MS-MARCO | Tighter CIs ±3pp; 1400 new pipeline runs + 1200 judge calls. | |
| Stay on 50 + bootstrap CIs | Same data, add 1000-resample bootstrap CIs. | |

**User's choice:** Stay on existing 50 clean queries (Recommended)
**Notes:** Bootstrap CIs were folded into "Claude's discretion" in D-09 — not blocking, recommended.

### Q5: Judge call seeding — single-seed or multi-seed?

| Option | Description | Selected |
|--------|-------------|----------|
| Single-seed + standing caveat | One call per pair; matches Phase 3.3-07 EVAL-V2-01 caveat. 300 calls. | ✓ |
| 3-seed with majority vote | Tighter Metric 3 numbers at 3× cost. 900 calls. | |
| Single-seed + temperature=0 | One call but force determinism on judge. | |

**User's choice:** Single-seed + standing caveat (Recommended)

---

## Answer-Degraded Definition (Metric 2)

### Q6: What counts as the 'answer degraded' signal?

| Option | Description | Selected |
|--------|-------------|----------|
| Judge-only (collapses with M3) | Reuse same judge for M2 aggregation; no GT annotation. | ✓ |
| ROUGE-L token-overlap drop | Lexical, fully reproducible; penalizes paraphrase. | |
| Layered: lexical floor + judge tiebreak | ROUGE-L gates trivial cases, judge resolves middle range. | |
| Exact-match on QA subset | Hand-labeled known-answer subset (~10–20 queries). | |

**User's choice:** Judge-only (Recommended)

### Q7: Metric 2 denominator framing?

| Option | Description | Selected |
|--------|-------------|----------|
| All 50 clean queries | M2 = (chunks_removed>0 AND degraded) / 50. Defense-comparable. Literal ROADMAP wording. | ✓ |
| Subset where chunks_removed > 0 | M2 = degraded / count(chunks_removed>0). Different denominators per defense. | |

**User's choice:** All 50 clean queries (Recommended)

---

## Writeup Integration + 76% Framing

### Q8: Where do the new numbers land?

| Option | Description | Selected |
|--------|-------------|----------|
| Standalone Phase 5 doc + extend ablation_table.json | New `docs/phase5_honest_fpr.md`; one-paragraph callout in 3.4 §4. | ✓ |
| In-place patch of phase3_results.md §4 | Rewrite §4, demote 76% to footnote, regenerate D-04. Mutates submitted artifact. | |
| Both: in-place patch AND standalone addendum | Strongest narrative; most work. | |

**User's choice:** Standalone Phase 5 doc + extend ablation_table.json (Recommended)
**Notes:** Lowest risk to already-submitted Phase 3.4 deliverable.

### Q9: How is the original 76% framed in the new doc?

| Option | Description | Selected |
|--------|-------------|----------|
| Loose upper bound, with mechanism | '76% is the upper bound; honest metrics are X/Y/Z'. No retraction language. | ✓ |
| Explicit retraction | 'Phase 3.4 §4 overstates user-visible utility loss…' Stronger epistemic stance. | |
| Methodology footnote only, lead with new numbers | Phase 5 doc treats new metrics as canonical; 76% appears once in footnote. | |

**User's choice:** Loose upper bound, with mechanism (Recommended)

---

## Judge Prompt + Schema + Edge Cases

### Q10: Judge prompt template?

| Option | Description | Selected |
|--------|-------------|----------|
| A/B 'is B substantively worse than A?' | Direct binary degradation question with order randomization. | ✓ |
| Pairwise preference 'which is better' | MT-Bench style; conflates 'different' with 'degraded'. | |
| Rubric scoring 1–5 each, then delta | Most fine-grained; 6× the prompt cost. | |

**User's choice:** A/B with order randomization (Recommended)

### Q11: What goes into `logs/ablation_table.json` per defense row?

| Option | Description | Selected |
|--------|-------------|----------|
| Three new top-level keys | Add `per_chunk_fpr`, `answer_preserved_fpr`, `judge_fpr` + `judge_model`, `judge_n_calls`. Back-compat. | ✓ |
| Nested `honest_fpr` block | Cleaner namespacing but breaks scripts that flatten the row. | |
| Separate file `logs/honest_fpr.json` | Zero risk to existing artifacts; downstream needs to join two files. | |

**User's choice:** Three new top-level keys (Recommended)
**Notes:** Per-cell verdicts go in separate `logs/judge_fpr_llama.json` to keep ablation_table.json compact.

### Q12: Judge edge cases — refusals/ties/parse failures?

| Option | Description | Selected |
|--------|-------------|----------|
| TIE = preserved; refusals retry once then preserved | Conservative for the defense; doesn't inflate FPR. Audit trail logged. | ✓ |
| TIE = degraded; refusals retry then drop from denominator | Aggressive for defense; biases toward larger FPR. | |
| Three-way: preserved / degraded / unknown | Most honest; requires more writeup explanation. | |

**User's choice:** TIE = preserved; retry once then preserved (Recommended)
**Notes:** Three-way breakdown still appears in per-cell `judge_fpr_llama.json` for transparency, but the headline `judge_fpr` number folds unknowns into preserved.

---

## Claude's Discretion

- Exact threshold for "substantively worse" — judge interprets directly, no Claude post-processing rule.
- Bootstrap CIs (1000 resamples) — recommended but not blocking.
- JSON-Lines vs single JSON for `judge_fpr_llama.json` — JSON-Lines preferred but not blocking.
- Optional summary figure (4-FPR-column bar chart × 6 defenses) — recommended if scope allows.
- Whether per-chunk FPR uses `top_k` from config or counts actual retrieved chunks per query.
- Logging verbosity for `scripts/run_judge_fpr.py` — match existing `scripts/run_eval.py`.
- Exact wording of the Phase 3.4 §4 callout paragraph.

## Deferred Ideas

- Cross-LLM generalization (mistral, gemma4) of the three metrics.
- Cross-judge sanity check (gemma4 on 20-query subset, Cohen's kappa).
- Multi-seed (3-seed majority) judge calls.
- 200-query MS-MARCO eval set expansion.
- Hand-annotated GT subset for exact-match Metric 2.
- In-place rewrite of Phase 3.4 §4 + D-04 figure regeneration.
- ROUGE-L lexical Metric 2 path (fallback if judge-only proves unreliable).
- Bootstrap CIs (kept as discretion, not deferred — listed for reference).

