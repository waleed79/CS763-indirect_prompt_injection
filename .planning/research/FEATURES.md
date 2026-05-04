# Feature Research

**Domain:** RAG Security / Indirect Prompt Injection (Attack + Defense Research)
**Researched:** 2026-03-31
**Confidence:** MEDIUM (based on training knowledge up to May 2025; web verification unavailable)

## Feature Landscape

### Table Stakes (Reviewers / Graders Expect These)

Features that any credible RAG prompt injection study must include. Missing these makes the work unconvincing.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Functional RAG pipeline (retriever + generator) | Cannot study RAG attacks without a working RAG system | MEDIUM | Embedding model + vector store + LLM; use off-the-shelf components (e.g., sentence-transformers + FAISS + an API LLM) |
| Multiple attack strategies (minimum 3) | A single attack type proves nothing about generalizability; reviewers expect variation | MEDIUM | Naive injection ("Ignore previous instructions..."), context-hijacking (embed payload in plausible text), optimized adversarial triggers (gradient-based or iterative refinement) |
| Attack Success Rate (ASR) metric | The standard metric in every prompt injection paper; without it, results are anecdotal | LOW | Binary classification: did the LLM produce the attacker-desired output? Requires clear rubric (exact match, semantic match, or LLM-as-judge) |
| At least one defense mechanism | Attack-only papers are demonstrations, not research; the field expects mitigation proposals | HIGH | BERT-based classifier on retrieved chunks, or perplexity filtering, or instruction-data separation |
| Defense effectiveness measurement | Must quantify how well the defense works, not just claim it works | LOW | ASR-before-defense vs ASR-after-defense; retrieval quality retention (recall/MRR on clean queries) |
| Controlled corpus with poisoning simulation | Need reproducible, measurable poisoning — not hand-waved "imagine if..." | MEDIUM | Clean corpus + injected poisoned documents at controlled ratios (e.g., 1%, 5%, 10% poisoning rates) |
| Retrieval quality baseline (clean performance) | Must prove the RAG system works correctly before showing it can be broken | LOW | Standard retrieval metrics on clean queries: recall@k, MRR, answer correctness |
| Multiple LLM targets (minimum 2) | Single-LLM results are not generalizable; reviewers will ask "does this work on other models?" | LOW | Use at least 2 models (e.g., GPT-3.5/4 via API + an open model like Llama-2 or Mistral) |
| Reproducible experimental setup | Course requirement (GitHub repo with replication instructions); also basic scientific practice | MEDIUM | Fixed random seeds, documented hyperparameters, versioned dependencies, clear instructions |
| Literature survey and threat model | Must position work relative to existing research; define attacker capabilities and goals | LOW | Cite Greshake et al. 2023, PoisonedRAG (Zou et al. 2024), OWASP Top 10 for LLMs |

### Differentiators (Publishable Contribution)

Features that elevate from "competent course project" to "conference-worthy contribution." Not all are needed -- pick 1-2.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Gradient-based adversarial trigger optimization | Goes beyond hand-crafted prompts to show optimized attacks (ala GCG / AutoDAN); much stronger attack results | HIGH | Requires open-weight model for gradient access; computationally expensive; builds on Zou et al. "Universal and Transferable Adversarial Attacks" (2023) |
| Retrieval-aware attack crafting | Attacks optimized to be retrieved (high cosine similarity to target queries) rather than just injected randomly; most papers skip this | MEDIUM | Co-optimize for retrieval relevance + attack payload effectiveness; this is a genuine gap in current literature |
| Attention-mask / instruction hierarchy defense | Novel defense where retrieved context is structurally separated from instructions in the LLM's attention mechanism | HIGH | Requires model internals access (open-weight model); inspired by OpenAI's "instruction hierarchy" paper; genuinely novel if done well |
| Systematic poisoning ratio analysis | Controlled experiments varying poison percentage (0.1%, 0.5%, 1%, 5%, 10%) with full ASR curves | MEDIUM | Simple experimentally but provides high-value quantitative insight; most papers test 1-2 ratios only |
| Cross-domain corpus evaluation | Test on multiple knowledge domains (e.g., medical QA, legal docs, general knowledge) to show attack generalizability | MEDIUM | Requires curating 2-3 corpora; shows whether certain domains are more vulnerable |
| LLM-as-judge evaluation with inter-rater agreement | Use GPT-4 as automated evaluator for ASR, validated against human labels on a subset | MEDIUM | Stronger than regex/exact-match; publishable methodology contribution; requires careful prompt engineering for the judge |
| Adaptive defense (adversary knows about defense) | Test if attacks can be re-optimized to bypass the proposed defense; shows defense robustness | HIGH | Arms-race evaluation; standard in adversarial ML papers; significantly strengthens defense claims |
| Latency and throughput analysis of defense | Show that defense is practical (adds <X ms per query) not just effective | LOW | Easy to measure; often overlooked; reviewers appreciate deployment-aware evaluation |
| Comparison with existing defenses | Benchmark proposed defense against known approaches (PPL filtering, paraphrasing, spotlighting) | MEDIUM | Positions contribution relative to SOTA; essential for publication but optional for course project |

### Anti-Features (Deliberately NOT Build)

Features that seem appealing but would waste time, add complexity without value, or fall outside the project's scope.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-world corpus poisoning (e.g., editing Wikipedia) | Feels more "realistic" | Ethically problematic; logistically impossible in a course timeline; legally risky; simulated poisoning is the accepted standard | Simulate poisoning by injecting documents into a local corpus at controlled rates |
| Multi-modal attacks (images, PDFs with hidden text) | Expanding attack surface | Massively increases scope; multi-modal RAG is a separate research area; 2-person team cannot do both well | Stay text-only; note multi-modal as future work |
| Production-grade RAG system with auth, API, UI | Makes demos look impressive | Engineering effort with zero research value; course grades research quality not polish | CLI scripts or Jupyter notebooks are fine; focus time on experimental rigor |
| Direct prompt injection attacks | Completeness | Well-studied, different threat model (attacker = user); conflates two distinct problems; indirect injection via corpus is the novel angle | Clearly scope to indirect/third-party injection; cite direct injection papers as related work |
| Fine-tuning the LLM itself | "Better" defense | Requires significant compute; changes the experimental variable (model); undermines generalizability claims | Use inference-time defenses (input filtering, output checking) that work with any LLM |
| Building a custom embedding model | Optimal retrieval | Weeks of work for marginal gain; off-the-shelf embeddings (all-MiniLM-L6-v2, text-embedding-3-small) are the standard baseline | Use pre-trained sentence-transformers; document which model and version |
| Comprehensive prompt injection taxonomy | Academic completeness | Literature survey work, not experimental contribution; others have done this well already (Greshake et al.) | Cite existing taxonomies; focus energy on experiments |
| Real-time defense system / streaming | Production relevance | Course project, not a product; adds engineering complexity with no research insight | Batch evaluation is standard in research papers |

## Feature Dependencies

```
[Functional RAG Pipeline]
    |-- requires --> [Controlled Corpus with Poisoning Simulation]
    |-- requires --> [Retrieval Quality Baseline]
    |
    |-- enables --> [Multiple Attack Strategies]
    |                   |-- enables --> [Attack Success Rate Measurement]
    |                   |-- enables --> [Gradient-based Trigger Optimization] (differentiator)
    |                   |-- enables --> [Retrieval-aware Attack Crafting] (differentiator)
    |
    |-- enables --> [Defense Mechanism]
                        |-- requires --> [ASR Measurement] (to measure improvement)
                        |-- enables --> [Defense Effectiveness Measurement]
                        |-- enables --> [Adaptive Defense Testing] (differentiator)
                        |-- enables --> [Latency Analysis] (differentiator)

[Multiple LLM Targets]
    |-- independent of --> [Attack Strategies] (run same attacks on different LLMs)
    |-- enables --> [Generalizability Claims]

[LLM-as-Judge Evaluation] (differentiator)
    |-- enhances --> [ASR Measurement]
    |-- requires --> [Human-labeled validation subset]

[Systematic Poisoning Ratio Analysis] (differentiator)
    |-- requires --> [Controlled Corpus]
    |-- requires --> [ASR Measurement]
    |-- enhances --> [All attack/defense results]
```

### Dependency Notes

- **Attack strategies require RAG pipeline:** Cannot test attacks without a working retrieval + generation system.
- **Defense requires ASR measurement:** Must be able to measure attack success before and after defense to quantify improvement.
- **Gradient-based optimization requires open-weight model:** Cannot compute gradients through API-only models (GPT-3.5/4). Need Llama-2 or Mistral for this differentiator.
- **Adaptive defense testing requires both attack and defense:** This is the final step -- re-optimize attacks against the defense and measure residual ASR.
- **LLM-as-Judge is independent but enhances everything:** Can be added as a measurement improvement without changing experimental setup.

## MVP Definition

### Phase 1: Foundation (v1 -- due already, 2026-03-27)

Minimum viable experimental setup.

- [x] Literature survey and threat model definition
- [x] RAG pipeline with embedding model + vector store + LLM
- [x] Clean corpus with baseline retrieval performance
- [x] Initial attack design (at least 1 naive injection strategy)

### Phase 2: Core Experiments (v1.x -- due 2026-04-12)

Core attack and defense experiments that constitute the main contribution.

- [ ] 3+ attack strategies implemented and measured (naive, context-hijack, optimized)
- [ ] ASR measurement framework with clear rubric
- [ ] Controlled poisoning at multiple ratios (at minimum 1%, 5%, 10%)
- [ ] At least one defense mechanism implemented (BERT classifier or perplexity filter)
- [ ] Defense effectiveness quantified (ASR reduction + retrieval quality retention)
- [ ] Testing on 2+ LLM targets

### Phase 3: Polish and Differentiation (v2 -- due 2026-04-30)

Features that strengthen the contribution for the final presentation and potential publication.

- [ ] Retrieval-aware attack crafting (optimize for both retrieval and attack success)
- [ ] Systematic poisoning ratio sweep with ASR curves
- [ ] LLM-as-judge evaluation (validated against human labels)
- [ ] Latency analysis of defense mechanism
- [ ] Comparison with at least one baseline defense approach
- [ ] Ablation studies on defense parameters

### Future Consideration (Post-Course)

Features to defer unless pursuing publication.

- [ ] Gradient-based adversarial trigger optimization -- requires significant compute and open-weight model setup
- [ ] Adaptive defense evaluation (arms-race testing) -- strong for publication but complex
- [ ] Cross-domain corpus evaluation -- meaningful but time-intensive
- [ ] Attention-mask instruction hierarchy defense -- genuinely novel but implementation-heavy

## Feature Prioritization Matrix

| Feature | Research Value | Implementation Cost | Priority |
|---------|---------------|---------------------|----------|
| Functional RAG pipeline | HIGH | MEDIUM | P1 |
| Multiple attack strategies (3+) | HIGH | MEDIUM | P1 |
| ASR measurement framework | HIGH | LOW | P1 |
| Controlled corpus + poisoning simulation | HIGH | MEDIUM | P1 |
| Retrieval quality baseline | HIGH | LOW | P1 |
| Defense mechanism (BERT classifier) | HIGH | HIGH | P1 |
| Defense effectiveness measurement | HIGH | LOW | P1 |
| Multiple LLM targets (2+) | MEDIUM | LOW | P1 |
| Reproducible setup (seeds, docs) | HIGH | LOW | P1 |
| Literature survey + threat model | HIGH | LOW | P1 |
| Systematic poisoning ratio analysis | HIGH | MEDIUM | P2 |
| LLM-as-judge evaluation | MEDIUM | MEDIUM | P2 |
| Retrieval-aware attack crafting | HIGH | MEDIUM | P2 |
| Latency analysis | MEDIUM | LOW | P2 |
| Comparison with baseline defenses | MEDIUM | MEDIUM | P2 |
| Gradient-based trigger optimization | HIGH | HIGH | P3 |
| Adaptive defense testing | HIGH | HIGH | P3 |
| Cross-domain corpus evaluation | MEDIUM | MEDIUM | P3 |
| Attention-mask defense | HIGH | HIGH | P3 |

**Priority key:**
- P1: Must have -- required for a credible CS 763 course project
- P2: Should have -- elevates the project; pursue in Phase 3 if time allows
- P3: Nice to have -- publication-grade features; defer unless pursuing venue submission

## Comparable Work Feature Analysis

| Feature | Greshake et al. (2023) | PoisonedRAG (Zou et al. 2024) | Pasquini et al. (2024) | Our Approach |
|---------|------------------------|-------------------------------|------------------------|--------------|
| Attack taxonomy | Comprehensive taxonomy | Focused on corpus poisoning | Neural exec attacks | Focused: 3 attack types at varying sophistication |
| Optimized triggers | No (manual) | Yes (optimization-based) | Yes (neural) | Start manual, add optimization if time permits |
| Defense proposal | Minimal | None (attack-focused) | Minimal | Core contribution: BERT-based context sanitization |
| Poisoning ratio analysis | No | Partial | No | Systematic sweep (our differentiator) |
| Multiple LLMs | Yes | Yes | Yes | Yes (2+ models) |
| Retrieval-aware attacks | No | Yes | No | Yes (planned differentiator) |
| Reproducible code | Partial | Yes | Partial | Full repo with replication instructions (course requirement) |

## Sources

- Greshake et al., "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection" (2023, arXiv:2302.12173) -- foundational paper on indirect prompt injection taxonomy
- Zou et al., "PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models" (2024, arXiv:2402.07867) -- closest comparable work on corpus poisoning attacks
- Zou et al., "Universal and Transferable Adversarial Attacks on Aligned Language Models" (2023, arXiv:2307.15043) -- GCG attack methodology for gradient-based trigger optimization
- OWASP Top 10 for Large Language Model Applications (2023/2025) -- industry standard vulnerability classification
- Pasquini et al., "Neural Exec: Learning (and Learning from) Execution Triggers for Prompt Injection Attacks" (2024) -- advanced attack methodology
- Wallace et al., "Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions" (2024, OpenAI) -- inspiration for attention-mask defense approach

**Confidence note:** All sources are from training data (cutoff May 2025). Web verification was unavailable. Paper titles and arXiv IDs should be verified before citing. The feature landscape assessment is MEDIUM confidence -- the core features are well-established in the field, but newer 2025-2026 papers may have shifted what counts as table stakes vs differentiator.

---
*Feature research for: RAG Security / Indirect Prompt Injection*
*Researched: 2026-03-31*
