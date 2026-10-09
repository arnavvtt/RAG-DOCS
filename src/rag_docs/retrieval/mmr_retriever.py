from typing import List, Tuple

from langchain_chroma import Chroma
from langchain_core.documents import Document


def retrieve_mmr(
    query: str,
    vectorstore: Chroma,
    top_k: int = 4,
    fetch_k: int = 20,
    lambda_mult: float = 0.5,
) -> List[Document]:
    """MMR retrieval: relevance + diversity.

    fetch_k: how many candidates to fetch before MMR reranks
    lambda_mult: 0 = max diversity, 1 = max relevance
    """
    return vectorstore.max_marginal_relevance_search(
        query=query,
        k=top_k,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult,
    )