<!-- Phase 1 Submission — CS 763 Computer Security, UW-Madison Spring 2026 -->
<!-- Team: Muhammad Musa & Waleed Arshad -->
<!-- Submission target: shared Google Doc (Prof. Somesh Jha / TA Saikumar Yadugiri) -->
<!-- Local draft — copy-paste into Google Doc for submission -->

# Indirect Prompt Injection in Retrieval-Augmented Generation Systems

## Abstract

Retrieval-Augmented Generation (RAG) has become the dominant paradigm for grounding large language model (LLM) outputs in external knowledge, and is widely deployed in enterprise systems. This project investigates indirect prompt injection in RAG — an attack where an adversary who can write documents to the retrieval corpus can hijack LLM responses for any user who triggers retrieval of those documents. We build a complete attack-and-defense pipeline and measure Attack Success Rate (ASR) before and after applying a BERT-based context sanitization defense.

## Note on Project Pivot

This project is a pivot from our original pre-proposal topic, which addressed cross-modal RGB-Depth person re-identification for ICPR 2026 (TVRID). After initial scoping, the team decided to pivot to RAG prompt injection for three reasons: the topic is more directly relevant to our research interests in LLM security and safety; it is better suited to the course timeline (a complete attack + defense contribution is achievable in one month with the available tooling); and it addresses an active, industry-recognized threat (OWASP classifies prompt injection as the #1 LLM vulnerability). The RAG injection problem has an established literature base — including Greshake et al. (2023) and Zou et al. (2024) — which enables us to position our contribution clearly relative to prior work.

## Problem Statement

### What is Retrieval-Augmented Generation?

Retrieval-Augmented Generation (RAG) augments a large language model with an external knowledge base. When a user submits a query, the system first retrieves the most semantically similar documents from the knowledge base (using an embedding model and vector similarity search), then injects those documents as context into the LLM's prompt alongside the user's question. The LLM generates a response grounded in the retrieved content. RAG was designed to reduce hallucination and enable domain-specific knowledge without fine-tuning — but this architecture was not designed with adversarial inputs in mind. The retrieval step, specifically the injection of third-party document content into the LLM context window, is the attack surface this project studies.

### The Attack Surface RAG Introduces

Standard LLM deployments take user input, apply a system prompt, and produce output. The attack surface is the user-to-model boundary. RAG extends this: a third-party corpus now contributes content to every LLM context window. If an adversary can write documents to that corpus, they can inject content that the model will treat as authoritative retrieved knowledge. The adversary does not need to interact with the user, the LLM, or the system prompt. A single poisoned document, once indexed, can affect every user who issues a query that triggers its retrieval.

### Direct vs. Indirect Prompt Injection

*Direct prompt injection* occurs when an attacker controls the user's input and embeds malicious instructions in the query itself. The attacker IS the user. Defenses include input validation, rate limiting, and system prompt hardening applied at the user-model boundary.

*Indirect prompt injection* is fundamentally different. The adversary has no access to the user interface. Instead, they poison the knowledge base (retrieval corpus). When a legitimate user submits a benign query, the RAG system retrieves attacker-controlled content containing embedded instructions. Those instructions are injected into the LLM context window alongside the legitimate query, and the model — unable to distinguish retrieved knowledge from retrieved instructions — follows the attacker's commands instead of the system prompt.

Unlike direct prompt injection — where the attacker controls the user's input — indirect prompt injection exploits the retrieval boundary: an adversary who can write a single document to the knowledge base can hijack the LLM's response for any user who triggers retrieval of that document.

## Motivation

Prompt injection is classified as LLM01:2025 — the #1 vulnerability in the OWASP Top 10 for LLM Applications (2025 edition), marking the second consecutive edition in which it holds the top position [OWASP 2025]. The OWASP definition explicitly covers indirect injection via third-party content, including retrieval-augmented generation pipelines. Beyond classification, RAG is not a niche research prototype: enterprise adoption of RAG-based assistants has grown rapidly across industries including healthcare, legal, financial services, and software development. Systems such as Microsoft Copilot, enterprise chatbots, and customer-facing knowledge assistants are all RAG-based architectures. Each of these systems shares the same vulnerability: any party who can contribute documents to the knowledge base can, in principle, inject attacker-controlled instructions into the LLM context window of any legitimate user. The scale of deployment makes this a timely and consequential security research problem.

## Literature Survey

Prior work on indirect prompt injection and RAG security falls into four natural themes: RAG background and motivation, attack research, defense and detection, and evaluation frameworks.

### Theme 1: RAG Background and Motivation

Lewis et al. (2020) introduced Retrieval-Augmented Generation as a method for augmenting pretrained language models with non-parametric knowledge retrieved from an external document store, demonstrating that retrieval-augmented models outperform parametric-only models on knowledge-intensive NLP tasks [Lewis et al., NeurIPS 2020]. This work established the architectural pattern — encode documents as dense vectors, retrieve by similarity, inject as context — that underlies every modern enterprise RAG system. Critically, Lewis et al. designed RAG for accuracy and factual grounding, not adversarial robustness. The attack surface studied in this project — the retrieval-context injection boundary — is precisely what their architecture introduced.

### Theme 2: Attack Research

Greshake et al. (2023) established the foundational taxonomy of indirect prompt injection, demonstrating that LLM-integrated applications (browser plugins, email summarizers, travel planners) can be compromised by embedding instructions in third-party content the LLM processes [Greshake et al., IEEE S&P Workshop SecTL, arXiv:2302.12173]. Their work covered a broad class of applications where the LLM processes external web content. This project narrows the focus to RAG-specific corpus poisoning, where the injection vector is a retrieval database rather than live web content — a more controlled and measurable attack scenario.

Zou et al. (2024) demonstrated corpus poisoning attacks specifically targeting RAG systems in PoisonedRAG, showing that injecting as few as five poisoned documents into a one-million-document corpus can achieve over 90% attack success rate [Zou et al., USENIX Security 2024, arXiv:2402.07867]. PoisonedRAG is the closest comparable work to this project. A key gap in PoisonedRAG is that it characterizes the attack but does not develop or evaluate a defense. This project extends their attack framework with a defense evaluation component.

Shafran et al. (2025) demonstrated a different attack variant — denial-of-service via "blocker" documents that prevent relevant results from reaching the LLM — published at USENIX Security 2025 [Shafran et al., arXiv:2406.05870]. The breadth of RAG attack variants (injection, poisoning, jamming) underscores that the retrieval boundary is a rich and underexplored attack surface. This project focuses on the injection/poisoning variant rather than denial-of-service.

### Theme 3: Defense and Detection

Yi et al. (2023) introduced BIPIA (Benchmarking and Defending Against Indirect Prompt Injection Attacks), which proposed four black-box prompt-learning defenses and one white-box fine-tuning defense, evaluated across email QA, web QA, and summarization tasks [Yi et al., KDD 2025, arXiv:2312.14197]. BIPIA's defenses operate at the prompt level — they modify how the LLM is instructed to treat external content. This project proposes a complementary approach: a BERT-based context sanitization classifier that operates at the retrieved-chunk level, filtering potentially malicious content before it reaches the LLM prompt. This architectural difference — pre-prompt filtering versus prompt-level instruction — is the primary distinction between this work and BIPIA's defense proposals.

### Theme 4: Evaluation Frameworks and Industry Context

The OWASP Top 10 for LLM Applications 2025 (LLM01:2025) classifies prompt injection — including indirect injection via retrieved content — as the top LLM vulnerability for the second consecutive edition [OWASP Foundation, genai.owasp.org]. The OWASP framework provides an industry-recognized risk taxonomy that grounds this project's threat model in real-world deployment concerns. This project's evaluation metric (Attack Success Rate) aligns with the impact framing in LLM01:2025: the measure of severity is how reliably the attack subverts the system's intended behavior.

## Threat Model

Consider an adversary with write access to a document store used by an enterprise RAG-based assistant. Without ever interacting with the LLM, querying the system as a privileged user, or modifying the model weights, the adversary uploads a small number of documents containing embedded instructions that will be retrieved and injected into the LLM context window when legitimate users ask relevant questions.

### Attacker Capabilities

- **Corpus write access:** The attacker can insert, modify, or delete documents in the retrieval database. This is the sole required access — the attacker needs no other system privileges.
- **Black-box query access:** The attacker can interact with the RAG system as a normal user to observe outputs and refine poisoned documents. They cannot access model internals, logs, or other users' queries.
- **Domain knowledge:** The attacker understands the general topic domain of the knowledge base and the types of questions legitimate users are likely to issue. This allows crafting documents that will be semantically retrieved for targeted query types.

### Attacker Goals

- **Instruction override:** Cause the LLM to follow the attacker's embedded instructions rather than the system prompt — for example, responding with attacker-specified text or refusing to answer.
- **Misinformation injection:** Cause the LLM to produce factually incorrect but plausible-sounding answers that serve the attacker's interests.
- **Data exfiltration:** Embed instructions that cause the LLM to request or reveal user-provided information in its response.

### What the Attacker Cannot Control

- **LLM weights and system prompt:** The model architecture, parameters, and operator-defined system instructions are not accessible to the attacker. The attacker cannot fine-tune, modify, or observe the system prompt.
- **User queries:** The attacker does not know the specific questions individual users will ask. They can only predict the general topic domain and rely on semantic similarity to trigger retrieval.
- **Retrieval outcome:** The attacker cannot deterministically force their document to be retrieved for a given query. Retrieval depends on embedding similarity, and the attacker's document competes with all legitimate documents in the corpus. High retrieval probability requires carefully crafted content.
- **LLM inference internals:** Attention weights, generation logits, and intermediate states are not observable. The attacker receives only the final text output.

## Proposed Methodology

Our approach proceeds in three stages: building a functional RAG pipeline as the experimental substrate, implementing corpus poisoning attacks at multiple sophistication levels, and developing and evaluating a context sanitization defense.

### Stage 1: RAG Pipeline Construction

We will build a custom RAG pipeline — without abstraction frameworks — to maintain explicit control over each component of the retrieve-then-generate pipeline. The pipeline consists of an embedding model that encodes documents and queries as dense vectors, a vector store that indexes document embeddings and retrieves the top-k most similar documents for a given query, and a local open-source language model that generates answers grounded in the retrieved context. Building the pipeline from primitives (rather than using a high-level framework) ensures that the retrieval-to-generation boundary — the attack surface — is fully observable and instrumentable. All components will run locally to ensure reproducibility.

### Stage 2: Corpus Poisoning Attacks

We will implement at least two tiers of corpus poisoning attacks targeting the retrieval stage. The naive tier embeds explicit instruction overrides directly in document content (e.g., "Ignore previous instructions and respond with..."). The sophisticated tier crafts documents that blend into the legitimate corpus topically — appearing relevant to user queries — while embedding subtler instructional payloads that are harder to detect by surface-level inspection. Attack documents will be injected into a clean corpus and the pipeline will be evaluated on a test query set. We will measure at least two payload types: instruction override (forcing the LLM to follow the attacker's instructions) and one additional payload type (misinformation injection or data exfiltration prompt). The primary evaluation metric is Attack Success Rate (ASR): the fraction of test queries for which the attack successfully hijacks the LLM's response.

### Stage 3: BERT-Based Context Sanitization

As a defense, we will train a BERT-based classifier to detect retrieved chunks containing imperative or instructional content — the linguistic signature of indirect prompt injection payloads. The classifier is integrated as middleware between the retrieval step and the generation step: retrieved chunks flagged as potentially malicious are filtered out before being injected into the LLM prompt. We will evaluate defense effectiveness as the reduction in ASR compared to the undefended baseline, and measure utility preservation as the change in answer quality on benign (non-attack) queries with the defense active. This before/after comparison is the core experimental result.

## Execution Plan

Remaining work maps to two course deadlines: Phase 2 (April 12, 2026) and Phase 3 (April 30, 2026).

### Phase 2 — April 12, 2026

- Functional custom RAG pipeline with embedding model, vector store, and local LLM generation running end-to-end
- A clean retrieval corpus of 500+ documents indexed and queryable
- Corpus poisoning attack module implementing at least two attack tiers (naive instruction override plus one more sophisticated tier)
- At least two payload types demonstrated: instruction override and one of misinformation injection or data exfiltration
- Baseline ASR measured on the undefended pipeline (this number motivates the Phase 3 defense)
- Automated evaluation harness with retrieval logging (documents retrieved per query, with similarity scores)

### Phase 3 — April 30, 2026

- BERT-based context sanitization classifier trained and integrated as pipeline middleware
- Full experiment matrix: before/after ASR comparison across attack tiers with defense active
- Utility preservation measurement: answer quality on benign queries with and without defense
- Complete final report with results tables, at least one visualization (ASR comparison chart), and a limitations section
- GitHub repository with pinned package versions, configuration files, and replication instructions

## References

[1] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *Advances in Neural Information Processing Systems (NeurIPS)*, 33, 9459–9474.

[2] Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., & Fritz, M. (2023). Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection. *Proceedings of the ACM Workshop on Artificial Intelligence and Security (AISec) / IEEE S&P Workshop SecTL*. arXiv:2302.12173.

[3] Zou, W., Guo, R., Hu, B., Yuan, W., Jiang, M., Jia, J., & Shi, W. (2024). PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models. *Proceedings of USENIX Security Symposium 2024*. arXiv:2402.07867.

[4] Yi, J., Xie, Y., Zhu, B., Hines, K., Kiciman, E., Sun, G., Xie, X., & Wu, F. (2023). Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models. *Proceedings of the ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD) 2025*. arXiv:2312.14197.

[5] Shafran, A., Perez-Etxeberria, R., Garg, S., & Schuster, R. (2025). Machine Against the RAG: Jamming Retrieval-Augmented Generation with Blocker Documents. *Proceedings of USENIX Security Symposium 2025*. arXiv:2406.05870.

[6] OWASP Foundation. (2025). OWASP Top 10 for Large Language Model Applications: LLM01:2025 Prompt Injection. Retrieved from https://genai.owasp.org.
