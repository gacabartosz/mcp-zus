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

    naglowek = root.find("k:naglowek_KEDU", _NS)
    documents_el = root.find("k:dokumenty", _NS)

    documents: list[dict[str, Any]] = []
    if documents_el is not None:
        for doc in documents_el:
            documents.append(
                {
                    "type": etree.QName(doc).localname,
                    "data": _xml_to_dict(doc),
                }
            )

    return {
        "naglowek": _xml_to_dict(naglowek) if naglowek is not None else {},
        "documents": documents,
    }


__all__ = ["parse_kedu"]
