"""MCP tools — KEDU module."""
from __future__ import annotations

from pydantic import BaseModel, Field

from mcp_zus.kedu.builder import build_kedu, kedu_digest
from mcp_zus.kedu.jdg import build_jdg_monthly
from mcp_zus.kedu.models import (
    DraInput,
    JdgMonthlyInput,
    ZcnaInput,
    ZiuaInput,
    ZuaInput,
    ZwuaInput,
)
from mcp_zus.kedu.parser import parse_kedu
from mcp_zus.kedu.validator import ValidationReport, validate_kedu


class BuildKeduResponse(BaseModel):
    xml: str
    digest_sha256: str
    validation: ValidationReport | None = None


def tool_build_kedu_dra(input: DraInput, validate: bool = True) -> BuildKeduResponse:
    xml = build_kedu([input])
    return BuildKeduResponse(
        xml=xml.decode("utf-8"),
        digest_sha256=kedu_digest(xml),
        validation=validate_kedu(xml) if validate else None,
    )


def tool_build_kedu_zua(input: ZuaInput, validate: bool = True) -> BuildKeduResponse:
    xml = build_kedu([input])
    return BuildKeduResponse(
        xml=xml.decode("utf-8"),
        digest_sha256=kedu_digest(xml),
        validation=validate_kedu(xml) if validate else None,
    )


def tool_build_kedu_zwua(input: ZwuaInput, validate: bool = True) -> BuildKeduResponse:
    xml = build_kedu([input])
    return BuildKeduResponse(
        xml=xml.decode("utf-8"),
        digest_sha256=kedu_digest(xml),
        validation=validate_kedu(xml) if validate else None,
    )


def tool_build_kedu_ziua(input: ZiuaInput, validate: bool = True) -> BuildKeduResponse:
    xml = build_kedu([input])
    return BuildKeduResponse(
        xml=xml.decode("utf-8"),
        digest_sha256=kedu_digest(xml),
        validation=validate_kedu(xml) if validate else None,
    )


def tool_build_kedu_zcna(input: ZcnaInput, validate: bool = True) -> BuildKeduResponse:
    xml = build_kedu([input])
    return BuildKeduResponse(
        xml=xml.decode("utf-8"),
        digest_sha256=kedu_digest(xml),
        validation=validate_kedu(xml) if validate else None,
    )


def tool_build_jdg_monthly(input: JdgMonthlyInput, validate: bool = True) -> BuildKeduResponse:
    xml = build_jdg_monthly(input)
    return BuildKeduResponse(
        xml=xml.decode("utf-8"),
        digest_sha256=kedu_digest(xml),
        validation=validate_kedu(xml) if validate else None,
    )


class ValidateInput(BaseModel):
    xml: str = Field(description="KEDU XML to validate against XSD 5.6")


def tool_validate_kedu(input: ValidateInput) -> ValidationReport:
    return validate_kedu(input.xml)


class ParseInput(BaseModel):
    xml: str = Field(description="KEDU XML to parse")


def tool_parse_kedu(input: ParseInput) -> dict:
    return parse_kedu(input.xml)


__all__ = [
    "tool_build_jdg_monthly",
    "tool_build_kedu_dra",
    "tool_build_kedu_zcna",
    "tool_build_kedu_ziua",
    "tool_build_kedu_zua",
    "tool_build_kedu_zwua",
    "tool_parse_kedu",
    "tool_validate_kedu",
]
