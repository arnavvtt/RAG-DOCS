from rag_docs.services.ingest_service import ingest_directory

print("Running full ingestion pipeline...")
store = ingest_directory(raw_dir="data/raw")

# Check collection size
collection = store._collection
count = collection.count()
print(f"\n✅ Vectors stored: {count}")

# Peek at a few stored items
results = collection.get(limit=3, include=["metadatas", "documents"])
print("\nSample stored chunks:")
for i, (meta, doc) in enumerate(zip(results["metadatas"], results["documents"])):
    print(f"\n[{i+1}] chunk_id: {meta.get('chunk_id')}")
    print(f"    source  : {meta.get('filename')}")
    print(f"    chars   : {len(doc)}")
    print(f"    text    : {doc[:80]}...")