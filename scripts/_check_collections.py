import chromadb
client = chromadb.PersistentClient(path='.chroma')
for c in client.list_collections():
    try:
        count = c.count()
    except Exception as e:
        count = f'ERR:{e}'
    print(f'{c.name}: {count}')
