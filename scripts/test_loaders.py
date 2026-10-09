from pathlib import Path
from rag_docs.ingestion.loaders import load_directory

docs = load_directory(Path("data/raw"))

print(f"Total Documents: {len(docs)}")
print("-" * 60)

for d in docs:
    filename = d.metadata.get("filename")
    page = d.metadata.get("page")
    chars = len(d.page_content)
    preview = d.page_content[:80].replace("\n", " ")
    print(f"File: {filename}")
    print(f"  page   : {page}")
    print(f"  chars  : {chars}")
    print(f"  preview: {preview}...")
    print()