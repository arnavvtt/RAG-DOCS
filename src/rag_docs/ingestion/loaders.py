from pathlib import Path
from typing import List
import logging

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

logger = logging.getLogger(__name__)

# Extensions we know how to handle
SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".mdx", ".txt"}


def _load_text_file(file_path: Path) -> List[Document]:
    """Load a .md, .mdx, or .txt file into a single Document."""
    text = file_path.read_text(encoding="utf-8")
    return [
        Document(
            page_content=text,
            metadata={
                "source": str(file_path),
                "filename": file_path.name,
                "doc_type": file_path.suffix.lstrip("."),
                "page": None,
            },
        )
    ]


def _load_pdf_file(file_path: Path) -> List[Document]:
    """Load a PDF using PyPDFLoader (returns one Document per page)."""
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()

    for doc in docs:
        doc.metadata["filename"] = file_path.name
        doc.metadata["doc_type"] = "pdf"

    return docs


def load_file(file_path: Path) -> List[Document]:
    """Load a single file and return a list of Documents."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {ext}. "
            f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    if ext == ".pdf":
        docs = _load_pdf_file(file_path)
    else:
        docs = _load_text_file(file_path)

    logger.info("Loaded %d document(s) from %s", len(docs), file_path.name)
    return docs


def load_directory(dir_path: Path) -> List[Document]:
    """Load every supported file from a directory (non-recursive).

    Logs warnings for unsupported extensions so silent skips don't happen.
    """
    dir_path = Path(dir_path)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    all_docs: List[Document] = []
    skipped: List[str] = []

    for file_path in sorted(dir_path.iterdir()):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            skipped.append(file_path.name)
            continue

        try:
            all_docs.extend(load_file(file_path))
        except Exception as exc:
            logger.error("Failed to load %s: %s", file_path.name, exc)

    if skipped:
        logger.warning(
            "Skipped %d file(s) with unsupported extensions: %s",
            len(skipped),
            skipped,
        )

    logger.info(
        "Loaded %d document(s) from directory %s", len(all_docs), dir_path
    )
    return all_docs