from typing import Dict, List, Tuple

from langchain_chroma import Chroma
from langchain_core.documents import Document

from rag_docs.core.embeddings import get_embeddings
from rag_docs.generation.chain import build_rag_chain
from rag_docs.vectorstore.chroma import load_vectorstore


def ask(
    question: str,
    vectorstore: Chroma = None,
    top_k: int = 4,
) -> Dict:
    """Answer a question using RAG. Returns answer + sources + raw results."""
    if vectorstore is None:
        vectorstore = load_vectorstore(get_embeddings())

    chain, retrieve_and_format = build_rag_chain(vectorstore, top_k=top_k)

    # Run retrieval separately so we can return citations
    intermediate = retrieve_and_format(question)
    results: List[Tuple[Document, float]] = intermediate["_results"]

    answer = chain.invoke(question)

    sources = []
    for i, (doc, score) in enumerate(results, start=1):
        sources.append({
            "ref": i,
            "filename": doc.metadata.get("filename"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "page": doc.metadata.get("page"),
            "score": round(score, 3),
        })

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }