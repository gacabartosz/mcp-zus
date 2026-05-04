"""MCP tools — ePUAP transport."""
from __future__ import annotations

from pydantic import BaseModel

from mcp_zus.epuap.client import EpuapClient


class SendToZusInput(BaseModel):
    signed_xml_path: str
    document_kind: str  # np. "ZUS-PEL", "ZUS-RWN", "OK-WUD"


def tool_epuap_send_to_zus(input: SendToZusInput) -> dict:
    with open(input.signed_xml_path, "rb") as f:
        xml = f.read()
    return EpuapClient().send_to_zus(xml, input.document_kind)


class FetchUppInput(BaseModel):
    message_id: str


def tool_epuap_fetch_upp(input: FetchUppInput) -> bytes:
    return EpuapClient().fetch_upp(input.message_id)


def tool_epuap_list_inbox() -> list[dict]:
    return EpuapClient().list_inbox()


__all__ = [
    "tool_epuap_fetch_upp",
    "tool_epuap_list_inbox",
    "tool_epuap_send_to_zus",
]
