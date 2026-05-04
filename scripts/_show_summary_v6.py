import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

with open("logs/eval_matrix/_summary_v6.json", encoding="utf-8") as f:
    cells = json.load(f)

print(f"Total cells: {len(cells)}")
print()

# Show last 30 (the new Phase 6 additions)
new_cells = [c for c in cells if "gpt-oss" in c.get("model", "")]
old_cells = [c for c in cells if "gpt-oss" not in c.get("model", "")]
print(f"Phase 06 cells: {len(new_cells)}  |  Existing cells: {len(old_cells)}")
print()
print(f"{'model':<26} {'defense':<12} {'tier':<6} {'asr_overall':>11} {'asr_t1':>7} {'asr_t1b':>8} {'asr_t2':>7} {'asr_t3':>7} {'asr_t4':>7}")
print("-" * 95)
for c in new_cells:
    agg = c.get("aggregate", {})
    print(
        f"  {c['model']:<24} {c['defense']:<12} {c['tier']:<6} "
        f"{agg.get('asr_overall', c.get('asr_overall', '?')):>11} "
        f"{agg.get('asr_tier1', c.get('asr_tier1', '?')):>7} "
        f"{agg.get('asr_tier1b', c.get('asr_tier1b', '?')):>8} "
        f"{agg.get('asr_tier2', c.get('asr_tier2', '?')):>7} "
        f"{agg.get('asr_tier3', c.get('asr_tier3', '?')):>7} "
        f"{agg.get('asr_tier4', c.get('asr_tier4', '?')):>7}"
    )
