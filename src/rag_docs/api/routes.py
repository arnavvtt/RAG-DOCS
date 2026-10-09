from fastapi import APIRouter, HTTPException

from rag_docs.api.schemas import AskRequest, AskResponse, HealthResponse
from rag_docs.core.embeddings import get_embeddings
from rag_docs.services.qa_service import ask
from rag_docs.vectorstore.chroma import load_vectorstore

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    """Health check — confirms vectorstore is loaded."""
    store = load_vectorstore(get_embeddings())
    if store is None:
        raise HTTPException(status_code=503, detail="Vectorstore not found. Run ingestion first.")
    return HealthResponse(status="ok", chunks_indexed=store._collection.count())


@router.post("/ask", response_model=AskResponse)
def ask_endpoint(request: AskRequest):
    """Answer a question using the RAG pipeline."""
    try:
        result = ask(request.question, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {e}")

    return AskResponse(**result)