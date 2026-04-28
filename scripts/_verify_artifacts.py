"""Verify all 3 model artifacts are valid."""
import json
from pathlib import Path
from transformers import DistilBertForSequenceClassification

# Check BERT checkpoint
bert = DistilBertForSequenceClassification.from_pretrained('models/bert_classifier')
print(f'BERT loaded OK: num_labels={bert.config.num_labels}')

# Check LR JSON
lr_data = json.loads(Path('models/lr_meta_classifier.json').read_text())
assert len(lr_data['lr_coef'][0]) == 4, f'Expected 4 features, got {len(lr_data["lr_coef"][0])}'
print(f'LR coef shape: {len(lr_data["lr_coef"])}x{len(lr_data["lr_coef"][0])}')
print(f'LR intercept: {lr_data["lr_intercept"]}')
print(f'Scaler mean: {lr_data["scaler_mean"]}')
assert "lr_coef" in lr_data
assert "lr_intercept" in lr_data
assert "scaler_mean" in lr_data
assert "scaler_scale" in lr_data
print('LR OK')

# Check Signal 4 baseline
s4 = json.loads(Path('models/signal4_baseline.json').read_text())
assert "mu" in s4 and "std" in s4
print(f'Signal 4 baseline: mu={s4["mu"]:.4f}, std={s4["std"]:.4f}')
assert s4["std"] > 0
print('S4 OK')

print('All artifacts OK')
