"""Phase 7: Honest FPR metrics — gpt-oss extension.

Computes M1/M2/M3 for {gpt-oss:20b-cloud, gpt-oss:120b-cloud} x {fused, def02}
= 4 cells from the Phase 6 v6 logs. M1+M2 require zero cloud calls; M3 issues
~200 calls against gpt-oss:20b-cloud (judge) at --delay 3.

Usage:
    python scripts/run_judge_fpr_gptoss.py --delay 3
    python scripts/run_judge_fpr_gptoss.py --dry-run  # M1 only, no cloud calls
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# Phase 5 importlib reuse (RESEARCH §"Pattern 1" — single source of truth)
# ---------------------------------------------------------------------------
_phase5_path = Path(__file__).parent / "run_judge_fpr.py"
_spec = importlib.util.spec_from_file_location("run_judge_fpr", _phase5_path)
_phase5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_phase5)

parse_verdict       = _phase5.parse_verdict
load_clean_records  = _phase5.load_clean_records   # works as-is on v6 schema (encoding='utf-8' fix in Plan 01)
randomize_ab        = _phase5.randomize_ab
atomic_write_json   = _phase5.atomic_write_json
judge_one           = _phase5.judge_one
JudgeAuthError      = _phase5.JudgeAuthError
JUDGE_SYSTEM_PROMPT = _phase5.JUDGE_SYSTEM_PROMPT
JUDGE_USER_TEMPLATE = _phase5.JUDGE_USER_TEMPLATE
TOP_K               = _phase5.TOP_K       # 5
N_CLEAN             = _phase5.N_CLEAN     # 50
MAX_RETRIES         = _phase5.MAX_RETRIES if hasattr(_phase5, "MAX_RETRIES") else 1

try:
    from ollama import Client
    _OLLAMA_AVAILABLE = True
except ImportError:
    _OLLAMA_AVAILABLE = False
    Client = None  # type: ignore[assignment,misc]

# ---------------------------------------------------------------------------
# Phase 7 D-09 — hardcoded path map; loud-fail at startup if any path missing
# ---------------------------------------------------------------------------
CELL_LOG_MAP: dict[tuple[str, str], str] = {
    ("gpt-oss:20b-cloud",  "fused"): "logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json",
    ("gpt-oss:20b-cloud",  "def02"): "logs/eval_matrix/gptoss20b_cloud__def02__all_tiers_v6.json",
    ("gpt-oss:120b-cloud", "fused"): "logs/eval_matrix/gptoss120b_cloud__fused__all_tiers_v6.json",
    ("gpt-oss:120b-cloud", "def02"): "logs/eval_matrix/gptoss120b_cloud__def02__all_tiers_v6.json",
}
OFF_LOG_MAP: dict[str, str] = {
    "gpt-oss:20b-cloud":  "logs/eval_harness_undefended_gptoss20b_v6.json",
    "gpt-oss:120b-cloud": "logs/eval_harness_undefended_gptoss120b_v6.json",
}
JUDGE_MODEL_DEFAULT = "gpt-oss:20b-cloud"  # D-11 inheritance from Phase 5 D-03


# ---------------------------------------------------------------------------
# Loud-fail helper (D-09)
# ---------------------------------------------------------------------------

def _assert_paths_exist() -> None:
    """Raise AssertionError at startup if any CELL_LOG_MAP or OFF_LOG_MAP path is missing."""
    missing = []
    for (m, d), p in CELL_LOG_MAP.items():
        if not Path(p).exists():
            missing.append(f"  CELL_LOG_MAP[({m!r}, {d!r})] = {p}")
    for m, p in OFF_LOG_MAP.items():
        if not Path(p).exists():
            missing.append(f"  OFF_LOG_MAP[{m!r}] = {p}")
    if missing:
        raise AssertionError("Phase 7 input paths missing:\n" + "\n".join(missing))


# ---------------------------------------------------------------------------
# Per-cell evaluation loop (generalize Phase 5 run_for_defense → run_for_cell)
# ---------------------------------------------------------------------------

def run_for_cell(
    client: "Client",
    args: argparse.Namespace,
    model: str,
    defense: str,
    cell_path: Path,
    off_records: list,
    cache_for_cell: dict,
    rng: random.Random,
) -> "tuple[dict, float, float, float, int]":
    """Run judge evaluation for one (model, defense) cell against 50 clean queries.

    Mirrors run_judge_fpr.py:213-343 run_for_defense, generalized for composite
    (model, defense) keys per Phase 7 PATTERNS.md §"Per-cell loop pattern".

    Args:
        client: Ollama client (or None in dry-run mode).
        args: parsed CLI args.
        model: RAG target model name, e.g. "gpt-oss:20b-cloud".
        defense: defense key, e.g. "fused" or "def02".
        cell_path: path to Phase 6 v6 eval log for this cell.
        off_records: 50 clean records from the matching OFF_LOG_MAP baseline.
        cache_for_cell: pre-loaded verdict cache for this cell.
        rng: seeded Random instance for A/B assignment.

    Returns:
        (verdicts_dict, m1, m2, m3, n_calls)
        verdicts_dict: {qid_str: verdict_record}
        m1: per_chunk_fpr
        m2: answer_preserved_fpr (degraded AND chunks_removed>0)
        m3: judge_fpr (any DEGRADED)
        n_calls: actual cloud calls made (0 in dry-run)
    """
    def_records = load_clean_records(cell_path)

    # RESEARCH §A2 mitigation: assert query strings align by position
    for i, (off_r, def_r) in enumerate(zip(off_records, def_records)):
        assert off_r["query"] == def_r["query"], (
            f"({model},{defense}) record {i}: query mismatch\n"
            f"  off: {off_r['query'][:60]!r}\n"
            f"  def: {def_r['query'][:60]!r}"
        )

    verdicts_dict: dict = {}
    n_calls = 0
    degraded_count = 0
    degraded_with_removal_count = 0

    print(f"\n[({model}, {defense})] Evaluating {N_CLEAN} clean queries ...")

    for i, (off_rec, def_rec) in enumerate(zip(off_records, def_records)):
        qid = str(50 + i)  # Phase 5 D-04 — clean queries occupy indices 50..99
        q = off_rec["query"]
        chunks_removed = def_rec["chunks_removed"]

        print(f"  [{i+1:02d}/{N_CLEAN:02d}] {q[:60]}")

        # --- Cache hit: reuse stored verdict --------------------------------
        if qid in cache_for_cell:
            cached = cache_for_cell[qid]
            verdict_record = cached
            verdict = cached.get("verdict", "PRESERVED")
            print(f"         [cache] verdict={verdict}")

        # --- Dry-run: sentinel record, M1 computed regardless ---------------
        elif args.dry_run:
            # In dry-run, set a sentinel so M2/M3 default to 0.
            # M1 is computed from def_records[*].chunks_removed regardless.
            verdict = "PRESERVED"
            verdict_record = {
                "verdict": "SKIP_DRYRUN",
                "ab_assignment": "n/a",
                "raw_response": "",
                "retry_count": 0,
            }

        # --- Live judge call ------------------------------------------------
        else:
            answer_a, answer_b, ab_assignment = randomize_ab(
                off_rec["answer"], def_rec["answer"], rng
            )

            verdict, raw_response, err = judge_one(
                client, args.model, q, answer_a, answer_b, args.delay
            )
            n_calls += 1

            retry_count = 0
            if verdict is None:
                # D-12: retry once on parse failure / call error
                print(f"         [retry] parse failure — retrying once")
                verdict, raw_response, err = judge_one(
                    client, args.model, q, answer_a, answer_b, args.delay
                )
                n_calls += 1
                retry_count = 1
                if verdict is None:
                    # Still None after retry — treat as PRESERVED (conservative, D-12)
                    verdict = "PRESERVED"
                    raw_response = raw_response or "[retry failed — defaulted to PRESERVED]"

            print(f"         verdict={verdict} | ab={ab_assignment}")

            verdict_record = {
                "verdict": verdict,
                "ab_assignment": ab_assignment,
                "raw_response": raw_response,
                "retry_count": retry_count,
            }

        verdicts_dict[qid] = verdict_record

        # Track degraded counts for M2/M3
        # Note: In dry-run, SKIP_DRYRUN verdict is not DEGRADED, so M2/M3 stay 0.
        v = verdict_record.get("verdict", "PRESERVED")
        if v == "DEGRADED":
            degraded_count += 1
            if chunks_removed > 0:
                degraded_with_removal_count += 1

    # --- Metric computation (mirror run_judge_fpr.py:332-339) ---------------
    # M1: per_chunk_fpr = sum(chunks_removed) / (TOP_K * N_CLEAN)
    m1_numerator = sum(r["chunks_removed"] for r in def_records)
    m1 = m1_numerator / (TOP_K * N_CLEAN)

    # M2: answer_preserved_fpr = count(chunks_removed>0 AND verdict==DEGRADED) / N_CLEAN
    m2 = degraded_with_removal_count / N_CLEAN

    # M3: judge_fpr = count(verdict==DEGRADED) / N_CLEAN
    m3 = degraded_count / N_CLEAN

    print(f"  [({model}, {defense})] M1={m1:.4f}  M2={m2:.4f}  M3={m3:.4f}  calls={n_calls}")

    return verdicts_dict, m1, m2, m3, n_calls


# ---------------------------------------------------------------------------
# Argument parser (mirrors run_judge_fpr.py:350-375)
# ---------------------------------------------------------------------------

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Phase 7 honest FPR (gpt-oss extension)"
    )
    p.add_argument(
        "--model",
        default=JUDGE_MODEL_DEFAULT,
        help="Judge model (default: gpt-oss:20b-cloud per Phase 5 D-03)",
    )
    p.add_argument(
        "--delay",
        type=int,
        default=3,
        help="Seconds between cloud calls (Phase 2.4 cloud convention)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute M1 only; skip cloud calls (D-Discretion fast-path)",
    )
    p.add_argument(
        "--cache",
        type=str,
        default="logs/judge_fpr_gptoss_v7.json.cache",
        help="Per-cell checkpoint cache (D-12 / WR-01)",
    )
    p.add_argument(
        "--out-ablation",
        type=str,
        default="logs/ablation_table_gptoss_v7.json",
    )
    p.add_argument(
        "--out-verdicts",
        type=str,
        default="logs/judge_fpr_gptoss_v7.json",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="RNG seed for A/B randomization",
    )
    return p


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: "list[str] | None" = None) -> int:
    """CLI entry point. Returns 0 on success, 1 on auth error, 2 on config error."""
    args = build_argparser().parse_args(argv)
    _assert_paths_exist()

    rng = random.Random(args.seed)

    # Load both off baselines (D-09) — keyed by model, not by defense
    off_records_by_model: dict[str, list] = {}
    for model, off_fname in OFF_LOG_MAP.items():
        off_records_by_model[model] = load_clean_records(Path(off_fname))

    # Resume from cache if present (D-12 / WR-01)
    cache_path = Path(args.cache)
    all_verdicts: dict = {}
    if cache_path.exists():
        try:
            all_verdicts = json.loads(cache_path.read_text(encoding="utf-8"))
            print(f"[cache] Resuming from {cache_path}")
        except Exception as e:
            print(f"[cache] Ignoring unreadable cache: {e}")
            all_verdicts = {}

    # Optional cloud client (skip instantiation in dry-run to guarantee zero calls)
    client = None
    if not args.dry_run:
        if not _OLLAMA_AVAILABLE:
            print("FATAL: ollama package not available; install or pass --dry-run")
            return 2
        client = Client()

    accumulated: dict[tuple[str, str], tuple[float, float, float, int]] = {}
    try:
        for (model, defense), cell_fname in CELL_LOG_MAP.items():
            cache_for_cell = all_verdicts.get(model, {}).get(defense, {})
            verdicts_for_cell, m1, m2, m3, n = run_for_cell(
                client, args, model, defense,
                Path(cell_fname),
                off_records_by_model[model],
                cache_for_cell,
                rng,
            )
            all_verdicts.setdefault(model, {})[defense] = verdicts_for_cell
            accumulated[(model, defense)] = (m1, m2, m3, n)
            # Per-cell checkpoint (WR-01). Skip in dry-run to avoid writing
            # SKIP_DRYRUN sentinels that would pollute a subsequent real M3 run.
            if not args.dry_run:
                atomic_write_json(cache_path, all_verdicts)
            print(
                f"[cell] ({model}, {defense}): "
                f"M1={m1:.4f} M2={m2:.4f} M3={m3:.4f} n_calls={n}"
            )
    except JudgeAuthError as exc:
        print(f"FATAL: {exc}")
        return 1

    # D-02 ablation table (accumulate in memory, single-write-at-end per WR-01)
    ablation_v7: dict = {}
    for (model, defense), (m1, m2, m3, n) in accumulated.items():
        # Composite-key transform: "gpt-oss:20b-cloud" → "gptoss20b_cloud" (D-02/D-03)
        key = (
            model
            .replace("gpt-oss:", "gptoss")
            .replace("-cloud", "_cloud")
            + "__" + defense
        )
        ablation_v7[key] = {
            "model":                model,
            "defense_mode":         defense,
            "per_chunk_fpr":        m1,
            "answer_preserved_fpr": m2,
            "judge_fpr":            m3,
            "judge_model":          args.model,
            "judge_n_calls":        n,
        }

    # In --dry-run, skip writing ablation/verdicts to avoid clobbering Plan 04 output.
    # Just print the dry-run M1 summary and exit 0.
    if args.dry_run:
        print("[dry-run] M1-only summary:")
        for key, row in ablation_v7.items():
            print(f"  {key}: M1={row['per_chunk_fpr']:.4f}")
        print("[dry-run] Skipping ablation/verdicts write (zero cloud calls made).")
        return 0

    # Composite-key sanity assertion at write-time — guard against typos (D-02/D-03)
    expected = {
        "gptoss20b_cloud__fused",
        "gptoss20b_cloud__def02",
        "gptoss120b_cloud__fused",
        "gptoss120b_cloud__def02",
    }
    assert set(ablation_v7.keys()) == expected, (
        f"D-02/D-03 violation: expected {expected}, got {set(ablation_v7.keys())}"
    )
    assert "no_defense" not in str(ablation_v7), "D-03 violation: trivial no_defense row leaked"

    # D-04 verdicts file (nested model → defense → qid)
    final_verdicts = {
        "phase": "07",
        "judge_model": args.model,
        "judge_prompt_template": JUDGE_USER_TEMPLATE,
        "verdicts": all_verdicts,
    }

    # Single-write-at-end (WR-01) — minimizes Windows non-atomic-replace window
    Path("logs").mkdir(exist_ok=True)
    atomic_write_json(Path(args.out_ablation), ablation_v7)
    atomic_write_json(Path(args.out_verdicts), final_verdicts)
    print(
        f"[done] Wrote {args.out_ablation} ({len(ablation_v7)} cells) "
        f"and {args.out_verdicts}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
