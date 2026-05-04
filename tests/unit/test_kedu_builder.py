"""Unit tests — KEDU builder produces well-formed XML with correct namespace."""
from __future__ import annotations

from datetime import date

from lxml import etree

from mcp_zus.kedu.builder import KEDU_NS, build_kedu, kedu_digest
from mcp_zus.kedu.models import (
    DraInput,
    Insured,
    Payer,
    ZcnaInput,
    ZuaInput,
    ZwuaInput,
)

VALID_NIP = "1234563218"
VALID_PESEL = "44051401359"


def _payer() -> Payer:
    return Payer(nip=VALID_NIP, nazwa_skrocona="ACME Sp. z o.o.")


def _insured() -> Insured:
    return Insured(
        pesel=VALID_PESEL,
        nazwisko="Kowalski",
        imie_pierwsze="Jan",
        data_urodzenia=date(1980, 5, 15),
    )


def test_build_dra_returns_bytes():
    dra = DraInput(payer=_payer(), period=date(2026, 5, 1), skladka_emerytalna=917.99)
    xml = build_kedu([dra])
    assert isinstance(xml, bytes)
    assert b"<?xml" in xml
    root = etree.fromstring(xml)
    assert etree.QName(root).localname == "KEDU"
    assert etree.QName(root).namespace == KEDU_NS


def test_build_zua_contains_pesel():
    zua = ZuaInput(
        payer=_payer(),
        insured=_insured(),
        kod_tytulu_ubezpieczenia="0110",
        data_powstania_obowiazku=date(2026, 5, 1),
    )
    xml = build_kedu([zua])
    assert VALID_PESEL.encode() in xml
    assert b"ZUSZUA" in xml  # XSD requires ZUS-prefixed element name


def test_build_zwua_has_kod_przyczyny():
    zwua = ZwuaInput(
        payer=_payer(),
        insured=_insured(),
        kod_tytulu_ubezpieczenia="0110",
        data_wyrejestrowania=date(2026, 6, 30),
        kod_przyczyny_wyrejestrowania="100",
    )
    xml = build_kedu([zwua])
    assert b"ZUSZWUA" in xml
    assert b"100" in xml


def test_build_zcna_has_family_member():
    employee = _insured()
    family = Insured(pesel="44051401359", nazwisko="Kowalska", imie_pierwsze="Maria")
    zcna = ZcnaInput(
        payer=_payer(),
        insured=employee,
        family_member=family,
        stopien_pokrewienstwa="04",  # małżonek
        data_powstania_uprawnienia=date(2020, 6, 14),
    )
    xml = build_kedu([zcna])
    assert b"ZUSZCNA" in xml
    assert b"Kowalska" in xml


def test_build_kedu_multiple_documents():
    docs = [
        DraInput(payer=_payer(), period=date(2026, 5, 1)),
        ZuaInput(
            payer=_payer(),
            insured=_insured(),
            kod_tytulu_ubezpieczenia="0110",
            data_powstania_obowiazku=date(2026, 5, 1),
        ),
    ]
    xml = build_kedu(docs)
    assert b"ZUSDRA" in xml
    assert b"ZUSZUA" in xml


def test_envelope_has_wersja_schematu_attribute():
    """KEDU root must have wersja_schematu='1' attribute per XSD."""
    dra = DraInput(payer=_payer(), period=date(2026, 5, 1))
    xml = build_kedu([dra])
    assert b'wersja_schematu="1"' in xml


def test_envelope_uses_dot_in_naglowek_name():
    """Per XSD, header element is `naglowek.KEDU` not `naglowek_KEDU`."""
    dra = DraInput(payer=_payer(), period=date(2026, 5, 1))
    xml = build_kedu([dra])
    assert b"naglowek.KEDU" in xml


def test_kedu_digest_is_hex_string():
    dra = DraInput(payer=_payer(), period=date(2026, 5, 1))
    xml = build_kedu([dra])
    digest = kedu_digest(xml)
    assert len(digest) == 64  # SHA-256 hex
    assert all(c in "0123456789abcdef" for c in digest)


def test_build_kedu_empty_raises():
    import pytest
    with pytest.raises(ValueError, match="at least one"):
        build_kedu([])


def test_naglowek_contains_program_meta():
    dra = DraInput(payer=_payer(), period=date(2026, 5, 1))
    xml = build_kedu([dra])
    assert b"mcp-zus" in xml
    assert b"MCP-ZUS" in xml


def test_jdg_monthly_builds_dra():
    from mcp_zus.kedu.jdg import build_jdg_monthly
    from mcp_zus.kedu.models import JdgMonthlyInput

    inp = JdgMonthlyInput(payer=_payer(), period=date(2026, 5, 1), basis_kind="standard")
    xml = build_jdg_monthly(inp)
    assert b"ZUSDRA" in xml
    assert b"liczba_ubezpieczonych" in xml


def test_jdg_ulga_na_start_zeros_skladki():
    from mcp_zus.kedu.jdg import build_jdg_monthly
    from mcp_zus.kedu.models import JdgMonthlyInput

    inp = JdgMonthlyInput(payer=_payer(), period=date(2026, 5, 1), basis_kind="ulga_na_start")
    xml = build_jdg_monthly(inp)
    parsed = etree.fromstring(xml)
    emer = parsed.find(".//{http://www.zus.pl/2024/KEDU_5_6}emerytalne")
    assert emer is not None
    assert emer.text == "0.00"
