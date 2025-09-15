"""Functions for extracting hyperlinks from supported document formats."""

from typing import BinaryIO, List
from docx import Document
from PyPDF2 import PdfReader

from link_patterns import URL_PATTERN


def extract_pdf_links(file: BinaryIO) -> List[str]:
    """Extract hyperlinks from a PDF file.

    Parameters
    ----------
    file: BinaryIO
        A file-like object containing PDF data.

    Returns
    -------
    List[str]
        A list of extracted URLs from the PDF.
    """
    pdf_reader = PdfReader(file)
    links: List[str] = []
    for page in pdf_reader.pages:
        if "/Annots" in page:
            annotations = page["/Annots"]
            for annotation in annotations:
                a_entry = annotation.get_object().get("/A")
                if isinstance(a_entry, dict):
                    uri = a_entry.get("/URI")
                    if uri:
                        links.append(uri)
    return links


def extract_docx_links(file: BinaryIO) -> List[str]:
    """Extract hyperlinks from a DOCX file.

    Parameters
    ----------
    file: BinaryIO
        A file-like object containing DOCX data.

    Returns
    -------
    List[str]
        A list of extracted URLs from the DOCX.
    """
    doc = Document(file)
    links: List[str] = []
    for rel in doc.part.rels.values():
        if "hyperlink" in rel.reltype:
            url = rel._target  # type: ignore[attr-defined]
            if url:
                links.append(url)
    for para in doc.paragraphs:
        links.extend(URL_PATTERN.findall(para.text))
    return links
