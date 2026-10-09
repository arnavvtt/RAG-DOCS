from typing import List, Tuple

from langchain_core.documents import Document


def format_context(results: List[Tuple[Document, float]]) -> str:
    """Format retrieved chunks into a numbered context block with sources."""
    lines = []
    for i, (doc, score) in enumerate(results, start=1):
        source = doc.metadata.get("filename", "unknown")
        page = doc.metadata.get("page")
        chunk_id = doc.metadata.get("chunk_id", "?")

        source_label = source
        if page is not None:
            source_label += f", page {page}"

        lines.append(
            f"[{i}] (source: {source_label}, chunk: {chunk_id}, score: {score:.3f})"
        )
        lines.append(doc.page_content.strip())
        lines.append("")

    return "\n".join(lines).strip()