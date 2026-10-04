# Document Link Extractor

A Python package for extracting hyperlinks from PDF and DOCX files, with an optional
Streamlit interface. The library does not require Streamlit.
Requires Python 3.11 or newer.

## Features

- Extract PDF annotation targets and links in selectable text, including indirect
  annotation actions and relative targets with a document base URI.
- Extract DOCX links from paragraphs, nested tables, text boxes, content controls,
  headers, footers, footnotes, endnotes, comments, and Word HYPERLINK fields.
- Detect HTTP, HTTPS, FTP, and mailto links in text, preserving query strings,
  fragments, balanced brackets, and URLs split across Word formatting runs.
- Remove exact duplicates while keeping a predictable order.
- Read password-protected PDFs, including AES encryption, with a supplied password.
- Copy results or download a UTF-8 text file named after the source document.
- Process documents once per request and keep results within the current session.

## Installation

The distribution is `pdf-hyperlink-extractor`; import it as
`pdf_hyperlink_extractor`. It is prepared for release but has not been published
to PyPI. Install from this checkout, GitHub, or a built wheel.

### pip

Use a virtual environment and install only the extraction library:

```bash
python -m venv .venv
```

Activate with `.\.venv\Scripts\Activate.ps1` on Windows PowerShell, or
`source .venv/bin/activate` on Linux/macOS. From the repository root:

```bash
python -m pip install .
```

For the optional interface:

```bash
python -m pip install ".[streamlit]"
pdf-hyperlink-extractor-ui
```

From another project, install directly from GitHub:

```bash
python -m pip install "pdf-hyperlink-extractor @ git+https://github.com/thomasjjj/pdf_hyperlink_extractor.git"
# Include the UI if needed:
python -m pip install "pdf-hyperlink-extractor[streamlit] @ git+https://github.com/thomasjjj/pdf_hyperlink_extractor.git"
```

### uv

In this checkout, install the library without development dependencies:

```bash
uv sync --locked --no-dev
```

To install and run the optional interface:

```bash
uv sync --locked --no-dev --extra streamlit
uv run --locked --no-dev --extra streamlit pdf-hyperlink-extractor-ui
```

From another uv project:

```bash
uv add "pdf-hyperlink-extractor @ git+https://github.com/thomasjjj/pdf_hyperlink_extractor.git"
# Include the UI if needed:
uv add "pdf-hyperlink-extractor[streamlit] @ git+https://github.com/thomasjjj/pdf_hyperlink_extractor.git"
```

Both installers support wheels built from this repository:

```bash
python -m pip install dist/pdf_hyperlink_extractor-0.1.0-py3-none-any.whl
uv pip install dist/pdf_hyperlink_extractor-0.1.0-py3-none-any.whl
```

The library includes `pypdf[crypto]` for AES-encrypted PDFs and `python-docx`.
Streamlit and its dependencies are installed only with the `streamlit` extra.

The UI launcher accepts Streamlit options, for example
`pdf-hyperlink-extractor-ui --server.port 8502`. You can also use
`python -m pdf_hyperlink_extractor.ui`. The existing
`streamlit run streamlit_app.py` checkout command remains available after
installation; `requirements.txt` installs the package with the UI for Streamlit
hosting services.

## Using the app

1. Upload a PDF or DOCX file. Uppercase extensions are also accepted.
2. For a protected PDF, enter its password. Leave the field blank otherwise.
3. Select **Extract links**.
4. Copy the displayed list with the code block's copy button, or select
   **Download links as text**.

Downloads and ordinary app reruns reuse the results. Uploading a different file
or removing the upload clears the previous results and password. Extraction
errors appear in the app with guidance for correcting the input.

## Python API

```python
from pdf_hyperlink_extractor import ExtractionError, extract_links

# A path supplies its own filename and is closed after extraction.
try:
    links = extract_links("example.pdf", password="")
except ExtractionError as error:
    print(error)
else:
    print("\n".join(links))

# Bytes and unnamed streams need a filename for format detection.
with open("example.docx", "rb") as document:
    links = extract_links(document.read(), filename="example.docx")
```

You can also call the format-specific functions directly:

```python
from pdf_hyperlink_extractor import extract_docx_links, extract_pdf_links

with open("example.pdf", "rb") as document:
    links = extract_pdf_links(document, password="")

with open("example.docx", "rb") as document:
    links = extract_docx_links(document)
```

All functions accept bytes, paths, or seekable binary streams and return
`list[str]`. Caller-owned streams remain open at their original position, even
when extraction fails. `ExtractionError` inherits from `ValueError`;
`PdfPasswordError` identifies an incorrect or missing PDF password. The API does
not import Streamlit. `DocumentSource` is exported for type annotations, and
the package includes a `py.typed` marker. Legacy top-level imports such as
`extractors`, `pdf_extractor`, and `streamlit_app` remain available in a source
checkout; installed consumers should use `pdf_hyperlink_extractor`.

PDF results list annotations before text links on each page, in page order.
DOCX results follow content order within the body, then other story parts in
package order. Deduplication compares exact strings, preserving URL case and
case-sensitive paths. Embedded targets retain their original punctuation;
text detection trims surrounding prose punctuation.

## Limitations and privacy

- Scanned PDFs need OCR before their image text can be searched. Existing link
  annotations can still be extracted; the app does not perform OCR.
- Plain-text links must include a supported scheme (`http://`, `https://`,
  `ftp://`, or `mailto:`). Bare email addresses and `www.` text are not inferred.
- Line breaks delimit text links. The extractor does not guess how to reconnect
  line-wrapped PDF URLs.
- Internal bookmarks and page destinations are omitted. DOCX story parts are
  scanned even when a particular header or footer is inactive in Word.
- Encrypted DOCX files and legacy `.doc` files are unsupported.
- Files are processed in memory by the server running Streamlit. This app does
  not save documents, passwords, or results to disk or a shared extraction cache.
  When hosted remotely, uploads are sent to that host for processing.
- Severely malformed documents produce an error; PDF text failures are reported
  instead of silently returning a partial list.

## Development and verification

Dependencies are declared in `pyproject.toml`. `uv.lock` pins development and UI
dependencies; commit lockfile updates when changing dependencies.

With uv (the `dev` group is included by default):

```bash
uv sync --locked --extra streamlit
uv run --locked --extra streamlit ruff check .
uv run --locked --extra streamlit ruff format --check .
uv run --locked --extra streamlit pytest --cov --cov-report=term-missing
```

With pip, upgrade pip for dependency-group support, then install the editable
package, UI extra, and development group:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[streamlit]" --group dev
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov --cov-report=term-missing
```

For core-only development, omit the `streamlit` extra. UI tests skip when
Streamlit is absent; run `pytest -m "not streamlit"` for only the core tests.

Build wheel and source distributions with either frontend:

```bash
uv build
# Or, with the development dependencies installed:
python -m build
python -m twine check dist/*
```

With uv on PATH, verify wheel installations in clean environments outside the
checkout, including encrypted PDF extraction, DOCX extraction, the optional UI,
and the installed server launcher:

```bash
python -m scripts.verify_installation dist
```

Tests generate documents in memory and cover extraction, encryption, malformed
inputs, stream ownership, API compatibility, and real Streamlit upload,
password, and download flows. CI runs lint, formatting, and tests on Windows and
Linux with Python 3.11 through 3.14, enforcing at least 90% coverage. Additional
CI jobs build both distribution formats with pip/uv tooling, verify clean
installs, and run the core suite without Streamlit on Windows and Linux.
Codespaces installs the development dependencies and starts the app on port 8501.

Run the reproducible large-document benchmark:

```bash
python -m scripts.benchmark_extraction --paragraphs 5000 --pages 100 --runs 5
# Or: uv run --locked --extra streamlit python -m scripts.benchmark_extraction
```

The benchmark checks output correctness and reports median parsing times; document
generation is excluded from those times. XML traversal avoids repeatedly creating
paragraph objects, links are deduplicated during collection, and the UI uses one
result display instead of one element per link.

## Code layout

- `src/pdf_hyperlink_extractor/`: installed library, type information, optional UI,
  and launcher. Its `__init__.py` exposes the public API.
- Top-level Python modules: checkout compatibility wrappers.
- `tests/`: generated fixtures and regression tests.
- `scripts/`: development benchmarks and installation verification.
- `pyproject.toml`: package metadata, dependency groups, and tool configuration.
- `uv.lock`: reproducible development dependencies.
