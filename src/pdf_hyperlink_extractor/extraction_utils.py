"""Input handling shared by the document extractors."""

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from io import BytesIO
from os import PathLike
from typing import BinaryIO

from .extraction_errors import ExtractionError

DocumentSource = bytes | str | PathLike[str] | BinaryIO


@contextmanager
def open_document(source: DocumentSource) -> Iterator[BinaryIO]:
    """Read from the start and restore caller-owned streams, including on failure."""
    if isinstance(source, bytes):
        with BytesIO(source) as stream:
            yield stream
    elif isinstance(source, (str, PathLike)):
        with ExitStack() as stack:
            try:
                stream = stack.enter_context(open(source, "rb"))
            except OSError as exc:
                raise ExtractionError("Unable to open document. Check the file path.") from exc
            yield stream
    else:
        try:
            position = source.tell()
            if not isinstance(source.read(0), bytes):
                raise ExtractionError("Provide a seekable binary document stream.")
            source.seek(0)
        except (AttributeError, OSError, ValueError) as exc:
            raise ExtractionError("Provide a seekable binary document stream.") from exc
        try:
            yield source
        finally:
            source.seek(position)
