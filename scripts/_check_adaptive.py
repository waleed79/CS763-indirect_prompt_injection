import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

files = [
    ("gpt-oss:20b  no_defense", "logs/eval_harness_undefended_gptoss20b_v6.json"),
    ("gpt-oss:120b no_defense", "logs/eval_harness_undefended_gptoss120b_v6.json"),
    ("gpt-oss:20b  fused",      "logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json"),
    ("gpt-oss:20b  def02",      "logs/eval_matrix/gptoss20b_cloud__def02__all_tiers_v6.json"),
    ("gpt-oss:120b fused",      "logs/eval_matrix/gptoss120b_cloud__fused__all_tiers_v6.json"),
    ("gpt-oss:120b def02",      "logs/eval_matrix/gptoss120b_cloud__def02__all_tiers_v6.json"),
]

print(f"{'cell':<30} {'asr_adaptive':>12} {'cond_asr_adaptive':>18} {'paired_asr_adaptive':>20}")
print("-" * 82)
for label, path in files:
    agg = json.loads(open(path, encoding="utf-8").read())["aggregate"]
    print(f"  {label:<28} {agg.get('asr_adaptive', 'N/A'):>12} "
          f"{agg.get('conditional_asr_adaptive', 'N/A'):>18.4f} "
          f"{agg.get('paired_asr_adaptive', 'N/A'):>20}")
