# Document Link Extractor

A Streamlit app and Python API for extracting hyperlinks from PDF and DOCX files.
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

Create and activate a virtual environment, then install the application:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

The dependencies include the maintained `pypdf` library and its crypto extra for
[AES PDF decryption](https://pypdf.readthedocs.io/en/stable/user/encryption-decryption.html).

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
from extractors import ExtractionError, extract_links

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
from extractors import extract_docx_links, extract_pdf_links

with open("example.pdf", "rb") as document:
    links = extract_pdf_links(document, password="")

with open("example.docx", "rb") as document:
    links = extract_docx_links(document)
```

All functions accept bytes, paths, or seekable binary streams and return
`list[str]`. Caller-owned streams remain open at their original position, even
when extraction fails. `ExtractionError` inherits from `ValueError`;
`PdfPasswordError` identifies an incorrect or missing PDF password. The API does
not import Streamlit. Existing imports from `pdf_extractor` and `streamlit_app`
continue to work.

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

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
python -m pytest --cov --cov-report=term-missing
```

Tests generate documents in memory and cover extraction, encryption, malformed
inputs, stream ownership, API compatibility, and real Streamlit upload,
password, and download flows. CI runs lint, formatting, and tests on Windows and
Linux with Python 3.11 through 3.14, enforcing at least 90% coverage. Codespaces
installs the development dependencies and starts the app on port 8501.

Run the reproducible large-document benchmark:

```bash
python -m scripts.benchmark_extraction --paragraphs 5000 --pages 100 --runs 5
```

The benchmark checks output correctness and reports median parsing times; document
generation is excluded from those times. XML traversal avoids repeatedly creating
paragraph objects, links are deduplicated during collection, and the UI uses one
result display instead of one element per link.

## Code layout

- `extractors.py`: public API and format dispatch.
- `pdf_extractor.py`, `docx_extractor.py`: format-specific parsing.
- `link_patterns.py`: shared text-link detection and punctuation handling.
- `extraction_utils.py`, `extraction_errors.py`: input ownership and readable errors.
- `streamlit_app.py`: upload, password, result, and download UI.
- `tests/`: generated fixtures and regression tests.
- `scripts/`: development performance checks.
