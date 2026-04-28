"""Check test queries file."""
import json
data = json.load(open('data/test_queries.json'))
print(f'Total queries: {len(data)}')
paired = [q for q in data if q.get('paired', False)]
unpaired = [q for q in data if not q.get('paired', False)]
print(f'Paired (attack): {len(paired)}')
print(f'Unpaired (clean): {len(unpaired)}')
print(f'Sample: {data[0]}')
