from pathlib import Path

from rag_docs.chunking.splitter import chunk_documents
from rag_docs.ingestion.cleaning import clean_documents, clean_text
from rag_docs.ingestion.loaders import load_directory


def test_clean_text_collapses_whitespace():
    assert clean_text("hello    world") == "hello world"
    assert clean_text("a\n\n\n\nb") == "a\n\nb"


def test_load_directory_returns_documents():
    docs = load_directory(Path("data/raw"))
    assert len(docs) >= 3
    assert all(d.metadata.get("filename") for d in docs)


def test_chunking_preserves_metadata():
    docs = load_directory(Path("data/raw"))
    docs = clean_documents(docs)
    chunks = chunk_documents(docs)
    assert len(chunks) > 0
    for chunk in chunks:
        assert "chunk_id" in chunk.metadata
        assert "filename" in chunk.metadata
        assert "source" in chunk.metadata


def test_chunk_size_within_bounds():
    docs = load_directory(Path("data/raw"))
    docs = clean_documents(docs)
    chunks = chunk_documents(docs, chunk_size=800, chunk_overlap=150)
    sizes = [len(c.page_content) for c in chunks]
    assert max(sizes) <= 900
    assert min(sizes) > 50