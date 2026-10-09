from rag_docs.core.embeddings import get_embeddings
from rag_docs.vectorstore.chroma import load_vectorstore

store = load_vectorstore(get_embeddings())

# Query for the first chunk of pydantic models file
results = store._collection.get(
    where={"chunk_id": "pydantic__concepts_models.md::chunk_0000"},
    include=["documents", "metadatas"],
)

print(f"Chunks found: {len(results['ids'])}\n")

for i in range(len(results["ids"])):
    meta = results["metadatas"][i]
    doc = results["documents"][i]
    print(f"--- {meta['chunk_id']} ---")
    print(f"Chars: {len(doc)}")
    print(f"Full content:\n")
    print(doc)
    print("\n" + "=" * 70 + "\n")