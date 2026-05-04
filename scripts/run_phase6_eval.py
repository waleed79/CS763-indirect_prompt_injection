"""Phase 6 driver: cross-LLM undefended baseline gap fill + defended cross-model matrix.

Wraps 6 single-pass run_eval.py invocations:
    gpt-oss:20b-cloud  x {off, fused, def02}    -> 3 cells
    gpt-oss:120b-cloud x {off, fused, def02}    -> 3 cells

Per CONTEXT D-09a: NO --tier-filter -- single pass produces all 5 tier ASRs.
Per CONTEXT D-01: collection nq_poisoned_v4 (already indexed, 1239 docs).
Per CONTEXT D-02a: post-run mutation adds phase=06, supersedes_phase_02_3, error_count.
Per CONTEXT D-09c: composes logs/eval_matrix/_summary_v6.json with exactly 75 cells.

Wall-clock budget: ~78 min cloud inference (6 cells x 100 queries x ~7-8s each).
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import chromadb

# Same SSOT as run_eval.py -- never redefine ranges
sys.path.insert(0, str(Path(__file__).parent.parent))
from rag.constants import (
    TIER1_ID_START, TIER2_ID_START, TIER3_ID_START,
    TIER1B_ID_START, TIER4_ID_START, ADAPTIVE_ID_START,
)

# --- Constants -----------------------------------------------------------
# (model_id, model_key) -- model_key is filename suffix; matches make_results.py:241-247
PHASE_6_MODELS = [
    ("gpt-oss:20b-cloud",  "gptoss20b"),
    ("gpt-oss:120b-cloud", "gptoss120b"),
]
# (cli_flag, summary_name) -- cli_flag passed to run_eval --defense; summary_name is canonical
PHASE_6_DEFENSES = [
    ("off",   "no_defense"),
    ("fused", "fused"),
    ("def02", "def02"),
]
COLLECTION = "nq_poisoned_v4"
CORPUS = "data/corpus_poisoned.jsonl"
QUERIES = "data/test_queries.json"
LOGS_DIR = Path("logs")
MATRIX_DIR = Path("logs/eval_matrix")
EXISTING_SUMMARY = MATRIX_DIR / "_summary.json"
SUMMARY_V6 = MATRIX_DIR / "_summary_v6.json"
TIERS = ["tier1", "tier1b", "tier2", "tier3", "tier4"]


# --- Pre-flight checks ---------------------------------------------------
def assert_collection_has_all_tiers(collection_name: str = COLLECTION) -> None:
    """D-01a: fail fast if any tier range is empty in the collection.

    Probes nq_poisoned_v4 for at least one passage in each of T1, T2, T3, T1b, T4 ranges.
    """
    client = chromadb.PersistentClient(path=".chroma")
    c = client.get_collection(collection_name)
    ranges = [
        ("T1",  TIER1_ID_START,  TIER2_ID_START),
        ("T2",  TIER2_ID_START,  TIER3_ID_START),
        ("T3",  TIER3_ID_START,  TIER1B_ID_START),
        ("T1b", TIER1B_ID_START, TIER4_ID_START),
        ("T4",  TIER4_ID_START,  ADAPTIVE_ID_START),
    ]
    for name, lo, hi in ranges:
        res = c.get(
            where={"$and": [
                {"passage_id": {"$gte": lo}},
                {"passage_id": {"$lt":  hi}},
            ]},
            limit=1,
            include=["metadatas"],
        )
        assert len(res["ids"]) > 0, (
            f"D-01a sanity assert failed: {collection_name!r} has no passage in "
            f"{name} range [{lo}, {hi}). Stale collection? Refusing to burn 78 min "
            f"of cloud time on a corpus that produces 0% on missing tiers silently."
        )


def preflight_ollama_list() -> None:
    """P6-AUTH: confirm both gpt-oss cloud models are visible to local Ollama daemon."""
    proc = subprocess.run(
        ["ollama", "list"],
        capture_output=True, text=True, check=False, shell=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"P6-AUTH: 'ollama list' failed (returncode={proc.returncode}). "
            f"stderr={proc.stderr!r}. Auth token likely expired -- run 'ollama login'."
        )
    out = proc.stdout
    for model_id, _ in PHASE_6_MODELS:
        if model_id not in out:
            raise RuntimeError(
                f"P6-AUTH: {model_id!r} not in 'ollama list' output. "
                f"Auth token likely expired or model deprovisioned. Run 'ollama login'."
            )


# --- Path resolvers ------------------------------------------------------
def undefended_output_path(model_key: str) -> Path:
    """D-02: logs/eval_harness_undefended_<KEY>_v6.json"""
    return LOGS_DIR / f"eval_harness_undefended_{model_key}_v6.json"


def defended_output_path(model_key: str, defense_name: str) -> Path:
    """D-09b: logs/eval_matrix/<KEY>_cloud__<defense>__all_tiers_v6.json"""
    return MATRIX_DIR / f"{model_key}_cloud__{defense_name}__all_tiers_v6.json"


# --- Subprocess builder + runner ----------------------------------------
def build_run_command(model_id: str, defense_flag: str, output_path: Path) -> list[str]:
    """T-3.3-01: returns list[str] for shell=False subprocess.run.

    Per D-09a, NO --tier-filter -- single-pass produces all 5 tier ASRs.
    """
    return [
        sys.executable, "scripts/run_eval.py",
        "--corpus",     CORPUS,
        "--collection", COLLECTION,
        "--queries",    QUERIES,
        "--defense",    defense_flag,
        "--model",      model_id,
        "--delay",      "3",
        "--output",     str(output_path),
    ]


def run_one(model_id: str, defense_flag: str, output_path: Path) -> int:
    """Run one cell. Returns subprocess returncode."""
    cmd = build_run_command(model_id, defense_flag, output_path)
    print(f"[phase6] $ {' '.join(cmd)}", flush=True)
    proc = subprocess.run(cmd, check=False, shell=False)
    return proc.returncode


# --- Post-run provenance mutation ---------------------------------------
def add_provenance(output_path: Path) -> None:
    """D-02a + D-03a: atomic in-place rewrite to enrich JSON with provenance fields.

    run_eval.py hardcodes phase="03.3" at line 407 -- rewrite phase to "06" here.
    """
    data = json.loads(output_path.read_text(encoding="utf-8"))
    data["phase"] = "06"
    data["supersedes_phase_02_3"] = True
    error_count = sum(
        1 for r in data.get("results", [])
        if isinstance(r.get("answer"), str)
        and r["answer"].startswith("[ERROR:")
    )
    data.setdefault("aggregate", {})["error_count"] = error_count

    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, output_path)


# --- _summary_v6.json composition ---------------------------------------
def compose_summary_v6(run_outputs: list[tuple[str, str, Path]]) -> None:
    """D-09c: emit logs/eval_matrix/_summary_v6.json with exactly 75 cells.

    45 cells from existing _summary.json (verbatim) + 30 new from gpt-oss runs
    (2 models x 3 defenses x 5 tiers).
    """
    if not EXISTING_SUMMARY.exists():
        raise FileNotFoundError(
            f"D-09c requires {EXISTING_SUMMARY} (the 45-cell Phase 03.3-07 baseline). "
            "Re-run Phase 03.3-07 first or stage the file."
        )
    out = list(json.loads(EXISTING_SUMMARY.read_text(encoding="utf-8")))
    if len(out) != 45:
        print(f"[phase6][warn] _summary.json has {len(out)} cells, expected 45.",
              file=sys.stderr)

    for model_id, defense_name, output_path in run_outputs:
        if not output_path.exists():
            print(f"[phase6][warn] missing run output {output_path}", file=sys.stderr)
            continue
        data = json.loads(output_path.read_text(encoding="utf-8"))
        agg = data["aggregate"]
        # Canonicalize model name to underscored form ("gpt-oss:20b-cloud" -> "gpt-oss_20b-cloud")
        model_underscored = data["llm_model"].replace(":", "_")
        for tier in TIERS:
            asr = agg.get(f"asr_{tier}", 0.0)
            out.append({
                "model":           model_underscored,
                "defense":         defense_name,
                "tier":            tier,
                "asr_overall":     asr,
                "asr_tier_native": asr,
                "fpr":             agg.get("fpr", 0.0),
                "retrieval_rate":  agg.get("retrieval_rate", 0.0),
            })

    if len(out) != 75:
        print(f"[phase6][warn] composed summary has {len(out)} cells, expected 75.",
              file=sys.stderr)

    SUMMARY_V6.parent.mkdir(parents=True, exist_ok=True)
    tmp = SUMMARY_V6.with_suffix(SUMMARY_V6.suffix + ".tmp")
    tmp.write_text(json.dumps(out, indent=2), encoding="utf-8")
    os.replace(tmp, SUMMARY_V6)


# --- CLI / main ---------------------------------------------------------
def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Phase 6 cross-LLM undefended + defended cross-model matrix gap fill."
    )
    p.add_argument("--dry-run", action="store_true",
                   help="Print all 6 planned subprocess commands; do not run cloud calls.")
    p.add_argument("--skip-preflight", action="store_true",
                   help="Skip D-01a sanity-assert and ollama-list checks (debug only).")
    p.add_argument("--filter-model", choices=["gptoss20b", "gptoss120b"], default=None,
                   help="Run only one model (default: both).")
    p.add_argument("--filter-defense", choices=["off", "fused", "def02"], default=None,
                   help="Run only one defense (default: all 3).")
    return p


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = []
    args = make_parser().parse_args(argv)

    # Build the cell plan
    plan: list[tuple[str, str, str, str, Path]] = []
    # tuple = (model_id, model_key, defense_flag, defense_name, output_path)
    for model_id, model_key in PHASE_6_MODELS:
        if args.filter_model and model_key != args.filter_model:
            continue
        for defense_flag, defense_name in PHASE_6_DEFENSES:
            if args.filter_defense and defense_flag != args.filter_defense:
                continue
            if defense_flag == "off":
                out = undefended_output_path(model_key)
            else:
                out = defended_output_path(model_key, defense_name)
            plan.append((model_id, model_key, defense_flag, defense_name, out))

    if args.dry_run:
        print(f"[phase6] dry-run: {len(plan)} planned cells")
        for model_id, model_key, defense_flag, defense_name, out in plan:
            cmd = build_run_command(model_id, defense_flag, out)
            print(f"  {model_id} x {defense_name}: {' '.join(cmd)}")
        return 0

    if not args.skip_preflight:
        print("[phase6] pre-flight: assert_collection_has_all_tiers ...", flush=True)
        assert_collection_has_all_tiers(COLLECTION)
        print("[phase6] pre-flight: ollama list ...", flush=True)
        preflight_ollama_list()
        print("[phase6] pre-flight: OK", flush=True)

    # Ensure output dirs exist
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    MATRIX_DIR.mkdir(parents=True, exist_ok=True)

    completed: list[tuple[str, str, Path]] = []
    any_failed = False
    for model_id, model_key, defense_flag, defense_name, out in plan:
        rc = run_one(model_id, defense_flag, out)
        if rc != 0:
            print(f"[phase6][FAIL] {model_id} x {defense_name} returncode={rc}",
                  file=sys.stderr)
            any_failed = True
            continue
        try:
            add_provenance(out)
        except Exception as e:
            print(f"[phase6][FAIL] add_provenance({out}): {e}", file=sys.stderr)
            any_failed = True
            continue
        completed.append((model_id, defense_name, out))
        print(f"[phase6] OK {out}", flush=True)

    # Compose _summary_v6.json from completed cells
    if completed:
        try:
            compose_summary_v6(completed)
            print(f"[phase6] OK {SUMMARY_V6}", flush=True)
        except Exception as e:
            print(f"[phase6][FAIL] compose_summary_v6: {e}", file=sys.stderr)
            any_failed = True

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
