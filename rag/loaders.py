"""Document loaders.

Each loader returns a list of ``(text, page)`` units so that page numbers
survive into the retrieval results. A "page" is logical: PDFs have real
pages, while txt/md/docx are treated as a single page-1 unit.
"""
import os
from typing import List, Tuple

Unit = Tuple[str, int]  # (text, page_number)


def _load_pdf(path: str) -> List[Unit]:
    from pypdf import PdfReader

    reader = PdfReader(path)
    units: List[Unit] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            units.append((text, i))
    return units


def _load_docx(path: str) -> List[Unit]:
    import docx

    document = docx.Document(path)
    text = "\n".join(p.text for p in document.paragraphs if p.text.strip())
    return [(text, 1)] if text.strip() else []


def _load_text(path: str) -> List[Unit]:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    return [(text, 1)] if text.strip() else []


_LOADERS = {
    ".pdf": _load_pdf,
    ".docx": _load_docx,
    ".txt": _load_text,
    ".md": _load_text,
}


def load_document(path: str) -> List[Unit]:
    """Load a single document into a list of (text, page) units."""
    ext = os.path.splitext(path)[1].lower()
    loader = _LOADERS.get(ext)
    if loader is None:
        raise ValueError(f"Unsupported file type: {ext}")
    return loader(path)


def is_supported(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in _LOADERS
