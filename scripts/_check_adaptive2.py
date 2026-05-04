import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "logs/eval_harness_undefended_gptoss20b_v6.json"
d = json.loads(open(path, encoding="utf-8").read())

results = d["results"]
n = len(results)

adaptive_retrieved = sum(1 for r in results if r.get("adaptive_retrieved", False))
adaptive_hijacked  = sum(1 for r in results if r.get("hijacked_adaptive", False))

print(f"Total queries:          {n}")
print(f"Adaptive retrieved:     {adaptive_retrieved}  ({adaptive_retrieved/n:.2%} of all queries)")
print(f"Adaptive hijacked:      {adaptive_hijacked}")
print(f"asr_adaptive (raw /n):  {adaptive_hijacked/n:.4f}")
if adaptive_retrieved > 0:
    print(f"Conditional ASR:        {adaptive_hijacked/adaptive_retrieved:.4f}  ({adaptive_hijacked}/{adaptive_retrieved})")

print()
print("From aggregate block:")
agg = d["aggregate"]
for k in sorted(agg):
    if "adaptive" in k:
        print(f"  {k}: {agg[k]}")

# Also check corpus for how many adaptive docs exist
print()
import pathlib
corpus_path = pathlib.Path("data/corpus_poisoned.jsonl")
adaptive_docs = 0
if corpus_path.exists():
    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        doc = json.loads(line)
        tier = doc.get("tier", doc.get("attack_tier", ""))
        if "adaptive" in str(tier).lower() or str(doc.get("doc_id","")).startswith("9"):
            adaptive_docs += 1
    print(f"Adaptive docs in corpus: {adaptive_docs}")
