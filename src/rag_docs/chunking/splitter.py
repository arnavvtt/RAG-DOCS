import logging
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150


def build_splitter(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> RecursiveCharacterTextSplitter:
    """Create a recursive splitter configured for technical docs."""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        length_function=len,
    )


def chunk_documents(
    docs: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Document]:
    """Split documents into smaller chunks, preserving metadata."""
    splitter = build_splitter(chunk_size, chunk_overlap)
    all_chunks: List[Document] = []

    for doc in docs:
        # split_documents copies metadata from parent to each chunk
        chunks = splitter.split_documents([doc])

        # Add a stable chunk_id per chunk
        for i, chunk in enumerate(chunks):
            source = chunk.metadata.get("filename", "unknown")
            chunk.metadata["chunk_id"] = f"{source}::chunk_{i:04d}"

        all_chunks.extend(chunks)

    logger.info(
        "Chunked %d document(s) into %d chunks (size=%d, overlap=%d)",
        len(docs), len(all_chunks), chunk_size, chunk_overlap,
    )
    return all_chunks