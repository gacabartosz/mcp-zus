"""Unit tests — KEDU parser round-trips."""
from __future__ import annotations

from datetime import date

from mcp_zus.kedu.builder import build_kedu
from mcp_zus.kedu.models import (
    DraInput,
    Insured,
    Payer,
    ZuaInput,
)
from mcp_zus.kedu.parser import parse_kedu


def test_parse_extracts_naglowek_and_documents():
    payer = Payer(nip="1234563218", nazwa_skrocona="ACME")
    dra = DraInput(payer=payer, period=date(2026, 5, 1))
    xml = build_kedu([dra])

    parsed = parse_kedu(xml)
    assert "naglowek" in parsed
    assert "documents" in parsed
    assert len(parsed["documents"]) == 1
    assert parsed["documents"][0]["type"] == "DRA"


def test_parse_multiple_documents():
    payer = Payer(nip="1234563218", nazwa_skrocona="ACME")
    insured = Insured(pesel="44051401359", nazwisko="K", imie_pierwsze="J")
    docs = [
        DraInput(payer=payer, period=date(2026, 5, 1)),
        ZuaInput(
            payer=payer,
            insured=insured,
            kod_tytulu_ubezpieczenia="0110",
            data_powstania_obowiazku=date(2026, 5, 1),
        ),
    ]
    xml = build_kedu(docs)
    parsed = parse_kedu(xml)
    types = {d["type"] for d in parsed["documents"]}
    assert types == {"DRA", "ZUA"}


def test_parse_rejects_non_kedu():
    import pytest
    bad = b'<?xml version="1.0"?><not-kedu/>'
    with pytest.raises(ValueError, match="KEDU"):
        parse_kedu(bad)


def test_parse_naglowek_has_program():
    payer = Payer(nip="1234563218", nazwa_skrocona="ACME")
    dra = DraInput(payer=payer, period=date(2026, 5, 1))
    xml = build_kedu([dra])
    parsed = parse_kedu(xml)
    assert "program" in parsed["naglowek"]
    assert parsed["naglowek"]["program"]["producent"] == "mcp-zus"
