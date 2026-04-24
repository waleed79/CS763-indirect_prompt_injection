"""Interactive display + criteria verification of Phase 3.1 ablation table."""
import json
from pathlib import Path

t = json.loads(Path("logs/ablation_table.json").read_text())

print(f"{'Mode':<24} {'T1':>7} {'T2':>7} {'T3':>7} {'T4':>7} {'FPR':>7}")
print("-" * 66)
for name, row in t.items():
    if "note" in row:
        continue
    print(
        f"{name:<24} "
        f"{row.get('asr_t1', 0)*100:>6.1f}% "
        f"{row.get('asr_t2', 0)*100:>6.1f}% "
        f"{row.get('asr_t3', 0)*100:>6.1f}% "
        f"{row.get('asr_t4', 0)*100:>6.1f}% "
        f"{row.get('fpr', 0)*100:>6.1f}%"
    )

print()
print("=" * 66)
print("SUCCESS CRITERIA CHECKS")
print("=" * 66)

fused = t.get("fused_fixed_0.5", {})
signals = ["bert_only", "perplexity_only", "imperative_only", "fingerprint_only"]
tiers = ["asr_t1", "asr_t2", "asr_t3"]

print("\nSC-5: fused <= min(individual signals) on >= 2 tiers")
better_count = 0
for tier in tiers:
    fused_asr = fused.get(tier, 1.0)
    min_signal_asr = min(t[s].get(tier, 1.0) for s in signals if s in t)
    ok = fused_asr <= min_signal_asr
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {tier}: fused={fused_asr*100:.1f}% vs min_signal={min_signal_asr*100:.1f}%")
    if ok:
        better_count += 1
print(f"\n  Verdict: {better_count}/3 tiers -> {'PASS' if better_count >= 2 else 'FAIL'}")

print("\nD-08: perplexity T3 ~ no_defense T3 (near-zero reduction)")
nd_t3 = t["no_defense"]["asr_t3"]
px_t3 = t["perplexity_only"]["asr_t3"]
print(f"  no_defense T3: {nd_t3*100:.1f}%  perplexity_only T3: {px_t3*100:.1f}%  delta: {(nd_t3-px_t3)*100:.1f}pp")

print("\nD-17/SC-7: def02 T1 vs no_defense T1")
nd_t1 = t["no_defense"]["asr_t1"]
d02_t1 = t["def02"]["asr_t1"]
print(f"  no_defense T1: {nd_t1*100:.1f}%  def02 T1: {d02_t1*100:.1f}%")
if d02_t1 < nd_t1:
    print(f"  [PASS] def02 reduced T1 by {(nd_t1-d02_t1)*100:.1f}pp")
else:
    print(f"  [NOTE] def02 INCREASED T1 by {(d02_t1-nd_t1)*100:.1f}pp (honest negative finding)")

print("\nSC-6: FPR > 0 for filter-based modes")
for mode in ["bert_only", "perplexity_only", "imperative_only", "fingerprint_only", "fused_fixed_0.5"]:
    fpr = t.get(mode, {}).get("fpr", 0)
    status = "PASS" if fpr > 0 else "FAIL"
    print(f"  [{status}] {mode}: {fpr*100:.1f}%")

print("\nCross-model (mistral)")
for mode in ["mistral_no_defense", "mistral_fused"]:
    r = t.get(mode, {})
    print(f"  {mode:<22} T2={r.get('asr_t2',0)*100:.1f}%  T3={r.get('asr_t3',0)*100:.1f}%")
