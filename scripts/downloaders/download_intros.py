import time
from pathlib import Path

import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    # FastAPI intro
    ("fastapi/fastapi", "master", "docs/en/docs/index.md", "fastapi__index.md"),
    ("fastapi/fastapi", "master", "docs/en/docs/tutorial/index.md", "fastapi__tutorial_index.md"),
    ("fastapi/fastapi", "master", "docs/en/docs/tutorial/first-steps.md", "fastapi__tutorial_first-steps.md"),
    ("fastapi/fastapi", "master", "docs/en/docs/tutorial/path-params.md", "fastapi__tutorial_path-params.md"),
    ("fastapi/fastapi", "master", "docs/en/docs/tutorial/query-params.md", "fastapi__tutorial_query-params.md"),
    ("fastapi/fastapi", "master", "docs/en/docs/tutorial/body.md", "fastapi__tutorial_body.md"),
    # Pydantic intro
    ("pydantic/pydantic", "main", "docs/why.md", "pydantic__why.md"),
    ("pydantic/pydantic", "main", "docs/index.md", "pydantic__index.md"),
    ("pydantic/pydantic", "main", "docs/concepts/models.md", "pydantic__concepts_models_full.md"),
    # LangChain intro
    ("langchain-ai/langchain", "master", "docs/docs/concepts/architecture.mdx", "langchain__concepts_architecture.mdx"),
    ("langchain-ai/langchain", "master", "docs/docs/concepts/rag.mdx", "langchain__concepts_rag.mdx"),
    ("langchain-ai/langchain", "master", "docs/docs/concepts/index.mdx", "langchain__concepts_index.mdx"),
    # ChromaDB intro
    ("chroma-core/chroma", "main", "docs/mintlify/introduction.mdx", "chromadb__introduction.mdx"),
    ("chroma-core/chroma", "main", "docs/mintlify/docs/overview.mdx", "chromadb__overview.mdx"),
    # Streamlit intro
    ("streamlit/docs", "main", "content/get-started/fundamentals/main-concepts.md", "streamlit__main-concepts.md"),
    # Typer intro
    ("fastapi/typer", "master", "docs/tutorial/index.md", "typer__tutorial_index.md"),
]

saved = 0
for repo, branch, path, fname in FILES:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and len(r.text) > 100:
            (RAW_DIR / fname).write_text(r.text, encoding="utf-8")
            print(f"[ok] {fname} ({len(r.text):,} chars)")
            saved += 1
        else:
            print(f"[skip] {fname}: status {r.status_code}")
        time.sleep(0.05)
    except Exception as e:
        print(f"[skip] {fname}: {e}")

print(f"\nDone. {saved} intro files saved.")