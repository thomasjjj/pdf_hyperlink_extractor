"""Public API for document link extraction, independent of Streamlit."""

from os import PathLike
from pathlib import Path

from docx_extractor import extract_docx_links
from extraction_errors import ExtractionError, PdfPasswordError
from extraction_utils import DocumentSource
from pdf_extractor import extract_pdf_links


def extract_links(
    source: DocumentSource,
    filename: str | PathLike[str] | None = None,
    *,
    password: str = "",
) -> list[str]:
    """Choose an extractor by filename, accepting mixed-case PDF/DOCX suffixes.

    Paths and named streams provide their own filename. For bytes and unnamed
    streams, pass filename explicitly. No document data is written to disk.
    """
    if filename is None:
        filename = source if isinstance(source, (str, PathLike)) else getattr(source, "name", "")
    if not isinstance(filename, (str, PathLike)):
        raise ExtractionError("Unsupported file type. Please provide a PDF or DOCX filename.")
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_links(source, password=password)
    if suffix == ".docx":
        return extract_docx_links(source)
    raise ExtractionError("Unsupported file type. Please choose a PDF or DOCX file.")


__all__ = [
    "ExtractionError",
    "PdfPasswordError",
    "extract_links",
    "extract_pdf_links",
    "extract_docx_links",
]
