"""MCP tools — PUE Browser Companion."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from mcp_zus.pue.attach import attach
from mcp_zus.pue.pages import dokumenty as p_dok
from mcp_zus.pue.pages import korespondencja as p_kor
from mcp_zus.pue.pages import ubezpieczeni as p_ubz


class AttachInput(BaseModel):
    cdp_url: str = Field(default="http://localhost:9222", description="Chrome DevTools Protocol URL")


class AttachResponse(BaseModel):
    attached: bool
    url: str
    title: str
    is_logged_in: bool


async def tool_attach(input: AttachInput) -> AttachResponse:
    async with attach(input.cdp_url) as session:
        info = await session.whoami()
        return AttachResponse(attached=True, **info)


class ListInput(BaseModel):
    limit: int = Field(default=20, ge=1, le=200)


async def tool_list_dokumenty(input: ListInput) -> list[dict]:
    async with attach() as session:
        return await p_dok.list_dokumenty(session, limit=input.limit)


async def tool_list_ubezpieczeni(input: ListInput) -> list[dict]:
    async with attach() as session:
        return await p_ubz.list_ubezpieczeni(session, limit=input.limit)


async def tool_list_korespondencja(input: ListInput) -> list[dict]:
    async with attach() as session:
        return await p_kor.list_korespondencja(session, limit=input.limit)


class DownloadUpoInput(BaseModel):
    reference: str
    dest_path: str


class DownloadUpoResponse(BaseModel):
    saved_to: str


async def tool_download_upo(input: DownloadUpoInput) -> DownloadUpoResponse:
    async with attach() as session:
        path = await p_dok.download_upo(session, input.reference, Path(input.dest_path))
    return DownloadUpoResponse(saved_to=str(path))


class UploadKeduInput(BaseModel):
    signed_xml_path: str


async def tool_upload_kedu(input: UploadKeduInput) -> dict:
    async with attach() as session:
        return await p_dok.upload_kedu(session, Path(input.signed_xml_path))


class ReadPismoInput(BaseModel):
    pismo_id: str
    mark_read: bool = False


async def tool_read_pismo(input: ReadPismoInput) -> dict:
    async with attach() as session:
        return await p_kor.read_pismo(session, input.pismo_id, mark_read=input.mark_read)


__all__ = [
    "tool_attach",
    "tool_download_upo",
    "tool_list_dokumenty",
    "tool_list_korespondencja",
    "tool_list_ubezpieczeni",
    "tool_read_pismo",
    "tool_upload_kedu",
]
