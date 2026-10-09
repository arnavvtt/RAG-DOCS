from pathlib import Path
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

# Default location — must match .gitignore's 'data/chroma'
DEFAULT_PERSIST_DIR = "data/chroma"
DEFAULT_COLLECTION = "docs"


def build_vectorstore(
    chunks: List[Document],
    embeddings: Embeddings,
    persist_directory: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION,
) -> Chroma:
    """Create (or overwrite) a persistent Chroma collection from chunks."""
    Path(persist_directory).mkdir(parents=True, exist_ok=True)

    store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )
    return store


def load_vectorstore(
    embeddings: Embeddings,
    persist_directory: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION,
) -> Optional[Chroma]:
    """Load an existing persistent collection, or return None if missing."""
    if not Path(persist_directory).exists():
        return None

    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )


def delete_collection(
    embeddings: Embeddings,
    persist_directory: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION,
) -> None:
    """Drop a collection entirely (used before re-indexing)."""
    store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    store.delete_collection()