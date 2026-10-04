import subprocess
import sys
from io import BytesIO, StringIO

import pytest

from pdf_hyperlink_extractor import (
    ExtractionError,
    extract_docx_links,
    extract_links,
    extract_pdf_links,
)
from tests.document_builders import build_sample_docx_bytes, build_sample_pdf_bytes


@pytest.mark.parametrize(
    "suffix, builder, extractor",
    [
        ("PDF", build_sample_pdf_bytes, extract_pdf_links),
        ("DoCx", build_sample_docx_bytes, extract_docx_links),
    ],
)
def test_dispatch_accepts_bytes_paths_and_named_streams(tmp_path, suffix, builder, extractor):
    data = builder()
    expected = extractor(data)
    assert extract_links(data, f"sample.{suffix}") == expected
    path = tmp_path / f"sample.{suffix}"
    path.write_bytes(data)
    assert extract_links(path) == expected
    assert extract_links(str(path)) == expected
    with path.open("rb") as stream:
        stream.seek(5)
        assert extract_links(stream) == expected
        assert stream.tell() == 5
        assert not stream.closed


@pytest.mark.parametrize(
    "extractor, builder",
    [
        (extract_pdf_links, build_sample_pdf_bytes),
        (extract_docx_links, build_sample_docx_bytes),
    ],
)
def test_stream_position_and_ownership_are_preserved(extractor, builder):
    stream = BytesIO(builder())
    stream.seek(10)
    first = extractor(stream)
    assert extractor(stream) == first
    assert stream.tell() == 10
    assert not stream.closed


@pytest.mark.parametrize("extractor", [extract_pdf_links, extract_docx_links])
def test_failed_extraction_restores_stream(extractor):
    stream = BytesIO(b"invalid document")
    stream.seek(3)
    with pytest.raises(ExtractionError):
        extractor(stream)
    assert stream.tell() == 3
    assert not stream.closed


@pytest.mark.parametrize("filename", [None, "x.txt", "x.doc", "x.pdf.exe"])
def test_unsupported_file_types(filename):
    with pytest.raises(ExtractionError, match="Unsupported file type"):
        extract_links(b"invalid", filename)


@pytest.mark.parametrize("extractor", [extract_pdf_links, extract_docx_links])
def test_missing_path_is_reported(tmp_path, extractor):
    with pytest.raises(ExtractionError, match="Unable to open document"):
        extractor(tmp_path / "missing.file")


def test_closed_stream_is_reported():
    stream = BytesIO(b"data")
    stream.close()
    with pytest.raises(ExtractionError, match="seekable binary"):
        extract_pdf_links(stream)


def test_text_stream_is_rejected():
    stream = StringIO("not binary")
    stream.seek(4)
    with pytest.raises(ExtractionError, match="binary"):
        extract_docx_links(stream)
    assert stream.tell() == 4


def test_stream_with_numeric_name_requires_filename():
    stream = BytesIO(build_sample_pdf_bytes())
    stream.name = 42
    with pytest.raises(ExtractionError, match="filename"):
        extract_links(stream)


def test_dispatch_forwards_pdf_password():
    from tests.document_builders import build_pdf

    data = build_pdf("https://example.com", password="secret")
    assert extract_links(data, "protected.pdf", password="secret") == ["https://example.com"]


def test_core_api_does_not_import_streamlit():
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import pdf_hyperlink_extractor; assert 'streamlit' not in sys.modules",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
