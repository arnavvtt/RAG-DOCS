from rag_docs.core.embeddings import get_embeddings
from rag_docs.retrieval.retriever import retrieve
from rag_docs.vectorstore.chroma import load_vectorstore

store = load_vectorstore(get_embeddings())
print(f"Total chunks in store: {store._collection.count()}\n")

for query in ["What is RAG?", "What is retrieval?", "What is a knowledge base?"]:
    print(f"=== Query: {query} ===")
    results = retrieve(query, store, top_k=4)
    for i, (doc, score) in enumerate(results, start=1):
        fname = doc.metadata.get("filename", "?")
        preview = doc.page_content[:100].replace("\n", " ")
        print(f"  [{i}] score={score:.4f} | {fname}")
        print(f"      {preview}...")
    print()