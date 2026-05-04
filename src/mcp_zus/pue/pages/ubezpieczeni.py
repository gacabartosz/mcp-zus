"""PUE — lista ubezpieczonych pracowników płatnika."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mcp_zus.pue.selectors import Ubezpieczeni as Sel

if TYPE_CHECKING:
    from mcp_zus.pue.attach import PueSession


async def list_ubezpieczeni(session: PueSession, *, limit: int = 50) -> list[dict[str, Any]]:
    page = session.page
    await page.goto(
        "https://www.zus.pl/portal/portal-platnika/ubezpieczeni",
        wait_until="networkidle",
    )
    rows = await page.query_selector_all(Sel.LIST_ROW)
    out: list[dict[str, Any]] = []
    for row in rows[:limit]:
        cells = await row.query_selector_all("td")
        out.append({"cells": [await c.inner_text() for c in cells]})
    return out


__all__ = ["list_ubezpieczeni"]
