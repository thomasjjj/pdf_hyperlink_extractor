import re
from typing import List

from PyPDF2 import PdfReader, errors

# Regular expression pattern for matching URLs within PDF text
URL_PATTERN = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


def extract_pdf_links(file) -> List[str]:
    """Extract hyperlinks from a PDF file.

    The function scans both annotation dictionaries and visible text objects
    for links.  Links embedded via annotations (\"/Annots\") are retrieved
    directly, while links present only in the rendered text are located using
    regular expression matching on the page's extracted text.

    Parameters
    ----------
    file : typing.BinaryIO
        File-like object of the PDF to be parsed.

    Returns
    -------
    List[str]
        A list of hyperlinks found within the document.  An empty list is
        returned if no links are found.

    Raises
    ------
    ValueError
        If the PDF is encrypted and cannot be decrypted or if it is
        malformed.
    """
    links: List[str] = []
    try:
        reader = PdfReader(file)
    except errors.PdfReadError as exc:
        raise ValueError("Unable to read PDF") from exc

    if getattr(reader, "is_encrypted", False):
        # Attempt to decrypt with an empty password; if it still fails, raise
        try:
            reader.decrypt("")
        except errors.PdfReadError as exc:
            raise ValueError("Encrypted PDF cannot be decrypted") from exc

    for page in reader.pages:
        # Extract links from annotation dictionaries
        if "/Annots" in page:
            for annotation in page["/Annots"]:
                action = annotation.get_object().get("/A")
                if isinstance(action, dict):
                    uri = action.get("/URI")
                    if uri:
                        links.append(uri)

        # Extract text-based links
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        links.extend(re.findall(URL_PATTERN, text))

    return links


__all__ = ["extract_pdf_links", "URL_PATTERN"]
