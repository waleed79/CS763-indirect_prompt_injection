import json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "logs/eval_harness_undefended_gptoss20b_v6.json"
with open(path) as f:
    d = json.load(f)

print(f"=== {path} ===")
print(f"model:    {d.get('model')}")
print(f"defense:  {d.get('defense')}")
print(f"phase:    {d.get('phase')}")
print(f"results:  {len(d.get('results', []))} entries")
print()

# Top-level ASR / metric fields
for k in sorted(d):
    if any(x in k for x in ["asr","retrieval","fpr","error_count","supersede","provenance"]):
        print(f"  {k}: {d[k]}")

print()
results = d.get("results", [])
if not results:
    print("ERROR: results list is EMPTY")
    sys.exit(1)

# Count non-empty responses
empty = sum(1 for r in results if not str(r.get("response","")).strip())
print(f"  empty responses: {empty}/{len(results)}")

# Show first 3 results
for i, r in enumerate(results[:3]):
    resp = str(r.get("response",""))
    hijacked = r.get("hijacked", r.get("hijacked_tier1"))
    print(f"\n  result[{i}]:")
    print(f"    query:     {str(r.get('query',''))[:80]}")
    print(f"    hijacked:  {hijacked}")
    print(f"    response:  {resp[:120]}")
