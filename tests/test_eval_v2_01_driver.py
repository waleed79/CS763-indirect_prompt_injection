"""EVAL-V2-01 cross-model matrix driver smoke tests.

Security: verifies driver uses subprocess with list argv (no shell=True) — T-3.3-01.

Run with:
    pytest tests/test_eval_v2_01_driver.py -x -k smoke
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

try:
    from scripts.run_eval_matrix import main as run_matrix_main
    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _MODULE_AVAILABLE,
    reason="scripts.run_eval_matrix not yet implemented (Wave 2 EVAL-V2-01 plan)",
)


class TestMatrixDriverSmoke:
    def test_smoke_list_argv_no_shell(self):
        """Every subprocess.run call MUST use list argv (never shell=True)."""
        with patch("scripts.run_eval_matrix.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            run_matrix_main()
            assert mock_run.call_count >= 1
            for call in mock_run.call_args_list:
                argv = call[0][0]
                assert isinstance(argv, list), f"expected list argv, got {type(argv).__name__}"
                kwargs = call[1] if len(call) > 1 else {}
                assert kwargs.get("shell", False) is not True, (
                    "subprocess.run must NOT use shell=True (command injection risk, T-3.3-01)"
                )

    def test_smoke_9_combinations_default(self):
        """Default matrix: 3 LLMs × 3 defenses × 5 tiers = 45 invocations (or 9 if per-tier in one call)."""
        with patch("scripts.run_eval_matrix.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            run_matrix_main()
            # Accept 9 (per-tier in single run), 36 (4 tiers, pre-D13 amendment),
            # or 45 (5 tiers per CONTEXT D-13 amendment 2026-04-24: T1+T1b+T2+T3+T4)
            assert mock_run.call_count in (9, 36, 45), (
                f"expected 9, 36, or 45 subprocess calls, got {mock_run.call_count}"
            )

    def test_smoke_argv_contains_required_flags(self):
        """First subprocess call must include --defense, --model, --delay, --collection, --corpus, --output."""
        with patch("scripts.run_eval_matrix.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            run_matrix_main()
            first_argv = mock_run.call_args_list[0][0][0]
            for required in ["--defense", "--model", "--delay", "--collection", "--corpus", "--output"]:
                assert required in first_argv, f"missing {required} in argv: {first_argv}"

    def test_smoke_cloud_model_uses_delay_3(self):
        """Any invocation naming a *-cloud model must pass --delay 3."""
        with patch("scripts.run_eval_matrix.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            run_matrix_main()
            cloud_calls = [
                call for call in mock_run.call_args_list
                if any("cloud" in str(a) for a in call[0][0])
            ]
            assert len(cloud_calls) > 0, "expected at least one gemma4:*-cloud invocation"
            for call in cloud_calls:
                argv = call[0][0]
                delay_idx = argv.index("--delay")
                assert argv[delay_idx + 1] == "3", f"cloud model must use --delay 3, got {argv[delay_idx+1]}"
