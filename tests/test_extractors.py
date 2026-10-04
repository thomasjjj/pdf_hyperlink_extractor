from io import BytesIO

import pytest
from docx import Document

import extractors
import pdf_extractor
import pdf_hyperlink_extractor
from pdf_hyperlink_extractor import docx_extractor
from tests.document_builders import (
    add_hyperlink,
    build_encrypted_pdf_bytes,
    build_sample_docx_bytes,
    build_sample_pdf_bytes,
)

PDF_EXTRACTORS = [
    pytest.param(extractors.extract_pdf_links, id="extractors"),
    pytest.param(pdf_extractor.extract_pdf_links, id="pdf_extractor"),
    pytest.param(pdf_hyperlink_extractor.extract_pdf_links, id="package"),
]
DOCX_EXTRACTORS = [
    pytest.param(extractors.extract_docx_links, id="extractors"),
    pytest.param(pdf_hyperlink_extractor.extract_docx_links, id="package"),
    pytest.param(docx_extractor.extract_docx_links, id="docx_extractor"),
]


@pytest.mark.parametrize("extract_pdf_links", PDF_EXTRACTORS)
def test_extract_pdf_links(extract_pdf_links):
    pdf_file = BytesIO(build_sample_pdf_bytes())
    links = extract_pdf_links(pdf_file)
    assert set(links) == {"https://example.com", "https://example.org"}


@pytest.mark.parametrize("extract_pdf_links", PDF_EXTRACTORS)
def test_extract_pdf_links_encrypted(extract_pdf_links):
    encrypted_pdf = BytesIO(build_encrypted_pdf_bytes())
    with pytest.raises(ValueError, match="Encrypted PDF cannot be decrypted"):
        extract_pdf_links(encrypted_pdf)


@pytest.mark.parametrize("extract_pdf_links", PDF_EXTRACTORS)
def test_extract_pdf_links_empty_password(extract_pdf_links):
    pdf_file = BytesIO(build_encrypted_pdf_bytes(password=""))
    assert set(extract_pdf_links(pdf_file)) == {"https://example.com", "https://example.org"}


@pytest.mark.parametrize("extract_pdf_links", PDF_EXTRACTORS)
def test_extract_pdf_links_invalid(extract_pdf_links):
    with pytest.raises(ValueError, match="Unable to read PDF"):
        extract_pdf_links(BytesIO(b"This is not a PDF"))


@pytest.mark.parametrize("extract_docx_links", DOCX_EXTRACTORS)
def test_extract_docx_links(extract_docx_links):
    docx_file = BytesIO(build_sample_docx_bytes())
    links = extract_docx_links(docx_file)
    assert set(links) == {"https://example.com", "https://example.org"}


@pytest.mark.parametrize("extract_docx_links", DOCX_EXTRACTORS)
def test_extract_docx_links_deduplicates_in_order(extract_docx_links):
    document = Document()
    paragraph = document.add_paragraph("Example link: ")
    add_hyperlink(paragraph, "https://example.com", "Example")
    document.add_paragraph("https://example.org https://example.com")
    document.add_paragraph("https://example.org https://example.net")
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)

    assert extract_docx_links(buffer) == [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ]
