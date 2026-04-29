# IPI ↔ Web-Security Taxonomy: Mapping Classical Vulnerability Classes to Indirect Prompt Injection

## Overview

Indirect Prompt Injection (IPI) in Retrieval-Augmented Generation (RAG) systems is the
re-emergence of well-understood web-security attack patterns in a new execution context.
This document maps classical web-security vulnerability classes to their mechanistic analogs
in IPI attacks on RAG pipelines, anchoring IPI research within the established security
literature. Practitioners who reason fluently about XSS and SSRF can immediately apply
analogous defensive intuitions to LLM-based systems.

Each row identifies: a classical **Web Attack Class** with its canonical reference, the
corresponding **IPI Analog**, the shared **Mechanism**, the applicable **Defensive Control**
in both web and IPI contexts, and a concrete **Citation**.

---

## Taxonomy Table

| Web Attack Class | IPI Analog | Mechanism | Defensive Control | Citation |
|-----------------|------------|-----------|-------------------|----------|
| **Stored (Persistent) Cross-Site Scripting (XSS)** — attacker injects malicious script into a trusted data store (e.g., a database-backed page); when a victim's browser fetches and renders the page, the script executes with the victim's privileges. | **Corpus Poisoning / Indirect Prompt Injection via Retrieved Documents** — attacker inserts adversarially crafted documents into the RAG vector store; when a user query retrieves those documents, the LLM executes the embedded instructions (e.g., overriding its system prompt) in an elevated trust context. | In both cases the attacker plants content in a trusted persistent store that is not directly controlled by the victim at query time. The executing agent (browser / LLM) treats content from that store as trusted, creating a confused-deputy situation. The attack is asynchronous (stored at write time, triggered at read time), and the victim system cannot distinguish injected content from legitimate content at retrieval time. | **Web:** Output encoding (HTML escaping) and Content-Security-Policy prevent script execution; DOM sanitization (DOMPurify) strips injection-enabling tags. **IPI:** Phase 3.1 FusedDefense (4-signal LR meta-classifier over BERT + perplexity + imperative ratio + retrieval z-score) filters injection-bearing chunks before LLM prompt assembly, achieving 0% ASR on Tiers 1–3. Substring-based anchor detection (HACKED, COMPROMISED, INFILTRATED) provides a lightweight first-pass filter analogous to WAF blocklist rules. | OWASP Top 10 A03:2021 Injection; CWE-79 (Improper Neutralization of Input During Web Page Generation); Phase 2.2 corpus poisoning results (plan 03.3-02-PLAN) — Tier 1 ASR = 88% on mistral:7b undefended; Phase 3.1 FusedDefense results (03.1-SUMMARY.md) — fused ASR = 0% on Tiers 1–3. |
| **Server-Side Request Forgery (SSRF)** — attacker supplies a crafted resource reference to a vulnerable server endpoint; the server issues an outbound request to an internal resource (e.g., EC2 metadata at 169.254.169.254) the attacker cannot reach directly, exfiltrating credentials or pivoting to internal services. | **Tool-Call Injection / Agentic RAG Tool Hijack** — in an agentic RAG pipeline where the LLM can call external tools (web search, API endpoints), an attacker injects instructions into retrieved documents that coerce the LLM into issuing tool calls it would not otherwise make, exploiting the LLM's privileged position as a trusted orchestrator. | In both cases, the attacker exploits the server's/agent's elevated capability position. The attacked system has legitimate access to resources the attacker cannot directly reach (internal network / tool APIs with user-level permissions). The attacker only needs to control a single input that the trusted agent will faithfully relay. Both vulnerabilities arise from failure to enforce request-intent verification — the system cannot distinguish attacker-coerced requests from legitimate ones at execution time. | **Web:** Allowlisting outbound request destinations; blocking metadata service IPs (169.254.0.0/16); network segmentation. **IPI:** Tool-call allowlisting (restrict which tools the LLM can invoke); capability scoping (principle of least privilege — read-only tools cannot exfiltrate data); output filtering on tool-call arguments (flag calls whose arguments contain retrieval-derived content absent from the original user query). | OWASP API Security Top 10 API7:2023 (Server Side Request Forgery); CWE-918 (Server-Side Request Forgery); Capital One 2019 AWS breach (SSRF against EC2 metadata endpoint, 106M records exfiltrated); Greshake et al. (2023) "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injections" (demonstrates tool-call injection via retrieved content in agentic pipelines). |
| **Content-Security-Policy (CSP) — W3C Level 3** — a declarative, centralized browser policy that restricts what resources the browser will execute when rendering a page. Rather than sanitizing every injection pathway, CSP configures the interpreter (browser) to enforce source allowlists, moving enforcement from content validation to interpreter configuration. | **Context Sanitization Layer (BERT-based FusedDefense classifier, Phase 3.1)** — a pre-generation filtering layer that intercepts retrieved document chunks before LLM prompt assembly. Rather than enumerating all possible injection patterns, the sanitizer configures the pipeline to discard any chunk scoring above a threshold on injection-bearing signals, regardless of exact payload content. | Both are **declarative, centralized policy layers** applied at the boundary between an untrusted data source and a powerful downstream interpreter. Both shift security from per-content validation (infeasible to enumerate all attack variants) to per-execution context configuration enforced universally. Both impose a utility cost: CSP's `default-src 'none'` breaks applications without careful allowlisting; FusedDefense has FPR = 76% on clean queries (retrieval_rate drops 88% → 34% at threshold = 0.10), directly analogous to an overly strict CSP blocking legitimate resources. Both accept this tradeoff in high-security contexts. | This row IS the defensive control, mapping to the Phase 3.1 FusedDefense classifier (DistilBERT fine-tuned on injection-labeled passages + perplexity + imperative ratio + retrieval z-score meta-LR). At fixed threshold: FPR = 76%, ASR = 0% on Tiers 1–3. At tuned threshold = 0.10: retrieval_rate = 34%, same security guarantee — mirroring CSP's strict/permissive spectrum. | W3C Content Security Policy Level 3 (https://www.w3.org/TR/CSP3/); OWASP Content Security Policy Cheat Sheet; Phase 3.1 FusedDefense results (03.1-SUMMARY.md) — fused_fixed_0.5 achieves 0% ASR on T1/T2/T3 for llama3.2:3b and mistral:7b; threshold = 0.10 calibration documented in plan 03.1-07. |

---

## Implications

This taxonomy establishes that IPI attacks on RAG systems are classical confused-deputy and
injection attacks instantiated in a new execution substrate (transformer LLMs replacing
browsers and application servers). Defensive implications follow directly: perimeter-based
filtering analogous to CSP can achieve 0% ASR on known attack tiers, but with the same
coverage-vs-utility tradeoff documented in web security for decades. The key open research
question — analogous to CSP Level 3's strict-dynamic nonce mechanism — is how to enforce
content integrity guarantees for RAG-retrieved chunks that preserve utility while eliminating
the IPI attack surface.

*Generated for Phase 3.3 Plan 06 (EVAL-08). Canonical reference: `.planning/phases/03.3-quick-evaluation-additions/03.3-06-PLAN.md`.*
