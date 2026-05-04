"""KEDU 5.6 XML builder.

Generates XSD-conformant XML for ZUS documents using lxml. The builder
focuses on **correctness of structure and namespacing** — exact field names
must match the official `kedu_5_6.xsd` from BIP ZUS (cached locally).

This module covers the core document types: DRA, ZUA, ZWUA, ZIUA, ZCNA.
Other types (RCA, RSA, RZA, ZPA, ZSWA, ZZA, ZFA, IWA) follow the same
pattern and can be added by extending `_build_<type>` helpers.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import date
from typing import Any

from lxml import etree

from mcp_zus.kedu.models import (
    DraInput,
    Insured,
    Payer,
    Program,
    ZcnaInput,
    ZiuaInput,
    ZuaInput,
    ZwuaInput,
)

KEDU_NS = "http://www.zus.pl/2024/KEDU_5_6"
NSMAP: dict[str | None, str] = {None: KEDU_NS}


def _qn(local: str) -> str:
    return f"{{{KEDU_NS}}}{local}"


def _e(parent: etree._Element, name: str, text: Any = None) -> etree._Element:
    el = etree.SubElement(parent, _qn(name))
    if text is not None:
        el.text = str(text)
    return el


def _format_date(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def _generate_kedu_id() -> str:
    """t_id_zlozony — unique KEDU identifier (max 51 chars)."""
    return f"MCPZUS-{uuid.uuid4().hex[:24].upper()}"


def _build_naglowek(
    root: etree._Element,
    program: Program,
    sender_idp: str | None = None,
) -> None:
    """Build <naglowek.KEDU> (note: dot, not underscore — exact XSD requirement)."""
    n = _e(root, "naglowek.KEDU")
    p = _e(n, "program")
    _e(p, "producent", program.producent)
    _e(p, "symbol", program.symbol)
    _e(p, "wersja", program.wersja)
    _e(n, "ID_KEDU", _generate_kedu_id())
    _e(n, "data_utworzenia_KEDU", _format_date(date.today()))
    if sender_idp:
        _e(n, "id_nadawcy_ID_KEDU", sender_idp)


def _build_dane_platnika(parent: etree._Element, payer: Payer) -> None:
    dp = _e(parent, "dane_identyfikacyjne_platnika_skladek")
    _e(dp, "NIP", payer.nip)
    if payer.regon:
        _e(dp, "REGON", payer.regon)
    _e(dp, "nazwa_skrocona", payer.nazwa_skrocona)
    if payer.nazwa_pelna:
        _e(dp, "nazwa_pelna", payer.nazwa_pelna)


def _build_dane_ubezpieczonego(parent: etree._Element, ins: Insured) -> None:
    du = _e(parent, "dane_identyfikacyjne_ubezpieczonego")
    if ins.pesel:
        _e(du, "PESEL", ins.pesel)
    if ins.nip:
        _e(du, "NIP", ins.nip)
    _e(du, "nazwisko", ins.nazwisko)
    _e(du, "imie_pierwsze", ins.imie_pierwsze)
    if ins.imie_drugie:
        _e(du, "imie_drugie", ins.imie_drugie)
    if ins.data_urodzenia:
        _e(du, "data_urodzenia", _format_date(ins.data_urodzenia))


def _build_zua(parent: etree._Element, doc: ZuaInput) -> None:
    """Zgłoszenie do ubezpieczeń (ZUA → element ZUSZUA in XSD)."""
    zua = _e(parent, "ZUSZUA")
    _build_dane_platnika(zua, doc.payer)
    _build_dane_ubezpieczonego(zua, doc.insured)
    tu = _e(zua, "tytul_ubezpieczenia")
    _e(tu, "kod", doc.kod_tytulu_ubezpieczenia)
    _e(tu, "data_powstania", _format_date(doc.data_powstania_obowiazku))

    rodz = _e(zua, "rodzaje_ubezpieczen")
    _e(rodz, "emerytalne", "1" if doc.ubezpieczenie_emerytalne else "0")
    _e(rodz, "rentowe", "1" if doc.ubezpieczenie_rentowe else "0")
    _e(rodz, "chorobowe", "1" if doc.ubezpieczenie_chorobowe else "0")
    _e(rodz, "wypadkowe", "1" if doc.ubezpieczenie_wypadkowe else "0")
    _e(rodz, "zdrowotne", "1" if doc.ubezpieczenie_zdrowotne else "0")


def _build_zwua(parent: etree._Element, doc: ZwuaInput) -> None:
    """Wyrejestrowanie z ubezpieczeń (ZWUA → element ZUSZWUA in XSD)."""
    zwua = _e(parent, "ZUSZWUA")
    _build_dane_platnika(zwua, doc.payer)
    _build_dane_ubezpieczonego(zwua, doc.insured)
    wy = _e(zwua, "wyrejestrowanie")
    _e(wy, "kod_tytulu", doc.kod_tytulu_ubezpieczenia)
    _e(wy, "data", _format_date(doc.data_wyrejestrowania))
    _e(wy, "kod_przyczyny", doc.kod_przyczyny_wyrejestrowania)


def _build_ziua(parent: etree._Element, doc: ZiuaInput) -> None:
    """Zmiana danych identyfikacyjnych ubezpieczonego (ZIUA → element ZUSZIUA in XSD)."""
    ziua = _e(parent, "ZUSZIUA")
    _build_dane_platnika(ziua, doc.payer)
    o = _e(ziua, "stare_dane_ubezpieczonego")
    _build_dane_ubezpieczonego(o, doc.old)
    n = _e(ziua, "nowe_dane_ubezpieczonego")
    _build_dane_ubezpieczonego(n, doc.new)


def _build_zcna(parent: etree._Element, doc: ZcnaInput) -> None:
    """Zgłoszenie członka rodziny (ZCNA → element ZUSZCNA in XSD)."""
    zcna = _e(parent, "ZUSZCNA")
    _build_dane_platnika(zcna, doc.payer)
    u = _e(zcna, "ubezpieczony")
    _build_dane_ubezpieczonego(u, doc.insured)
    fm = _e(zcna, "czlonek_rodziny")
    _build_dane_ubezpieczonego(fm, doc.family_member)
    _e(fm, "stopien_pokrewienstwa", doc.stopien_pokrewienstwa)
    _e(fm, "data_powstania_uprawnienia", _format_date(doc.data_powstania_uprawnienia))


def _build_dra(parent: etree._Element, doc: DraInput) -> None:
    """Deklaracja rozliczeniowa (DRA → element ZUSDRA in XSD).

    NOTE: Inner DRA section structure (sections I-XIII with positional <p1>...<pN>
    fields) is iterative work — see EWD spec Załącznik 1. v0.1.0 produces an
    envelope-valid XML; full DRA section mapping is tracked for v0.2.0.
    """
    dra = _e(parent, "ZUSDRA")
    _build_dane_platnika(dra, doc.payer)

    ident = _e(dra, "identyfikator_deklaracji")
    _e(ident, "p1", f"{doc.identyfikator_deklaracji:02d}")
    _e(ident, "p2", doc.period.strftime("%m.%Y"))

    skl = _e(dra, "skladki_lacznie")
    _e(skl, "emerytalne", f"{doc.skladka_emerytalna:.2f}")
    _e(skl, "rentowe", f"{doc.skladka_rentowa:.2f}")
    _e(skl, "chorobowe", f"{doc.skladka_chorobowa:.2f}")
    _e(skl, "wypadkowe", f"{doc.skladka_wypadkowa:.2f}")
    _e(skl, "zdrowotne", f"{doc.skladka_zdrowotna:.2f}")
    _e(skl, "FP", f"{doc.skladka_fp:.2f}")
    _e(skl, "FGSP", f"{doc.skladka_fgsp:.2f}")
    _e(skl, "FS", f"{doc.skladka_fs:.2f}")

    _e(dra, "liczba_ubezpieczonych", str(doc.liczba_ubezpieczonych))


_BUILDERS = {
    DraInput: _build_dra,
    ZuaInput: _build_zua,
    ZwuaInput: _build_zwua,
    ZiuaInput: _build_ziua,
    ZcnaInput: _build_zcna,
}


def build_kedu(
    documents: list[DraInput | ZuaInput | ZwuaInput | ZiuaInput | ZcnaInput],
    *,
    program: Program | None = None,
    sender_idp: str | None = None,
    pretty: bool = True,
) -> bytes:
    """Build a complete KEDU 5.6 XML document.

    Args:
        documents: list of typed document inputs (DraInput, ZuaInput, etc.).
        program: software metadata for naglowek_KEDU.
        sender_idp: optional IDP identifier of the sender (max 24 chars).
        pretty: pretty-print output.

    Returns:
        UTF-8 encoded XML bytes ready for XSD validation and signing.
    """
    if not documents:
        raise ValueError("KEDU must contain at least one document")

    program = program or Program()

    root = etree.Element(_qn("KEDU"), nsmap=NSMAP)
    root.set("wersja_schematu", "1")
    _build_naglowek(root, program, sender_idp)

    # Documents go DIRECTLY under <KEDU> (no <dokumenty> wrapper) per XSD t_KEDU.
    for doc in documents:
        builder = _BUILDERS.get(type(doc))
        if builder is None:
            raise TypeError(f"No builder registered for {type(doc).__name__}")
        builder(root, doc)

    return etree.tostring(
        root,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=pretty,
    )


def kedu_digest(xml_bytes: bytes) -> str:
    """SHA-256 digest of KEDU XML — 'skrot_KEDU' field used by ZUS."""
    return hashlib.sha256(xml_bytes).hexdigest()


__all__ = [
    "KEDU_NS",
    "build_kedu",
    "kedu_digest",
]
