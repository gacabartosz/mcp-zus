"""Unit tests — BYO signing flow."""
from __future__ import annotations

import base64
import hashlib

from mcp_zus.crypto.byo import attach_signature, prepare_signing_payload


def test_prepare_returns_canonical_and_digest():
    xml = b'<?xml version="1.0" encoding="UTF-8"?><doc><a>x</a></doc>'
    payload = prepare_signing_payload(xml)
    assert b"<doc>" in payload.canonical_xml
    # digest matches sha256 of canonical
    expected = base64.b64encode(hashlib.sha256(payload.canonical_xml).digest()).decode()
    assert payload.digest_sha256_b64 == expected


def test_attach_signature_inserts_ds_signature():
    xml = b'<?xml version="1.0"?><doc><a>x</a></doc>'
    fake_sig = base64.b64encode(b"fake_signature_bytes").decode()
    out = attach_signature(xml, fake_sig, certificate_chain_pem=["MIIDfake"])
    assert b"Signature" in out
    assert fake_sig.encode() in out
    assert b"X509Certificate" in out
