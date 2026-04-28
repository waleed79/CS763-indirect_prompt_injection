# Project Research Summary

**Project:** RAG Security Research -- Indirect Prompt Injection Attack and Defense
**Domain:** Academic Security Research / Adversarial ML (CS 763 Course Project)
**Researched:** 2026-03-31
**Confidence:** MEDIUM-HIGH

## Executive Summary

This project is a security research study on indirect prompt injection attacks against Retrieval-Augmented Generation (RAG) systems. The standard approach in the literature is to build a minimal RAG pipeline (embedder, vector store, LLM), demonstrate that an adversary who can inject documents into the retrieval corpus can hijack LLM behavior, and then propose and evaluate a defense mechanism. The project scope is well-defined by established work (Greshake et al. 2023, PoisonedRAG 2024), and the architecture patterns are consistent across published systems. The recommended stack is intentionally lightweight -- Python 3.11, sentence-transformers, ChromaDB, and Ollama for local LLM inference -- because the research value is in the attack/defense methodology, not the infrastructure.

The recommended approach is to build a custom RAG pipeline (explicitly avoiding LangChain/LlamaIndex, which obscure the attack surface), implement three tiers of attack sophistication (naive, obfuscated, context-blending), and develop a BERT-based context sanitization defense. The key differentiator over existing work is a systematic poisoning ratio analysis combined with a defense that is evaluated honestly -- including utility degradation on clean queries, not just ASR reduction. Phase 1 (pipeline + corpus + initial attacks) is already partially complete per the project timeline.

The primary risks are methodological, not technical: trivially detectable attacks that make the defense look artificially effective, measuring ASR without controlling for retrieval rate, and evaluating the defense on the same attack distribution it was trained on. These are the mistakes that turn a publishable study into a dismissed one. The mitigation is straightforward -- design the attack taxonomy and evaluation protocol before writing implementation code, and always decompose ASR into retrieval rate and conditional ASR.

## Key Findings

### Recommended Stack

The stack is deliberately minimal. A RAG security research pipeline has exactly four components: corpus (JSON/JSONL), embedder (sentence-transformers), retriever (ChromaDB), and generator (Ollama). LangChain and LlamaIndex are explicitly anti-recommended because their abstractions hide the retrieval-to-generation boundary, which is the attack surface under study.

**Core technologies:**
- **Python 3.11:** Safe choice for torch/transformers/faiss compatibility; avoid 3.12+ edge cases with ML libraries
- **sentence-transformers (>=5.0):** Standard for encoding text to vectors; use `all-MiniLM-L6-v2` as default embedding model (22M params, 384-dim, well-studied)
- **ChromaDB (>=1.5):** Simplest local vector store; zero infrastructure, Python-native, sufficient for <100K docs
- **Ollama (>=0.6):** Local LLM inference for open-source models; start with `llama3.2:3b` (runs on CPU); critical for reproducibility without API costs
- **transformers (>=4.45):** For both loading target LLMs and the BERT-based defense classifier
- **scikit-learn (>=1.6):** Precision/recall/F1 computation for defense classifier evaluation

**Critical version note:** Pin Python to 3.11, pin torch to 2.x. These are the constraints that matter.

### Expected Features

**Must have (table stakes for a credible CS 763 project):**
- Functional RAG pipeline (embedder + vector store + LLM)
- 3+ attack strategies at varying sophistication levels
- Attack Success Rate (ASR) measurement with clear rubric
- At least one defense mechanism (BERT classifier recommended)
- Defense effectiveness quantified (ASR reduction + utility preservation)
- Controlled corpus with poisoning simulation at multiple ratios (1%, 5%, 10%)
- Retrieval quality baseline on clean queries
- Testing on 2+ LLM targets
- Reproducible setup (pinned seeds, documented hyperparameters, GitHub repo)
- Literature survey and threat model definition

**Should have (differentiators -- pick 1-2):**
- Retrieval-aware attack crafting (optimize for both retrieval and injection success) -- genuine gap in current literature
- Systematic poisoning ratio sweep with ASR curves (most papers test 1-2 ratios only)
- LLM-as-judge evaluation validated against human labels
- Latency analysis of defense mechanism

**Defer (post-course / publication-track):**
- Gradient-based adversarial trigger optimization (GCG-style) -- requires significant compute
- Adaptive defense evaluation (arms-race testing)
- Cross-domain corpus evaluation
- Attention-mask instruction hierarchy defense

### Architecture Approach

The architecture follows a standard pattern from published RAG security research: an evaluation harness orchestrates experiments across a matrix of (corpus variant, attack strategy, defense strategy, query set) configurations. The RAG pipeline is composed of pluggable components, with defense inserted as middleware between retrieval and context assembly. Attacks operate offline (poisoning the corpus before queries), while defenses operate online (filtering retrieved chunks at query time).

**Major components:**
1. **Corpus Manager** -- owns clean and poisoned document collections; handles chunking, embedding, and vector store population
2. **Attack Module** -- generates adversarial payloads and injects them into corpus chunks; uses plugin pattern (BaseAttack interface) for extensibility
3. **Defense Module** -- intercepts retrieved context before LLM sees it; BERT classifier or rule-based filter; also uses plugin pattern (BaseDefense interface)
4. **RAG Pipeline** -- core retrieve-then-generate flow; accepts optional defense as middleware; keeps pipeline code clean of experiment logic
5. **Evaluation Harness** -- runs experiment matrix, collects ASR/retrieval/defense metrics, generates plots and tables
6. **Metrics Collector** -- computes ASR (decomposed into retrieval rate and conditional ASR), retrieval quality (Recall@k, MRR), defense overhead (latency, false positive rate)

### Critical Pitfalls

1. **Trivially detectable attacks** -- Design a 3-tier attack taxonomy (naive, obfuscated, context-blending) before writing code. If a regex catches all your attacks, your defense proves nothing.
2. **Measuring ASR without controlling for retrieval** -- Always decompose into Retrieval Rate (RR) and Conditional ASR (cASR). Log retrieved chunks for every query. End-to-end ASR = RR x cASR.
3. **Defense evaluated on same attack distribution as training** -- Use held-out attack category evaluation: train defense on naive + obfuscated, evaluate on context-blending. Report both in-distribution and out-of-distribution performance.
4. **Ignoring utility degradation** -- Always report paired metrics: ASR reduction AND answer quality on clean queries. Plot the ASR-utility tradeoff curve by varying defense threshold. This curve is the core contribution graphic.
5. **Toy corpus** -- Use an established QA dataset (Natural Questions or MS MARCO subset, 1K+ passages minimum) as the corpus backbone. Hand-curated 100-doc corpora produce unrealistic retrieval dynamics.

## Implications for Roadmap

Based on research, the build order is dictated by strict dependencies. Each phase depends on the previous one.

### Phase 1: RAG Pipeline Foundation and Corpus Setup
**Rationale:** Everything else (attacks, defenses, evaluation) requires a working RAG pipeline. This is the root dependency. The corpus choice constrains all downstream experiments.
**Delivers:** End-to-end RAG query (user question in, LLM answer out), retrieval quality baseline on clean queries, established corpus from NQ/MS MARCO (1K+ passages), retrieval logging infrastructure.
**Addresses:** Functional RAG pipeline, retrieval quality baseline, controlled corpus, reproducible setup (config files, seed pinning).
**Avoids:** Toy corpus pitfall (#5), no reproducibility pitfall (#8), conflated threat model pitfall (#7 -- define threat model here).
**Status:** Partially complete (Phase 1 was due 2026-03-27).

### Phase 2: Attack Module
**Rationale:** Must demonstrate the vulnerability before defending against it. Attacks are conceptually simpler than defenses, and showing a high baseline ASR motivates the defense work.
**Delivers:** 3+ attack strategies (naive injection, obfuscated, context-blending), corpus poisoning at controlled ratios (1%, 5%, 10%), baseline ASR measurement decomposed into RR and cASR.
**Addresses:** Multiple attack strategies, ASR measurement framework, controlled poisoning simulation.
**Avoids:** Trivially detectable attacks pitfall (#1), no retrieval decomposition pitfall (#2).

### Phase 3: Evaluation Harness (Basic)
**Rationale:** Need measurement infrastructure BEFORE building defenses, so defense development has immediate quantitative feedback. Building evaluation after defense means flying blind.
**Delivers:** Automated ASR computation (with RR/cASR decomposition), retrieval quality metrics (Recall@k, MRR), experiment matrix runner, structured result logging.
**Addresses:** Defense effectiveness measurement prerequisites, reproducible experimental setup.
**Avoids:** Manual ASR counting anti-pattern, defense without baseline comparison pitfall (#4).

### Phase 4: Defense Module
**Rationale:** With attacks working and metrics in place, iterate on defense with immediate feedback. The defense is the core research contribution.
**Delivers:** BERT-based context sanitization classifier, rule-based filtering baseline, ASR reduction quantification, utility preservation metrics on clean queries, ASR-utility tradeoff curve.
**Addresses:** Defense mechanism, defense effectiveness measurement, utility degradation analysis.
**Avoids:** Overfitted defense evaluation pitfall (#3 -- use held-out attack category), ignoring utility degradation pitfall (#4).

### Phase 5: Full Evaluation, Differentiation, and Reporting
**Rationale:** All components are in place. Run the full experiment matrix, add differentiator features, and generate presentation materials.
**Delivers:** Full experiment matrix results (3 attacks x 2-3 defenses x multiple poison ratios), cross-model validation on second LLM, systematic poisoning ratio sweep with ASR curves, latency analysis, plots and tables for presentation.
**Addresses:** Multiple LLM targets, systematic poisoning ratio analysis (differentiator), retrieval-aware attack crafting (stretch differentiator), presentation materials.
**Avoids:** Single-model conclusions pitfall (#6), cherry-picked examples pitfall.

### Phase Ordering Rationale

- **Phase 1 before everything:** The RAG pipeline is the experimental substrate. Without it, nothing else can be tested or measured.
- **Phase 2 before Phase 4:** Must demonstrate the problem before proposing the solution. High baseline ASR is the motivation for the defense.
- **Phase 3 before Phase 4:** Measurement infrastructure must exist before defense development. Otherwise defense quality is assessed by "it seems to work" rather than quantitative metrics.
- **Phase 5 is integration:** Combines all components into a full evaluation. This is where differentiator features (poisoning ratio sweeps, cross-model validation) are added because they require all components to be stable.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Attack Module):** Designing obfuscated and context-blending attacks that are realistic but not trivially detectable requires careful study of existing attack examples from Greshake et al. and PoisonedRAG. The attack taxonomy needs validation against published examples.
- **Phase 4 (Defense Module):** BERT-based classifier training data preparation and threshold tuning require experimentation. The held-out evaluation protocol needs careful design to avoid the overfitting pitfall.

Phases with standard patterns (skip research-phase):
- **Phase 1 (RAG Pipeline):** Well-documented pattern. sentence-transformers + ChromaDB + Ollama is a straightforward integration with abundant examples.
- **Phase 3 (Evaluation Harness):** Standard experiment runner pattern. Metrics (ASR, Recall@k, MRR) are well-defined in the literature.
- **Phase 5 (Full Evaluation):** Execution of already-designed experiments. No novel patterns needed.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | All package versions verified via PyPI. Embedding model choices are established but MTEB rankings may have shifted. Core recommendations (ChromaDB, Ollama, sentence-transformers) are sound. |
| Features | MEDIUM | Based on training knowledge through May 2025. Core table-stakes features are well-established in the literature. Newer 2025-2026 papers may have shifted what counts as differentiator vs. table stakes. |
| Architecture | HIGH | Architecture patterns are consistent across published RAG security research. Plugin pattern for attacks/defenses, middleware pattern for defense insertion, experiment matrix runner are all standard. |
| Pitfalls | MEDIUM | Pitfalls are derived from published methodology critiques and common research anti-patterns. Specific to RAG security research, not generic advice. May miss newer pitfalls from 2025-2026 work. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Embedding model currency:** Could not verify current MTEB leaderboard. The recommended models (all-MiniLM-L6-v2, BGE-small) are established but may not be SOTA. This does not affect the research -- any reasonable embedding model demonstrates the attack surface.
- **Ollama model catalog:** Could not verify current model availability. Recommended models (llama3.2, mistral, phi3) were available as of early 2025 and are almost certainly still available, but should be confirmed.
- **Attack sophistication calibration:** The line between "obfuscated" and "context-blending" attacks needs empirical calibration during Phase 2. Published examples should be studied to set the right difficulty level.
- **Defense classifier training data:** Need to determine how to generate balanced training data for the BERT classifier. Options include using existing prompt injection datasets (if available) or generating synthetic labeled examples. This needs investigation in Phase 4 planning.
- **Deadline pressure:** Phase 1 was due 2026-03-27 (already past). Phase 2 core experiments due 2026-04-12 (12 days away). The timeline is tight. Prioritize P1 features ruthlessly; defer all P2/P3 features until Phase 5.

## Sources

### Primary (HIGH confidence)
- PyPI package index -- all version numbers verified 2026-03-31
- Ollama model library -- model sizes and quantization options
- HuggingFace model hub -- embedding model specifications

### Secondary (MEDIUM confidence)
- Greshake et al., "Not What You've Signed Up For" (2023, arXiv:2302.12173) -- indirect prompt injection taxonomy
- Zou et al., "PoisonedRAG" (2024, arXiv:2402.07867) -- corpus poisoning attacks on RAG
- Zou et al., "Universal and Transferable Adversarial Attacks" (2023, arXiv:2307.15043) -- GCG attack methodology
- OWASP Top 10 for LLM Applications (2023/2025) -- prompt injection as #1 vulnerability
- Pasquini et al., "Neural Exec" (2024) -- advanced attack methodology
- Wallace et al., "Instruction Hierarchy" (2024, OpenAI) -- instruction separation defense
- Liu et al., "Formalizing and Benchmarking Prompt Injection Attacks and Defenses" (2024)
- Yi et al., "BIPIA: Benchmarking and Defending Against Indirect Prompt Injection Attacks" (2023)

### Tertiary (LOW confidence)
- ArXiv IDs cited above should be verified before use in the final paper
- MTEB leaderboard rankings for embedding models (may have changed since May 2025)

---
*Research completed: 2026-03-31*
*Ready for roadmap: yes*
