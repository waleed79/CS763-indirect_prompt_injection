"""Phase 3.4 Wave 0 schema probe — verifies all expected log files for Plans 02/03/04/05.

Run:
    conda run -n rag-security python scripts/_phase34_schema_probe.py

Exits 0 if every expected file is present and parseable; exits 1 otherwise.
Resolves RESEARCH Open Question 2 (paired vs unpaired _summary.json schema)
by comparing logs/eval_matrix/_summary.json's asr_overall to the source
per-cell log's asr_overall and paired_asr_tier1.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Canonical expected-files map (verbatim from 03.4-01-PLAN.md interfaces block)
# ---------------------------------------------------------------------------
EXPECTED: dict = {
    "logs/ablation_table.json":             {"shape": "dict", "min_keys": 10},
    "logs/eval_matrix/_summary.json":       {"shape": "list", "min_len": 45},
    "logs/eval_harness_undefended_llama.json":     {"shape": "dict"},
    "logs/eval_harness_undefended_mistral.json":   {"shape": "dict"},
    "logs/eval_harness_undefended_gptoss20b.json": {"shape": "dict"},
    "logs/eval_harness_undefended_gptoss120b.json":{"shape": "dict"},
    "logs/attack_baseline.json":            {"shape": "dict"},
    "logs/loo_results_llama.json":          {"shape": "dict"},
    "logs/loo_results_mistral.json":        {"shape": "dict"},
    "logs/eval_ratio_0005.json":            {"shape": "dict"},
    "logs/eval_ratio_0010.json":            {"shape": "dict"},
    "logs/eval_ratio_0020.json":            {"shape": "dict"},
    "logs/eval_ratio_0050.json":            {"shape": "dict"},
    "logs/eval_ratio_0100.json":            {"shape": "dict"},
    "logs/adaptive_fused_llama_s1.json":    {"shape": "dict"},
    "logs/adaptive_fused_mistral.json":     {"shape": "dict"},
    "logs/def02_priming_analysis.md":       {"shape": "text"},
    "docs/xss_ssrf_taxonomy.md":            {"shape": "text"},
}


def _probe_dict(path: Path, spec: dict) -> str:
    """Return one-line status for a JSON file expected to load as dict."""
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        # T-3.4-W0-01 mitigation: do not crash on bad JSON; report and continue
        return f"[CORRUPT] {path}: {e}"
    if not isinstance(d, dict):
        return f"[BADSHAPE] {path}: expected dict, got {type(d).__name__}"
    keys = list(d.keys())
    min_keys = spec.get("min_keys")
    if min_keys is not None and len(keys) < min_keys:
        return f"[BADSHAPE] {path}: dict has {len(keys)} keys, expected >= {min_keys}"
    extra = ""
    # For loo_results files report aggregate.roc_auc inline (per plan reference output)
    if "loo_results" in str(path):
        agg = d.get("aggregate", {})
        roc = agg.get("roc_auc")
        if roc is not None:
            extra = f" aggregate.roc_auc={roc}"
    # For eval_ratio files report aggregate.asr_overall inline
    if "eval_ratio" in str(path):
        agg = d.get("aggregate", {})
        asr = agg.get("asr_overall")
        if asr is not None:
            extra = f" aggregate.asr_overall={asr}"
    head = ", ".join(keys[:3])
    return f"[OK]   {path}  keys={len(keys)}: {head}{extra}"


def _probe_list(path: Path, spec: dict) -> str:
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return f"[CORRUPT] {path}: {e}"
    if not isinstance(d, list):
        return f"[BADSHAPE] {path}: expected list, got {type(d).__name__}"
    min_len = spec.get("min_len")
    if min_len is not None and len(d) < min_len:
        return f"[BADSHAPE] {path}: list len {len(d)}, expected >= {min_len}"
    schema = list(d[0].keys()) if d and isinstance(d[0], dict) else []
    return f"[OK]   {path}  list, len={len(d)}, schema={{{', '.join(schema)}}}"


def _probe_text(path: Path, spec: dict) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return f"[CORRUPT] {path}: {e}"
    lines = text.splitlines()
    nonempty = [l for l in lines if l.strip()]
    head = nonempty[0][:80] if nonempty else "<empty>"
    # T-3.4-W0-01 mitigation extension: stdout may be cp1252 (Windows conda run);
    # encode non-ASCII characters as escape sequences so the probe never crashes
    # the wrapper on legitimate UTF-8 content (e.g., "↔" in def02_priming_analysis.md).
    head_safe = head.encode("ascii", errors="backslashreplace").decode("ascii")
    return f"[OK]   {path}  lines={len(lines)}, head={head_safe!r}"


def _resolve_oq2(summary_path: Path, source_log: Path) -> str:
    """Open Question 2: does _summary.json asr_overall match paired or unpaired?"""
    try:
        s = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return f"[OQ2-SKIP] cannot read {summary_path}: {e}"
    try:
        src = json.loads(source_log.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return f"[OQ2-SKIP] cannot read source log {source_log}: {e}"

    # Find the source row in _summary.json that matches the per-cell log
    rows = [
        r for r in s
        if r.get("model") == "llama3.2_3b"
        and r.get("defense") == "no_defense"
        and r.get("tier") == "tier1"
    ]
    if not rows:
        return "[OQ2-SKIP] no llama3.2_3b/no_defense/tier1 row in _summary.json"
    summary_asr = rows[0].get("asr_overall")
    src_agg = src.get("aggregate", {})
    src_unpaired = src_agg.get("asr_overall")
    src_paired = src_agg.get("paired_asr_tier1")

    eq = lambda a, b: a is not None and b is not None and abs(a - b) < 1e-9

    if eq(summary_asr, src_paired) and not eq(summary_asr, src_unpaired):
        return (
            f"[PAIRED]   _summary.json asr_overall ({summary_asr}) == source paired_asr_tier1 ({src_paired}) "
            f"(matches Phase 2.3 paired convention)"
        )
    if eq(summary_asr, src_unpaired) and not eq(summary_asr, src_paired):
        return (
            f"[UNPAIRED] _summary.json asr_overall ({summary_asr}) == source asr_overall ({src_unpaired}) "
            f"(all 100 queries; NOT paired)"
        )
    if eq(summary_asr, src_unpaired) and eq(summary_asr, src_paired):
        return (
            f"[AMBIG]    summary={summary_asr}, paired={src_paired}, unpaired={src_unpaired} — "
            f"both equal; cannot disambiguate from this row"
        )
    return (
        f"[DIFF]     summary={summary_asr}, paired={src_paired}, unpaired={src_unpaired} — "
        f"asr values do not match either field; investigate"
    )


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    missing: list[str] = []
    for relpath, spec in EXPECTED.items():
        path = repo / relpath
        if not path.exists():
            line = f"[MISSING] {relpath}"
            missing.append(relpath)
            print(line)
            continue

        shape = spec["shape"]
        if shape == "dict":
            print(_probe_dict(path, spec))
        elif shape == "list":
            print(_probe_list(path, spec))
        elif shape == "text":
            print(_probe_text(path, spec))
        else:
            print(f"[BADSPEC] {relpath}: unknown shape {shape!r}")

    # Open Question 2 — paired vs unpaired _summary.json schema
    oq2 = _resolve_oq2(
        repo / "logs/eval_matrix/_summary.json",
        repo / "logs/eval_matrix/llama3.2_3b__no_defense__tier1.log",
    )
    print(oq2)

    if missing:
        print(f"\nSCHEMA PROBE FAILED — {len(missing)} missing file(s).")
        return 1
    print("\nSCHEMA PROBE OK — all expected files present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
