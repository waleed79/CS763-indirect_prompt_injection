"""Validate all 7 llama defense log files."""
import json
import glob

files = glob.glob('logs/defense_*_llama.json')
print(f"Found {len(files)} llama log files")

all_valid = True
for fpath in sorted(files):
    try:
        data = json.load(open(fpath))
        assert 'defense_mode' in data, f"Missing defense_mode key in {fpath}"
        assert 'aggregate' in data, f"Missing aggregate key in {fpath}"
        assert 'fpr' in data['aggregate'], f"Missing fpr in aggregate in {fpath}"
        asr_t1 = data['aggregate'].get('asr_tier1', 0)
        asr_t2 = data['aggregate'].get('asr_tier2', 0)
        fpr = data['aggregate']['fpr']
        mode = data['defense_mode']
        print(f"  OK: {fpath} - mode={mode}, T1={asr_t1:.3f}, T2={asr_t2:.3f}, FPR={fpr:.3f}")
    except Exception as e:
        print(f"  FAILED: {fpath} - {e}")
        all_valid = False

print(f"\nAll valid: {all_valid}")

# Baseline sanity check
baseline = json.load(open('logs/defense_off_llama.json'))
t2_asr = baseline['aggregate']['asr_tier2']
assert t2_asr > 0, f"T2 undefended ASR should be > 0, got {t2_asr}"
print(f"Baseline sanity OK: T2 undefended ASR = {t2_asr:.3f}")
