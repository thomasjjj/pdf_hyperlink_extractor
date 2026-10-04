from io import BytesIO
from unittest.mock import patch

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.errors import DependencyError, PdfReadError
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, NullObject, NumberObject

from extractors import ExtractionError, PdfPasswordError, extract_pdf_links
from tests.document_builders import build_pdf


def test_pdf_deduplicates_across_pages_and_annotation_text():
    data = build_pdf(
        "https://example.com https://example.org mailto:a@example.com ftp://example.com/file",
        ("https://example.com",),
        page_count=2,
    )
    assert extract_pdf_links(data) == [
        "https://example.com",
        "https://example.org",
        "mailto:a@example.com",
        "ftp://example.com/file",
    ]


def test_pdf_resolves_indirect_actions_and_base_uri():
    data = build_pdf(
        targets=("../guide#intro", "https://elsewhere.example/path."),
        indirect_actions=True,
        base_uri="https://example.com/docs/",
    )
    assert extract_pdf_links(data) == [
        "https://example.com/guide#intro",
        "https://elsewhere.example/path.",
    ]


def test_pdf_annotation_without_base_preserves_authoritative_target():
    assert extract_pdf_links(build_pdf(targets=("relative.pdf", "mailto:a@example.com"))) == [
        "relative.pdf",
        "mailto:a@example.com",
    ]


@pytest.mark.parametrize("algorithm", ["RC4-128", "AES-128", "AES-256"])
def test_pdf_correct_password_and_wrong_password(algorithm):
    data = build_pdf("https://example.com", password="secret", algorithm=algorithm)
    with pytest.raises(PdfPasswordError):
        extract_pdf_links(data)
    with pytest.raises(PdfPasswordError):
        extract_pdf_links(data, password="wrong")
    assert extract_pdf_links(data, password="secret") == ["https://example.com"]


def test_pdf_ignores_malformed_annotation_values():
    writer = PdfWriter(clone_from=PdfReader(BytesIO(build_pdf("https://example.com"))))
    writer.pages[0][NameObject("/Annots")] = ArrayObject(
        [
            NullObject(),
            NumberObject(1),
            DictionaryObject(),
            DictionaryObject({NameObject("/A"): NullObject()}),
            DictionaryObject(
                {NameObject("/A"): DictionaryObject({NameObject("/URI"): NumberObject(1)})}
            ),
        ]
    )
    buffer = BytesIO()
    writer.write(buffer)
    assert extract_pdf_links(buffer) == ["https://example.com"]


def test_pdf_does_not_silently_drop_failed_text_extraction():
    with (
        patch("pypdf._page.PageObject.extract_text", side_effect=PdfReadError("broken stream")),
        pytest.raises(ExtractionError, match="PDF page 1"),
    ):
        extract_pdf_links(build_pdf(targets=("https://example.com",)))


def test_pdf_reports_missing_encryption_dependencies():
    with (
        patch("pdf_extractor.PdfReader", side_effect=DependencyError("crypto unavailable")),
        pytest.raises(ExtractionError, match="crypto dependencies"),
    ):
        extract_pdf_links(build_pdf())


@pytest.mark.parametrize("data", [b"", b"%PDF-1.4\ntruncated", b"not a pdf"])
def test_pdf_bad_input(data):
    with pytest.raises(ExtractionError, match="Unable to read PDF"):
        extract_pdf_links(data)


def test_pdf_without_links():
    assert extract_pdf_links(build_pdf()) == []


@pytest.mark.parametrize("error", [ValueError("invalid token"), TypeError("bad dictionary")])
def test_pdf_parser_data_errors_are_readable(error):
    with (
        patch("pdf_extractor.PdfReader", side_effect=error),
        pytest.raises(ExtractionError, match="Unable to read PDF"),
    ):
        extract_pdf_links(build_pdf())


def test_pdf_reports_unsupported_features():
    with (
        patch("pdf_extractor.PdfReader", side_effect=NotImplementedError("encryption handler")),
        pytest.raises(ExtractionError, match="unsupported"),
    ):
        extract_pdf_links(build_pdf())


def test_pdf_bad_base_metadata_does_not_hide_annotation_links():
    writer = PdfWriter(clone_from=PdfReader(BytesIO(build_pdf(targets=("https://example.com",)))))
    writer.root_object[NameObject("/URI")] = DictionaryObject(
        {
            NameObject("/Base"): NumberObject(42),
        }
    )
    buffer = BytesIO()
    writer.write(buffer)
    assert extract_pdf_links(buffer) == ["https://example.com"]
