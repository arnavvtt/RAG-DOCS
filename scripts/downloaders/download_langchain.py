"""Download LangChain docs from langchain-ai/docs repo (src/oss/)."""
import time
from pathlib import Path
import re

import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

REPO = "langchain-ai/docs"
BRANCH = "main"
SRC_PATH = "src/oss"
MAX_FILES = 20

def sanitize(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def fetch_tree(repo: str, branch: str):
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json().get("tree", [])

print(f"Fetching tree from {REPO}...")
tree = fetch_tree(REPO, BRANCH)

mdx_files = [
    item for item in tree
    if item.get("type") == "blob"
    and item.get("path", "").startswith(SRC_PATH + "/")
    and item["path"].endswith(".mdx")
]

print(f"Found {len(mdx_files)} .mdx files under {SRC_PATH}/")

# Prefer concept/overview/tutorial files
priority_keywords = ["concept", "overview", "rag", "retriev", "embed", "vector", "chunk", "document", "splitter", "prompt", "chat", "message"]
priority = [f for f in mdx_files if any(k in f["path"].lower() for k in priority_keywords)]
rest = [f for f in mdx_files if f not in priority]
ordered = priority + rest

# Limit
if len(ordered) > MAX_FILES:
    step = max(1, len(ordered) // MAX_FILES)
    ordered = ordered[::step][:MAX_FILES]

saved = 0
for item in ordered:
    raw_url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{item['path']}"
    try:
        r = requests.get(raw_url, timeout=30)
        r.raise_for_status()
        content = r.text
    except Exception as e:
        print(f"[skip] {item['path']}: {e}")
        continue

    rel = item["path"][len(SRC_PATH) + 1:]
    fname = f"langchain__{sanitize(rel).replace('/', '__')}"
    out = RAW_DIR / fname
    out.write_text(content, encoding="utf-8")
    saved += 1
    print(f"[ok] {fname}  ({len(content):,} chars)")
    time.sleep(0.05)

print(f"\nDone. {saved} LangChain files saved to {RAW_DIR}")