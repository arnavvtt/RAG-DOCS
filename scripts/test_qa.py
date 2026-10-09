from rag_docs.services.qa_service import ask

questions = [
    "What are the distance metrics supported in ChromaDB?",
    "How do I install FastAPI?",
    "What is RAG and why is it used?",
    "What is the capital of France?",  # Should trigger "I don't know"
]

for q in questions:
    print("=" * 70)
    print(f"Q: {q}")
    print("-" * 70)

    result = ask(q)

    print(f"A: {result['answer']}\n")
    print("Sources:")
    for s in result["sources"]:
        print(f"  [{s['ref']}] {s['filename']} (score: {s['score']})")
    print()