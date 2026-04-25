import json
t = json.load(open('logs/ablation_table.json'))
required = ['eval05_aggregation', 'atk08_vs_fused_llama', 'atk09_vs_nodefense_llama', 'threshold_sweep', 'causal_attribution']
for k in required:
    print(f'{k}: {"PRESENT" if k in t else "MISSING"}')
print('EVAL-05 asr_adaptive mean:', t.get('eval05_aggregation', {}).get('metrics', {}).get('asr_adaptive', {}).get('mean', 'MISSING'))
print('Threshold sweep entries:', len(t.get('threshold_sweep', {}).get('thresholds', [])))
print('Causal attribution llama ROC AUC:', t.get('causal_attribution', {}).get('llama3_2_3b', {}).get('roc_auc', 'MISSING'))
