from rag_docs.core.embeddings import get_embeddings
from rag_docs.retrieval.retriever import retrieve
from rag_docs.retrieval.mmr_retriever import retrieve_mmr
from rag_docs.vectorstore.chroma import load_vectorstore

store = load_vectorstore(get_embeddings())
query = "What is ChromaDB?"

print("=" * 70)
print("REGULAR (similarity):")
print("=" * 70)
for doc, score in retrieve(query, store, top_k=4):
    print(f"  score={score:.3f} | {doc.metadata['chunk_id']}")

print()
print("=" * 70)
print("MMR (diversity):")
print("=" * 70)
for doc in retrieve_mmr(query, store, top_k=4):
    print(f"  {doc.metadata['chunk_id']}")