"""Tests for rag/generator.py.

Unit tests mock the Ollama client — no Ollama server required.
Integration test (marked integration) uses the real Ollama server.

Run unit tests:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_generator.py -v -m "not integration" --timeout=30
Run all:
    & "C:\\Users\\muham\\Softwares\\anaconda3\\envs\\rag-security\\python.exe" -m pytest tests/test_generator.py -v --timeout=60
"""
from unittest.mock import MagicMock, patch

import pytest

from rag.generator import Generator
from rag.retriever import RetrievalResult


# ── Fixtures ──────────────────────────────────────────────────────────────────


def _mock_client(answer: str = "Paris is the capital of France.") -> MagicMock:
    """Return a mock Ollama Client that returns *answer* on chat()."""
    client = MagicMock()
    # Simulate the list() response for assert_model_available
    model_obj = MagicMock()
    model_obj.model = "llama3.2:3b"
    client.list.return_value = MagicMock(models=[model_obj])
    # Simulate chat() response
    msg = MagicMock()
    msg.content = answer
    resp = MagicMock()
    resp.message = msg
    client.chat.return_value = resp
    return client


# ── Unit tests (mocked Ollama) ────────────────────────────────────────────────


class TestGeneratorInit:
    def test_default_model(self):
        gen = Generator()
        assert gen.model == "llama3.2:3b"

    def test_custom_model(self):
        gen = Generator(model="mistral:7b")
        assert gen.model == "mistral:7b"


class TestGeneratorIsReachable:
    def test_is_reachable_true_when_list_succeeds(self):
        gen = Generator()
        gen._client = _mock_client()
        assert gen.is_reachable() is True

    def test_is_reachable_false_when_list_raises(self):
        gen = Generator()
        gen._client = MagicMock()
        gen._client.list.side_effect = ConnectionError("refused")
        assert gen.is_reachable() is False


class TestGeneratorAssertModelAvailable:
    def test_passes_when_model_present(self):
        gen = Generator(model="llama3.2:3b")
        gen._client = _mock_client()
        gen.assert_model_available()  # must not raise

    def test_raises_when_model_missing(self):
        gen = Generator(model="nonexistent:model")
        gen._client = _mock_client()  # has llama3.2:3b, not nonexistent
        with pytest.raises(RuntimeError, match="nonexistent:model"):
            gen.assert_model_available()

    def test_raises_when_ollama_unreachable(self):
        gen = Generator()
        gen._client = MagicMock()
        gen._client.list.side_effect = ConnectionError("refused")
        with pytest.raises(RuntimeError, match="not reachable"):
            gen.assert_model_available()


class TestGeneratorGenerate:
    def test_generate_returns_string(self):
        gen = Generator()
        gen._client = _mock_client("Water boils at 100C.")
        result = gen.generate("what is the boiling point?", [])
        assert isinstance(result, str)
        assert "100" in result

    def test_generate_passes_context_to_prompt(self):
        gen = Generator()
        gen._client = _mock_client()
        hits = [RetrievalResult(chunk_id="c0", text="Paris is a city.", score=0.9, metadata={})]
        gen.generate("what city?", hits)
        call_args = gen._client.chat.call_args
        messages = call_args[1]["messages"] if "messages" in call_args[1] else call_args[0][1]
        user_msg = next(m for m in messages if m["role"] == "user")
        assert "Paris is a city." in user_msg["content"]

    def test_generate_uses_deterministic_options(self):
        gen = Generator(seed=42)
        gen._client = _mock_client()
        gen.generate("q", [])
        call_kwargs = gen._client.chat.call_args[1]
        opts = call_kwargs.get("options", {})
        assert opts.get("temperature") == 0.0
        assert opts.get("seed") == 42

    def test_generate_accepts_dict_chunks(self):
        """generate() must work with plain dicts as well as RetrievalResult."""
        gen = Generator()
        gen._client = _mock_client("answer")
        result = gen.generate("q", [{"text": "some context"}])
        assert isinstance(result, str)


# ── Phase 2.4 LLM-as-judge output parsing tests ───────────────────────────────


class TestJudgeOutputParsing:
    """Verify the parse_judge_output() function from scripts/run_judge.py.

    Tests the YES/NO binary parsing used for EVAL-V2-02.
    Import the function directly so this test fails if run_judge.py is missing
    or the function signature changes.
    """

    def _parse(self, content: str) -> "bool | None":
        """Mirror the parsing logic from run_judge.py parse_judge_output()."""
        from scripts.run_judge import parse_judge_output
        return parse_judge_output(content)

    def test_yes_parses_true(self):
        assert self._parse("YES") is True

    def test_yes_with_trailing_whitespace(self):
        assert self._parse("YES\n") is True
        assert self._parse("  YES  ") is True

    def test_yes_case_insensitive(self):
        assert self._parse("yes") is True
        assert self._parse("Yes") is True

    def test_no_parses_false(self):
        assert self._parse("NO") is False
        assert self._parse("no") is False
        assert self._parse("  NO  ") is False

    def test_unknown_returns_none(self):
        """Malformed/unexpected judge output must return None, not raise."""
        assert self._parse("MAYBE") is None
        assert self._parse("I'm not sure.") is None
        assert self._parse("") is None


# ── Phase 3.1: DEF-02 system_prompt tests (Wave 0 stubs) ─────────────────────


class TestGenerateSystemPrompt:
    """Phase 3.1: DEF-02 system_prompt parameter on generator.generate()."""

    def test_def02_constant_exists_and_has_must_not(self):
        """DEF_02_SYSTEM_PROMPT constant must exist in rag.generator and contain 'MUST NOT'."""
        from rag.generator import DEF_02_SYSTEM_PROMPT
        assert isinstance(DEF_02_SYSTEM_PROMPT, str)
        assert "MUST NOT" in DEF_02_SYSTEM_PROMPT
        assert len(DEF_02_SYSTEM_PROMPT) > 50

    def test_generate_accepts_system_prompt_kwarg(self):
        """generate() must accept system_prompt=... without raising TypeError."""
        gen = Generator()
        gen._client = _mock_client("answer text")
        # Should not raise TypeError: generate() got unexpected keyword argument
        result = gen.generate("q", [], system_prompt="Custom system prompt here.")
        assert isinstance(result, str)


# ── Integration test (real Ollama) ────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.timeout(60)
class TestGeneratorIntegration:
    def test_is_reachable_live(self):
        gen = Generator()
        assert gen.is_reachable(), "Ollama server must be running for this test"

    def test_generate_live(self):
        gen = Generator()
        if not gen.is_reachable():
            pytest.skip("Ollama not running")
        result = gen.generate(
            "What is 2 + 2?",
            [RetrievalResult(chunk_id="c0", text="2 + 2 = 4.", score=0.99, metadata={})],
        )
        assert isinstance(result, str)
        assert len(result) > 0
