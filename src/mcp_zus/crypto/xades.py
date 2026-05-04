"""XAdES signing using `signxml` (when private key is available locally).

This module wraps `signxml.XMLSigner` with the XAdES-BES profile
typically required by ZUS / ePUAP / OK-WUD endpoints.

USAGE: only when self-hosting and the user explicitly provides their
own .p12 / .pem locally. MCP server itself NEVER reads private keys.
"""
from __future__ import annotations

from pathlib import Path


def sign_with_signxml(
    xml: bytes,
    *,
    cert_path: str | Path,
    key_path: str | Path,
    key_password: str | None = None,
    digest_algo: str = "sha256",
) -> bytes:
    """Sign XML using local PEM key + cert via signxml (XAdES-BES).

    NOT used by the MCP server — provided as a helper for users who self-host
    and want a one-shot signing utility.
    """
    try:
        from signxml import XMLSigner, methods
    except ImportError as exc:
        raise RuntimeError("signxml not installed; run: uv pip install signxml") from exc

    from lxml import etree

    cert_pem = Path(cert_path).read_bytes()
    key_pem = Path(key_path).read_bytes()

    doc = etree.fromstring(xml)
    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm=digest_algo,
        c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
    )
    signed = signer.sign(doc, key=key_pem, cert=cert_pem, passphrase=key_password)
    return etree.tostring(signed, xml_declaration=True, encoding="UTF-8")


__all__ = ["sign_with_signxml"]
