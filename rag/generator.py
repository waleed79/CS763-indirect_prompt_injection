"""Ollama-backed LLM generator for the RAG pipeline (RAG-01).

Uses the Ollama Python client (>=0.6) through a Client instance (not module-
level functions) so that tests can inject a fake client without monkeypatching
the global module (RESEARCH.md Anti-Patterns).

Decision refs: D-04 (llama3.2:3b), Pattern 4 (RAG context prompt)
"""
from __future__ import annotations

from ollama import Client, ResponseError


class Generator:
    """Wraps Ollama chat() to produce answers grounded in retrieved context.

    Parameters
    ----------
    model:
        Ollama model tag (e.g. ``llama3.2:3b``).
    host:
        Ollama server base URL.
    seed:
        Random seed passed to Ollama's sampler for reproducibility.
    """

    _SYSTEM_PROMPT = (
        "You are a helpful assistant. Answer the user's question using ONLY "
        "the information in the CONTEXT section below. If the context does "
        "not contain the answer, say so explicitly."
    )

    def __init__(
        self,
        model: str = "llama3.2:3b",
        host: str = "http://localhost:11434",
        seed: int = 42,
    ) -> None:
        self.model = model
        self.host = host
        self.seed = seed
        self._client = Client(host=host)

    # ── Health check ──────────────────────────────────────────────────────────

    def is_reachable(self) -> bool:
        """Return True if the Ollama server responds to a ping.

        Used by the notebook health-check cell and RAGPipeline init.
        """
        try:
            self._client.list()
            return True
        except Exception:
            return False

    def assert_model_available(self) -> None:
        """Raise RuntimeError with a helpful message if the model is not pulled.

        Raises
        ------
        RuntimeError
            If Ollama is unreachable or the model is missing.
        """
        try:
            response = self._client.list()
            # ollama>=0.6 returns an object with a .models attribute
            models_obj = response.models if hasattr(response, "models") else response.get("models", [])
            names = {
                (m.model if hasattr(m, "model") else m.get("model", ""))
                for m in models_obj
            }
        except Exception as exc:
            raise RuntimeError(
                f"Ollama not reachable at {self.host}. "
                "Start it with: ollama serve"
            ) from exc

        if self.model not in names:
            raise RuntimeError(
                f"Model '{self.model}' is not pulled. "
                f"Run: ollama pull {self.model}"
            )

    # ── Generation ────────────────────────────────────────────────────────────

    def generate(self, query: str, context_chunks: list) -> str:
        """Produce an LLM answer conditioned on *query* and *context_chunks*.

        Parameters
        ----------
        query:
            The user's question.
        context_chunks:
            List of dicts or RetrievalResult objects. Must have a ``text``
            attribute or key.

        Returns
        -------
        str
            Raw LLM response text.

        Raises
        ------
        RuntimeError
            If Ollama is unreachable or the model is missing (404).
        """
        context_block = "\n\n".join(
            f"[{i + 1}] {(c.text if hasattr(c, 'text') else c['text'])}"
            for i, c in enumerate(context_chunks)
        )
        user_prompt = f"CONTEXT:\n{context_block}\n\nQUESTION: {query}"

        try:
            resp = self._client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.0, "seed": self.seed},
            )
        except ResponseError as exc:
            if exc.status_code == 404:
                raise RuntimeError(
                    f"Model '{self.model}' not found. "
                    f"Run: ollama pull {self.model}"
                ) from exc
            raise

        # ollama>=0.6 returns a ChatResponse object
        msg = resp.message if hasattr(resp, "message") else resp["message"]
        content = msg.content if hasattr(msg, "content") else msg["content"]
        return content
