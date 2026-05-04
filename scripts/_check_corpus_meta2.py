import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import chromadb

client = chromadb.PersistentClient(path=".chroma")
col = client.get_collection("nq_poisoned_v4")

# Get all docs - ids are returned by default
result = col.get(limit=1239, include=["documents", "metadatas"])
ids = result["ids"]
metas = result["metadatas"]
texts = result["documents"]

# All metadata keys
all_keys = set()
for m in metas:
    all_keys.update(m.keys())
print("All metadata keys:", sorted(all_keys))

# ID patterns
id_prefixes = {}
for id_ in ids:
    prefix = id_.split("_")[0] if "_" in id_ else id_[:5]
    id_prefixes[prefix] = id_prefixes.get(prefix, 0) + 1
print("\nID prefix counts:", dict(sorted(id_prefixes.items())))

# Check for injection keywords
injection_keywords = ["ignore previous", "system:", "your new task", "you are now",
                       "disregard", "[[", "INSTRUCTIONS:", "override", "jailbreak",
                       "forget your", "new instruction"]
injection_docs = []
for id_, meta, text in zip(ids, metas, texts):
    lower = text.lower()
    if any(kw.lower() in lower for kw in injection_keywords):
        injection_docs.append((id_, meta, text[:200]))

print(f"\nDocs containing injection keywords: {len(injection_docs)}")
for id_, meta, snippet in injection_docs[:10]:
    print(f"  id={id_!r} meta={meta}")
    print(f"  text: {snippet!r}")
    print()

# Also check for any doc with 'adaptive' in text
adaptive_text = [(id_, text[:150]) for id_, text in zip(ids, texts) if "adaptive" in text.lower()]
print(f"\nDocs with 'adaptive' in text: {len(adaptive_text)}")
