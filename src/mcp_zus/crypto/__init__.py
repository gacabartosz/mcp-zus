"""XAdES helpers (BYO key — server NEVER holds the private key).

Three-step flow for every signed XML:
    1. `prepare_signing_payload(xml)` — server returns canonicalized payload + digest.
    2. User signs locally (Szafir, Certum, signxml CLI, hardware token).
    3. `attach_signature(xml, signature, cert_chain)` — server embeds the
       signature in the document.
"""
from __future__ import annotations
