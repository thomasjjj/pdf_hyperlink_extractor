"""Checkout compatibility wrapper; use pdf_hyperlink_extractor.streamlit_app in new code."""

from pdf_hyperlink_extractor.streamlit_app import (
    ExtractionError,
    extract_docx_links,
    extract_links,
    extract_pdf_links,
    main,
)

__all__ = ["ExtractionError", "extract_docx_links", "extract_links", "extract_pdf_links", "main"]


if __name__ == "__main__":
    main()
