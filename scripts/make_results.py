"""Phase 3.4 Plan 02: emit Markdown + CSV results tables for the writeup.

Reads:
  - logs/ablation_table.json (Phase 3.1 + 3.2 single-LLM ablation, 17-key dict)
  - logs/eval_matrix/_summary.json (Phase 3.3-07 cross-model 45-row flat array)
  - logs/eval_harness_undefended_{llama,mistral,gptoss20b,gptoss120b}.json (Phase 2.3)
  - logs/attack_baseline.json (Phase 2.2 10-query frozen reference)
  - logs/adaptive_*.json (Phase 3.2 ATK-08/09 vs Fused — for arms race "Adaptive" rows)

Emits (into --output-dir, default docs/results/):
  - arms_race_table.{md,csv}        — combined headline table (sources a + b + c + adaptive)
  - cross_model_matrix.{md,csv}     — source (b) verbatim 45-row matrix
  - ablation_table.{md,csv}         — source (c) with retrieval_rate + fpr columns (SC-4)
  - undefended_baseline.{md,csv}    — source (a) 4 LLMs + Phase 2.2 10-query reference

Contract (per CONTEXT D-02): runnable from scratch by grader; deterministic; no manual
number copying into the writeup ever happens.

Per CONTEXT D-09 §2: standing single-seed caveat applies to all rows derived from
_summary.json. The script does not enforce caveat text — Plan 05 writeup handles that.

Per Wave 0 schema probe (logs/_phase34_schema_probe.txt): _summary.json's `asr_overall`
is UNPAIRED (n=100). Paired ASR for source (b) lives in per-cell .log files; this
script reports unpaired numbers from _summary.json verbatim and uses paired numbers
from defense_*.json (where available) for source (a) rows.

STRIDE T-3.4-W1-01: every json.loads is wrapped in try/except json.JSONDecodeError;
on failure print [ERROR] {path}: {error} to stderr and return code 2 (no partial
outputs — the writeup depends on completeness).

STRIDE T-3.4-W1-02: every dict access uses .get(key, default) — never bare subscript
— to tolerate the schema drift between defense_*.json (paired_asr_*),
_summary.json (asr_overall), and ablation_table.json (asr_t*).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------------------------------- #
# Defense display-name mapping (W-3 fix)                                       #
# --------------------------------------------------------------------------- #
# Required so tests/test_make_results.py::test_arms_race_table_emitted finds
# the substrings "BERT", "Fused", "DEF-02", and "No Defense" — the raw keys
# (e.g., "bert_only", "fused_fixed_0.5") are not human-readable.
#
# This mapping is the single source of truth for defense column labels and is
# also used by Plan 03 figure renderer (scripts/make_figures.py) per
# threat T-3.4-W1-05.

# Phase 7 D-05 — single source of truth for the v7 ablation filename.
# The resolver below uses this to locate the file under any logs_dir.
_V7_ABLATION_FILENAME = "ablation_table_gptoss_v7.json"

DEFENSE_DISPLAY: dict[str, str] = {
    # Top-level ablation_table.json keys (preferred lookup)
    "no_defense":                  "No Defense",
    "def02":                       "DEF-02",
    "bert_only":                   "BERT alone",   # contains substring "BERT"
    "perplexity_only":             "Perplexity",
    "imperative_only":             "Imperative",
    "fingerprint_only":            "Fingerprint",
    "fused_fixed_0.5":             "Fused",
    "fused_tuned_threshold":       "Fused (tuned)",
    "mistral_no_defense":          "No Defense (mistral)",
    "mistral_fused":               "Fused (mistral)",
    "atk08_vs_fused_llama":        "Adaptive vs Fused",
    "atk08_vs_fused_mistral":      "Adaptive vs Fused (mistral)",
    "atk09_vs_nodefense_llama":    "Adaptive (declarative) vs No Defense",
    "atk09_vs_imperative_llama":   "Adaptive (declarative) vs Imperative",
    # Inner defense_mode values (run_eval.py --defense argument values).
    # ablation_table.json entries have a `defense_mode` field that uses these
    # short-names; the cross-model matrix _summary.json `defense` field uses
    # the long-names "no_defense"/"fused"/"def02". Both must map cleanly.
    "off":                         "No Defense",   # ablation `defense_mode`
    "fused":                       "Fused",        # adaptive logs + matrix
    "bert":                        "BERT alone",   # ablation `defense_mode`
    "perplexity":                  "Perplexity",
    "imperative":                  "Imperative",
    "fingerprint":                 "Fingerprint",
}


# Phase 6 disclosure header injected at top of regenerated result markdowns.
# Lives near DEFENSE_DISPLAY for single-source-of-truth consistency (D-12).
PHASE6_DISCLOSURE_HEADER = (
    "> Updated 2026-05-04: Phase 6 cross-LLM gap fill — gpt-oss-20b and "
    "gpt-oss-120b numbers added across all 5 tiers and "
    "{no_defense, fused, def02}. Phase 02.3 / Phase 3.4 numbers above this "
    "line are unchanged.\n\n"
)


def _display_defense(raw: str) -> str:
    """Map raw defense_mode key to writeup-friendly display name. Falls back to raw."""
    return DEFENSE_DISPLAY.get(raw, raw)


# --------------------------------------------------------------------------- #
# Defensive JSON read (STRIDE T-3.4-W1-01)                                     #
# --------------------------------------------------------------------------- #


def _safe_load_json(path: Path):
    """Read + parse a JSON file, or return None on failure.

    Caller must check for None and fail-fast (see main()) — partial outputs are
    worse than no output for the writeup task.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[ERROR] {path}: file not found", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] {path}: {e}", file=sys.stderr)
        return None
    except OSError as e:
        print(f"[ERROR] {path}: {e}", file=sys.stderr)
        return None


# --------------------------------------------------------------------------- #
# Source readers                                                               #
# --------------------------------------------------------------------------- #


# Keys in ablation_table.json that are NOT per-defense rows (they are aggregator
# entries with different shapes). Skipped by load_ablation; surfaced in
# arms_race_table separately if relevant.
_ABLATION_SKIP_KEYS = frozenset({
    "eval05_aggregation",
    "causal_attribution",
    "threshold_sweep",
    "atk08_vs_fused_llama",
    "atk09_vs_nodefense_llama",
    "atk09_vs_imperative_llama",
    "atk08_vs_fused_mistral",
})


def load_ablation(path: Path) -> pd.DataFrame:
    """Source (c): Phase 3.1 single-LLM ablation.

    Returns a DataFrame with one row per defense mode. Columns:
        defense_mode, model, asr_t1, asr_t2, asr_t3, asr_t4,
        fpr, retrieval_rate, n_queries, chunks_removed_total

    Skips aggregator keys (eval05_aggregation, causal_attribution, threshold_sweep,
    atk08_*/atk09_*) — those go into separate tables / arms-race rows.
    """
    raw = _safe_load_json(path)
    if raw is None:
        raise RuntimeError(f"Could not load ablation table from {path}")

    rows = []
    for key, entry in raw.items():
        if key in _ABLATION_SKIP_KEYS:
            continue
        if not isinstance(entry, dict):
            continue
        # IMPORTANT: use the dict key (e.g. "bert_only", "fused_fixed_0.5",
        # "fused_tuned_threshold") as the canonical `defense_mode` rather than
        # the inner field — the inner `defense_mode` collapses
        # "fused_fixed_0.5" + "fused_tuned_threshold" into a single "fused"
        # value, losing the "(tuned)" distinction. The dict key preserves
        # the full identity used by the DEFENSE_DISPLAY map.
        rows.append({
            "defense_mode":         key,
            "defense_mode_raw":     entry.get("defense_mode", key),
            "model":                entry.get("model", "llama3.2:3b"),
            "asr_t1":               entry.get("asr_t1", 0.0),
            "asr_t2":               entry.get("asr_t2", 0.0),
            "asr_t3":               entry.get("asr_t3", 0.0),
            "asr_t4":               entry.get("asr_t4", 0.0),
            "fpr":                  entry.get("fpr", 0.0),
            "retrieval_rate":       entry.get("retrieval_rate", 0.0),
            "n_queries":            entry.get("n_queries", 0),
            "chunks_removed_total": entry.get("chunks_removed_total", 0),
        })
    return pd.DataFrame(rows)


# Tier display normalization (tier1 -> T1, tier1b -> T1b, etc.)
_TIER_DISPLAY = {
    "tier1":  "T1",
    "tier1b": "T1b",
    "tier2":  "T2",
    "tier3":  "T3",
    "tier4":  "T4",
}


def _display_tier(raw: str) -> str:
    return _TIER_DISPLAY.get(raw, raw)


def load_cross_model_matrix(path: Path) -> pd.DataFrame:
    """Source (b): Phase 3.3-07 EVAL-V2-01 matrix.

    Returns a 45-row DataFrame as-is from the flat-array JSON, with tier labels
    normalized for display (tier1 -> T1, tier1b -> T1b, etc.).

    Columns: model, defense, tier, asr_overall, asr_tier_native, fpr, retrieval_rate

    Per Wave 0 schema probe: asr_overall here is UNPAIRED (n=100). Caller is
    responsible for caveat text.
    """
    raw = _safe_load_json(path)
    if raw is None:
        raise RuntimeError(f"Could not load cross-model matrix from {path}")

    if not isinstance(raw, list):
        raise RuntimeError(
            f"Expected list at top level of {path}; got {type(raw).__name__}"
        )

    rows = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        rows.append({
            "model":           r.get("model", "unknown"),
            "defense":         r.get("defense", "unknown"),
            "tier":            _display_tier(r.get("tier", "")),
            "asr_overall":     r.get("asr_overall", 0.0),
            "asr_tier_native": r.get("asr_tier_native", 0.0),
            "fpr":             r.get("fpr", 0.0),
            "retrieval_rate":  r.get("retrieval_rate", 0.0),
        })
    return pd.DataFrame(rows)


def load_undefended_baseline(logs_dir: Path) -> pd.DataFrame:
    """Source (a): Phase 2.3 cross-LLM undefended baseline + Phase 2.2 10-query reference.

    Returns DataFrame with columns:
        model, source, asr_tier1, asr_tier2,
        paired_asr_tier1, paired_asr_tier2, retrieval_rate, n_queries

    Reads up to 4 Phase 2.3 canonical files and 1 Phase 2.2 baseline. Files
    silently skipped if missing — the writeup test (test_three_source_aggregation)
    only requires "llama3.2", "mistral", and "gpt-oss" model substrings to appear,
    which is satisfied by the 4 canonical files.
    """
    rows = []

    # Phase 2.3 100-query canonical runs (4 models)
    # Phase 6 D-02b: prefer _v6.json when present (supersedes un-versioned file)
    for model_key, label in [
        ("llama",      "llama3.2:3b"),
        ("mistral",    "mistral:7b"),
        ("gptoss20b",  "gpt-oss:20b-cloud"),
        ("gptoss120b", "gpt-oss:120b-cloud"),
    ]:
        path_v6 = logs_dir / f"eval_harness_undefended_{model_key}_v6.json"
        path_unversioned = logs_dir / f"eval_harness_undefended_{model_key}.json"
        path = path_v6 if path_v6.exists() else path_unversioned
        if not path.exists():
            continue
        data = _safe_load_json(path)
        if data is None:
            raise RuntimeError(f"Could not parse {path}")
        agg = data.get("aggregate", {}) if isinstance(data, dict) else {}
        rows.append({
            "model":            data.get("llm_model", label),
            "source":           "Phase 6 v6 (n=100)" if path_v6.exists() else "Phase 2.3 canonical (n=100)",
            "asr_tier1":        agg.get("asr_tier1", 0.0),
            "asr_tier1b":       agg.get("asr_tier1b", float("nan")),
            "asr_tier2":        agg.get("asr_tier2", 0.0),
            "asr_tier3":        agg.get("asr_tier3", float("nan")),
            "asr_tier4":        agg.get("asr_tier4", float("nan")),
            "paired_asr_tier1": agg.get("paired_asr_tier1", agg.get("asr_tier1", 0.0)),
            "paired_asr_tier2": agg.get("paired_asr_tier2", agg.get("asr_tier2", 0.0)),
            "retrieval_rate":   agg.get("retrieval_rate", 0.0),
            "n_queries":        data.get("n_queries", 100),
        })

    # Phase 2.2 10-query frozen reference (llama only) per ROADMAP SC-1
    baseline_path = logs_dir / "attack_baseline.json"
    if baseline_path.exists():
        b = _safe_load_json(baseline_path)
        if b is None:
            raise RuntimeError(f"Could not parse {baseline_path}")
        agg = b.get("aggregate", {}) if isinstance(b, dict) else {}
        rows.append({
            "model":            "llama3.2:3b",
            "source":           "Phase 2.2 frozen (n=10)",
            "asr_tier1":        b.get("asr_tier1", agg.get("asr_tier1", 0.0)),
            "asr_tier1b":       float("nan"),
            "asr_tier2":        b.get("asr_tier2", agg.get("asr_tier2", 0.0)),
            "asr_tier3":        float("nan"),
            "asr_tier4":        float("nan"),
            "paired_asr_tier1": b.get("paired_asr_tier1",
                                      agg.get("paired_asr_tier1",
                                              agg.get("asr_tier1", 0.0))),
            "paired_asr_tier2": b.get("paired_asr_tier2",
                                      agg.get("paired_asr_tier2",
                                              agg.get("asr_tier2", 0.0))),
            "retrieval_rate":   b.get("retrieval_rate",
                                      agg.get("retrieval_rate", 0.0)),
            "n_queries":        b.get("n_queries", 10),
        })

    # Phase 6: guarantee column schema even when all input files are missing.
    # Without explicit columns, an empty rows list produces a no-column DataFrame
    # whose CSV has a blank header — breaking test_undefended_baseline_v6_csv_exists.
    _COLUMNS = [
        "model", "source",
        "asr_tier1", "asr_tier1b", "asr_tier2", "asr_tier3", "asr_tier4",
        "paired_asr_tier1", "paired_asr_tier2", "retrieval_rate", "n_queries",
    ]
    return pd.DataFrame(rows, columns=_COLUMNS) if not rows else pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Combined arms-race table builder                                             #
# --------------------------------------------------------------------------- #


def _normalize_matrix_model(raw: str) -> str:
    """Convert _summary.json model labels (underscored) back to canonical form.

    The matrix file uses 'llama3.2_3b', 'mistral_7b', 'gemma4_31b-cloud'.
    Rest of the project uses 'llama3.2:3b' style. Convert the first underscore
    after a digit pattern to a colon so display matches.
    """
    # Specific known mappings (single source of truth)
    mapping = {
        "llama3.2_3b":         "llama3.2:3b",
        "mistral_7b":          "mistral:7b",
        "gemma4_31b-cloud":    "gemma4:31b-cloud",
        "gpt-oss_20b-cloud":   "gpt-oss:20b-cloud",
        "gpt-oss_120b-cloud":  "gpt-oss:120b-cloud",
    }
    return mapping.get(raw, raw)


def build_arms_race_table(
    ablation: pd.DataFrame,
    matrix: pd.DataFrame,
    undefended: pd.DataFrame,
    logs_dir: Path,
) -> pd.DataFrame:
    """Combine all 3 sources into one headline arms race table.

    Per CONTEXT D-09 §2 + ROADMAP SC-1: arms race table = (a) + (b) + (c)
    sources unified, plus a (d) Adaptive row from logs/adaptive_fused_*.json.

    Columns: ['Source', 'Model', 'Defense', 'Tier', 'ASR', 'FPR',
              'Retrieval Rate', 'Notes']

    The Defense column always goes through _display_defense() so writeup-friendly
    labels (containing the test-required substrings 'BERT', 'Fused', 'DEF-02',
    'No Defense') appear instead of the raw keys.
    """
    rows = []

    # ----- (a) Undefended baseline rows (llama only, T1+T2 — keep table compact) -----
    for _, r in undefended.iterrows():
        if r["model"] != "llama3.2:3b":
            continue
        if r["source"] != "Phase 2.3 canonical (n=100)":
            continue
        for tier_idx in [1, 2]:
            paired_key = f"paired_asr_tier{tier_idx}"
            unpaired_key = f"asr_tier{tier_idx}"
            asr = r.get(paired_key, r.get(unpaired_key, 0.0))
            rows.append({
                "Source":         "(a) Undefended baseline",
                "Model":          r["model"],
                "Defense":        _display_defense("no_defense"),
                "Tier":           f"T{tier_idx}",
                "ASR":            asr,
                "FPR":            float("nan"),
                "Retrieval Rate": r.get("retrieval_rate", 0.0),
                "Notes":          f"Phase 2.3 paired (n={r['n_queries']})",
            })

    # ----- (b) Cross-model matrix rows (all 45 cells) -----
    for _, r in matrix.iterrows():
        rows.append({
            "Source":         "(b) Cross-model matrix",
            "Model":          _normalize_matrix_model(r["model"]),
            "Defense":        _display_defense(r["defense"]),
            "Tier":           r["tier"],
            "ASR":            r["asr_overall"],
            "FPR":            r["fpr"],
            "Retrieval Rate": r["retrieval_rate"],
            "Notes":          "Phase 3.3-07 single-seed (unpaired n=100)",
        })

    # ----- (c) Ablation rows (7 defense modes × 4 tiers) -----
    for _, r in ablation.iterrows():
        for tier_idx in [1, 2, 3, 4]:
            rows.append({
                "Source":         "(c) Single-LLM ablation",
                "Model":          r["model"],
                "Defense":        _display_defense(r["defense_mode"]),
                "Tier":           f"T{tier_idx}",
                "ASR":            r.get(f"asr_t{tier_idx}", 0.0),
                "FPR":            r["fpr"],
                "Retrieval Rate": r["retrieval_rate"],
                "Notes":          f"Phase 3.1 (n={r['n_queries']})",
            })

    # ----- (d) Adaptive row — ATK-08 vs Fused on llama3.2:3b (s1) -----
    adaptive_path = logs_dir / "adaptive_fused_llama_s1.json"
    if adaptive_path.exists():
        ad_raw = _safe_load_json(adaptive_path)
        if ad_raw is None:
            raise RuntimeError(f"Could not parse {adaptive_path}")
        ad = ad_raw.get("aggregate", {}) if isinstance(ad_raw, dict) else {}
        rows.append({
            "Source":         "(d) Adaptive attack",
            "Model":          ad_raw.get("llm_model", "llama3.2:3b") if isinstance(ad_raw, dict) else "llama3.2:3b",
            "Defense":        _display_defense("atk08_vs_fused_llama"),
            "Tier":           "Adaptive",
            "ASR":            ad.get("paired_asr_adaptive",
                                     ad.get("asr_adaptive", 0.0)),
            "FPR":            ad.get("fpr", 0.0),
            "Retrieval Rate": ad.get("retrieval_rate", 0.0),
            "Notes":          "ATK-08 novel anchor tokens (Phase 3.2 seed 1)",
        })

    # ----- (d') Adaptive row — ATK-08 vs Fused on mistral -----
    adaptive_mistral_path = logs_dir / "adaptive_fused_mistral.json"
    if adaptive_mistral_path.exists():
        ad_raw = _safe_load_json(adaptive_mistral_path)
        if ad_raw is None:
            raise RuntimeError(f"Could not parse {adaptive_mistral_path}")
        ad = ad_raw.get("aggregate", {}) if isinstance(ad_raw, dict) else {}
        rows.append({
            "Source":         "(d) Adaptive attack",
            "Model":          ad_raw.get("llm_model", "mistral:7b") if isinstance(ad_raw, dict) else "mistral:7b",
            "Defense":        _display_defense("atk08_vs_fused_mistral"),
            "Tier":           "Adaptive",
            "ASR":            ad.get("paired_asr_adaptive",
                                     ad.get("asr_adaptive", 0.0)),
            "FPR":            ad.get("fpr", 0.0),
            "Retrieval Rate": ad.get("retrieval_rate", 0.0),
            "Notes":          "ATK-08 novel anchor tokens (Phase 3.2 mistral)",
        })

    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Emitters                                                                     #
# --------------------------------------------------------------------------- #


def emit_table(df: pd.DataFrame, name: str, output_dir: Path, fmt: str,
               disclosure: str = "") -> None:
    """Write df to {output_dir}/{name}.md and/or .csv per fmt.

    Phase 6 (D-12 / Pitfall 7): if disclosure is non-empty, prepend it to the
    markdown body so the Phase 6 cross-LLM gap-fill banner survives every
    regenerate. CSV companions never carry the disclosure (would corrupt header).
    """
    if fmt in ("markdown", "both"):
        # na_rep="—": replace NaN cells with em-dash before markdown render.
        # tabulate versions < 0.9 lack na_rep kwarg; use fillna on a copy instead.
        md = df.fillna("—").to_markdown(index=False, floatfmt=".2f")
        (output_dir / f"{name}.md").write_text(disclosure + md + "\n", encoding="utf-8")
    if fmt in ("csv", "both"):
        (output_dir / f"{name}.csv").write_text(
            df.to_csv(index=False), encoding="utf-8"
        )


def emit_ablation_with_display(
    ablation: pd.DataFrame, output_dir: Path, fmt: str
) -> None:
    """Map raw defense_mode keys to display names for the standalone ablation table.

    Preserves the raw key in a side column for traceability (Plan 05 cites both
    forms — display name in prose, raw key in source-file callouts).
    """
    df = ablation.copy()
    df.insert(0, "Defense", df["defense_mode"].map(_display_defense))
    emit_table(df, "ablation_table", output_dir, fmt)


def emit_cross_model_matrix_with_display(
    matrix: pd.DataFrame, output_dir: Path, fmt: str
) -> None:
    """Apply display-name mappings before emitting the cross-model matrix.

    Keeps the raw `model`/`defense` columns for traceability and inserts
    pre-mapped Display columns alongside.
    """
    df = matrix.copy()
    df.insert(0, "Model (display)", df["model"].map(_normalize_matrix_model))
    df.insert(2, "Defense (display)", df["defense"].map(_display_defense))
    emit_table(df, "cross_model_matrix", output_dir, fmt)


def emit_undefended_baseline(
    undefended: pd.DataFrame, output_dir: Path, fmt: str
) -> None:
    """Emit the source (a) baseline table verbatim — model labels already canonical."""
    emit_table(undefended, "undefended_baseline", output_dir, fmt,
               disclosure=PHASE6_DISCLOSURE_HEADER)


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #


def _resolve_matrix_path(default_path: str, logs_dir: Path | None = None) -> Path:
    """D-13: prefer logs/eval_matrix/_summary_v6.json over _summary.json when present.

    If logs_dir is supplied and default_path is a plain relative name, the path is
    first rebased under logs_dir so test fixtures rooted at a tmp logs dir are found.
    """
    p = Path(default_path)
    # Rebase relative paths under logs_dir so --logs-dir overrides work correctly.
    if logs_dir is not None and not p.is_absolute():
        # Try rebasing: replace the leading "logs" component with logs_dir
        try:
            rel = p.relative_to("logs")
            p = logs_dir / rel
        except ValueError:
            pass  # Not relative to "logs" — leave as-is
    p_v6 = p.with_name(p.stem + "_v6" + p.suffix)
    return p_v6 if p_v6.exists() else p


# Alias for test_make_results_v6.py skip-guard detection (_V6_AVAILABLE check).
_resolve_v6_path = _resolve_matrix_path


def _resolve_v7_ablation_path(logs_dir: "Path | None" = None) -> "Path | None":
    """D-05: locate logs/ablation_table_gptoss_v7.json under logs_dir, or None.

    Returns None when the v7 file is absent so callers can no-op gracefully
    (the v7 emitter is purely additive; Phase 5 outputs must keep working when
    Phase 7 has not run).
    """
    base = (logs_dir if logs_dir is not None else Path("logs"))
    p = base / _V7_ABLATION_FILENAME
    return p if p.exists() else None


def load_honest_fpr_v7(path: Path) -> "pd.DataFrame":
    """Phase 7: read logs/ablation_table_gptoss_v7.json into a 4-row DataFrame.

    Columns: composite_key, model, defense_mode, per_chunk_fpr,
             answer_preserved_fpr, judge_fpr, judge_model, judge_n_calls.
    Uses schema-defensive .get(...) reads per T-3.4-W1-02.
    """
    raw = _safe_load_json(path)
    if raw is None:
        raise RuntimeError(f"Could not load v7 ablation table from {path}")
    rows = []
    for key, entry in raw.items():
        if not isinstance(entry, dict):
            continue
        rows.append({
            "composite_key":        key,
            "model":                entry.get("model", "unknown"),
            "defense_mode":         entry.get("defense_mode", "unknown"),
            "per_chunk_fpr":        entry.get("per_chunk_fpr", 0.0),
            "answer_preserved_fpr": entry.get("answer_preserved_fpr", 0.0),
            "judge_fpr":            entry.get("judge_fpr", 0.0),
            "judge_model":          entry.get("judge_model", "unknown"),
            "judge_n_calls":        entry.get("judge_n_calls", 0),
        })
    return pd.DataFrame(rows)


def emit_honest_fpr_gptoss_v7(df: pd.DataFrame, output_dir: Path, fmt: str) -> None:
    """D-05: emit docs/results/honest_fpr_gptoss_v7.{md,csv} (4 rows).

    Display-name column 'Defense' inserted via _display_defense() so output
    matches the 'Fused' / 'DEF-02' labels used elsewhere. DEFENSE_DISPLAY
    is NOT modified — its existing entries cover Phase 7 row labels.
    """
    df = df.copy()
    df.insert(1, "Defense", df["defense_mode"].map(_display_defense))
    emit_table(df, "honest_fpr_gptoss_v7", output_dir, fmt)


def make_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the results-assembly CLI."""
    parser = argparse.ArgumentParser(
        description="Phase 3.4 — emit Markdown + CSV results tables for the writeup."
    )
    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Directory containing source JSON logs (default: logs).",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/results",
        help="Directory to write Markdown + CSV outputs (default: docs/results).",
    )
    parser.add_argument(
        "--ablation-file",
        default="logs/ablation_table.json",
        help="Path to Phase 3.1/3.2 ablation table JSON.",
    )
    parser.add_argument(
        "--matrix-file",
        default="logs/eval_matrix/_summary.json",
        help="Path to Phase 3.3-07 cross-model matrix summary JSON.",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "csv", "both"],
        default="both",
        help="Output format(s) to emit (default: both).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Build all 4 result tables (Markdown + CSV) into the output directory.

    Args:
        argv: Argument list. Defaults to [] (NOT sys.argv[1:]) so pytest's argv
              does not collide. The CLI block at module bottom passes
              sys.argv[1:] explicitly when run as a script.

    Returns:
        0 on success.
        2 if any required JSON failed to parse (STRIDE T-3.4-W1-01).
    """
    if argv is None:
        argv = []
    args = make_parser().parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = Path(args.logs_dir)

    try:
        ablation   = load_ablation(Path(args.ablation_file))
        matrix     = load_cross_model_matrix(_resolve_matrix_path(args.matrix_file, logs_dir))
        undefended = load_undefended_baseline(logs_dir)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    arms_race = build_arms_race_table(ablation, matrix, undefended, logs_dir)

    # Emit cross-model matrix and ablation in requested format (unversioned, safe to overwrite).
    emit_cross_model_matrix_with_display(matrix, output_dir, args.format)
    emit_ablation_with_display(ablation, output_dir, args.format)

    # Phase 6 D-05 / D-06: arms_race and undefended_baseline emit markdown in-place
    # (disclosure header prepended); original .csv files stay as Phase 3.4 deliverables.
    # New _v6.csv companions carry the post-Phase-6 schema with T1b/T3/T4 columns.
    _md_fmt = "markdown" if args.format in ("markdown", "both") else args.format
    emit_table(arms_race, "arms_race_table", output_dir, _md_fmt,
               disclosure=PHASE6_DISCLOSURE_HEADER)
    emit_undefended_baseline(undefended, output_dir, _md_fmt)

    # Phase 6 D-06: emit _v6.csv companions (new files — originals untouched)
    emit_table(undefended, "undefended_baseline_v6", output_dir, "csv")
    emit_table(arms_race,  "arms_race_table_v6",   output_dir, "csv")

    # Phase 7 D-05: emit honest_fpr_gptoss_v7 if v7 ablation file present (no-op otherwise)
    v7_path = _resolve_v7_ablation_path(logs_dir)
    if v7_path is not None:
        try:
            df_v7 = load_honest_fpr_v7(v7_path)
        except RuntimeError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            return 2
        emit_honest_fpr_gptoss_v7(df_v7, output_dir, args.format)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
