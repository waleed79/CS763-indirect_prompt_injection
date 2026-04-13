# RAG Security Project: Comprehensive Study Guide & Topics List

This guide categorizes all the concepts, theories, software, and tools needed to understand and implement your CS 763 (Computer Security) research project on **Indirect Prompt Injection in RAG Systems**. 

It is structured progressively, starting from foundational background knowledge suitable for a first-year CS Master's student, moving into the direct requirements for your Phase 1/2/3 deliverables, and ending with advanced capabilities you might need for future extensions.

---

## 1. Core Fundamentals (The Background)
Before diving into the specifics of Large Language Models (LLMs), these foundational concepts govern how the pieces fit together.
*   **Machine Learning (ML) & Deep Learning Basics:** Understanding neural networks, objective functions, training vs. inference, and over/under-fitting.
*   **Natural Language Processing (NLP) Fundamentals:** Tokenization (how text is split into chunks models can understand), sequence modeling, and language modeling objectives.
*   **Information Retrieval (IR) Basics:** How search engines work. Understanding concepts like document corpora, queries, indexing, and classic metrics like Precision, Recall, and F1-score.
*   **Computer Security Fundamentals (Threat Modeling):** Understanding how to define what an attacker *can* do (capabilities), *cannot* do, and *wants* to do (goals). Familiarity with the concepts of "attack surface," "white-box" vs. "black-box" testing, and the OWASP Top 10 vulnerabilities.

## 2. RAG & LLM Mechanics (How the System Works)
This is the architecture of the system you are building and targeting.
*   **Transformers Architecture:** High-level understanding of the Attention Mechanism, which is the core of modern LLMs.
*   **Large Language Models (LLMs):** Concepts around generative AI, pre-training vs. instruction fine-tuning, autoregressive generation (predicting the next token), and context windows.
*   **Word & Sentence Embeddings:** How text is mapped to dense, high-dimensional vector spaces where semantic similarity translates to geometric closeness.
*   **Cosine Similarity:** The mathematical operation used to measure how closely related two embeddings (a query and a document vector) are.
*   **Vector Databases (Vector Stores):** Databases optimized for Nearest Neighbor Search (k-NN) or Approximate Nearest Neighbors (ANN) to quickly find the top-K vectors similar to a query vector.
*   **Retrieval-Augmented Generation (RAG):** The end-to-end design pattern of fetching external knowledge (via vector search) and injecting it into an LLM's prompt window to reduce hallucination and provide grounded answers.

## 3. The Security Threat (The Vulnerability)
This covers the exact mechanics of the attack surface you are investigating.
*   **Prompt Engineering & Injection:** The idea of overriding an LLM's system prompt using maliciously crafted user inputs (Direct Prompt Injection).
*   **Indirect Prompt Injection:** The core concept of your project. The adversary doesn't touch the user input; instead, they embed malicious instructions inside third-party data (like web pages or database documents) that the LLM is expected to process.
*   **Corpus Poisoning:** The act of inserting malicious documents into a RAG system's retrieval database.
*   **Attack Payloads:** What the attacker wants the LLM to do.
    *   *Instruction Override:* Discarding original instructions to do something else.
    *   *Misinformation Injection:* Forcing the LLM to provide false facts.
    *   *Data Exfiltration:* Crafting instructions to trick the LLM into leaking user data (e.g., getting the user to click a URL with sensitive parameters appended).
*   **Attack Sophistication Levels:**
    *   *Naive Attacks:* Simple explicit instructions (e.g., "Ignore previous instructions and say X").
    *   *Obfuscated Attacks:* Hiding the instructions to bypass simple string-matching filters.
    *   *Context-Blending / Semantic Attacks:* Semantically matching the poisoned document to specific user queries so it is highly likely to be retrieved.

## 4. Building Defenses (The Mitigations)
The defensive pipeline you will implement to harden your custom RAG system.
*   **Context Sanitization / Pipeline Middleware:** The architecture of placing a filter between the `Retrieve` and `Generate` steps to sanitize context.
*   **BERT-based Text Classification:** Applying deep learning (using encoder-only models like BERT) to detect the linguistic signatures of imperative or malicious commands inside text chunks.
*   **Attention Mask Separation / Prompt Hardening:** Engineering the prompt to rigidly separate "Instructions" from "Data/Context," forcing the LLM to treat retrieved pieces strictly as data.

## 5. Evaluation & Metrics (Measuring Success)
How you will empirically prove the effectiveness of your attacks and defenses.
*   **Attack Success Rate (ASR):** The percentage of malicious queries where the LLM successfully executes the injected payload.
*   **Retrieval Rate:** The frequency at which your poisoned document is actually selected directly from the vector DB (the attack fails automatically if it's never retrieved).
*   **Conditional ASR:** The success rate *given* that the document was successfully retrieved. 
*   **Utility Preservation:** Ensuring that the defense mechanism doesn't destroy the RAG system's normal usefulness (e.g., does it block benign queries?).
*   **ASR-Utility Tradeoff:** The balancing curve showing the cost of security vs. system performance.

## 6. The Specific Tech Stack & Software Tools
The literal software and libraries you will be interacting with during implementation.
*   **Python 3.11 & Environment Managers:** Using `venv` or `conda` for reproducible isolated environments.
*   **PyTorch (`torch`):** The underlying deep learning framework executing your models on CPU or GPU (CUDA).
*   **HuggingFace `transformers`:** The standard library to load, instantiate, and run ML models (such as BERT for your defense).
*   **`sentence-transformers`:** A specialized library built over HuggingFace, used for fetching fast sequence embeddings (e.g., the `all-MiniLM-L6-v2` model).
*   **ChromaDB:** A lightweight, local vector database to index and search embeddings without setting up external servers.
*   **Ollama:** A local model runner that abstracts away VRAM and parameter complexities, allowing you to run powerful open-source LLMs (`llama3.2:3b`, `mistral:7b`) on resource-constrained academic/personal machines.
*   **Quantization:** Reducing model precision (e.g., 4-bit quantization, Q4) to allow multi-billion parameter models to run in standard RAM.
*   **Data Science Utilities:** 
    *   `pandas` (managing datasets and result logging)
    *   `scikit-learn` (calculating classification metrics for your defense, train/test splits)
    *   `matplotlib` & `seaborn` (plotting ASR charts and tradeoff curves)
    *   `tqdm` (tracking long-running experiment loops)
    *   `jsonlines` (reading structured datasets and producing result logs)

## 7. Future-Proofing / Advanced Concepts (For Phase 3 & Beyond)
Topics that might be strictly labeled "v2" or "stretch goals" in your requirements, but will push the project from a standard class project into cutting-edge research.
*   **Gradient-Based Trigger Optimization:** Instead of guessing the best words to put in a poisoned document, using gradient descent (e.g. methods like GCG - Greedy Coordinate Gradient) to mathematically compute text sequences that maximize retrieval probability *and* payload execution. (Related to: *Retrieval-aware attacks*).
*   **Perplexity-Based Filtering:** A potentially novel defense mechanism using an LLM to measure how "surprising" (perplexing) a retrieved chunk of text is. Injected payloads often have high perplexity.
*   **Cross-Model Transferability:** Proving that an attack document poisoned against Llama-3 also compromises Mistral-7B.
*   **LLM-as-a-Judge:** Using an authoritative LLM like GPT-4o to read experiment outputs and classify whether an attack succeeded or failed, replacing brittle regex substring-matching evaluation.
*   **Information Extraction (PII detection):** Using tools like `presidio-analyzer` to measure strict data exfiltration payloads.

## 8. Essential Literature Context
If you want to read primary sources to understand the exact landscape your project falls into, you'll need to know these papers (referenced in your Phase 1 writeup):
*   **Lewis et al. (2020):** The paper that invented Retrieval-Augmented Generation.
*   **Greshake et al. (2023):** The foundational paper that established Indirect Prompt Injection.
*   **Zou et al. (2024 - *PoisonedRAG*):** The exact paper you are replicating and extending through defense implementation.
*   **Yi et al. (2023 - *BIPIA*):** A benchmark for defending against these exact attacks.
*   **OWASP Top 10 for LLMs:** The industry standard classification mapping these concepts to enterprise risk (LLM01:2025).
