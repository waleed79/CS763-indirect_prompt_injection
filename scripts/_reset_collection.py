import chromadb
client = chromadb.PersistentClient(path='.chroma')
for c in client.list_collections():
    if c.name == 'nq_poisoned_v3':
        client.delete_collection('nq_poisoned_v3')
        print('deleted nq_poisoned_v3')
print('Collections after reset:')
for c in client.list_collections():
    print(f'  {c.name}: {c.count()}')
