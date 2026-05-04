import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import chromadb

client = chromadb.PersistentClient(path=".chroma")
col = client.get_collection("nq_poisoned_v4")
result = col.get(limit=1239, include=["documents", "metadatas"])
ids = result["ids"]
metas = result["metadatas"]
texts = result["documents"]

# Classify by passage_id range
clean = [(id_, m, t) for id_, m, t in zip(ids, metas, texts) if m.get("passage_id", 0) < 20000]
poisoned = [(id_, m, t) for id_, m, t in zip(ids, metas, texts) if m.get("passage_id", 0) >= 20000]

print(f"Clean docs (passage_id < 20000):   {len(clean)}")
print(f"Poisoned docs (passage_id >= 20000): {len(poisoned)}")

# Classify poisoned by text patterns
tier_patterns = {
    "T1_naive":        ["IGNORE PREVIOUS", "ignore all previous", "Ignore the above", "ignore the previous"],
    "T1b_homoglyph":   ["іgnore", "ιgnore", "1gnore"],  # Cyrillic/Greek i + ignore variants
    "T2_smuggling":    ["NOTE TO AI", "NOTE:", "ASSISTANT NOTE", "AI ASSISTANT"],
    "T3_semantic":     ["COMPROMISED", "MAINTENANCE MODE"],
    "T4_fragmented":   ["[PART-A]", "[PART-B]", "[FRAG-"],
    "adaptive":        ["adaptive", "tier-9", "tier_9", "ATK-08", "ATK-09"],
}

tier_counts = {t: 0 for t in tier_patterns}
unclassified = []

for id_, m, text in poisoned:
    matched = False
    for tier, patterns in tier_patterns.items():
        if any(p.lower() in text.lower() for p in patterns):
            tier_counts[tier] += 1
            matched = True
            break
    if not matched:
        unclassified.append((id_, m, text[:150]))

print("\nPoisoned doc tier breakdown (by text patterns):")
for t, n in tier_counts.items():
    print(f"  {t}: {n}")
print(f"  unclassified: {len(unclassified)}")

if unclassified[:5]:
    print("\nUnclassified samples:")
    for id_, m, snippet in unclassified[:5]:
        print(f"  id={id_!r} pid={m.get('passage_id')} text={snippet!r}")

# Show adaptive doc samples
adaptive_docs = [(id_, m, text) for id_, m, text in poisoned
                 if any(p.lower() in text.lower() for p in tier_patterns["adaptive"])]
print(f"\nAdaptive docs: {len(adaptive_docs)}")
for id_, m, text in adaptive_docs[:5]:
    print(f"  id={id_!r} pid={m.get('passage_id')}")
    print(f"  text: {text[:250]!r}")
    print()
