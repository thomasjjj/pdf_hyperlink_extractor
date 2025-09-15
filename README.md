# Document Link Extractor

A lightweight Streamlit app for extracting hyperlinks from PDF and DOCX files.

## Features


- Upload a PDF or DOCX file and retrieve all hyperlinks.
- Detects links from PDF annotations and DOCX hyperlink relations or plain text.
- Deduplicates results and lets you download them as a text file.
- Runs entirely in the browser via Streamlit.
- Centralized regex patterns for URLs, mailto, and FTP links.
- Stops processing encrypted PDFs that cannot be decrypted.

## Installation

```bash
pip install -r requirements.txt
```


## Usage

### Launch the Streamlit app

```bash
streamlit run streamlit_app.py
```

### Use the extraction functions directly

```python
from streamlit_app import extract_pdf_links, extract_docx_links

with open("example.pdf", "rb") as fh:
    print(extract_pdf_links(fh))

with open("example.docx", "rb") as fh:
    print(extract_docx_links(fh))
```

## FAQ

**Which file formats are supported?**  
PDF and DOCX files.

**Does the app store my documents?**  
No. Uploaded files are processed in memory and discarded after extraction.

**How are duplicate links handled?**  
Duplicates are removed before displaying or downloading the list of links.


