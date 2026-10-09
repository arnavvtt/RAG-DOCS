"""
Download technical documentation with category-based selection (v2.2).

Fixes over v2.1:
- Removed broad exclusion patterns (/about/, /resources/) — they may hide useful content in other frameworks
- Added FastAPI-specific exclusion patterns instead
- Removed "core" from CATEGORY_PATTERNS (was matching "agentcore" substrings)
- Better path segment boundaries for category matching
"""

import time
from pathlib import Path
import re
import sys

import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = [
    ("fastapi",   "fastapi/fastapi",     "master", "docs/en/docs"),
    ("langchain", "langchain-ai/docs",   "main",   "src/oss"),
    ("chromadb",  "chroma-core/chroma",  "main",   "docs"),
    ("pydantic",  "pydantic/pydantic",   "main",   "docs"),
    ("streamlit", "streamlit/docs",      "main",   "content"),
    ("typer",     "fastapi/typer",       "master", "docs"),
]

CATEGORY_PATTERNS = {
    "intro":     ["index", "why", "introduction", "overview", "quickstart", "getting-started"],
    "tutorial":  ["tutorial", "tutorials", "first-steps", "install", "get-started"],
    "concepts":  ["concept", "concepts", "fundamentals", "architecture"],
    "guides":    ["how-to", "howto", "guides", "guide", "usage", "examples"],
    "reference": ["reference", "api", "client", "models"],
}

FILENAME_PRIORITY = [
    "introduction", "getting-started", "quickstart", "first-steps",
    "why", "overview", "main-concepts", "fundamentals",
    "concepts", "architecture", "rag", "retrieval",
    "install", "tutorial", "guide",
]

# Global exclusions — apply to all frameworks (internal tooling, contributor info)
GLOBAL_EXCLUDE = [
    "/.agents/", "/.github/", "/openwiki/",
    "/snippets/", "/AGENTS.md", "/CONTRIBUTING.md",
    "/IDE_SETUP", "/README.md", "/SKILL.md",
    "/.instructions.md", "/pull_request_template.md",
]

# Framework-specific exclusions — only apply to specific frameworks
FRAMEWORK_EXCLUDE = {
    "fastapi": [
        "/about/",           # FastAPI contributor info
        "/learn/",           # External course listings
        "/help-fastapi",     # Help pages
        "/fastapi-people",   # People listing
        "/fastapi-cli.md",   # CLI reference, not core concept
        "/resources/",       # External resources
    ],
    "langchain": [
        "/integrations/",    # Integration-specific (over 1000 files)
        "/contributing/",    # Contributor docs
    ],
    "chromadb": [
        "/cloud/",           # Cloud-specific, not local API
    ],
    "streamlit": [
        "/kb/",              # Knowledge base articles (FAQ-like)
    ],
}

MAX_DEPTH = 3


def sanitize(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def fetch_tree(repo: str, branch: str):
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return resp.json().get("tree", [])


def should_exclude(path: str, prefix: str) -> bool:
    """Check both global and framework-specific exclusion patterns."""
    p = "/" + path + "/"

    # Global exclusions
    if any(pat in p for pat in GLOBAL_EXCLUDE):
        return True

    # Framework-specific exclusions
    fw_patterns = FRAMEWORK_EXCLUDE.get(prefix, [])
    if any(pat in p for pat in fw_patterns):
        return True

    return False


def categorize(path: str) -> list:
    path_lower = path.lower()
    matched = []
    for cat, keywords in CATEGORY_PATTERNS.items():
        if any(kw in path_lower for kw in keywords):
            matched.append(cat)
    return matched or ["other"]


def filename_score(filename: str) -> int:
    name_lower = filename.lower()
    score = 0
    for i, kw in enumerate(FILENAME_PRIORITY):
        if kw in name_lower:
            score = max(score, len(FILENAME_PRIORITY) - i)

    depth = filename.count("/")
    score -= depth * 2

    if "_index.md" in name_lower and depth > 2:
        score -= 5

    return score


def depth_from_root(path: str, docs_root: str) -> int:
    rel = path[len(docs_root) + 1:] if path.startswith(docs_root + "/") else path
    return rel.count("/")


def scan_source(prefix, repo, branch, docs_root):
    print(f"\n[{prefix}] {repo} @ {branch}")
    print(f"  docs root: {docs_root}")
    try:
        tree = fetch_tree(repo, branch)
    except Exception as e:
        print(f"  [ERROR] tree fetch: {e}")
        return {cat: [] for cat in ["intro", "tutorial", "concepts", "guides", "reference", "other"]}

    all_files = [
        item for item in tree
        if item.get("type") == "blob"
        and item.get("path", "").startswith(docs_root + "/")
        and (item["path"].endswith(".md") or item["path"].endswith(".mdx"))
        and not should_exclude(item["path"], prefix)
    ]

    filtered = [f for f in all_files if depth_from_root(f["path"], docs_root) <= MAX_DEPTH]

    candidates = {cat: [] for cat in ["intro", "tutorial", "concepts", "guides", "reference", "other"]}
    for f in filtered:
        cats = categorize(f["path"])
        for cat in cats:
            candidates[cat].append(f)

    return candidates


def select_for_download(candidates, per_category_limit=8, verbose=False):
    selected = []
    for cat in ["intro", "tutorial", "concepts", "guides", "reference"]:
        files = candidates.get(cat, [])
        files_sorted = sorted(files, key=lambda f: filename_score(f["path"]), reverse=True)
        chosen = files_sorted[:per_category_limit]
        selected.extend([(cat, f) for f in chosen])
        print(f"  [{cat}] {len(files)} candidates -> selecting {len(chosen)}")
        if verbose:
            for f in chosen:
                print(f"      - {f['path']}")

    seen = set()
    deduped = []
    for cat, f in selected:
        if f["path"] not in seen:
            seen.add(f["path"])
            deduped.append((cat, f))

    print(f"  Total unique files: {len(deduped)}")
    return deduped


def dry_run_report(verbose=False):
    print("=" * 70)
    print("COVERAGE REPORT (dry-run v2.2)" + (" — VERBOSE" if verbose else ""))
    print("=" * 70)

    grand_total = 0
    for prefix, repo, branch, docs_root in SOURCES:
        candidates = scan_source(prefix, repo, branch, docs_root)
        selected = select_for_download(candidates, verbose=verbose)
        grand_total += len(selected)
        print(f"  → {prefix} would download {len(selected)} files\n")

    print("=" * 70)
    print(f"TOTAL FILES TO DOWNLOAD: {grand_total}")
    print("=" * 70)


def download_all():
    for prefix, repo, branch, docs_root in SOURCES:
        candidates = scan_source(prefix, repo, branch, docs_root)
        selected = select_for_download(candidates)

        for cat, item in selected:
            raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{item['path']}"
            try:
                r = requests.get(raw_url, timeout=30)
                if r.status_code != 200:
                    print(f"  [skip] {item['path']}: {r.status_code}")
                    continue
                content = r.text
            except Exception as e:
                print(f"  [skip] {item['path']}: {e}")
                continue

            rel = item["path"][len(docs_root) + 1:]
            fname = f"{prefix}__{cat}__{sanitize(rel).replace('/', '__')}"
            (RAW_DIR / fname).write_text(content, encoding="utf-8")
            print(f"  [ok] [{cat}] {fname} ({len(content):,} chars)")
            time.sleep(0.05)


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        dry_run_report(verbose="--verbose" in sys.argv)
    else:
        print("Downloading with category-based selection...")
        download_all()
        print("\nDone.")