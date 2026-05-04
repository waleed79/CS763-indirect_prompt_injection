import json

with open("logs/eval_harness_undefended_gptoss20b_v6.json") as f:
    d = json.load(f)

print("ALL top-level keys:", list(d.keys()))
print()
r = d["results"][0]
print("result[0] ALL keys:", list(r.keys()))
print()
for k, v in r.items():
    print(f"  {k}: {repr(v)[:200]}")
