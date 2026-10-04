"""Extract PDF hyperlink targets and links in selectable text."""

from collections.abc import Iterator
from urllib.parse import urljoin
from zlib import error as ZlibError

from pypdf import PdfReader
from pypdf.errors import DependencyError, PyPdfError
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject

from .extraction_errors import ExtractionError, PdfPasswordError
from .extraction_utils import DocumentSource, open_document
from .link_patterns import find_links


def _resolve(value: object) -> object:
    return value.get_object() if isinstance(value, IndirectObject) else value


def _annotation_links(page: DictionaryObject, base_uri: str) -> Iterator[str]:
    annotations = _resolve(page.get("/Annots"))
    if not isinstance(annotations, ArrayObject):
        return
    for reference in annotations:
        annotation = _resolve(reference)
        if not isinstance(annotation, DictionaryObject):
            continue
        action = _resolve(annotation.get("/A"))
        if not isinstance(action, DictionaryObject):
            continue
        target = _resolve(action.get("/URI"))
        if isinstance(target, str) and target.strip():
            yield urljoin(base_uri, target.strip()) if base_uri else target.strip()


def extract_pdf_links(source: DocumentSource, *, password: str = "") -> list[str]:
    """Return unique annotation and text links in page order.

    Accept document bytes, a path, or a seekable binary stream. Caller-owned
    streams are left open at their original position. Encrypted files are tried
    with the given password (empty by default). Failures raise ExtractionError,
    a ValueError subclass, rather than silently returning incomplete results.
    Scanned images require OCR outside this extractor.
    """
    with open_document(source) as stream:
        try:
            reader = PdfReader(stream)
            if reader.is_encrypted and not reader.decrypt(password):
                raise PdfPasswordError(
                    "Encrypted PDF cannot be decrypted. Enter the correct PDF password."
                )

            catalog = reader.trailer["/Root"]
            uri_info = _resolve(catalog.get("/URI"))
            base_uri = uri_info.get("/Base", "") if isinstance(uri_info, dict) else ""
            if not isinstance(base_uri, str):
                base_uri = ""

            links: dict[str, None] = {}
            for page_number, page in enumerate(reader.pages, start=1):
                links.update(dict.fromkeys(_annotation_links(page, base_uri)))
                try:
                    text = page.extract_text() or ""
                except (PyPdfError, ValueError, TypeError, KeyError, IndexError, ZlibError) as exc:
                    raise ExtractionError(
                        f"Unable to extract text from PDF page {page_number}. "
                        "Try opening and resaving the PDF."
                    ) from exc
                links.update(dict.fromkeys(find_links(text)))
            return list(links)
        except DependencyError as exc:
            raise ExtractionError(
                "PDF encryption is unsupported. Install the pypdf crypto dependencies."
            ) from exc
        except ExtractionError:
            raise
        except NotImplementedError as exc:
            raise ExtractionError(
                "This PDF uses an unsupported encryption or PDF feature."
            ) from exc
        except (PyPdfError, OSError, ValueError, TypeError, KeyError, IndexError, ZlibError) as exc:
            raise ExtractionError("Unable to read PDF. Check that the file is valid.") from exc


__all__ = ["extract_pdf_links"]
