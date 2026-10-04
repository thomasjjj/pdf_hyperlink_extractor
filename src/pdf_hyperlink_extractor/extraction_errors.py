"""User-facing document extraction errors."""


class ExtractionError(ValueError):
    """The input document cannot be processed."""


class PdfPasswordError(ExtractionError):
    """The supplied password cannot decrypt the PDF."""
