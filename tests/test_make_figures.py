"""Wave 0 stub for scripts/make_figures.py (Wave 1 Plan 03).

Skips until make_figures.py is implemented. After Plan 03 lands, all tests must pass.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
try:
    _spec = importlib.util.spec_from_file_location(
        "make_figures", _SCRIPTS_DIR / "make_figures.py"
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    main = _mod.main
    _AVAILABLE = True
except (AttributeError, FileNotFoundError, Exception):
    _AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AVAILABLE, reason="scripts/make_figures.py not yet implemented (Wave 1 Plan 03)"
)


class TestMakeFiguresSmoke:
    EXPECTED_PNGS = [
        "fig1_arms_race.png",          # D-03
        "fig2_utility_security.png",   # D-04 two-panel
        "fig3_loo_causal.png",         # D-05 two-panel
        "fig4_ratio_sweep.png",        # D-06
        "fig5_cross_model_heatmap.png",# D-12
    ]

    def test_main_runs_with_no_args(self, tmp_path):
        rc = main(["--output-dir", str(tmp_path)])
        assert rc == 0

    def test_all_five_pngs_emitted(self, tmp_path):
        """PH3-02: 5 PNGs in output directory after run, each >1KB (real PNG)."""
        main(["--output-dir", str(tmp_path)])
        for name in self.EXPECTED_PNGS:
            path = tmp_path / name
            assert path.exists(), f"expected {name} to be written"
            assert path.stat().st_size > 1024, f"{name} suspiciously small (<1KB)"

    def test_agg_backend_used(self):
        """Verify Pattern 1 deterministic figure setup is in effect (no display)."""
        import matplotlib
        # After importing make_figures, the backend should be Agg (non-interactive)
        assert matplotlib.get_backend().lower() == "agg", (
            f"matplotlib backend should be Agg, got {matplotlib.get_backend()}"
        )
