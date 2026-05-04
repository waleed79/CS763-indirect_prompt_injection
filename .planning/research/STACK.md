# Stack Research

**Domain:** RAG Security Research (Indirect Prompt Injection Attack + Defense)
**Researched:** 2026-03-31
**Confidence:** MEDIUM-HIGH (versions verified via PyPI; library selection based on domain expertise and ecosystem maturity, not live web search)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11 | Runtime | Best balance of library compatibility and performance. 3.12+ has edge-case issues with some ML libraries. 3.11 is the safe choice for torch/transformers/faiss compatibility. |
| PyTorch | >=2.7,<2.12 | ML framework | Required by transformers, sentence-transformers, and any fine-tuning work. The universal substrate for ML research. Pin to 2.x LTS range. |
| transformers | >=4.45,<6.0 | Model loading & inference | HuggingFace transformers is the standard for loading open-source LLMs and BERT-based classifiers. Needed for both the RAG LLM and the defense classifier. |
| sentence-transformers | >=5.0,<6.0 | Embedding models | The standard way to encode text into vectors for retrieval. Wraps HuggingFace models with cosine-similarity-optimized APIs. |
| ChromaDB | >=1.5,<2.0 | Vector store | Simplest local vector store for research. Zero external infrastructure, Python-native, good enough for <100K documents. Perfect for a course project. |
| Ollama (python client) | >=0.6,<1.0 | Local LLM inference | Run open-source LLMs locally (Llama 3, Mistral, Phi-3) without GPU cluster. Ollama handles model management, quantization, and serving. Critical for reproducibility without API costs. |
| openai | >=2.0,<3.0 | API-based LLM inference (optional) | If budget allows or for comparison experiments, OpenAI's API provides GPT-4o access. Use as a secondary target LLM to test attack transferability. |

### Embedding Models (run via sentence-transformers)

| Model | Parameters | Purpose | Why Recommended |
|-------|-----------|---------|-----------------|
| `all-MiniLM-L6-v2` | 22M | Primary embedding model | Fast, lightweight, well-studied. Ideal for rapid iteration. 384-dim embeddings fit easily in memory. |
| `BAAI/bge-small-en-v1.5` | 33M | Alternative / comparison | BGE models are top performers on MTEB leaderboard. Good for showing attack generalizes across embedding models. |
| `all-mpnet-base-v2` | 110M | Higher-quality baseline | If you need to show attacks work on higher-quality retrieval too. 768-dim. |

**Rationale:** Use `all-MiniLM-L6-v2` as the default. It is the most commonly used embedding model in RAG research, making results comparable to prior work. Switch to BGE for ablation studies showing attack transferability.

### LLM Targets (run via Ollama)

| Model | Parameters | Purpose | Why Recommended |
|-------|-----------|---------|-----------------|
| `llama3.2:3b` | 3B | Primary attack target | Small enough to run on personal hardware. Llama 3 family is the most studied open-source LLM. |
| `mistral:7b` | 7B | Secondary target (if GPU available) | Different architecture, tests generalizability. Strong instruction-following makes it a good injection target. |
| `phi3:mini` | 3.8B | Alternative small target | Microsoft's Phi-3 is competitive at small scale. Good for diversity of targets. |

**Rationale:** Start with `llama3.2:3b` via Ollama. It runs on CPU (slowly) or a single consumer GPU. The project doesn't need GPT-4-class models -- the attack surface exists at all model scales, and smaller models are actually *easier* to hijack (weaker instruction-following).

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| scikit-learn | >=1.6,<2.0 | Metrics, classification utilities | Computing precision/recall/F1 for defense classifier, cosine similarity utilities, train/test splits |
| datasets (HuggingFace) | >=4.0,<5.0 | Dataset loading | Loading standard QA datasets (Natural Questions, SQuAD) as the clean retrieval corpus |
| pandas | >=2.0 | Data manipulation | Organizing experiment results, attack success rates, generating comparison tables |
| matplotlib + seaborn | latest | Visualization | Plotting ASR curves, defense effectiveness charts, retrieval quality metrics for the presentation |
| numpy | >=1.24 | Numerical operations | Array manipulation for embeddings, similarity calculations |
| tqdm | latest | Progress bars | Long-running attack/defense experiments need progress tracking |
| jsonlines / json | stdlib | Data serialization | Storing poisoned corpus, experiment configs, results logs |

### Defense-Specific Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| transformers (BERT) | (same as above) | Defense classifier | Load `bert-base-uncased` or `distilbert-base-uncased` for the context sanitization classifier that detects imperative/injected commands in retrieved chunks |
| presidio-analyzer | >=2.2 | PII detection baseline | Optional: detect data exfiltration payloads in LLM outputs as a defense signal |
| re (stdlib) | stdlib | Pattern matching | Rule-based detection of injection patterns (imperative sentences, "ignore previous", prompt markers) |

### Attack-Specific Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| garak | >=0.14 | LLM vulnerability scanner (reference) | Use as reference for attack taxonomy and prompt injection patterns, but build custom attacks for the RAG-specific pipeline |
| Custom code | N/A | Corpus poisoning engine | You will write this. No off-the-shelf library does RAG-specific indirect injection well. The attack is: craft documents with embedded instructions, insert into vector store, measure retrieval + hijack rates. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Jupyter Notebook / Lab | Experiment iteration | Run attacks interactively, visualize results, iterate on injection strategies |
| pytest | Testing | Validate pipeline components, ensure reproducibility |
| conda / venv | Environment isolation | Use conda for PyTorch/CUDA compatibility, or venv if CPU-only |
| Ollama (server) | Local LLM serving | Install separately (not pip). Manages model downloads and serves inference API on localhost:11434 |
| git + GitHub | Version control + submission | Required deliverable: GitHub repo with replication instructions |

## Installation

```bash
# Create environment
conda create -n rag-security python=3.11 -y
conda activate rag-security

# Core ML stack
pip install torch torchvision  # or conda install pytorch for CUDA support
pip install transformers>=4.45
pip install sentence-transformers>=5.0

# Vector store
pip install chromadb>=1.5

# LLM inference
pip install ollama>=0.6
pip install openai>=2.0  # optional, for API-based experiments

# Data & metrics
pip install datasets>=4.0
pip install scikit-learn>=1.6
pip install pandas>=2.0
pip install matplotlib seaborn

# Defense utilities
pip install presidio-analyzer>=2.2  # optional

# Attack reference
pip install garak>=0.14  # optional, for reference patterns

# Dev tools
pip install jupyter pytest tqdm

# Install Ollama server separately:
# https://ollama.com/download
# Then: ollama pull llama3.2:3b
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| ChromaDB | FAISS (`faiss-cpu` 1.13.2) | If you need sub-millisecond retrieval at >1M vectors. Overkill for this project's scale (<10K docs), and ChromaDB is simpler to set up. FAISS lacks built-in persistence and metadata filtering. |
| ChromaDB | Pinecone / Weaviate | Never for this project. Cloud-hosted vector DBs add complexity, cost, and network dependency. Research needs local reproducibility. |
| Ollama | vLLM (0.18.1) | If you have a dedicated GPU server and need high-throughput batch inference. vLLM is faster but harder to set up on Windows and requires more VRAM. Use Ollama for simplicity. |
| Ollama | HuggingFace `transformers.pipeline` | If you want to skip the Ollama server and load models directly. More control but more boilerplate. Ollama abstracts model management cleanly. |
| sentence-transformers | Direct HuggingFace model + mean pooling | Only if you need custom pooling strategies. sentence-transformers handles this correctly out of the box. |
| LangChain (1.2.14) | Custom RAG pipeline | For this project: build custom. LangChain adds massive dependency bloat and abstraction layers that obscure the attack surface. You need to understand every step of retrieve-then-generate to attack it. |
| LlamaIndex (0.14.19) | Custom RAG pipeline | Same rationale as LangChain. Abstraction hides the components you need to attack. Build the pipeline manually with ~100 lines of code. |
| garak | Custom attack suite | garak is a general LLM vulnerability scanner, not RAG-specific. Use it for reference/inspiration but write custom corpus poisoning attacks. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LangChain / LlamaIndex for the RAG pipeline | These frameworks abstract away the retrieval-to-generation boundary, which is exactly the attack surface you are studying. You need explicit control over: (1) how documents are embedded, (2) how retrieval scores work, (3) how context is injected into prompts, (4) how the LLM processes that context. Abstraction is the enemy of security research. | Build a custom pipeline: `sentence-transformers` for embedding, `chromadb` for storage/retrieval, `ollama` for generation. ~100-150 lines of Python. |
| OpenAI embeddings API | Costs money per call, rate limits slow iteration, and you cannot inspect the embedding model internals (needed for understanding why poisoned docs get retrieved). | `sentence-transformers` with open-source models. Free, local, inspectable. |
| Pinecone / managed vector DBs | Adds network latency, costs, requires API keys, and cannot be easily reproduced by graders. | ChromaDB. Local, free, zero-config. |
| `langchain-experimental` security tools | These are wrappers around basic patterns. For a security research project, you need to understand the primitives, not use someone else's defense wrapper. | Build defenses from scratch using `transformers` (BERT classifier) and custom heuristics. |
| Python 3.12+ | Some ML libraries (especially torch extensions, faiss) may have compatibility issues. 3.11 is the safe, well-tested choice. | Python 3.11 |

## Stack Patterns by Variant

**If running on CPU only (no GPU):**
- Use `all-MiniLM-L6-v2` (smallest embedding model)
- Use `llama3.2:3b` via Ollama with Q4 quantization (runs on CPU, ~4GB RAM)
- Expect ~5-10 seconds per LLM inference. Budget experiment time accordingly.
- ChromaDB will be fine -- vector search is not the bottleneck.

**If you have a CUDA GPU (even a GTX 1060+ with 6GB VRAM):**
- Same embedding model, but inference will be instant
- `llama3.2:3b` via Ollama will be near real-time
- Can try `mistral:7b` for cross-model experiments
- Install `torch` with CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu121`

**If you have access to a university HPC cluster:**
- Can run `mistral:7b` or even `llama3:8b` natively via transformers
- Use `vllm` for batch inference over large experiment matrices
- Still use ChromaDB locally -- the bottleneck is LLM inference, not retrieval

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| torch >=2.7 | transformers >=4.45 | Transformers 5.x requires torch 2.x. Check CUDA version matches torch build. |
| sentence-transformers >=5.0 | transformers >=4.45 | sentence-transformers 5.x pins transformers compatibility. |
| chromadb >=1.5 | sentence-transformers | ChromaDB can use sentence-transformers as its default embedding function. |
| ollama >=0.6 | Python 3.11 | Pure Python client, no special requirements. Server must be installed separately. |
| faiss-cpu 1.13.2 | numpy >=1.24 | If using FAISS instead of ChromaDB. |

## Architecture Note for Roadmap

The stack is intentionally minimal. A RAG security research pipeline has exactly 4 components:

1. **Corpus** -- A set of text documents (clean + poisoned). Just JSON/JSONL files.
2. **Embedder** -- `sentence-transformers` encodes text to vectors.
3. **Retriever** -- `chromadb` stores vectors and returns top-k by cosine similarity.
4. **Generator** -- `ollama` takes a prompt (user query + retrieved context) and produces output.

The attack injects malicious documents into (1) that are designed to be retrieved in (3) and hijack (4). The defense sits between (3) and (4), filtering retrieved context.

Do NOT over-engineer this. The value is in the attack/defense methodology, not the infrastructure.

## Sources

- PyPI package index (pip index versions) -- verified all version numbers on 2026-03-31 (HIGH confidence)
- HuggingFace model hub -- embedding model recommendations based on MTEB leaderboard standings (MEDIUM confidence, leaderboard changes frequently but these models are well-established)
- Ollama model library -- model sizes and quantization options (HIGH confidence, well-documented)
- Training data knowledge of RAG architecture patterns and security research methodology (MEDIUM confidence)
- garak project -- LLM vulnerability scanning patterns (MEDIUM confidence, verified package exists on PyPI)

**Gaps:**
- Could not verify current MTEB leaderboard rankings (WebSearch unavailable). The recommended embedding models are established choices but newer models may outperform them. This does not affect the project -- any reasonable embedding model will demonstrate the attack surface.
- Could not verify Ollama's current model catalog. The recommended models (llama3.2, mistral, phi3) were available as of early 2025 and are almost certainly still available.
- promptbench (0.0.4) exists on PyPI but appears unmaintained. Not recommended.
- rebuff (0.0.5) exists but is also unmaintained (last release was 2023). Not recommended.

---
*Stack research for: RAG Security Research (Indirect Prompt Injection)*
*Researched: 2026-03-31*
