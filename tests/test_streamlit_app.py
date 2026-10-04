from pathlib import Path
from unittest.mock import patch

import pytest
import streamlit as st
from docx import Document
from streamlit.testing.v1 import AppTest

from extractors import extract_links
from tests.document_builders import (
    build_pdf,
    build_sample_docx_bytes,
    build_sample_pdf_bytes,
    save_docx,
)

APP_PATH = Path(__file__).resolve().parents[1] / "streamlit_app.py"


@pytest.fixture
def app():
    result = AppTest.from_file(APP_PATH).run()
    assert not result.exception
    return result


def upload(app, filename, data):
    mime = (
        "application/pdf"
        if filename.lower().endswith(".pdf")
        else ("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    )
    app.file_uploader[0].set_value((filename, data, mime)).run()
    assert not app.exception
    return app


def submit(app):
    app.button[0].click().run()
    assert not app.exception
    return app


def test_initial_screen(app):
    assert app.title[0].value == "Document Link Extractor"
    assert app.button[0].disabled
    assert not app.download_button
    assert not app.text_input


@pytest.mark.parametrize(
    "filename, builder",
    [
        ("report.PDF", build_sample_pdf_bytes),
        ("report.DoCx", build_sample_docx_bytes),
    ],
)
def test_upload_extract_and_download(app, filename, builder):
    data = builder()
    expected = "\n".join(extract_links(data, filename))
    upload(app, filename, data)
    assert not app.code
    with patch("streamlit.download_button", wraps=st.download_button) as download:
        submit(app)
    assert app.success[0].value == "Found 2 unique links."
    assert app.code[0].value == expected
    assert download.call_args.args[1] == expected
    assert download.call_args.kwargs["file_name"] == "report_links.txt"
    assert download.call_args.kwargs["mime"] == "text/plain; charset=utf-8"
    assert app.download_button[0].proto.ignore_rerun


def test_reruns_and_downloads_do_not_parse_again(app):
    upload(app, "report.pdf", build_sample_pdf_bytes())
    with patch("extractors.extract_links", wraps=extract_links) as extract:
        submit(app)
        app.run()
        app.download_button[0].click().run()
    assert extract.call_count == 1
    assert app.code[0].value == "https://example.com\nhttps://example.org"


def test_password_retry(app):
    upload(app, "protected.pdf", build_pdf("https://example.com", password="secret"))
    assert app.text_input[0].proto.type == app.text_input[0].proto.PASSWORD
    submit(app)
    assert "correct PDF password" in app.error[0].value
    assert not app.download_button
    app.text_input[0].input("wrong")
    submit(app)
    assert app.error
    app.text_input[0].input("secret")
    submit(app)
    assert not app.error
    assert app.code[0].value == "https://example.com"
    assert app.success[0].value == "Found 1 unique link."


@pytest.mark.parametrize("filename", ["broken.pdf", "broken.docx"])
def test_invalid_upload_is_a_friendly_error(app, filename):
    upload(app, filename, b"invalid document")
    submit(app)
    assert app.error
    assert not app.download_button
    assert not app.code


def test_new_upload_clears_results_and_password(app):
    upload(app, "protected.pdf", build_pdf("https://example.com", password="secret"))
    app.text_input[0].input("secret")
    submit(app)
    assert app.code
    upload(app, "second.pdf", build_pdf("https://second.example"))
    assert not app.code
    assert app.text_input[0].value == ""
    submit(app)
    assert app.code[0].value == "https://second.example"


def test_removed_upload_clears_results(app):
    upload(app, "report.pdf", build_sample_pdf_bytes())
    submit(app)
    app.file_uploader[0].set_value(None).run()
    assert not app.exception
    assert not app.code
    assert app.button[0].disabled


def test_no_links_reports_pdf_ocr_limitation(app):
    upload(app, "blank.pdf", build_pdf())
    submit(app)
    assert app.info[0].value == "No links found in the document."
    assert any("OCR" in caption.value for caption in app.caption)
    assert not app.download_button


def test_results_are_isolated_to_a_session(app):
    upload(app, "report.pdf", build_sample_pdf_bytes())
    submit(app)
    other = AppTest.from_file(APP_PATH).run()
    assert not other.exception
    assert not other.code
    assert not other.download_button


def test_no_links_in_docx_has_no_pdf_ocr_message(app):
    upload(app, "blank.docx", save_docx(Document()))
    submit(app)
    assert app.info[0].value == "No links found in the document."
    assert not any("OCR" in caption.value for caption in app.caption)
    assert not app.download_button
