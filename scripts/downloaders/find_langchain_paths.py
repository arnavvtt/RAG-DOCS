import requests

repo = "langchain-ai/docs"
branch = "main"

url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
r = requests.get(url, timeout=60)
tree = r.json().get("tree", [])

mdx_files = [
    t["path"] for t in tree
    if t.get("type") == "blob" and t["path"].endswith((".md", ".mdx"))
]

print(f"Total markdown files in {repo}: {len(mdx_files)}")

from collections import Counter
top_folders = Counter(p.split("/")[0] for p in mdx_files)
print("\nTop-level folders:")
for folder, count in top_folders.most_common():
    print(f"  {folder}/ : {count} files")

print("\nFirst 30 paths:")
for p in mdx_files[:30]:
    print(f"  {p}")

print("\nPaths containing 'concept':")
for p in mdx_files:
    if "concept" in p.lower():
        print(f"  {p}")

print("\nPaths containing 'rag':")
for p in mdx_files:
    if "rag" in p.lower():
        print(f"  {p}")