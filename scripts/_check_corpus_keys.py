import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

corpus = open("data/corpus_poisoned.jsonl", encoding="utf-8")
seen_keys = set()
tier_counts = {}
sample_nonclean = []

for line in corpus:
    line = line.strip()
    if not line:
        continue
    doc = json.loads(line)
    seen_keys.update(doc.keys())
    for field in ["tier", "attack_tier", "is_poisoned", "poison_tier", "type", "doc_type", "category"]:
        v = doc.get(field)
        if v is not None and v not in ("clean", None, False, 0, ""):
            key = f"{field}={v}"
            tier_counts[key] = tier_counts.get(key, 0) + 1
            if len(sample_nonclean) < 3:
                sample_nonclean.append({"doc_id": doc.get("doc_id"), field: v, "keys": list(doc.keys())[:8]})

print("All keys seen:", sorted(seen_keys))
print()
print("Non-clean tier values:")
for k, v in sorted(tier_counts.items()):
    print(f"  {k}: {v}")
print()
print("Sample non-clean docs:")
for s in sample_nonclean:
    print(" ", s)

# Also check first doc to see structure
corpus.seek(0)
first = json.loads(next(l for l in corpus if l.strip()))
print()
print("First doc keys/values (all fields):")
for k, v in first.items():
    print(f"  {k}: {repr(v)[:80]}")
