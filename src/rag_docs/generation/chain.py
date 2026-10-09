from typing import Dict, List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_mistralai import ChatMistralAI

from rag_docs.core.config import settings
from rag_docs.generation.prompts import RAG_PROMPT
from rag_docs.retrieval.formatter import format_context
from rag_docs.retrieval.retriever import retrieve


def get_llm() -> ChatMistralAI:
    return ChatMistralAI(
        model="ministral-8b-2512",
        api_key=settings.mistral_api_key,
        temperature=0.1,
        max_retries=0,
    )


def build_rag_chain(vectorstore: Chroma, top_k: int = 4):
    """Build the RAG chain: query -> retrieve -> format -> prompt -> LLM -> text."""
    llm = get_llm()

    def retrieve_and_format(query: str) -> Dict:
        results = retrieve(query, vectorstore, top_k=top_k)
        return {
            "context": format_context(results),
            "question": query,
            "_results": results,  # keep for citation
        }

    chain = (
        RunnableLambda(retrieve_and_format)
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain, retrieve_and_format