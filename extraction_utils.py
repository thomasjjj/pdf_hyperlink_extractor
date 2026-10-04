"""Checkout compatibility wrapper; use pdf_hyperlink_extractor.extraction_utils in new code."""

from pdf_hyperlink_extractor.extraction_utils import (
    DocumentSource,
    open_document,
)

__all__ = ["DocumentSource", "open_document"]
