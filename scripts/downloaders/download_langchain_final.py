"""
Download verified LangChain Python documentation.

All URLs verified from docs.langchain.com — no 404s.
Scope: RAG, retrieval, documents, loaders, splitters, embeddings,
vector stores, retrievers, knowledge base tutorial.
"""

import time
from pathlib import Path
import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://docs.langchain.com/oss/python"

# (output_filename, url_path)
TARGETS = [
    # --- Core LangChain overview & concepts ---
    ("langchain__overview.md",              f"{BASE}/langchain/overview.md"),
    ("langchain__component-architecture.md", f"{BASE}/langchain/component-architecture.md"),

    # --- RAG & Retrieval (the big one) ---
    ("langchain__deepagents__retrieval.md", f"{BASE}/deepagents/retrieval.md"),
    ("langchain__langgraph__agentic-rag.md", f"{BASE}/langgraph/agentic-rag.md"),

    # --- Knowledge Base / Semantic Search Tutorial ---
    ("langchain__knowledge-base.md",        f"{BASE}/langchain/knowledge-base.md"),

    # --- Agentic patterns ---
    ("langchain__agents.md",                f"{BASE}/langchain/agents.md"),
    ("langchain__quickstart.md",            f"{BASE}/langchain/quickstart.md"),
]

print(f"Downloading {len(TARGETS)} verified LangChain files...\n")

saved = 0
failed = []

for fname, url in TARGETS:
    dest = RAW_DIR / fname
    if dest.exists():
        print(f"[skip] {fname} (exists)")
        continue

    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            print(f"[fail] {fname} — HTTP {r.status_code}")
            failed.append(fname)
            continue
        if len(r.text) < 500:
            print(f"[fail] {fname} — too small ({len(r.text)} chars)")
            failed.append(fname)
            continue
        dest.write_text(r.text, encoding="utf-8")
        print(f"[ok]   {fname} ({len(r.text):,} chars)")
        saved += 1
        time.sleep(0.1)
    except Exception as e:
        print(f"[fail] {fname} — {e}")
        failed.append(fname)

print(f"\n{'='*60}")
print(f"SAVED: {saved} | FAILED: {len(failed)}")
if failed:
    print("\nFailed:")
    for f in failed:
        print(f"  - {f}")

# Final count
total = len(list(RAW_DIR.glob("*.md")) + list(RAW_DIR.glob("*.mdx")))
print(f"\nTotal files in data/raw/: {total}")