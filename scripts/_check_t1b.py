import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

with open("logs/eval_matrix/_summary_v6.json", encoding="utf-8") as f:
    cells = json.load(f)

print("T1b no_defense values for llama and mistral:")
for c in cells:
    if c["tier"] == "tier1b" and c["defense"] == "no_defense":
        print(f"  {c['model']:<25} asr_overall={c['asr_overall']}")

print()
print("All tiers no_defense for llama:")
for c in cells:
    if "llama" in c["model"] and c["defense"] == "no_defense":
        print(f"  {c['tier']:<8} asr={c['asr_overall']}")

print()
print("All tiers no_defense for mistral:")
for c in cells:
    if "mistral" in c["model"] and c["defense"] == "no_defense":
        print(f"  {c['tier']:<8} asr={c['asr_overall']}")
