import sys
from rag_docs.core.embeddings import get_embeddings
from rag_docs.retrieval.retriever import retrieve
from rag_docs.vectorstore.chroma import load_vectorstore

query = sys.argv[1] if len(sys.argv) > 1 else "what is pydantic"
print(f"Query: {query}\n")

store = load_vectorstore(get_embeddings())
print(f"Total chunks in store: {store._collection.count()}\n")

results = retrieve(query, store, top_k=8)

print(f"Top-8 chunks retrieved:\n")
for i, (doc, score) in enumerate(results, start=1):
    filename = doc.metadata.get("filename", "?")
    preview = doc.page_content[:150].replace("\n", " ")
    print(f"[{i}] score={score:.4f} | {filename}")
    print(f"    {preview}...\n")