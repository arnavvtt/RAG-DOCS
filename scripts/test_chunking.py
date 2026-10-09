from pathlib import Path
from rag_docs.ingestion.loaders import load_directory
from rag_docs.ingestion.cleaning import clean_documents
from rag_docs.chunking.splitter import chunk_documents

# Full ingestion pipeline so far
docs = load_directory(Path("data/raw"))
docs = clean_documents(docs)
chunks = chunk_documents(docs)

print(f"Documents : {len(docs)}")
print(f"Chunks    : {len(chunks)}")
print(f"Avg chars : {sum(len(c.page_content) for c in chunks) // len(chunks)}")
print("-" * 70)

for c in chunks[:5]:
    meta = c.metadata
    print(f"chunk_id : {meta['chunk_id']}")
    print(f"  source : {meta['filename']}")
    print(f"  page   : {meta['page']}")
    print(f"  chars  : {len(c.page_content)}")
    print(f"  text   : {c.page_content[:90]}...")
    print()