"""Quick verification script for ratio sweep corpus files."""
import json

for ratio, expected in [('0005', 5), ('0010', 10), ('0020', 20), ('0050', 50), ('0100', 100)]:
    path = f'data/corpus_ratio_{ratio}.jsonl'
    lines = [json.loads(l) for l in open(path, encoding='utf-8')]
    poisoned = [p for p in lines if p['passage_id'] >= 20000]
    assert len(poisoned) == expected, f'{path}: expected {expected}, got {len(poisoned)}'
    ids = [p['passage_id'] for p in lines]
    assert len(ids) == len(set(ids)), f'{path}: duplicate passage_ids found'
    print(f'{path}: {len(lines)} total, {len(poisoned)} poisoned  OK')
print('ALL 5 FILES OK')
