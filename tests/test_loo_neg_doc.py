"""Wave 0 stub for logs/loo_negative_result_analysis.md (Wave 1 Plan 04, D-16).

Skips until the analysis doc is committed. After Plan 04 lands, all tests must pass.
"""
from __future__ import annotations
from pathlib import Path

import pytest

LOO_DOC = Path(__file__).parent.parent / "logs" / "loo_negative_result_analysis.md"

pytestmark = pytest.mark.skipif(
    not LOO_DOC.exists(),
    reason="logs/loo_negative_result_analysis.md not yet written (Wave 1 Plan 04, D-16)",
)


class TestLooNegDocStructure:
    def setup_method(self):
        self.text = LOO_DOC.read_text(encoding="utf-8")

    def test_six_required_sections(self):
        """D-16: 6 required subsections."""
        for n in range(1, 7):
            assert f"## {n}." in self.text, f"missing section ## {n}."

    def test_per_model_aucs_cited(self):
        """D-16 §2 + RESEARCH line 343: per-model LOO AUCs."""
        assert "0.372" in self.text, "must cite llama AUC 0.372"
        assert "0.410" in self.text, "must cite mistral AUC 0.410"

    def test_redundancy_mechanism_explained(self):
        """D-16 §3 (i) + (ii): injected chunks redundant + clean chunks unique."""
        assert "redundant" in self.text.lower() or "redundancy" in self.text.lower()
        assert "anti-correlat" in self.text.lower() or "inverted" in self.text.lower() or "below random" in self.text.lower()

    def test_counterfactual_section(self):
        """D-16 §4: counterfactual ('what would have to be true for LOO to work')."""
        assert "counterfactual" in self.text.lower() or "would have to be" in self.text.lower() or "if injected chunks" in self.text.lower()

    def test_pointers_section(self):
        """D-16 §6: pointers must include Greshake + def02_priming_analysis."""
        assert "Greshake" in self.text, "§6 Pointers must cite Greshake et al. 2023"
        assert "def02_priming_analysis" in self.text or "DEF-02" in self.text, (
            "§6 Pointers must reference def02_priming_analysis as analog"
        )
