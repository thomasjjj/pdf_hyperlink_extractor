"""Extract document links without requiring the optional Streamlit interface."""

from .extraction_errors import ExtractionError, PdfPasswordError
from .extraction_utils import DocumentSource
from .extractors import extract_docx_links, extract_links, extract_pdf_links

__all__ = [
    "DocumentSource",
    "ExtractionError",
    "PdfPasswordError",
    "extract_docx_links",
    "extract_links",
    "extract_pdf_links",
]
