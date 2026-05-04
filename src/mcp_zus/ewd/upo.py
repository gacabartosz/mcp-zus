"""Parse UPO (Urzędowe Poświadczenie Odbioru) XML from ZUS."""
from __future__ import annotations

from typing import Any

from lxml import etree


def parse_upo(xml: bytes) -> dict[str, Any]:
    """Best-effort parse of UPO. Real UPO format varies; refine when you have samples."""
    root = etree.fromstring(xml)
    return {
        "root_tag": etree.QName(root).localname,
        "elements": {etree.QName(c).localname: (c.text or "").strip() for c in root.iter() if c.text and c.text.strip()},
    }


__all__ = ["parse_upo"]
