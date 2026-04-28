"""Verify corpus_poisoned.jsonl and nq_poisoned_v5 collection."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Corpus check
entries = [json.loads(l) for l in open('data/corpus_poisoned.jsonl')]
adaptive = [e for e in entries if e.get('passage_id', 0) >= 20500]
print(f'Adaptive entries: {len(adaptive)}')
assert len(adaptive) >= 30, f'Expected >=30 adaptive entries, got {len(adaptive)}'
first_adaptive_id = min(e['passage_id'] for e in adaptive)
print(f'First adaptive passage_id: {first_adaptive_id}')
assert first_adaptive_id == 20500, f'Expected 20500, got {first_adaptive_id}'
print('PASS: corpus check')

# Collection check
import chromadb
c = chromadb.PersistentClient('.chroma')
col = c.get_collection('nq_poisoned_v5')
print(f'nq_poisoned_v5 count: {col.count()}')
assert col.count() >= 1050, f'Expected >=1050, got {col.count()}'
print('PASS: collection check')
