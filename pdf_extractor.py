from typing import List

from PyPDF2 import PdfReader, errors

from link_patterns import URL_PATTERN


def extract_pdf_links(file) -> List[str]:
    """Extract hyperlinks from a PDF file.

    The function scans both annotation dictionaries and visible text objects
    for links. Links embedded via annotations ("/Annots") are retrieved
    directly, while links present only in the rendered text are located using
    :data:`link_patterns.URL_PATTERN`.

    Parameters
    ----------
    file : typing.BinaryIO
        File-like object of the PDF to be parsed.

    Returns
    -------
    List[str]
        A list of hyperlinks found within the document. An empty list is
        returned if no links are found.

    Raises
    ------
    ValueError
        If the PDF cannot be read or if decryption with an empty password
        fails.
    """
    links: List[str] = []
    try:
        reader = PdfReader(file)
    except errors.PdfReadError as exc:
        raise ValueError("Unable to read PDF") from exc

    if getattr(reader, "is_encrypted", False):
        # Attempt to decrypt with an empty password and stop if it fails
        try:
            result = reader.decrypt("")
        except errors.PdfReadError as exc:
            raise ValueError("Encrypted PDF cannot be decrypted") from exc
        if result == 0:
            raise ValueError("Encrypted PDF cannot be decrypted")

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
        links.extend(URL_PATTERN.findall(text))

    return links


__all__ = ["extract_pdf_links"]

