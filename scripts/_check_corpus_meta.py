import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import chromadb

client = chromadb.PersistentClient(path=".chroma")
col = client.get_collection("nq_poisoned_v4")

# Get a sample of docs - first 10 and docs with high IDs
result_start = col.get(limit=5, include=["metadatas", "documents"])
print("=== First 5 docs metadata ===")
for i, (id_, meta) in enumerate(zip(result_start["ids"], result_start["metadatas"])):
    print(f"  id={id_} meta={meta}")
    print(f"  text[:80]={result_start['documents'][i][:80]!r}")
    print()

# Get docs where id starts with "p_" or high doc_id numbers
result_all = col.get(include=["metadatas", "ids"])
metas = result_all["metadatas"]
ids = result_all["ids"]

# Find all unique metadata keys
all_keys = set()
for m in metas:
    all_keys.update(m.keys())
print("All metadata keys:", sorted(all_keys))

# Check for docs that are NOT passage_id == standard clean
non_standard = [(id_, m) for id_, m in zip(ids, metas) if not str(id_).startswith("passage_")]
print(f"\nNon-'passage_' prefixed IDs: {len(non_standard)}")

# Check for docs with text containing "ignore previous" or similar injection
result_texts = col.get(limit=1239, include=["documents", "metadatas", "ids"])
injection_docs = []
for id_, meta, text in zip(result_texts["ids"], result_texts["metadatas"], result_texts["documents"]):
    lower = text.lower()
    if any(kw in lower for kw in ["ignore previous", "system:", "your new task", "you are now", "disregard"]):
        injection_docs.append((id_, meta, text[:150]))

print(f"\nDocs containing injection keywords: {len(injection_docs)}")
for id_, meta, snippet in injection_docs[:5]:
    print(f"  id={id_} meta={meta}")
    print(f"  snippet: {snippet!r}")
    print()
