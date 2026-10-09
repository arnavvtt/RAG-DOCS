"""
Discover actual paths for LangChain Python documentation in langchain-ai/docs.
Read-only. No downloads.
"""

import requests
from collections import Counter

REPO = "langchain-ai/docs"
BRANCH = "main"

print(f"Fetching tree for {REPO}@{BRANCH}...")
url = f"https://api.github.com/repos/{REPO}/git/trees/{BRANCH}?recursive=1"
r = requests.get(url, timeout=60)
r.raise_for_status()
tree = r.json().get("tree", [])

# All markdown files
mdx = [t["path"] for t in tree if t.get("type") == "blob" and t["path"].endswith((".md", ".mdx"))]
print(f"Total markdown files: {len(mdx)}\n")

# Python-specific paths under src/oss
print("=" * 70)
print("ALL PATHS UNDER src/oss/ (LangChain Open Source)")
print("=" * 70)

oss_paths = [p for p in mdx if p.startswith("src/oss/")]
print(f"Total: {len(oss_paths)}\n")

# Group by top-level structure
print("--- Grouped by src/oss/X ---")
groups = Counter("/".join(p.split("/")[:3]) for p in oss_paths)
for path, count in sorted(groups.items()):
    print(f"  {path}/ : {count} files")

# List concept-level paths
print("\n--- All 'concepts' paths ---")
for p in oss_paths:
    if "concept" in p.lower():
        print(f"  {p}")

print("\n--- All 'retriev' paths ---")
for p in oss_paths:
    if "retriev" in p.lower():
        print(f"  {p}")

print("\n--- All 'rag' paths ---")
for p in oss_paths:
    if "rag" in p.lower():
        print(f"  {p}")

print("\n--- All 'vector' paths ---")
for p in oss_paths:
    if "vector" in p.lower():
        print(f"  {p}")

print("\n--- All 'embed' paths ---")
for p in oss_paths:
    if "embed" in p.lower():
        print(f"  {p}")

print("\n--- All 'splitter' or 'split' paths ---")
for p in oss_paths:
    if "split" in p.lower():
        print(f"  {p}")

print("\n--- All 'loader' paths ---")
for p in oss_paths:
    if "loader" in p.lower():
        print(f"  {p}")

print("\n--- All 'document' paths ---")
for p in oss_paths:
    if "document" in p.lower():
        print(f"  {p}")

# Python/langchain-specific
print("\n" + "=" * 70)
print("ALL PATHS UNDER src/oss/python/")
print("=" * 70)
py_paths = [p for p in oss_paths if p.startswith("src/oss/python/")]
print(f"Total: {len(py_paths)}\n")

# Top-level of python/
py_groups = Counter("/".join(p.split("/")[:5]) for p in py_paths)
for path, count in sorted(py_groups.items()):
    print(f"  {path}/ : {count} files")