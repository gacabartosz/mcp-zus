"""KEDU 5.6 — Kompleksowa Elektroniczna Dokumentacja Ubezpieczeniowa.

Offline XML builder/parser/validator for ZUS documents:
DRA, RCA, RSA, RZA, ZUA, ZWUA, ZIUA, ZCNA, ZPA, ZSWA, ZZA, ZFA, IWA.
"""
from __future__ import annotations

from mcp_zus.kedu.builder import build_kedu
from mcp_zus.kedu.parser import parse_kedu
from mcp_zus.kedu.validator import KeduValidationError, validate_kedu

KEDU_NS = "http://www.zus.pl/2024/KEDU_5_6"
KEDU_VERSION = "5.6"

__all__ = [
    "KEDU_NS",
    "KEDU_VERSION",
    "KeduValidationError",
    "build_kedu",
    "parse_kedu",
    "validate_kedu",
]
