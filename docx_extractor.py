"""Extract DOCX hyperlinks and text links across Word document stories."""

import re
from collections.abc import Iterator
from zipfile import BadZipFile

from docx import Document
from docx.opc.constants import CONTENT_TYPE as CT
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.exceptions import PackageNotFoundError
from docx.opc.part import Part, XmlPart
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from lxml.etree import XMLSyntaxError, iterwalk

from extraction_errors import ExtractionError
from extraction_utils import DocumentSource, open_document
from link_patterns import find_links

_STORY_TYPES = {
    CT.WML_DOCUMENT_MAIN,
    CT.WML_HEADER,
    CT.WML_FOOTER,
    CT.WML_FOOTNOTES,
    CT.WML_ENDNOTES,
    CT.WML_COMMENTS,
    CT.WML_DOCUMENT_GLOSSARY,
}
_PARAGRAPH = qn("w:p")
_TEXT = qn("w:t")
_HYPERLINK = qn("w:hyperlink")
_SIMPLE_FIELD = qn("w:fldSimple")
_INSTRUCTION = qn("w:instrText")
_FIELD_CHAR = qn("w:fldChar")
_BREAKS = {qn("w:tab"), qn("w:br"), qn("w:cr")}
_BOUNDARIES = {_PARAGRAPH, _HYPERLINK, _SIMPLE_FIELD}
_FIELD_TOKEN = re.compile(r'"([^"]*)"|(\S+)')
_VALUE_SWITCHES = {"\\l", "\\o", "\\t", "\\*"}


def _field_link(instruction: str) -> Iterator[str]:
    tokens = iter(
        match.group(1) if match.group(1) is not None else match.group(2)
        for match in _FIELD_TOKEN.finditer(instruction)
    )
    if next(tokens, "").upper() != "HYPERLINK":
        return
    target = ""
    anchor = ""
    for token in tokens:
        switch = token.lower()
        if switch in _VALUE_SWITCHES:
            value = next(tokens, "")
            if switch == "\\l":
                anchor = value
        elif token.startswith("\\") and not token.startswith("\\\\"):
            continue
        elif not target:
            target = token.strip()
    if target:
        yield target + "#" + anchor if anchor and "#" not in target else target


def _part_links(part: Part) -> Iterator[str]:
    """Walk XML once, retaining run continuity and separating paragraph text."""
    root = part.element if isinstance(part, XmlPart) else parse_xml(part.blob)
    text: list[str] = []
    instruction: list[str] = []
    for event, element in iterwalk(root, events=("start", "end")):
        tag = element.tag
        if event == "start":
            if tag in _BOUNDARIES:
                yield from find_links("".join(text))
                text.clear()
            if tag == _HYPERLINK:
                relationship = part.rels.get(element.get(qn("r:id")))
                if (
                    relationship is not None
                    and relationship.reltype == RT.HYPERLINK
                    and relationship.is_external
                ):
                    target = relationship.target_ref.strip()
                    anchor = element.get(qn("w:anchor"))
                    if anchor and "#" not in target:
                        target += "#" + anchor
                    if target:
                        yield target
            elif tag == _SIMPLE_FIELD:
                yield from _field_link(element.get(qn("w:instr"), ""))
        elif tag == _TEXT:
            text.append(element.text or "")
        elif tag in _BREAKS:
            text.append("\n")
        elif tag == _INSTRUCTION:
            instruction.append(element.text or "")
        elif tag == _FIELD_CHAR:
            yield from _field_link("".join(instruction))
            instruction.clear()
        elif tag in _BOUNDARIES:
            yield from find_links("".join(text))
            text.clear()
            if tag == _PARAGRAPH:
                yield from _field_link("".join(instruction))
                instruction.clear()


def extract_docx_links(source: DocumentSource) -> list[str]:
    """Return unique links from body, tables, text boxes, headers, and notes.

    Hyperlink relationships and Word HYPERLINK fields are included. Body links
    come first, followed by other story parts in package order. URLs split over
    formatting runs are joined, but distinct paragraphs are never joined.
    Input streams are restored; invalid documents raise ExtractionError.
    """
    with open_document(source) as stream:
        try:
            document = Document(stream)
            links: dict[str, None] = {}
            parts = document.part.package.parts
            parts = [document.part, *(part for part in parts if part is not document.part)]
            for part in parts:
                if part.content_type in _STORY_TYPES:
                    links.update(dict.fromkeys(_part_links(part)))
            return list(links)
        except (
            BadZipFile,
            PackageNotFoundError,
            XMLSyntaxError,
            OSError,
            KeyError,
            ValueError,
            RuntimeError,
            NotImplementedError,
        ) as exc:
            raise ExtractionError(
                "Unable to read DOCX. Check that the file is a valid, unencrypted DOCX."
            ) from exc


__all__ = ["extract_docx_links"]
