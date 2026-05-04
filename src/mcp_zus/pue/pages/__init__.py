"""Page Object Pattern for PUE screens.

Each module is a thin wrapper around a Playwright Page, exposing semantic
methods rather than raw selectors. Selectors live in `mcp_zus.pue.selectors`.
"""
from __future__ import annotations
