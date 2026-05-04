import json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = sys.argv[1] if len(sys.argv) > 1 else "logs/eval_harness_undefended_gptoss20b_v6.json"

with open(path, encoding="utf-8") as f:
    d = json.load(f)

print(f"=== METADATA ({path}) ===")
print(f"  llm_model:    {d.get('llm_model')}")
print(f"  defense_mode: {d.get('defense_mode')}")
print(f"  phase:        {d.get('phase')}")
print(f"  collection:   {d.get('collection')}")
print(f"  n_queries:    {d.get('n_queries')}")
print(f"  n_paired:     {d.get('n_paired')}")
print(f"  supersedes:   {d.get('supersedes_phase_02_3')}")

print()
print("=== AGGREGATE ASR ===")
agg = d.get("aggregate", {})
for k, v in sorted(agg.items()):
    print(f"  {k}: {v}")

results = d["results"]
empty_answers = sum(1 for r in results if not str(r.get("answer", "")).strip())
print()
print("=== RESPONSE QUALITY ===")
print(f"  total results: {len(results)}")
print(f"  empty answers: {empty_answers}  {'<-- PROBLEM' if empty_answers > 0 else '(good)'}")

print()
print("=== SAMPLE RESULTS (first 5) ===")
for i, r in enumerate(results[:5]):
    ans = str(r.get("answer", "")).strip().encode("ascii", errors="replace").decode()
    print(f"  [{i}] query: {r['query'][:60]}")
    print(f"       answer: {ans[:100]}")
    print(f"       hijacked: t1={r['hijacked_tier1']} t1b={r['hijacked_tier1b']} t2={r['hijacked_tier2']} t3={r['hijacked_tier3']} t4={r['hijacked_tier4']}")
    print()
