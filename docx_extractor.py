"""Checkout compatibility wrapper; use pdf_hyperlink_extractor.docx_extractor in new code."""

from pdf_hyperlink_extractor.docx_extractor import (
    extract_docx_links,
)

__all__ = ["extract_docx_links"]
