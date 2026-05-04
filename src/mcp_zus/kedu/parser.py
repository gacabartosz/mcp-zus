"""Parse existing KEDU 5.6 XML into Python dicts (LLM-friendly)."""
from __future__ import annotations

from typing import Any

from lxml import etree

from mcp_zus.kedu.builder import KEDU_NS

_NS = {"k": KEDU_NS}


def _text(el: etree._Element | None) -> str | None:
    return el.text if el is not None and el.text else None


def _xml_to_dict(el: etree._Element) -> Any:
    """Recursive lxml.Element → dict, dropping namespace prefixes from keys."""
    children = list(el)
    if not children:
        return el.text
    result: dict[str, Any] = {}
    for child in children:
        tag = etree.QName(child).localname
        value = _xml_to_dict(child)
        if tag in result:
            existing = result[tag]
            if isinstance(existing, list):
                existing.append(value)
            else:
                result[tag] = [existing, value]
        else:
            result[tag] = value
    return result


def parse_kedu(xml: bytes | str) -> dict[str, Any]:
    """Parse a KEDU 5.6 XML document into a structured dict.

    Returns:
        {
          "naglowek": { "program": {...}, "ID_KEDU": "...", "data_utworzenia_KEDU": "..." },
          "documents": [
            { "type": "DRA", "data": {...} },
            { "type": "ZUA", "data": {...} },
            ...
          ]
        }
    """
    if isinstance(xml, str):
        xml = xml.encode("utf-8")
    root = etree.fromstring(xml)

    if etree.QName(root).localname != "KEDU":
        raise ValueError(f"Root element must be KEDU, got {etree.QName(root).localname}")

    # XSD uses dot in element name: `naglowek.KEDU` — use full {ns}name form
    # because lxml's find() with prefixed paths doesn't accept dots in tag.
    naglowek = root.find(f"{{{KEDU_NS}}}naglowek.KEDU")
    if naglowek is None:
        naglowek = root.find(f"{{{KEDU_NS}}}naglowek_KEDU")  # legacy

    skip_tags = {
        f"{{{KEDU_NS}}}naglowek.KEDU",
        f"{{{KEDU_NS}}}naglowek_KEDU",
        f"{{{KEDU_NS}}}cechy.KEDU",
        f"{{{KEDU_NS}}}stopka.KEDU",
        f"{{{KEDU_NS}}}dokumenty",
        "{http://www.w3.org/2000/09/xmldsig#}Signature",
    }
    documents: list[dict[str, Any]] = []
    for child in root:
        if not isinstance(child.tag, str) or child.tag in skip_tags:
            continue
        documents.append(
            {"type": etree.QName(child).localname, "data": _xml_to_dict(child)}
        )

    legacy_wrapper = root.find(f"{{{KEDU_NS}}}dokumenty")
    if legacy_wrapper is not None:
        for doc in legacy_wrapper:
            documents.append(
                {"type": etree.QName(doc).localname, "data": _xml_to_dict(doc)}
            )

    return {
        "naglowek": _xml_to_dict(naglowek) if naglowek is not None else {},
        "documents": documents,
    }


__all__ = ["parse_kedu"]
