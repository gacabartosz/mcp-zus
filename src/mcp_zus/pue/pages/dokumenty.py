"""PUE — Dokumenty / Zestawy KEDU."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from mcp_zus.pue.selectors import Dokumenty as Sel

if TYPE_CHECKING:
    from mcp_zus.pue.attach import PueSession


async def list_dokumenty(session: PueSession, *, limit: int = 20) -> list[dict[str, Any]]:
    """List recent document sets (zestawy KEDU) visible in PUE."""
    page = session.page
    await page.goto("https://www.zus.pl/portal/portal-platnika/dokumenty", wait_until="networkidle")
    rows = await page.query_selector_all(Sel.LIST_ROW)
    out: list[dict[str, Any]] = []
    for row in rows[:limit]:
        cells = await row.query_selector_all("td")
        cell_text = [await c.inner_text() for c in cells]
        out.append({"cells": cell_text})
    return out


async def download_upo(session: PueSession, reference: str, dest: Path) -> Path:
    """Download UPO for a given zestaw reference."""
    page = session.page
    # Navigate to dokumenty list, find row with reference, click UPO link
    await page.goto("https://www.zus.pl/portal/portal-platnika/dokumenty", wait_until="networkidle")
    row = page.locator(f"{Sel.LIST_ROW}:has-text('{reference}')")
    upo_link = row.locator(Sel.UPO_DOWNLOAD_LINK).first
    async with page.expect_download() as dl_info:
        await upo_link.click()
    download = await dl_info.value
    dest.parent.mkdir(parents=True, exist_ok=True)
    await download.save_as(str(dest))
    return dest


async def upload_kedu(session: PueSession, signed_xml_path: Path) -> dict[str, Any]:
    """Upload a locally-signed KEDU XML through the PUE UI."""
    page = session.page
    await page.goto("https://www.zus.pl/portal/portal-platnika/dokumenty/upload", wait_until="networkidle")
    file_input = page.locator(Sel.UPLOAD_FILE_INPUT)
    await file_input.set_input_files(str(signed_xml_path))
    await page.locator(Sel.UPLOAD_SUBMIT).click()
    await page.wait_for_load_state("networkidle")
    confirmation = await page.content()
    return {"submitted": True, "page_title": await page.title(), "snippet": confirmation[:500]}


__all__ = ["download_upo", "list_dokumenty", "upload_kedu"]
