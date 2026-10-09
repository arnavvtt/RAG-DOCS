import sys
from rag_docs.core.embeddings import get_embeddings
from rag_docs.retrieval.formatter import format_context
from rag_docs.retrieval.retriever import retrieve
from rag_docs.generation.prompts import RAG_PROMPT
from rag_docs.vectorstore.chroma import load_vectorstore

query = sys.argv[1] if len(sys.argv) > 1 else "What is Pydantic?"
print(f"Query: {query}\n")

store = load_vectorstore(get_embeddings())
results = retrieve(query, store, top_k=4)

context = format_context(results)

# Print the exact prompt that goes to the LLM
prompt_value = RAG_PROMPT.format_messages(context=context, question=query)

print("=" * 70)
print("EXACT PROMPT SENT TO LLM")
print("=" * 70)
for msg in prompt_value:
    print(f"\n--- {msg.type.upper()} ---")
    print(msg.content)
print("=" * 70)