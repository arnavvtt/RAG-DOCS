from rag_docs.core.embeddings import get_embeddings
from rag_docs.retrieval.formatter import format_context
from rag_docs.retrieval.retriever import retrieve
from rag_docs.vectorstore.chroma import load_vectorstore

embeddings = get_embeddings()
store = load_vectorstore(embeddings)

query = "What are the distance metrics supported in ChromaDB?"
print(f"Query: {query}\n")

results = retrieve(query, store, top_k=4)

print(f"Retrieved {len(results)} chunks:\n")
for i, (doc, score) in enumerate(results, start=1):
    print(f"[{i}] score={score:.3f} | {doc.metadata.get('chunk_id')}")
    print(f"    {doc.page_content[:120]}...")
    print()

print("=" * 70)
print("Formatted context for LLM:")
print("=" * 70)
print(format_context(results))