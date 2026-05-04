"""MCP tools — EWD (skeleton; production requires accreditation)."""
from __future__ import annotations

from pydantic import BaseModel

from mcp_zus.ewd.client import EwdClient
from mcp_zus.ewd.upo import parse_upo


class SendInput(BaseModel):
    signed_xml_path: str


def tool_ewd_send(input: SendInput) -> dict:
    """Send signed KEDU through EWD (requires ZUS accreditation)."""
    with open(input.signed_xml_path, "rb") as f:
        xml = f.read()
    client = EwdClient()
    return client.send(xml)


class StatusInput(BaseModel):
    reference: str


def tool_ewd_status(input: StatusInput) -> dict:
    return EwdClient().get_status(input.reference)


def tool_ewd_fetch_upo(input: StatusInput) -> dict:
    upo_xml = EwdClient().fetch_upo(input.reference)
    return parse_upo(upo_xml)


__all__ = ["tool_ewd_fetch_upo", "tool_ewd_send", "tool_ewd_status"]
