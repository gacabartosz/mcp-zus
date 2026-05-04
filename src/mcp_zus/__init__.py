"""mcp-zus — Model Context Protocol server for Polish ZUS / PUE.

Modules:
    kedu   — KEDU 5.6 XML builder/parser/validator (offline)
    ewd    — Elektroniczna Wymiana Dokumentów (SOAP) for payers
    okwud  — Wnioski uprawnionych instytucji o udostępnienie danych (SOAP)
    epuap  — ePUAP WS-Skrytka transport
    pue    — PUE Browser Companion (Playwright + CDP attach)
    crypto — XAdES helpers (BYO key, never holds private keys)
"""
from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__"]
