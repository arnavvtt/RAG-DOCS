from rag_docs.core.embeddings import get_embeddings
from rag_docs.retrieval.retriever import retrieve
from rag_docs.vectorstore.chroma import load_vectorstore


def test_retrieval_returns_top_k():
    store = load_vectorstore(get_embeddings())
    results = retrieve("What is RAG?", store, top_k=3)
    assert len(results) == 3


def test_retrieval_scores_descending():
    store = load_vectorstore(get_embeddings())
    results = retrieve("What is RAG?", store, top_k=4)
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)


def test_retrieval_finds_relevant_source():
    store = load_vectorstore(get_embeddings())
    results = retrieve("What is RAG?", store, top_k=4)
    sources = [d.metadata.get("filename") for d, _ in results]
    assert "langchain_rag.md" in sources