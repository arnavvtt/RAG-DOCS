from pathlib import Path
from rag_docs.ingestion.loaders import load_directory
from rag_docs.ingestion.cleaning import clean_documents

# Load raw
docs = load_directory(Path("data/raw"))

# Compare before/after
print(f"Documents loaded : {len(docs)}")
print(f"Total chars (raw): {sum(len(d.page_content) for d in docs)}")

cleaned = clean_documents(docs)

print(f"Documents kept   : {len(cleaned)}")
print(f"Total chars (clean): {sum(len(d.page_content) for d in cleaned)}")
print("-" * 60)

# Show a before/after snippet
sample = docs[0]
sample_clean = cleaned[0]

print("BEFORE (first 200 chars):")
print(repr(sample.page_content[:200]))
print()
print("AFTER (first 200 chars):")
print(repr(sample_clean.page_content[:200]))
print()
print("Metadata preserved:", sample_clean.metadata)