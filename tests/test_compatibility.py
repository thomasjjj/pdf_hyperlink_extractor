"""Legacy checkout imports keep pointing to the installed implementation."""

import importlib

import pytest

import pdf_hyperlink_extractor


@pytest.mark.parametrize(
    "module, symbols",
    [
        ("extractors", pdf_hyperlink_extractor.__all__),
        ("pdf_extractor", ["extract_pdf_links"]),
        ("docx_extractor", ["extract_docx_links"]),
        ("extraction_errors", ["ExtractionError", "PdfPasswordError"]),
        ("extraction_utils", ["DocumentSource", "open_document"]),
        (
            "link_patterns",
            [
                "ALL_PATTERNS",
                "FTP_PATTERN",
                "LINK_PATTERN",
                "MAILTO_PATTERN",
                "URL_PATTERN",
                "find_links",
            ],
        ),
    ],
)
def test_checkout_imports_share_the_package_implementation(module, symbols):
    legacy = importlib.import_module(module)
    packaged = importlib.import_module(f"pdf_hyperlink_extractor.{module}")
    for symbol in symbols:
        assert getattr(legacy, symbol) is getattr(packaged, symbol)


@pytest.mark.streamlit
def test_checkout_streamlit_imports_remain_available():
    pytest.importorskip("streamlit")
    legacy = importlib.import_module("streamlit_app")
    packaged = importlib.import_module("pdf_hyperlink_extractor.streamlit_app")
    assert legacy.main is packaged.main
    assert legacy.extract_pdf_links is pdf_hyperlink_extractor.extract_pdf_links
    assert legacy.extract_docx_links is pdf_hyperlink_extractor.extract_docx_links
