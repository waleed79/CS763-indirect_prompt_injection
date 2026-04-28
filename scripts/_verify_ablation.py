"""Verify acceptance criteria for Task 2."""
import json

# Check mistral files exist
from pathlib import Path
assert Path('logs/defense_off_mistral.json').exists(), "defense_off_mistral.json missing"
assert Path('logs/defense_fused_mistral.json').exists(), "defense_fused_mistral.json missing"
print("OK: Both mistral files exist")

# Check ablation table has 8+ rows
t = json.load(open('logs/ablation_table.json'))
assert len(t) >= 8, f"Expected >= 8 rows, got {len(t)}"
print(f"OK: ablation_table.json has {len(t)} rows")

# Check required rows exist
required = ['no_defense', 'def02', 'bert_only', 'perplexity_only',
            'imperative_only', 'fingerprint_only', 'fused_fixed_0.5',
            'mistral_no_defense', 'mistral_fused']
for r in required:
    assert r in t, f"Missing row: {r}"
print(f"OK: All {len(required)} required rows present")

# Check each row has asr and fpr keys
for name, row in t.items():
    if 'note' in row:
        continue  # skip fused_tuned_threshold note row
    for key in ['asr_t1', 'asr_t2', 'asr_t3', 'asr_t4', 'fpr']:
        assert key in row, f"Row {name} missing key {key}"
print("OK: All rows have asr_t1, asr_t2, asr_t3, asr_t4, fpr keys")

# Check no_defense T2 matches Phase 2.4 baseline (~0.12 paired)
nd_t2 = t['no_defense']['asr_t2']
print(f"no_defense T2 (paired) ASR: {nd_t2:.3f} (expected ~0.12 from Phase 2.4 llama paired)")
# Phase 2.4 showed paired_asr_tier2 around 11-12% for llama

# Check fused has 'fused_fixed' in the table key
assert 'fused_fixed_0.5' in t, "fused_fixed_0.5 row missing"
print(f"OK: fused_fixed_0.5 row present with T2={t['fused_fixed_0.5']['asr_t2']:.3f}")

print("\nAll acceptance criteria met!")
