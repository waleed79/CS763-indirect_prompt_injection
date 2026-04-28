"""Quick verification of training data structure."""
import json

with open('data/corpus_poisoned.jsonl', encoding='utf-8') as f:
    lines = f.readlines()
pids = [json.loads(l)['passage_id'] for l in lines]
print('Total:', len(pids))
print('Range:', min(pids), '-', max(pids))
t1 = [p for p in pids if 20000 <= p <= 20049]
t2 = [p for p in pids if 20050 <= p <= 20099]
t3 = [p for p in pids if 20100 <= p <= 20149]
t4 = [p for p in pids if 20200 <= p <= 20299]
clean = [p for p in pids if p < 20000]
print(f'T1: {len(t1)} T2: {len(t2)} T3: {len(t3)} T4: {len(t4)} Clean: {len(clean)}')

queries = json.load(open('data/test_queries.json', encoding='utf-8'))
print('Total queries:', len(queries))
paired_true = [i for i, q in enumerate(queries) if q.get('paired') is True]
paired_false = [i for i, q in enumerate(queries) if q.get('paired') is False]
print(f'paired=True: {len(paired_true)} first_5: {paired_true[:5]}')
print(f'paired=False: {len(paired_false)} first_5: {paired_false[:5]}')
