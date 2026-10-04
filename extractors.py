"""Functions for extracting hyperlinks from supported document formats."""

from typing import BinaryIO, List

from docx import Document

from link_patterns import URL_PATTERN
from pdf_extractor import extract_pdf_links


def extract_docx_links(file: BinaryIO) -> List[str]:
    """Extract hyperlinks from a DOCX file.

    Links are collected from relationship targets and from visible text using
    :data:`link_patterns.URL_PATTERN`. Duplicate links are removed while
    preserving their first occurrence.

    Parameters
    ----------
    file: BinaryIO
        A file-like object containing DOCX data.

    Returns
    -------
    List[str]
        A list of unique URLs extracted from the DOCX.
    """
    doc = Document(file)
    links: List[str] = []
    for rel in doc.part.rels.values():
        if "hyperlink" in rel.reltype:
            url = getattr(rel, "target_ref", None)
            if url:
                links.append(url)
    for para in doc.paragraphs:
        links.extend(URL_PATTERN.findall(para.text))
    return list(dict.fromkeys(links))


__all__ = ["extract_pdf_links", "extract_docx_links"]
