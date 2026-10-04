"""Shared detection of HTTP(S), FTP, and mailto links in document text."""

import re
from collections.abc import Iterator

# Quotes and angle brackets delimit links; commas can be valid inside URLs.
_BODY = r"[^\s<>\"\u201c\u201d\u2018\u2019]"
_LAST = r"[^\s<>\"'\u201c\u201d\u2018\u2019.,;:!?]"
URL_PATTERN = re.compile(rf"https?://{_BODY}*{_LAST}", re.IGNORECASE)
MAILTO_PATTERN = re.compile(rf"mailto:{_BODY}*{_LAST}", re.IGNORECASE)
FTP_PATTERN = re.compile(rf"ftp://{_BODY}*{_LAST}", re.IGNORECASE)
ALL_PATTERNS = (URL_PATTERN, MAILTO_PATTERN, FTP_PATTERN)
LINK_PATTERN = re.compile(rf"(?:https?://|ftp://|mailto:){_BODY}+", re.IGNORECASE)
_ADJACENT_LINKS = re.compile(r"[,;](?=(?:https?://|ftp://|mailto:))", re.IGNORECASE)
_CLOSING_BRACKETS = {")": "(", "]": "[", "}": "{"}
_TRAILING_PUNCTUATION = frozenset(".,;:!?'")


def _clean_text_link(link: str) -> str:
    end = len(link)
    while end and link[end - 1] in _TRAILING_PUNCTUATION:
        end -= 1
    if end and link[end - 1] in _CLOSING_BRACKETS:
        excess = {
            closing: link.count(closing) - link.count(opening)
            for closing, opening in _CLOSING_BRACKETS.items()
        }
        while end and link[end - 1] in excess and excess[link[end - 1]] > 0:
            excess[link[end - 1]] -= 1
            end -= 1
            while end and link[end - 1] in _TRAILING_PUNCTUATION:
                end -= 1
    return link[:end]


def find_links(text: str) -> Iterator[str]:
    """Yield text links in order, removing prose punctuation and unpaired brackets.

    Balanced brackets, query strings, fragments, and URL case are preserved.
    Embedded hyperlink targets are authoritative and should not use this cleanup.
    """
    for match in LINK_PATTERN.finditer(text):
        for candidate in _ADJACENT_LINKS.split(match.group()):
            link = _clean_text_link(candidate)
            if link.partition(":")[2].removeprefix("//"):
                yield link
