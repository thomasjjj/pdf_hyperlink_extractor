"""Checkout compatibility wrapper; use pdf_hyperlink_extractor in new code."""

from pdf_hyperlink_extractor import (
    DocumentSource,
    ExtractionError,
    PdfPasswordError,
    extract_docx_links,
    extract_links,
    extract_pdf_links,
)

__all__ = [
    "DocumentSource",
    "ExtractionError",
    "PdfPasswordError",
    "extract_docx_links",
    "extract_links",
    "extract_pdf_links",
]
