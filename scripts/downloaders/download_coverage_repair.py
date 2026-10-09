import time
from pathlib import Path
import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    ("langchain__concepts_document_loaders.mdx",
     "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/concepts/document_loaders.mdx"),
    ("langchain__concepts_text_splitters.mdx",
     "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/concepts/text_splitters.mdx"),
    ("langchain__concepts_embedding_models.mdx",
     "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/concepts/embedding_models.mdx"),
    ("langchain__concepts_vectorstores.mdx",
     "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/concepts/vectorstores.mdx"),
    ("langchain__concepts_retrievers.mdx",
     "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/concepts/retrievers.mdx"),
    ("langchain__concepts_retrieval.mdx",
     "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/concepts/retrieval.mdx"),
    ("langchain__concepts_rag.mdx",
     "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/concepts/rag.mdx"),
    ("pydantic__concepts_settings.md",
     "https://raw.githubusercontent.com/pydantic/pydantic/main/docs/concepts/settings.md"),
    ("streamlit__concepts_session-state.md",
     "https://raw.githubusercontent.com/streamlit/docs/main/content/develop/concepts/architecture/session-state.md"),
]

print(f"Targeted coverage repair — {len(TARGETS)} files\n")

saved = 0
skipped = 0
failed = []

for fname, url in TARGETS:
    dest = RAW_DIR / fname
    if dest.exists():
        print(f"[skip] {fname} — already exists ({dest.stat().st_size} bytes)")
        skipped += 1
        continue
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            print(f"[fail] {fname} — HTTP {r.status_code}")
            failed.append(fname)
            continue
        if len(r.text) < 100:
            print(f"[fail] {fname} — response too small ({len(r.text)} chars)")
            failed.append(fname)
            continue
        dest.write_text(r.text, encoding="utf-8")
        print(f"[ok]   {fname} ({len(r.text):,} chars)")
        saved += 1
        time.sleep(0.05)
    except Exception as e:
        print(f"[fail] {fname} — {e}")
        failed.append(fname)

print(f"\nSaved: {saved} | Skipped: {skipped} | Failed: {len(failed)}")
if failed:
    print("\nFailed files:")
    for f in failed:
        print(f"  - {f}")