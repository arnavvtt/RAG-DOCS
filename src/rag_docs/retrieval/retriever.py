from typing import List, Tuple

from langchain_chroma import Chroma
from langchain_core.documents import Document


def retrieve(
    query: str,
    vectorstore: Chroma,
    top_k: int = 4,
) -> List[Tuple[Document, float]]:
    """Retrieve top-k documents similar to the query.

    Returns a list of (Document, similarity_score) tuples, sorted
    by relevance (highest first).
    """
    results = vectorstore.similarity_search_with_relevance_scores(
        query=query,
        k=top_k,
    )
    return results