"""Checkout compatibility wrapper; use pdf_hyperlink_extractor.link_patterns in new code."""

from pdf_hyperlink_extractor.link_patterns import (
    ALL_PATTERNS,
    FTP_PATTERN,
    LINK_PATTERN,
    MAILTO_PATTERN,
    URL_PATTERN,
    find_links,
)

__all__ = [
    "ALL_PATTERNS",
    "FTP_PATTERN",
    "LINK_PATTERN",
    "MAILTO_PATTERN",
    "URL_PATTERN",
    "find_links",
]
