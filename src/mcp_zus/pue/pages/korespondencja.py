"""PUE — skrzynka odbiorcza pism od ZUS."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mcp_zus.pue.selectors import Korespondencja as Sel

if TYPE_CHECKING:
    from mcp_zus.pue.attach import PueSession


async def list_korespondencja(session: PueSession, *, limit: int = 30) -> list[dict[str, Any]]:
    page = session.page
    await page.goto(
        "https://www.zus.pl/portal/portal-platnika/korespondencja",
        wait_until="networkidle",
    )
    rows = await page.query_selector_all(Sel.LIST_ROW)
    out: list[dict[str, Any]] = []
    for row in rows[:limit]:
        cells = await row.query_selector_all("td")
        out.append({"cells": [await c.inner_text() for c in cells]})
    return out


async def read_pismo(session: PueSession, pismo_id: str, *, mark_read: bool = False) -> dict[str, Any]:
    page = session.page
    await page.goto(
        f"https://www.zus.pl/portal/portal-platnika/korespondencja/{pismo_id}",
        wait_until="networkidle",
    )
    body = await page.content()
    return {"id": pismo_id, "title": await page.title(), "body_snippet": body[:1500]}


__all__ = ["list_korespondencja", "read_pismo"]
