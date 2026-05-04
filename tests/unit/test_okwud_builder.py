"""Unit tests — OK-WUD XML builder."""
from __future__ import annotations

from datetime import date

from lxml import etree

from mcp_zus.okwud import OKWUD_NS
from mcp_zus.okwud.builder import build_okwud
from mcp_zus.okwud.models import (
    DaneAdresoweWnioskodawcy,
    DaneIdentyfikacyjneWnioskodawcy,
    OkwudRequest,
    PodmiotUdostepnioneDane,
    RodzajWnioskodawcy,
    ZakresZadanychDanych,
)


def _sample_request() -> OkwudRequest:
    return OkwudRequest(
        cid="WNIO/2026/05/0001",
        wnioskodawca_dane=DaneIdentyfikacyjneWnioskodawcy(
            nazwa_skrocona="Sąd Rejonowy Wrocław",
            regon="000123456",
        ),
        wnioskodawca_adres=DaneAdresoweWnioskodawcy(
            kod_pocztowy="50-040",
            miejscowosc="Wrocław",
            numer_domu="12",
            ulica="Sądowa",
        ),
        rodzaj_wnioskodawcy=RodzajWnioskodawcy(rodzaj_kod="S"),
        przeznaczenie_danych="Postępowanie sądowe sygn. akt I C 123/26",
        podstawa_prawna=["art. 50 ust. 5 ustawy o systemie ubezpieczeń społecznych"],
        podmioty=[
            PodmiotUdostepnioneDane(
                imie="Jan",
                nazwisko="Kowalski",
                pesel="44051401359",
            )
        ],
        zakres=ZakresZadanychDanych(okresy_ubezpieczenia=True, podstawy_wymiaru=True),
        data_wniosku=date(2026, 5, 4),
    )


def test_build_okwud_returns_bytes():
    xml = build_okwud(_sample_request())
    assert isinstance(xml, bytes)
    assert b"<?xml" in xml


def test_build_okwud_namespace():
    xml = build_okwud(_sample_request())
    root = etree.fromstring(xml)
    assert etree.QName(root).namespace == OKWUD_NS
    assert etree.QName(root).localname == "Dokument"


def test_build_okwud_has_cid():
    xml = build_okwud(_sample_request())
    assert b"WNIO/2026/05/0001" in xml


def test_build_okwud_has_kod_instytucji():
    xml = build_okwud(_sample_request())
    assert b">S<" in xml or b">S</" in xml  # Sądy = "S"


def test_build_okwud_invalid_kod_raises():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        RodzajWnioskodawcy(rodzaj_kod="NOT_A_REAL_CODE")


def test_build_okwud_with_company_subject():
    req = _sample_request()
    req.podmioty = [PodmiotUdostepnioneDane(nazwa_skrocona="Firma X", nip="1234563218")]
    xml = build_okwud(req)
    assert b"Firma X" in xml
    assert b"1234563218" in xml
