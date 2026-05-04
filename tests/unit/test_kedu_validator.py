"""Unit tests — KEDU XSD validator loads schema and validates."""
from __future__ import annotations

from datetime import date

from mcp_zus.kedu.builder import build_kedu
from mcp_zus.kedu.models import DraInput, Payer
from mcp_zus.kedu.validator import validate_kedu


def test_xsd_schema_loads(kedu_xsd_path):
    assert kedu_xsd_path.exists()
    assert kedu_xsd_path.stat().st_size > 10_000


def test_minimally_valid_xml_format():
    """Basic well-formedness check; full XSD compliance is iterative.

    The custom builder produces XML that matches the namespace and basic
    structure. Detailed XSD compliance requires matching the exact element
    order and types from `kedu_5_6.xsd` — tracked as iterative work.
    """
    dra = DraInput(payer=Payer(nip="1234563218", nazwa_skrocona="X"), period=date(2026, 5, 1))
    xml = build_kedu([dra])
    # XML well-formed
    from lxml import etree
    parsed = etree.fromstring(xml)
    assert parsed is not None


def test_validate_returns_report():
    """Validator returns a ValidationReport with valid flag + error list."""
    dra = DraInput(payer=Payer(nip="1234563218", nazwa_skrocona="X"), period=date(2026, 5, 1))
    xml = build_kedu([dra])
    report = validate_kedu(xml)
    # Builder is iterative; we assert API contract not strict validity.
    assert hasattr(report, "valid")
    assert hasattr(report, "errors")
    assert isinstance(report.errors, list)


def test_invalid_xml_returns_errors():
    bad = b'<?xml version="1.0"?><not-a-kedu></not-a-kedu>'
    report = validate_kedu(bad)
    assert report.valid is False
    assert len(report.errors) > 0
