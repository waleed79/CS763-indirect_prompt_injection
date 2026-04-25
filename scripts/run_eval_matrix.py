"""Cross-model full-matrix evaluation driver for EVAL-V2-01.

Runs every combination of {LLM target} x {defense level} x {attack tier}
by invoking scripts/run_eval.py as a subprocess per cell.  Writes per-cell
JSONL logs under logs/eval_matrix/ and prints a summary table to stdout.

Usage:
    python scripts/run_eval_matrix.py [--dry-run] [--filter-model MODEL]
                                       [--filter-tier TIER]

Phase 3.3 EVAL-V2-01.  Security: T-3.3-01 — all subprocess.run calls use
list argv (never shell=True) to prevent command-injection.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

# ---------------------------------------------------------------------------
# Module-level constants (exact names/values required by test suite)
# ---------------------------------------------------------------------------

MODELS = ["llama3.2:3b", "mistral:7b", "gemma4:31b-cloud"]
TIERS = ["tier1", "tier1b", "tier2", "tier3", "tier4"]
DEFENSES_PRIMARY = ["no_defense", "fused", "causal"]
DEFENSES_FALLBACK = ["no_defense", "fused", "def02"]

# Phase 3.2 sentinel: if this file exists, causal artifacts are ready.
CAUSAL_ARTIFACT_PATH = "models/causal_attribution/ready.flag"

LOG_DIR = "logs/eval_matrix"

# Substring that identifies a cloud model (append --delay 3 for these).
CLOUD_MARKER = "cloud"

# Default corpus and collection used by the matrix driver.
# These match the Phase 2.4 poisoned corpus that contains all 5 attack tiers.
DEFAULT_CORPUS = "data/corpus_poisoned.jsonl"
DEFAULT_COLLECTION = "nq_poisoned_v4"

# Mapping from driver defense names to run_eval.py --defense flag values.
DEFENSE_FLAG_MAP = {
    "no_defense": "off",
    "fused": "fused",
    "causal": "causal",
    "def02": "def02",
}


# ---------------------------------------------------------------------------
# Helper functions (module-level, test-importable)
# ---------------------------------------------------------------------------


def resolve_defenses() -> list[str]:
    """Return the active defense list based on Phase 3.2 artifact availability.

    If CAUSAL_ARTIFACT_PATH exists, return DEFENSES_PRIMARY (includes causal).
    Otherwise print a warning to stderr and return DEFENSES_FALLBACK (def02
    substituted for causal — deadline-risk mitigation per CONTEXT D-12).
    """
    if os.path.exists(CAUSAL_ARTIFACT_PATH):
        return DEFENSES_PRIMARY
    print(
        f"[WARN] Phase 3.2 causal artifact not found at {CAUSAL_ARTIFACT_PATH}; "
        "falling back to DEF-02 per CONTEXT D-12",
        file=sys.stderr,
    )
    return DEFENSES_FALLBACK


def log_path_for(model: str, defense: str, tier: str) -> str:
    """Return the deterministic per-cell log path under LOG_DIR.

    Model name is sanitized: ':' and '/' replaced with '_'.
    """
    safe_model = model.replace(":", "_").replace("/", "_")
    return os.path.join(LOG_DIR, f"{safe_model}__{defense}__{tier}.log")


def build_run_command(
    model: str,
    defense: str,
    tier: str,
    output_path: str,
    corpus: str = DEFAULT_CORPUS,
    collection: str = DEFAULT_COLLECTION,
) -> list[str]:
    """Build the subprocess argv list for a single (model, defense, tier) cell.

    Security (T-3.3-01): returns a list, NEVER a string; caller must use
    subprocess.run(cmd, ...) without shell=True.

    Args:
        model:       Ollama model name (e.g. 'llama3.2:3b').
        defense:     run_eval.py defense flag value (already mapped via
                     DEFENSE_FLAG_MAP if the caller used a driver-level name).
        tier:        Tier name (e.g. 'tier1', 'tier1b', ...).
        output_path: Where run_eval.py writes its JSONL output.
        corpus:      Corpus JSONL path (default DEFAULT_CORPUS).
        collection:  ChromaDB collection name (default DEFAULT_COLLECTION).

    Returns:
        A list[str] of argv entries ready for subprocess.run.
    """
    delay_value = "3" if CLOUD_MARKER in model else "0"

    cmd: list[str] = [
        sys.executable,
        "scripts/run_eval.py",
        "--model", model,
        "--defense", defense,
        "--tier-filter", tier,
        "--output", output_path,
        "--corpus", corpus,
        "--collection", collection,
        "--delay", delay_value,
    ]
    return cmd


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def make_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the matrix driver CLI."""
    parser = argparse.ArgumentParser(
        description="EVAL-V2-01: cross-model full-matrix evaluation driver."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print argv lists without running subprocesses.",
    )
    parser.add_argument(
        "--filter-model",
        choices=MODELS,
        default=None,
        metavar="MODEL",
        help="Run only the specified model (must be in MODELS list).",
    )
    parser.add_argument(
        "--filter-tier",
        choices=TIERS,
        default=None,
        metavar="TIER",
        help="Run only the specified tier (must be in TIERS list).",
    )
    parser.add_argument(
        "--corpus",
        default=DEFAULT_CORPUS,
        help=f"Corpus JSONL path passed to run_eval.py (default: {DEFAULT_CORPUS}).",
    )
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help=f"ChromaDB collection name (default: {DEFAULT_COLLECTION}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the cross-model evaluation matrix.

    Args:
        argv: Argument list (default: sys.argv[1:] when None, or [] when called
              programmatically from tests without CLI context).

    Returns:
        0 if all cells succeeded.
        1 if any cell failed.
        2 if the matrix was interrupted (KeyboardInterrupt).
    """
    # When argv is None and we are NOT running as __main__, default to [] so
    # that argparse does not consume pytest's sys.argv entries.  When running
    # directly as a script, __name__ == "__main__" and the caller passes
    # sys.argv[1:] explicitly via the if __name__ == "__main__" block below.
    if argv is None:
        argv = []
    parser = make_parser()
    args = parser.parse_args(argv)

    # Create log directory if needed.
    os.makedirs(LOG_DIR, exist_ok=True)

    # Resolve defense list (checks Phase 3.2 sentinel).
    defenses = resolve_defenses()

    # Apply any CLI filters.
    models = [args.filter_model] if args.filter_model else MODELS
    tiers = [args.filter_tier] if args.filter_tier else TIERS

    # Track results for summary table.
    summary: list[dict] = []
    any_failed = False

    try:
        for model in models:
            for defense in defenses:
                # Map driver defense name to run_eval.py flag value.
                defense_flag = DEFENSE_FLAG_MAP.get(defense, defense)
                for tier in tiers:
                    output_path = log_path_for(model, defense, tier)
                    cmd = build_run_command(
                        model=model,
                        defense=defense_flag,
                        tier=tier,
                        output_path=output_path,
                        corpus=args.corpus,
                        collection=args.collection,
                    )
                    cell_id = f"{model}/{defense}/{tier}"

                    if args.dry_run:
                        print(cmd)
                        summary.append(
                            {
                                "model": model,
                                "defense": defense,
                                "tier": tier,
                                "status": "dry-run",
                                "log_path": output_path,
                            }
                        )
                    else:
                        # Security: shell=False (list argv only) — T-3.3-01.
                        proc = subprocess.run(cmd, check=False)
                        if proc.returncode != 0:
                            print(
                                f"[FAIL] {cell_id} -> exit {proc.returncode}",
                                file=sys.stderr,
                            )
                            any_failed = True
                            status = f"FAIL(rc={proc.returncode})"
                        else:
                            status = "OK"
                        summary.append(
                            {
                                "model": model,
                                "defense": defense,
                                "tier": tier,
                                "status": status,
                                "log_path": output_path,
                            }
                        )

    except KeyboardInterrupt:
        print("[INTERRUPTED] matrix incomplete", file=sys.stderr)
        return 2

    # Print summary table to stdout.
    _print_summary(summary)

    return 1 if any_failed else 0


def _print_summary(summary: list[dict]) -> None:
    """Print a plain-text summary table of matrix results to stdout."""
    col_w = [20, 12, 8, 24, 50]
    headers = ["model", "defense", "tier", "status", "log_path"]
    sep = "  ".join("-" * w for w in col_w)

    print()
    print("=" * sum(col_w) + "=" * (len(col_w) - 1) * 2)
    print("EVAL-V2-01 Matrix Summary")
    print("=" * sum(col_w) + "=" * (len(col_w) - 1) * 2)
    header_row = "  ".join(h.ljust(w) for h, w in zip(headers, col_w))
    print(header_row)
    print(sep)
    for row in summary:
        line = "  ".join(
            str(row.get(h, "")).ljust(w) for h, w in zip(headers, col_w)
        )
        print(line)
    print()
    n_ok = sum(1 for r in summary if r["status"] == "OK")
    n_fail = sum(1 for r in summary if "FAIL" in r["status"])
    n_dry = sum(1 for r in summary if r["status"] == "dry-run")
    print(
        f"Total cells: {len(summary)}  |  OK: {n_ok}  |  "
        f"FAIL: {n_fail}  |  dry-run: {n_dry}"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
