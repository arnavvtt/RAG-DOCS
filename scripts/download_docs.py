"""
Download technical documentation markdown files from GitHub repos.
Saves them to data/raw/ with a source prefix to avoid name collisions.
"""

import time
from pathlib import Path
import re

import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = [
    # (prefix, repo, branch, docs_path, max_files)
    ("fastapi",   "fastapi/fastapi",     "master", "docs/en/docs",             12),
    ("langchain", "langchain-ai/docs",   "main",   "src/oss/python/langchain", 10),
    ("chromadb",  "chroma-core/chroma",  "main",   "docs/mintlify",            10),
    ("pydantic",  "pydantic/pydantic",   "main",   "docs",                     10),
    ("streamlit", "streamlit/docs",      "main",   "content",                  10),
    ("typer",     "fastapi/typer",       "master", "docs",                     10),
]


def sanitize(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def fetch_tree(repo: str, branch: str):
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json().get("tree", [])


def download_source(prefix, repo, branch, docs_path, max_files):
    print(f"\n[{prefix}] {repo} @ {branch}  (docs: {docs_path})")
    try:
        tree = fetch_tree(repo, branch)
    except Exception as e:
        print(f"  [skip] tree fetch failed: {e}")
        return 0

    md_files = [
        item for item in tree
        if item.get("type") == "blob"
        and item.get("path", "").startswith(docs_path + "/")
        and (item["path"].endswith(".md") or item["path"].endswith(".mdx"))
    ]
    print(f"  found {len(md_files)} markdown files")

    if not md_files:
        return 0

    if len(md_files) > max_files:
        step = max(1, len(md_files) // max_files)
        md_files = md_files[::step][:max_files]

    saved = 0
    for item in md_files:
        raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{item['path']}"
        try:
            r = requests.get(raw_url, timeout=30)
            r.raise_for_status()
            content = r.text
        except Exception as e:
            print(f"  [skip] {item['path']}: {e}")
            continue

        rel = item["path"][len(docs_path) + 1:]
        fname = f"{prefix}__{sanitize(rel).replace('/', '__')}"
        out = RAW_DIR / fname
        out.write_text(content, encoding="utf-8")
        saved += 1
        print(f"  [ok] {fname}  ({len(content):,} chars)")
        time.sleep(0.05)

    return saved


def main():
    total = 0
    for prefix, repo, branch, path, limit in SOURCES:
        total += download_source(prefix, repo, branch, path, limit)
    print(f"\nDone. {total} new files saved to {RAW_DIR}")


if __name__ == "__main__":
    main()