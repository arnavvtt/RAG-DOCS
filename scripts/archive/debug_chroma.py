from pathlib import Path
from rag_docs.core.embeddings import get_embeddings
from rag_docs.vectorstore.chroma import load_vectorstore

print("=== data/chroma folder contents ===")
chroma_dir = Path("data/chroma")
if chroma_dir.exists():
    for item in chroma_dir.rglob("*"):
        if item.is_file():
            print(f"  {item} ({item.stat().st_size} bytes)")
else:
    print("  data/chroma does NOT exist")

print("\n=== Load store and count ===")
store = load_vectorstore(get_embeddings())
if store is None:
    print("  load_vectorstore returned None")
else:
    print(f"  Collection name: {store._collection.name}")
    print(f"  Chunk count: {store._collection.count()}")

    # Sample 5 chunks to see actual files
    results = store._collection.get(limit=5, include=["metadatas"])
    print("\n=== Sample of stored chunks ===")
    for meta in results["metadatas"]:
        print(f"  {meta.get('filename')} :: {meta.get('chunk_id')}")