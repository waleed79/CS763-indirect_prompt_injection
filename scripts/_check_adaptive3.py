import json, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Count adaptive docs in corpus by doc_id range
corpus = Path("data/corpus_poisoned.jsonl")
tiers = {}
for line in corpus.read_text(encoding="utf-8").splitlines():
    if not line.strip(): continue
    doc = json.loads(line)
    did = int(doc.get("doc_id", doc.get("id", 0)))
    t = doc.get("tier", "clean")
    tiers[t] = tiers.get(t, 0) + 1

print("Corpus tier breakdown:")
for t, n in sorted(tiers.items()):
    print(f"  {t}: {n}")

print()
# Check adaptive retrieval across all 6 cells
files = [
    ("20b  no_def", "logs/eval_harness_undefended_gptoss20b_v6.json"),
    ("120b no_def", "logs/eval_harness_undefended_gptoss120b_v6.json"),
    ("20b  fused",  "logs/eval_matrix/gptoss20b_cloud__fused__all_tiers_v6.json"),
    ("20b  def02",  "logs/eval_matrix/gptoss20b_cloud__def02__all_tiers_v6.json"),
    ("120b fused",  "logs/eval_matrix/gptoss120b_cloud__fused__all_tiers_v6.json"),
    ("120b def02",  "logs/eval_matrix/gptoss120b_cloud__def02__all_tiers_v6.json"),
]
print(f"{'cell':<14} {'n_retrieved':>12} {'n_hijacked':>11} {'cond_asr':>10} {'note'}")
print("-" * 65)
for label, path in files:
    d = json.loads(open(path, encoding="utf-8").read())
    results = d["results"]
    n_ret  = sum(1 for r in results if r.get("adaptive_retrieved", False))
    n_hij  = sum(1 for r in results if r.get("hijacked_adaptive", False))
    cond   = n_hij / n_ret if n_ret else 0.0
    note   = f"{n_hij}/{n_ret}" if n_ret else "no retrievals"
    print(f"  {label:<12} {n_ret:>12} {n_hij:>11} {cond:>10.3f}   {note}")
