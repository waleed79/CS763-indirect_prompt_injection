import json, io, sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout = open("scripts/_count_poisoned_out.txt", "w", encoding="utf-8")

import chromadb

client = chromadb.PersistentClient(path=".chroma")
col = client.get_collection("nq_poisoned_v4")
result = col.get(limit=1239, include=["documents", "metadatas"])
ids = result["ids"]
metas = result["metadatas"]
texts = result["documents"]

clean = [(id_, m, t) for id_, m, t in zip(ids, metas, texts) if m.get("passage_id", 0) < 20000]
poisoned = [(id_, m, t) for id_, m, t in zip(ids, metas, texts) if m.get("passage_id", 0) >= 20000]

print(f"Clean docs (passage_id < 20000):    {len(clean)}")
print(f"Poisoned docs (passage_id >= 20000): {len(poisoned)}")

# Classify by text patterns
tier_patterns = {
    "T1_naive":      ["IGNORE PREVIOUS INSTRUCTIONS", "ignore all previous", "Ignore the above",
                      "ignore the previous", "IGNORE ALL PRIOR"],
    "T1b_homoglyph": ["Ιgnore", "IgnorE", "іgnore", "ιgnore"],
    "T2_smuggling":  ["NOTE TO AI", "ASSISTANT NOTE", "<!-- INST", "<!--INST", "<!-", "<HIDDEN"],
    "T3_semantic":   ["COMPROMISED", "MAINTENANCE MODE", "safe mode", "diagnostic mode"],
    "T4_fragmented": ["[PART-A]", "[PART-B]", "[FRAG-", "PART1:", "PART2:"],
    "adaptive":      ["adaptive", "tier-9", "tier_9", "ATK-08", "ATK-09",
                      "query-aware", "query aware", "semantic camouflage"],
}

tier_counts = {t: 0 for t in tier_patterns}
tier_examples = {t: [] for t in tier_patterns}
unclassified = []

for id_, m, text in poisoned:
    matched = False
    for tier, patterns in tier_patterns.items():
        if any(p.lower() in text.lower() for p in patterns):
            tier_counts[tier] += 1
            if len(tier_examples[tier]) < 2:
                tier_examples[tier].append((id_, text[:200]))
            matched = True
            break
    if not matched:
        unclassified.append((id_, m, text[:150]))

print("\nPoisoned doc tier breakdown (by text patterns):")
total = 0
for t, n in tier_counts.items():
    print(f"  {t}: {n}")
    total += n
print(f"  unclassified: {len(unclassified)}")
print(f"  TOTAL classified: {total}")

print("\n=== UNCLASSIFIED SAMPLES ===")
for id_, m, snippet in unclassified[:10]:
    print(f"  id={id_} pid={m.get('passage_id')} text={snippet}")

print("\n=== ADAPTIVE SAMPLES ===")
for id_, snippet in tier_examples["adaptive"]:
    print(f"  id={id_}")
    print(f"  {snippet}")
    print()

# Also show a T3 sample
print("\n=== T3 SEMANTIC SAMPLES ===")
for id_, snippet in tier_examples["T3_semantic"]:
    print(f"  id={id_}")
    print(f"  {snippet}")
    print()

sys.stdout.close()
print("Done", file=sys.__stdout__)
