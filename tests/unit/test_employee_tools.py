"""Unit tests — high-level employee orchestrator tools."""
from __future__ import annotations

from datetime import date

from mcp_zus.kedu.models import Insured, Payer
from mcp_zus.tools import employee_tools

VALID_NIP = "1234563218"
VALID_PESEL = "44051401359"


def _payer() -> Payer:
    return Payer(nip=VALID_NIP, nazwa_skrocona="ACME")


def _insured() -> Insured:
    return Insured(pesel=VALID_PESEL, nazwisko="Kowalski", imie_pierwsze="Jan")


def test_register_employee_returns_zua_xml():
    inp = employee_tools.RegisterEmployeeInput(
        payer=_payer(),
        employee=_insured(),
        kod_tytulu="0110",
        data_powstania=date(2026, 5, 1),
    )
    response = employee_tools.tool_register_employee(inp)
    assert response.document_kind == "ZUA"
    assert "<ZUA" in response.xml or ":ZUA" in response.xml or "ZUA>" in response.xml


def test_deregister_employee_returns_zwua_xml():
    inp = employee_tools.DeregisterEmployeeInput(
        payer=_payer(),
        employee=_insured(),
        kod_tytulu="0110",
        data_wyrejestrowania=date(2026, 6, 30),
        kod_przyczyny="100",
    )
    response = employee_tools.tool_deregister_employee(inp)
    assert response.document_kind == "ZWUA"
    assert "100" in response.xml


def test_add_family_member_zcna():
    family = Insured(pesel=VALID_PESEL, nazwisko="Kowalska", imie_pierwsze="Maria")
    inp = employee_tools.AddFamilyMemberInput(
        payer=_payer(),
        employee=_insured(),
        family_member=family,
        stopien_pokrewienstwa="04",
        data_powstania_uprawnienia=date(2020, 6, 14),
    )
    response = employee_tools.tool_add_family_member(inp)
    assert response.document_kind == "ZCNA"
    assert "Kowalska" in response.xml
