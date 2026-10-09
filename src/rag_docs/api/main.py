from fastapi import FastAPI

from rag_docs.api.routes import router

app = FastAPI(
    title="RAG Docs Q&A API",
    description="Ask questions over technical documentation using Mistral + ChromaDB.",
    version="0.1.0",
)

app.include_router(router)