import re
import unicodedata
from typing import List

from langchain_core.documents import Document


# Matches 3 or more consecutive newlines (paragraph breaks kept as 2)
_MULTI_NEWLINE = re.compile(r"\n{3,}")

# Matches 2 or more spaces/tabs (kept as single space)
_MULTI_SPACE = re.compile(r"[ \t]{2,}")


def clean_text(text: str) -> str:
    """Normalize a single string of text."""
    if not text:
        return ""

    # 1. Unicode normalization (fixes smart quotes, weird dashes, etc.)
    text = unicodedata.normalize("NFKC", text)

    # 2. Normalize line endings to \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Collapse multiple spaces/tabs into one
    text = _MULTI_SPACE.sub(" ", text)

    # 4. Collapse 3+ newlines into 2 (preserves paragraph breaks)
    text = _MULTI_NEWLINE.sub("\n\n", text)

    # 5. Strip leading/trailing whitespace per line
    text = "\n".join(line.strip() for line in text.split("\n"))

    # 6. Strip leading/trailing whitespace of entire string
    text = text.strip()

    return text


def clean_documents(docs: List[Document]) -> List[Document]:
    """Clean page_content of every Document, preserving metadata."""
    cleaned: List[Document] = []

    for doc in docs:
        new_content = clean_text(doc.page_content)

        # Skip documents that became empty after cleaning
        if not new_content:
            continue

        cleaned.append(
            Document(page_content=new_content, metadata=doc.metadata)
        )

    return cleaned