from pathlib import Path

from rag_docs.chunking.splitter import chunk_documents
from rag_docs.ingestion.cleaning import clean_documents
from rag_docs.ingestion.loaders import load_directory

docs = load_directory(Path("data/raw"))
docs = clean_documents(docs)

configs = [
    (500, 100, "small"),
    (800, 150, "baseline"),
    (1200, 200, "large"),
]

print(f"{'Config':<12} {'Chunks':<8} {'Avg':<6} {'Min':<6} {'Max':<6}")
print("-" * 45)

for size, overlap, name in configs:
    chunks = chunk_documents(docs, chunk_size=size, chunk_overlap=overlap)
    sizes = [len(c.page_content) for c in chunks]
    print(
        f"{name:<12} {len(chunks):<8} "
        f"{sum(sizes) // len(sizes):<6} {min(sizes):<6} {max(sizes):<6}"
    )