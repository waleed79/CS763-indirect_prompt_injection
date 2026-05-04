import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Check ChromaDB collection for adaptive docs
import chromadb

client = chromadb.PersistentClient(path=".chroma")
print("Collections:", [c.name for c in client.list_collections()])

col = client.get_collection("nq_poisoned_v4")
print(f"Total docs in nq_poisoned_v4: {col.count()}")

# Get all metadata to find tiers
result = col.get(include=["metadatas"])
metas = result["metadatas"]

tier_counts = {}
for m in metas:
    t = m.get("tier", m.get("attack_tier", "clean"))
    tier_counts[t] = tier_counts.get(t, 0) + 1

print("\nTier breakdown in ChromaDB collection:")
for t, n in sorted(tier_counts.items()):
    print(f"  {t}: {n}")

# Check adaptive specifically
adaptive_ids = [result["ids"][i] for i, m in enumerate(metas) if "adaptive" in str(m.get("tier","")).lower()]
print(f"\nAdaptive docs: {len(adaptive_ids)}")
if adaptive_ids[:3]:
    print("Sample IDs:", adaptive_ids[:3])
    # Show one sample
    sample = col.get(ids=[adaptive_ids[0]], include=["metadatas","documents"])
    print("\nSample adaptive doc metadata:", sample["metadatas"][0])
    print("Sample text snippet:", sample["documents"][0][:200])
