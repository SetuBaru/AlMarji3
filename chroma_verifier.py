import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

for collection in client.list_collections():
    print(
        collection.name,
        "->",
        collection.count(),
        "documents"
    )