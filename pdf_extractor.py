"""Checkout compatibility wrapper; use pdf_hyperlink_extractor.pdf_extractor in new code."""

from pdf_hyperlink_extractor.pdf_extractor import (
    extract_pdf_links,
)

__all__ = ["extract_pdf_links"]
