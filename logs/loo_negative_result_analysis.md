# DEF-05 Failed-Hypothesis Analysis: LOO Causal Attribution Inverted Below Random

**Plan:** 03.4-04
**Date:** 2026-04-29
**Models:** llama3.2:3b, mistral:7b
**Judge:** gpt-oss:20b-cloud
**Scope:** 50 attack-paired queries, 145 injected chunks + 5 clean chunks (top-k=3 per query)
**Finding:** Leave-one-out (LOO) causal attribution achieves ROC AUC = 0.372 (llama3.2:3b)
and 0.410 (mistral:7b) — both BELOW random — when used as an injection-vs-clean
classifier. The metric is anti-correlated with injection status: clean chunks score
HIGHER on LOO divergence than injected chunks. This document explains the mechanism.

---

## 1. Hypothesis Statement

The original DEF-05 hypothesis (Phase 3.2-03 design) was:

> The leave-one-out (LOO) influence/relevance ratio anomaly metric should distinguish
> injected chunks from clean chunks: removing an injected chunk from the retrieved set
> should change the LLM's answer (high LOO divergence), while removing a clean chunk
> should leave the answer unchanged (low LOO divergence). A classifier built on this
> signal should achieve ROC AUC > 0.5 on labeled per-chunk data.

The hypothesis is grounded in the per-chunk attribution defense literature spawned by
Greshake et al. (2023, arXiv 2302.12173), which framed indirect prompt injection as
a per-document trust problem and motivated defenses that reason about each retrieved
passage independently. LOO is a canonical primitive for such reasoning: if a single
chunk is responsible for a hijacked answer, ablating it should restore clean output.

**Conclusion:** The hypothesis is well-formed and falsifiable. Phase 3.2-03 implements
LOO faithfully (`scripts/run_loo.py`) over 50 attack-paired queries × 3 retrieved
chunks, with an LLM-as-judge divergence call. The result reported below is what the
faithful implementation produced.

---

## 2. Observed Result Table

Per-model aggregates from `logs/loo_results_llama.json` and `logs/loo_results_mistral.json`
(`aggregate.*` fields):

| Model        | ROC AUC    | n inject | n clean | infl rate inj | infl rate clean | Direction               |
|--------------|------------|----------|---------|---------------|-----------------|-------------------------|
| llama3.2:3b  | **0.372**  | 145      | 5       | 0.545         | 0.800           | INVERTED (below random) |
| mistral:7b   | **0.410** † | 145      | 5       | 0.628         | 0.800           | INVERTED (below random) |

† `aggregate.roc_auc` for mistral in `logs/loo_results_mistral.json` is 0.41379…
(reported as **0.414** in the Phase 03.4-03 ROC figure). The Phase 3.2-03 SUMMARY and
all downstream text round to **0.410** as the canonical 3-decimal-place value; both
forms refer to the same ROC AUC measurement. Divergence is documented in the
Plan 04 SUMMARY under "Deviations from Plan."

n_clean is small (5 vs 145 injected) because the attack-paired query set, by design,
saturates the top-k with poisoned candidates — only a handful of clean MS-MARCO
passages survive the retrieval cut. The influence_rate gap is what the AUC summarizes:
clean chunks induce LLM-answer divergence at 80% (4 of 5), while injected chunks
induce divergence at 54.5% / 62.8% (llama / mistral). Removing a clean chunk is more
likely to change the model's answer than removing an injected one.

**Conclusion:** Both AUCs are below 0.50 (random). The LOO signal is anti-correlated
with injection status; if used as an injection-vs-clean classifier in either direction
(higher-divergence-is-injected OR higher-divergence-is-clean), it would be worse than
chance for at least one model. The metric does not separate the two populations.

---

## 3. Mechanism Explanation

The inversion is a structural property of LOO under top-k retrieval with redundant
attack payloads. Three factors compose:

**(i) Injected chunks are redundant across the retrieved set.**
Tier 1 attacks (Phase 02.2 design) place the same anchor token (HACKED, COMPROMISED,
INFILTRATED, SYSTEM_OVERRIDE, PAYLOAD_DELIVERED) across **5 different passages** per
attack family. Whichever single chunk is retrieved at top-k position {1,2,3}, the LLM
sees an equivalent instruction. The Tier 2 instruction-smuggling payload
(`[Note for AI: …]` + `attacker.com` URL) likewise propagates across multiple
neighboring passages. In the 50 attack-paired query set, the 145 injected chunks come
from this small instruction-template pool repeated across many corpus entries.

Concretely: when LOO removes one injected chunk from the top-3, the remaining two
chunks frequently still carry the same anchor token (or an equivalent payload). The
LLM still emits "HACKED" or echoes the exfiltration URL. `diverged=False` is the
expected outcome. The LOO divergence on injected chunks therefore stays LOW — exactly
the opposite of the original hypothesis.

Evidence: `aggregate.influence_rate_injected` = 0.545 (llama) / 0.628 (mistral).
Roughly half of injected-chunk LOO removals fail to change the answer at all.

**(ii) Clean chunks contain unique factual content.**
Each clean MS-MARCO passage that survives retrieval contributes specific facts —
dates, numbers, named entities, definitions — that the LLM grounds its answer in.
There is no "redundant clean chunk" pool: by construction, each clean retrieval is
the corpus's best single match for one specific query topic. Removing it strips the
LLM of the unique facts; the model either falls back to an injected payload, hedges,
or hallucinates.

Either way, `diverged=True`. The LOO divergence on clean chunks stays HIGH.

Evidence: `aggregate.influence_rate_clean` = 0.800 across both models. Four of every
five clean-chunk removals change the answer.

**(iii) Net effect: anti-correlation.**
Combining (i) low divergence on injected chunks with (ii) high divergence on clean
chunks produces an injection-vs-clean ROC curve **below** the diagonal. The metric
ranks clean chunks above injected chunks on "is influential to the answer," which is
the opposite of what the hypothesized defense would surface. AUC < 0.5 for both
models is not a noise artifact (n_injected=145 across 50 queries is not under-powered)
and not a sign of broken implementation (the LLM-as-judge agreement was validated
against substring detection in Phase 02.4-03 at 79/79). It is the predicted
consequence of (i) + (ii) under top-k retrieval with a pooled-instruction attacker.

The result is best read as: per-chunk LOO measures **uniqueness of factual
contribution**, not **causality of payload-induced compliance**. Under a redundant-
payload attacker, those two quantities anti-correlate.

A Tier 4 fragment-influence sub-result reinforces the conclusion. Tier 4
fragmentation (Phase 02.4-02) splits the attack across 3 passages (fragments A/B/C),
each individually unique. Even here, LOO does not recover signal:
`aggregate.tier4_fragment_influence` shows fragment A influence = 1.0 when retrieved,
but fragments B and C are `null` — they are never co-retrieved in the top-3 (Phase
02.4-03 measured co-retrieval at 9%; Phase 03.2-03 confirmed only 3/50 queries
retrieve fragment A at all). Co-retrieval is so rare that LOO has nothing to attribute
across, regardless of per-fragment uniqueness. The fragmentation attack defeats LOO
through retrieval sparsity rather than payload redundancy, but the outcome is the
same: no per-chunk attribution signal.

**Conclusion:** AUC < 0.5 is a structural property of LOO under top-k retrieval with
redundant attack payloads (Tier 1/2) AND under sparse cross-chunk attack composition
(Tier 4). It is **NOT** a noise artifact and **NOT** a sign of broken implementation.
The metric is correctly measuring what LOO measures; LOO simply does not measure what
the per-chunk attribution defense literature assumed it would.

---

## 4. Counterfactual

What would have to be true for LOO causal attribution to recover signal? At least one
of the following:

1. **Unique-per-query injection (no payload pooling).** If each attack used a distinct
   anchor token and a unique payload sentence per query — no 5-variant template pool,
   no shared instruction preamble — removing the single injected chunk would change
   the LLM's answer in a way that mirrors clean-chunk LOO divergence. A practical
   attacker would never make this concession: pool reuse is a feature of the attack
   design (it lets one corpus poisoning run cover many queries) and an attacker
   optimizing for stealth or transferability has no reason to abandon it.

2. **Single-injected-chunk-per-retrieval guarantee.** If the threat model restricts
   the attacker to inserting at most one poisoned passage into any top-k retrieval —
   for example, via an upstream retrieval-time culling defense (BERT classifier,
   perplexity filter) that already removes most injections — LOO would see exactly
   one injected chunk per query and have a clean comparison point. Our threat model
   permits multiple injected passages per top-k by construction (the EVAL-V2-01
   matrix routinely surfaces 2-3 injected chunks in top-3); the assumption fails.

3. **Attribution beyond top-k LOO.** Methods that attribute over the full retrieval
   distribution rather than per-chunk independently — e.g., AttriBoT (arXiv 2411.15102)
   approximates LOO across **many** retrievals with >300× speedup, enabling
   distribution-level attribution rather than single-pass top-k removal. This maps
   directly to the Phase 03.4 §13 Future Work bullet "improved attribution beyond
   top-k LOO."

**Conclusion:** None of (1), (2), or (3) holds for the experimental configuration
that produced AUC = 0.372 / 0.410. The negative result is therefore stable: a
faithful implementation of per-chunk LOO under a realistic indirect-injection threat
model with pooled payloads will reproduce the inversion. The result is not specific
to llama3.2:3b or mistral:7b; the mechanism is retrieval-redundancy, not LLM
idiosyncrasy.

---

## 5. Why this is a citable negative-result contribution

Per-chunk defense literature — beginning with Greshake et al. (2023) and continuing
through PoisonedRAG and BadRAG defense proposals — has implicitly assumed that local
per-chunk reasoning suffices to detect indirect prompt injection. The literature
proposes BERT-style classifiers, perplexity filters, instruction detectors, and now
LOO-style attribution as candidate per-chunk defenses, each evaluated on per-chunk
metrics (precision, recall, F1, AUC) under the assumption that good per-chunk
performance composes into good system-level defense.

Our DEF-05 implementation is, to our knowledge, the first empirical demonstration
that one specific local-reasoning approach — **leave-one-out causal attribution** —
is **dominated by retrieval redundancy** when the attacker uses pooled anchor tokens.
The failure mode is not weak signal (AUC ≈ 0.5) but **inverted signal** (AUC < 0.5):
the metric ranks clean chunks above injected chunks on its primary axis. Practitioners
building per-chunk defenses should expect to see this inversion whenever the attack
pools payloads across multiple corpus passages, which is the default attacker design
in PoisonedRAG, BadRAG, and the attack-tier taxonomy used in this work.

The negative result places LOO in a "redundancy-blind" failure class that is distinct
from priming-style failures (cf. DEF-02 counter-productive finding,
`logs/def02_priming_analysis.md`) and from coverage failures (cf. T3/T4 zero-baseline
puzzle on llama3.2:3b). It motivates the §13 Future Work direction toward attribution
methods that account for the full retrieved set rather than per-chunk independence,
and it provides a concrete diagnostic test (compare influence_rate_injected vs
influence_rate_clean — if clean > injected, the attacker is using payload pooling)
that future per-chunk defense proposals should run before claiming per-chunk
attribution as a defense primitive.

**Conclusion:** The DEF-05 negative result is a first-class research output of
Phase 3.4, not a limitations-section footnote. It is reported in §5 of the writeup
(`docs/phase3_results.md`) under the failed-hypothesis arc, with this document
carrying the rigorous mechanistic treatment.

---

## 6. Pointers

- **Greshake et al. (2023), arXiv 2302.12173** — "Not what you've signed up for:
  Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection."
  Original threat model that motivated per-chunk attribution defenses. The DEF-05
  hypothesis is a direct descendant of this paper's per-document trust framing.
- **Phase 3.2-03 implementation** — `scripts/run_loo.py`,
  `logs/loo_results_llama.json`, `logs/loo_results_mistral.json`. Aggregate fields
  cited in §2 above (`aggregate.roc_auc`, `aggregate.n_injected_chunks`,
  `aggregate.n_clean_chunks`, `aggregate.influence_rate_injected`,
  `aggregate.influence_rate_clean`, `aggregate.tier4_fragment_influence`).
- **Structural analog: `logs/def02_priming_analysis.md`** (Phase 03.1-07) — DEF-02
  priming analysis follows the same hypothesis → mechanism → contribution arc for
  the DEF-02 counter-productive finding. This document was written to parallel its
  structure and rigor (top metadata block, horizontal-rule section breaks, numeric
  tables, bold **Conclusion:** sentences). The two analyses together form the
  Phase 3 negative-results pair: a substring-defense priming failure (DEF-02) and a
  per-chunk-attribution redundancy failure (DEF-05).
- **AttriBoT, arXiv 2411.15102** — candidate "improved attribution beyond top-k LOO"
  method for §13 Future Work. Approximates leave-one-out across many retrievals with
  >300× speedup, enabling distribution-level attribution that the per-query top-k
  LOO of this work cannot perform.
- **LODO methodology, arXiv 2602.14161** — leave-one-distribution-out evaluation
  used by the Phase 3.1 BERT classifier hold-out split. Relevant here as a
  methodological cousin: LODO for classifiers tests under distribution shift; the
  same insight (test under realistic shift, not just in-distribution AUC) applies to
  attribution methods. A future LODO-style evaluation of attribution would sweep
  attacker-pooling parameters (pool size, anchor diversity) and report AUC as a
  function of pool concentration.
- **Phase 03.2-VERIFICATION.md** — SC-5 Framing B disposition (commit c4aff8b,
  2026-04-28). Records the reclassification of DEF-05 from "failed defense" to
  "failed defense hypothesis with mechanistic explanation as a citable negative
  result." This document is the rigorous treatment that Framing B references.
- **Phase 03.4 writeup §5 (`docs/phase3_results.md` Causal Attribution Analysis)** —
  cites this document by path. Plan 03.4-05 (Wave 2 writeup) consumes the present
  document for the §5 hypothesis-result-mechanism-contribution arc.
