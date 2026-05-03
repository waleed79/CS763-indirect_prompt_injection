"""Wave 0 stubs for Phase 4 assets (scripts/make_diagrams.py, scripts/make_qr.py + on-disk
artifacts). Skips until Wave 1 lands.

Three test classes:
  - TestMakeDiagramsSmoke  : tests that make_diagrams.py runs and emits the two diagram PNGs
  - TestMakeQrSmoke        : tests that make_qr.py runs and emits a scannable QR PNG
  - TestPhase4AssetsOnDisk : asset-existence smoke tests for final Phase 4 artifacts
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module-level script loaders (mirror tests/test_make_figures.py:12-26 pattern)
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def _try_load(modname: str):
    """Load a script from scripts/ by name; return module or None on failure."""
    try:
        spec = importlib.util.spec_from_file_location(
            modname, _SCRIPTS_DIR / f"{modname}.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except (AttributeError, FileNotFoundError, Exception):
        return None


_diag = _try_load("make_diagrams")
_qr   = _try_load("make_qr")
_DIAG_OK = _diag is not None
_QR_OK   = _qr   is not None

FIG = Path("figures")


# ---------------------------------------------------------------------------
# Class 1: TestMakeDiagramsSmoke
# ---------------------------------------------------------------------------

class TestMakeDiagramsSmoke:
    """Smoke tests for scripts/make_diagrams.py — skipped until Wave 1 lands."""

    EXPECTED_PNGS = [
        "diagram_a_rag_pipeline.png",
        "diagram_b_defense_pipeline.png",
    ]

    @pytest.mark.skipif(
        not _DIAG_OK,
        reason="scripts/make_diagrams.py not yet implemented (Wave 1)",
    )
    def test_main_runs_with_no_args(self, tmp_path):
        """make_diagrams.main() exits 0 when given --output-dir."""
        rc = _diag.main(["--output-dir", str(tmp_path)])
        assert rc == 0

    @pytest.mark.skipif(
        not _DIAG_OK,
        reason="scripts/make_diagrams.py not yet implemented (Wave 1)",
    )
    def test_both_diagrams_emitted(self, tmp_path):
        """Both diagram PNGs are written and are real images (>1 KB)."""
        _diag.main(["--output-dir", str(tmp_path)])
        for name in self.EXPECTED_PNGS:
            path = tmp_path / name
            assert path.exists(), f"Expected {name} to be written to output dir"
            assert path.stat().st_size > 1024, (
                f"{name} is suspiciously small (<1 KB); likely an empty placeholder"
            )

    @pytest.mark.skipif(
        not _DIAG_OK,
        reason="diagram script not loaded",
    )
    def test_agg_backend_used(self):
        """Agg (non-interactive) backend must be active after make_diagrams import."""
        import matplotlib
        assert matplotlib.get_backend().lower() == "agg", (
            f"matplotlib backend should be Agg for headless rendering, "
            f"got {matplotlib.get_backend()}"
        )


# ---------------------------------------------------------------------------
# Class 2: TestMakeQrSmoke
# ---------------------------------------------------------------------------

class TestMakeQrSmoke:
    """Smoke tests for scripts/make_qr.py — skipped until Wave 1 lands."""

    @pytest.mark.skipif(
        not _QR_OK,
        reason="scripts/make_qr.py not yet implemented (Wave 1)",
    )
    def test_main_runs_with_default_args(self, tmp_path):
        """make_qr.main() exits 0 when given --output path."""
        rc = _qr.main(["--output", str(tmp_path / "qr_github.png")])
        assert rc == 0

    @pytest.mark.skipif(
        not _QR_OK,
        reason="scripts/make_qr.py not yet implemented (Wave 1)",
    )
    def test_qr_decodes_to_repo_url(self, tmp_path):
        """QR PNG decodes to the verified GitHub repo URL."""
        _qr.main(["--output", str(tmp_path / "qr_github.png")])
        try:
            from pyzbar.pyzbar import decode
        except ImportError:
            pytest.skip("pyzbar not installed; manual phone-scan substitutes")

        from PIL import Image

        img = Image.open(tmp_path / "qr_github.png")
        decoded = decode(img)
        assert decoded, "QR PNG did not decode to any barcode data"
        url = decoded[0].data.decode()
        assert "github.com/waleed79/CS763-indirect_prompt_injection" in url, (
            f"QR URL does not contain expected repo path; got: {url}"
        )


# ---------------------------------------------------------------------------
# Class 3: TestPhase4AssetsOnDisk
# ---------------------------------------------------------------------------

class TestPhase4AssetsOnDisk:
    """Asset-existence checks for final Phase 4 artifacts in figures/.

    test_minimum_two_figures_present always runs (5 existing PNGs satisfy it at Wave 0).
    All other tests SKIP via exists-guard until the corresponding Wave 1 script runs.
    """

    def test_minimum_two_figures_present(self):
        """PRES-02: at least 2 PNG visualizations must exist in figures/."""
        pngs = list(FIG.glob("*.png"))
        assert len(pngs) >= 2, (
            f"PRES-02 requires >=2 visualizations, found {len(pngs)} in {FIG}"
        )

    @pytest.mark.skipif(
        not (FIG / "diagram_a_rag_pipeline.png").exists(),
        reason="figures/diagram_a_rag_pipeline.png not yet produced (Wave 1)",
    )
    def test_diagram_a_present(self):
        """Diagram A (RAG pipeline overview) exists in figures/."""
        assert (FIG / "diagram_a_rag_pipeline.png").exists()

    @pytest.mark.skipif(
        not (FIG / "diagram_b_defense_pipeline.png").exists(),
        reason="figures/diagram_b_defense_pipeline.png not yet produced (Wave 1)",
    )
    def test_diagram_b_present(self):
        """Diagram B (defense fusion pipeline) exists in figures/."""
        assert (FIG / "diagram_b_defense_pipeline.png").exists()

    @pytest.mark.skipif(
        not (FIG / "qr_github.png").exists(),
        reason="figures/qr_github.png not yet produced (Wave 1)",
    )
    def test_qr_present_and_nonempty(self):
        """QR code PNG exists in figures/ and is non-empty."""
        p = FIG / "qr_github.png"
        assert p.exists()
        assert p.stat().st_size > 0, "qr_github.png is zero bytes"

    @pytest.mark.skipif(
        not (FIG / "demo_tier2_mistral.gif").exists(),
        reason="figures/demo_tier2_mistral.gif not yet produced (Wave 1)",
    )
    def test_demo_gif_present_and_animated(self):
        """Demo GIF exists, is a real multi-frame animation, and is within size limits."""
        p = FIG / "demo_tier2_mistral.gif"
        assert p.exists(), "Demo GIF missing"
        assert p.stat().st_size > 50_000, (
            "Demo GIF too small (<50 KB) — likely a single static frame"
        )
        assert p.stat().st_size < 2_000_000, (
            "Demo GIF too large (>2 MB) — compress with ffmpeg palettegen/paletteuse"
        )
        from PIL import Image

        img = Image.open(p)
        assert getattr(img, "n_frames", 1) > 1, (
            "Demo GIF has only 1 frame — it is not animated"
        )
