"""Checkout compatibility wrapper; use pdf_hyperlink_extractor.extraction_errors in new code."""

from pdf_hyperlink_extractor.extraction_errors import (
    ExtractionError,
    PdfPasswordError,
)

__all__ = ["ExtractionError", "PdfPasswordError"]
