from langchain_core.embeddings import Embeddings

from rag_docs.core.config import settings


def get_embeddings(provider: str = "mistral") -> Embeddings:
    """Return an Embeddings instance for the given provider.

    Keeps the RAG pipeline provider-independent: callers receive an
    `Embeddings` interface, never a concrete provider class.
    """
    if provider == "mistral":
        from langchain_mistralai import MistralAIEmbeddings
        return MistralAIEmbeddings(
            model="mistral-embed",
            api_key=settings.mistral_api_key,
        )

    raise ValueError(f"Unknown embedding provider: {provider}")