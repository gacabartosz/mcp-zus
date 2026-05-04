"""MCP tools — Crypto / BYO signing flow."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from mcp_zus.crypto.byo import attach_signature, prepare_signing_payload


class PrepareSignInput(BaseModel):
    xml: str
    profile: Literal["xades-bes-zus", "xmldsig"] = "xades-bes-zus"


class PrepareSignResponse(BaseModel):
    canonical_xml: str
    digest_sha256_b64: str
    profile: str
    instructions: str


def tool_prepare_signing_payload(input: PrepareSignInput) -> PrepareSignResponse:
    payload = prepare_signing_payload(input.xml.encode("utf-8"), profile=input.profile)
    return PrepareSignResponse(
        canonical_xml=payload.canonical_xml.decode("utf-8"),
        digest_sha256_b64=payload.digest_sha256_b64,
        profile=payload.profile,
        instructions=(
            "Sign the digest_sha256_b64 with your kwalifikowany podpis (Szafir/Certum/local p12). "
            "Then call crypto.attach_signature with the resulting signature_b64."
        ),
    )


class AttachSignatureInput(BaseModel):
    xml: str
    signature_b64: str
    certificate_chain_pem: list[str]


def tool_attach_signature(input: AttachSignatureInput) -> str:
    out = attach_signature(
        input.xml.encode("utf-8"),
        signature_b64=input.signature_b64,
        certificate_chain_pem=input.certificate_chain_pem,
    )
    return out.decode("utf-8")


__all__ = ["tool_attach_signature", "tool_prepare_signing_payload"]
