"""Wave 0 stub for docs/phase3_results.md (Wave 2 Plan 05).

Skips until the writeup is committed. After Plan 05 lands, all tests must pass.
"""
from __future__ import annotations
from pathlib import Path

import pytest

WRITEUP_PATH = Path(__file__).parent.parent / "docs" / "phase3_results.md"

pytestmark = pytest.mark.skipif(
    not WRITEUP_PATH.exists(),
    reason="docs/phase3_results.md not yet written (Wave 2 Plan 05)",
)


class TestWriteupStructure:
    def setup_method(self):
        self.text = WRITEUP_PATH.read_text(encoding="utf-8")

    def test_thirteen_top_level_sections(self):
        """CONTEXT D-09: exactly 13 numbered sections (## 1. through ## 13.)."""
        for n in range(1, 14):
            assert f"## {n}." in self.text, f"missing section ## {n}."

    def test_all_five_figures_referenced(self):
        """PH3-02 + EVAL-03: writeup must reference each figure filename."""
        for fig in [
            "fig1_arms_race",
            "fig2_utility_security",
            "fig3_loo_causal",
            "fig4_ratio_sweep",
            "fig5_cross_model_heatmap",
        ]:
            assert fig in self.text, f"writeup missing reference to {fig}"

    def test_eight_academic_citations_present(self):
        """PH3-05: §11 + §12 cite the 8 canonical references from CONTEXT canonical_refs."""
        for cite in [
            "Greshake",          # arXiv 2302.12173
            "PoisonedRAG",       # Zou 2024 arXiv 2402.07867
            "BadRAG",            # arXiv 2406.00083
            "OWASP",             # OWASP LLM01:2025 + Top 10 + API
            "CSP",               # W3C CSP Level 3
            "CWE-79",            # XSS taxonomy row 1
            "CWE-918",           # SSRF taxonomy row 2
            "Capital One",       # 2019 SSRF breach
        ]:
            assert cite in self.text, f"writeup missing citation: {cite}"

    def test_section_5_loo_negative_result_cites_doc(self):
        """D-16: §5 must cite logs/loo_negative_result_analysis.md."""
        assert "loo_negative_result_analysis" in self.text, (
            "§5 must cite logs/loo_negative_result_analysis.md per D-16"
        )

    def test_section_9_three_required_limitations(self):
        """SC-5 / PH3-03: §9 names 3 required limitations."""
        # Limitation (a) T3/T4 zero-baseline puzzle
        assert "T3" in self.text and "T4" in self.text and "0%" in self.text
        # Limitation (b) DEF-02 counter-productive priming
        assert "DEF-02" in self.text and ("counter" in self.text.lower() or "priming" in self.text.lower())
        # Limitation (c) per-chunk vs cross-chunk-aware mechanism
        assert "redundant" in self.text.lower() or "redundancy" in self.text.lower()

    def test_section_10_failure_cases(self):
        """EVAL-04 + PH3-04: §10 enumerates failure cases."""
        # §10 must exist (covered by 13-section test) and discuss false-negative cases
        assert "false negative" in self.text.lower() or "failure case" in self.text.lower()

    def test_hero_findings_in_section_8(self):
        """D-15: gemma4 0%-everywhere (§8e) and Tier 1b homoglyph DEF-02 bypass (§8f)."""
        assert "gemma4" in self.text and "0%" in self.text
        assert "22%" in self.text and "35%" in self.text  # T1b 22% → 35% under DEF-02

    def test_loo_inverted_aucs_in_section_5(self):
        """D-05: §5 must cite the inverted AUC values."""
        assert "0.372" in self.text, "§5 must cite llama LOO AUC 0.372"
        assert "0.410" in self.text, "§5 must cite mistral LOO AUC 0.410"

    def test_utility_security_tradeoff_numbers(self):
        """SC-4: §4 must cite 88%→50% retrieval drop and 76% FPR cost."""
        assert "88%" in self.text and "50%" in self.text
        assert "76%" in self.text

    def test_ssrf_citation_correct(self):
        """RESEARCH Citation Correction 1: §12 must cite SSRF as API7:2023, not API10:2023."""
        assert "API7:2023" in self.text, "SSRF must be cited as API7:2023"
        assert "API10:2023" not in self.text, "API10:2023 is wrong attribution for SSRF"

    def test_attribot_lodo_disambiguated(self):
        """RESEARCH Citation Correction 2: §11 cites both 2602.14161 (LODO) and 2411.15102 (AttriBoT)."""
        assert "2602.14161" in self.text, "§11 must cite arXiv 2602.14161 for LODO methodology"
        # AttriBoT may appear in §13 Future Work; either §11 or §13 is acceptable for 2411.15102
        assert "2411.15102" in self.text, "AttriBoT (2411.15102) must be cited (§11 or §13)"

    def test_cr02_disclosure(self):
        """RESEARCH Open Question 4: §1 honestly discloses CR-02 (Signal 4 zero LR weight)."""
        # Wording flexibility — accept either "Signal 4" + ("zero" or "calibration") or "3-signal" or "CR-02"
        assert (
            ("Signal 4" in self.text and ("zero" in self.text.lower() or "calibration" in self.text.lower()))
            or "3-signal" in self.text
            or "CR-02" in self.text
        ), "§1 must honestly disclose CR-02 Signal 4 calibration issue"
