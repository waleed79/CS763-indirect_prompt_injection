"""Rebuild _summary_v6.json from all 6 Phase 6 harness outputs + 45 existing cells."""
import json, os, io, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

EXISTING = Path("logs/eval_matrix/_summary.json")
OUT = Path("logs/eval_matrix/_summary_v6.json")
TIERS = ["tier1", "tier1b", "tier2", "tier3", "tier4"]

# All 6 v6 harness outputs: (path, defense_name)
RUNS = [
    (Path("logs/eval_harness_undefended_gptoss20b_v6.json"),             "no_defense"),
    (Path("logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json"), "fused"),
    (Path("logs/eval_matrix/gptoss20b_cloud__def02__all_tiers_v6.json"), "def02"),
    (Path("logs/eval_harness_undefended_gptoss120b_v6.json"),             "no_defense"),
    (Path("logs/eval_matrix/gptoss120b_cloud__fused__all_tiers_v6.json"),"fused"),
    (Path("logs/eval_matrix/gptoss120b_cloud__def02__all_tiers_v6.json"),"def02"),
]

cells = json.loads(EXISTING.read_text(encoding="utf-8"))
print(f"Loaded {len(cells)} existing cells from {EXISTING}")

for path, defense_name in RUNS:
    if not path.exists():
        print(f"  MISSING: {path}")
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    agg = data["aggregate"]
    model = data["llm_model"].replace(":", "_")
    for tier in TIERS:
        asr = agg.get(f"asr_{tier}", 0.0)
        cells.append({
            "model":           model,
            "defense":         defense_name,
            "tier":            tier,
            "asr_overall":     asr,
            "asr_tier_native": asr,
            "fpr":             agg.get("fpr", 0.0),
            "retrieval_rate":  agg.get("retrieval_rate", 0.0),
        })
    print(f"  Added {model} x {defense_name} (5 tiers)")

print(f"\nTotal cells: {len(cells)}  (expected 75)")

tmp = OUT.with_suffix(".json.tmp")
tmp.write_text(json.dumps(cells, indent=2), encoding="utf-8")
os.replace(tmp, OUT)
print(f"Written: {OUT}")
