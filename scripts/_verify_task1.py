import json, pathlib
required = [
    'logs/adaptive_fused_llama_s1.json',
    'logs/adaptive_fused_llama_s2.json',
    'logs/adaptive_fused_llama_s3.json',
    'logs/adaptive_fused_mistral.json',
    'logs/adaptive_fused_t0.5_llama.json',
    'logs/adaptive_fused_t0.7_llama.json',
    'logs/adaptive_fused_t0.8_llama.json',
    'logs/adaptive_fused_t0.9_llama.json',
    'logs/adaptive_nodefense_llama.json',
    'logs/adaptive_imperative_llama.json',
]
for f in required:
    if not pathlib.Path(f).exists():
        print(f'MISSING: {f}')
    else:
        d = json.load(open(f))
        asr = d['aggregate'].get('asr_adaptive', 'MISSING')
        fpr = d['aggregate'].get('fpr', 'MISSING')
        print(f'OK {f}: asr_adaptive={asr}, fpr={fpr}')
