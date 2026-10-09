import logging
from pathlib import Path

from rag_docs.chunking.splitter import chunk_documents
from rag_docs.core.embeddings import get_embeddings
from rag_docs.ingestion.cleaning import clean_documents
from rag_docs.ingestion.loaders import load_directory
from rag_docs.vectorstore.chroma import build_vectorstore

logger = logging.getLogger(__name__)


def ingest_directory(
    raw_dir: str = "data/raw",
    embedding_provider: str = "mistral",
):
    """Full ingestion pipeline: load → clean → chunk → embed → store."""
    logger.info("Starting ingestion from %s", raw_dir)

    # 1. Load
    docs = load_directory(Path(raw_dir))
    logger.info("Loaded %d document(s)", len(docs))

    # 2. Clean
    docs = clean_documents(docs)
    logger.info("Cleaned to %d document(s)", len(docs))

    # 3. Chunk
    chunks = chunk_documents(docs)
    logger.info("Produced %d chunk(s)", len(chunks))

    # 4. Embed + Store
    embeddings = get_embeddings(provider=embedding_provider)
    store = build_vectorstore(chunks, embeddings)

    logger.info("Ingestion complete. Vector store ready.")
    return store