"""Bring-Your-Own-Key XAdES signing flow.

The server never holds the private key. It produces the canonicalized
payload to be signed and the SHA-256 digest. The user signs locally; the
server embeds the resulting <ds:Signature> into the document.
"""
from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass
from typing import Literal

from lxml import etree

XADES_NS = "http://uri.etsi.org/01903/v1.3.2#"
DSIG_NS = "http://www.w3.org/2000/09/xmldsig#"
SignatureProfile = Literal["xades-bes-zus", "xmldsig"]


@dataclass(slots=True)
class SigningPayload:
    """What the user needs to sign locally."""

    canonical_xml: bytes  # C14N(2001-03-15)
    digest_sha256_b64: str
    profile: SignatureProfile


def prepare_signing_payload(xml: bytes, *, profile: SignatureProfile = "xades-bes-zus") -> SigningPayload:
    """Canonicalize the XML and compute SHA-256 digest for user-side signing."""
    doc = etree.fromstring(xml)
    canonical = etree.tostring(doc, method="c14n", exclusive=False)
    digest = hashlib.sha256(canonical).digest()
    return SigningPayload(
        canonical_xml=canonical,
        digest_sha256_b64=base64.b64encode(digest).decode("ascii"),
        profile=profile,
    )


def attach_signature(xml: bytes, signature_b64: str, certificate_chain_pem: list[str]) -> bytes:
    """Embed user's signature into XML as <ds:Signature>.

    NOTE: For full XAdES-BES-ZUS profile (which requires SignedProperties,
    SigningCertificate, SignaturePolicyIdentifier, etc.) use `crypto.xades.sign_with_signxml`
    when you have a local key — that's the legitimate path for self-hosting.
    Here we provide a minimal `<ds:Signature>` template you can extend.
    """
    doc = etree.fromstring(xml)
    nsmap = {"ds": DSIG_NS}
    sig = etree.SubElement(doc, f"{{{DSIG_NS}}}Signature", nsmap=nsmap)
    si = etree.SubElement(sig, f"{{{DSIG_NS}}}SignedInfo")
    etree.SubElement(
        si, f"{{{DSIG_NS}}}CanonicalizationMethod",
        Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
    )
    etree.SubElement(
        si, f"{{{DSIG_NS}}}SignatureMethod",
        Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
    )
    sig_value = etree.SubElement(sig, f"{{{DSIG_NS}}}SignatureValue")
    sig_value.text = signature_b64
    key_info = etree.SubElement(sig, f"{{{DSIG_NS}}}KeyInfo")
    x509_data = etree.SubElement(key_info, f"{{{DSIG_NS}}}X509Data")
    for pem in certificate_chain_pem:
        cert = etree.SubElement(x509_data, f"{{{DSIG_NS}}}X509Certificate")
        cert.text = pem.strip().replace("-----BEGIN CERTIFICATE-----", "").replace(
            "-----END CERTIFICATE-----", ""
        ).strip()

    return etree.tostring(doc, xml_declaration=True, encoding="UTF-8")


__all__ = ["SigningPayload", "attach_signature", "prepare_signing_payload"]
