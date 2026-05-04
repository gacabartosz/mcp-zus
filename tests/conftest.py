"""Shared pytest fixtures."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def kedu_xsd_path() -> Path:
    return Path(__file__).parents[1] / "src" / "mcp_zus" / "kedu" / "schemas" / "kedu_5_6.xsd"


@pytest.fixture(scope="session")
def okwud_xsd_path() -> Path:
    return Path(__file__).parents[1] / "src" / "mcp_zus" / "okwud" / "schemas" / "okwud_2020_12_29.xsd"
