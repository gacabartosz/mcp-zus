"""OK-WUD XML builder — wniosek o udostępnienie danych ze zbiorów ZUS.

Generates XML conforming to crd.gov.pl/wzor/2020/12/29/10229/schemat.xsd.
The output is unsigned — user must sign with kwalifikowany podpis or PZ
before sending.
"""
from __future__ import annotations

from typing import Any

from lxml import etree

from mcp_zus.okwud import OKWUD_NS
from mcp_zus.okwud.models import OkwudRequest, PodmiotUdostepnioneDane

NSMAP: dict[str | None, str] = {
    None: OKWUD_NS,
    "str": "http://crd.gov.pl/xml/schematy/struktura/2009/11/16/",
    "meta": "http://crd.gov.pl/xml/schematy/meta/2009/11/16/",
    "oso": "http://crd.gov.pl/xml/schematy/osoba/2009/11/16/",
    "adr": "http://crd.gov.pl/xml/schematy/adres/2009/11/09/",
    "inst": "http://crd.gov.pl/xml/schematy/instytucja/2009/11/16/",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}


def _qn(local: str, prefix: str | None = None) -> str:
    ns = NSMAP[prefix] if prefix else OKWUD_NS
    return f"{{{ns}}}{local}"


def _e(parent: etree._Element, name: str, text: Any = None, *, prefix: str | None = None) -> etree._Element:
    el = etree.SubElement(parent, _qn(name, prefix))
    if text is not None:
        el.text = str(text)
    return el


def _build_podmiot(parent: etree._Element, p: PodmiotUdostepnioneDane) -> None:
    """One podmiot entry. OK-WUD spec requires NIP|REGON|PESEL|paszport."""
    if p.imie or p.nazwisko or p.pesel:
        if p.imie:
            _e(parent, "ImiePierwsze", p.imie)
        if p.nazwisko:
            _e(parent, "Nazwisko", p.nazwisko)
        if p.pesel:
            _e(parent, "PESEL", p.pesel)
        if p.rodzaj_dokumentu_tozsamosci:
            _e(parent, "RodzajDokumentuTozsamosci", p.rodzaj_dokumentu_tozsamosci)
        if p.numer_dokumentu_tozsamosci:
            _e(parent, "SeriaINumerDokumentu", p.numer_dokumentu_tozsamosci)
        if p.data_urodzenia:
            _e(parent, "DataUrodzenia", p.data_urodzenia.isoformat())
    if p.nazwa_skrocona:
        _e(parent, "NazwaSkrocona", p.nazwa_skrocona)
    if p.nazwa_pelna:
        _e(parent, "NazwaPelna", p.nazwa_pelna)
    if p.nip:
        _e(parent, "NIP", p.nip)
    if p.regon:
        _e(parent, "REGON", p.regon)


def build_okwud(request: OkwudRequest, *, pretty: bool = True) -> bytes:
    """Build a complete OK-WUD XML document (UNSIGNED)."""
    root = etree.Element(_qn("Dokument"), nsmap=NSMAP)

    # OpisDokumentu — minimalistyczny szkielet zgodny ze strukturą CRD
    opis = etree.SubElement(root, _qn("OpisDokumentu", "str"))
    cid = etree.SubElement(opis, _qn("CID", "str"))
    cid.text = request.cid

    dane_dok = etree.SubElement(root, _qn("DaneDokumentu", "str"))
    _e(dane_dok, "DataWystawienia", request.data_wniosku.isoformat(), prefix="str")

    # TrescDokumentu
    tresc = etree.SubElement(root, _qn("TrescDokumentu"))

    di = _e(tresc, "DaneIdentyfikacyjneWnioskodawcy")
    _e(di, "NazwaSkrocona", request.wnioskodawca_dane.nazwa_skrocona)
    if request.wnioskodawca_dane.nip:
        _e(di, "NIP", request.wnioskodawca_dane.nip)
    if request.wnioskodawca_dane.regon:
        _e(di, "REGON", request.wnioskodawca_dane.regon)

    da = _e(tresc, "DaneAdresoweWnioskodawcy")
    _e(da, "KodPocztowy", request.wnioskodawca_adres.kod_pocztowy)
    _e(da, "Miejscowosc", request.wnioskodawca_adres.miejscowosc)
    _e(da, "NumerDomu", request.wnioskodawca_adres.numer_domu)
    if request.wnioskodawca_adres.ulica:
        _e(da, "Ulica", request.wnioskodawca_adres.ulica)
    if request.wnioskodawca_adres.numer_lokalu:
        _e(da, "NumerLokalu", request.wnioskodawca_adres.numer_lokalu)

    rodz = _e(tresc, "RodzajWnioskodawcy")
    if request.rodzaj_wnioskodawcy.rodzaj_kod:
        _e(rodz, "RodzajWnioskodawcyWybor", request.rodzaj_wnioskodawcy.rodzaj_kod)
    elif request.rodzaj_wnioskodawcy.rodzaj_inny:
        _e(rodz, "RodzajWnioskodawcyInny", request.rodzaj_wnioskodawcy.rodzaj_inny)

    for pp in request.podstawa_prawna:
        _e(tresc, "PodstawaPrawna", pp)

    _e(tresc, "WskazaniePrzeznaczeniaDanych", request.przeznaczenie_danych)

    for podmiot in request.podmioty:
        di_pod = _e(tresc, "DaneIdentyfikacyjneKontaUdostepnioneDane")
        _build_podmiot(di_pod, podmiot)

        if any(
            [podmiot.kod_pocztowy, podmiot.miejscowosc, podmiot.ulica, podmiot.nr_domu]
        ):
            adr = _e(tresc, "DaneAdresoweKontaUdostepnioneDane")
            if podmiot.kod_pocztowy:
                _e(adr, "KodPocztowy", podmiot.kod_pocztowy)
            if podmiot.miejscowosc:
                _e(adr, "Miejscowosc", podmiot.miejscowosc)
            if podmiot.ulica:
                _e(adr, "Ulica", podmiot.ulica)
            if podmiot.nr_domu:
                _e(adr, "NumerDomu", podmiot.nr_domu)
            if podmiot.nr_lokalu:
                _e(adr, "NumerLokalu", podmiot.nr_lokalu)

    zakres_el = _e(tresc, "ZakresZadanychDanych")
    if request.zakres.dane_identyfikacyjne:
        _e(zakres_el, "DaneIdentyfikacyjne", "true")
    if request.zakres.okresy_ubezpieczenia:
        _e(zakres_el, "OkresyUbezpieczenia", "true")
    if request.zakres.podstawy_wymiaru:
        _e(zakres_el, "PodstawyWymiaru", "true")
    if request.zakres.swiadczenia:
        _e(zakres_el, "Swiadczenia", "true")
    if request.zakres.skladki:
        _e(zakres_el, "Skladki", "true")
    if request.zakres.inne:
        _e(zakres_el, "Inne", request.zakres.inne)

    _e(tresc, "Data", request.data_wniosku.isoformat())

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=pretty)


__all__ = ["build_okwud"]
