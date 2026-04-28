"""Check test_queries.json structure to find the correct key for question text."""
import json
with open('data/test_queries.json', encoding='utf-8') as f:
    queries = json.load(f)
print('Keys in query 0:', list(queries[0].keys()))
print('Query 0:', json.dumps(queries[0], ensure_ascii=False)[:300])
print('Query 50:', json.dumps(queries[50], ensure_ascii=False)[:300])
