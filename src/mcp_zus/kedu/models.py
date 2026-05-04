"""Pydantic models for KEDU document inputs (LLM-facing schema).

These are the high-level shapes that LLM (or human) provides; the builder
converts them to XSD-conformant KEDU 5.6 XML.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def _validate_nip(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) != 10:
        raise ValueError(f"NIP must be 10 digits, got {len(digits)}")
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    checksum = sum(int(d) * w for d, w in zip(digits[:9], weights, strict=True)) % 11
    if checksum == 10:
        raise ValueError("Invalid NIP — checksum failed")
    if checksum != int(digits[9]):
        raise ValueError("Invalid NIP — checksum digit mismatch")
    return digits


def _validate_pesel(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) != 11:
        raise ValueError(f"PESEL must be 11 digits, got {len(digits)}")
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = (10 - sum(int(d) * w for d, w in zip(digits[:10], weights, strict=True)) % 10) % 10
    if checksum != int(digits[10]):
        raise ValueError("Invalid PESEL — checksum digit mismatch")
    return digits


class Program(BaseModel):
    """Producent / wersja oprogramowania zgłoszone w nagłówku KEDU."""

    producent: str = "mcp-zus"
    symbol: str = "MCP-ZUS"
    wersja: str = "0.1.0"


class Payer(BaseModel):
    """Płatnik składek (sender of KEDU)."""

    nip: str
    nazwa_skrocona: str = Field(max_length=31)
    nazwa_pelna: str | None = Field(default=None, max_length=200)
    regon: str | None = None
    numer_zus: str | None = None  # IDP — identyfikator płatnika ZUS

    @field_validator("nip")
    @classmethod
    def _check_nip(cls, v: str) -> str:
        return _validate_nip(v)


class Insured(BaseModel):
    """Osoba ubezpieczona (employee / self-employed person)."""

    pesel: str | None = None
    nip: str | None = None
    nazwisko: str = Field(max_length=31)
    imie_pierwsze: str = Field(max_length=22)
    imie_drugie: str | None = Field(default=None, max_length=22)
    data_urodzenia: date | None = None
    obywatelstwo: str = "PL"

    @field_validator("pesel")
    @classmethod
    def _check_pesel(cls, v: str | None) -> str | None:
        return _validate_pesel(v) if v else None


class ZuaInput(BaseModel):
    """Zgłoszenie do ubezpieczeń (ZUA — registration)."""

    payer: Payer
    insured: Insured
    kod_tytulu_ubezpieczenia: str = Field(min_length=4, max_length=6)
    data_powstania_obowiazku: date
    kod_pracy_szczegolnej: str | None = None
    ubezpieczenie_emerytalne: bool = True
    ubezpieczenie_rentowe: bool = True
    ubezpieczenie_chorobowe: bool = False
    ubezpieczenie_wypadkowe: bool = True
    ubezpieczenie_zdrowotne: bool = True


class ZwuaInput(BaseModel):
    """Wyrejestrowanie z ubezpieczeń (ZWUA)."""

    payer: Payer
    insured: Insured
    kod_tytulu_ubezpieczenia: str = Field(min_length=4, max_length=6)
    data_wyrejestrowania: date
    kod_przyczyny_wyrejestrowania: str = Field(min_length=3, max_length=3)


class ZiuaInput(BaseModel):
    """Zmiana danych identyfikacyjnych ubezpieczonego (ZIUA)."""

    payer: Payer
    old: Insured
    new: Insured


class ZcnaInput(BaseModel):
    """Zgłoszenie członka rodziny do ubezpieczenia zdrowotnego (ZCNA)."""

    payer: Payer
    insured: Insured  # ubezpieczony — pracownik
    family_member: Insured
    stopien_pokrewienstwa: str = Field(min_length=2, max_length=2)
    data_powstania_uprawnienia: date


class DraInput(BaseModel):
    """Deklaracja rozliczeniowa (DRA)."""

    payer: Payer
    period: date  # pierwszy dzień miesiąca rozliczeniowego (np. 2026-05-01)
    identyfikator_deklaracji: int = Field(ge=1, le=89, default=1)  # 1 dla podstawowej

    # Sumy składek (PLN, gr precision = 2 miejsca po przecinku)
    skladka_emerytalna: float = 0.0
    skladka_rentowa: float = 0.0
    skladka_chorobowa: float = 0.0
    skladka_wypadkowa: float = 0.0
    skladka_zdrowotna: float = 0.0
    skladka_fp: float = 0.0  # Fundusz Pracy
    skladka_fgsp: float = 0.0  # Fundusz Gwarantowanych Świadczeń Pracowniczych
    skladka_fs: float = 0.0  # Fundusz Solidarnościowy

    # Liczba ubezpieczonych
    liczba_ubezpieczonych: int = Field(default=1, ge=0)


class JdgMonthlyInput(BaseModel):
    """High-level: comprehensive monthly DRA for a self-employed person (JDG).

    Generates DRA + RCA for samozatrudniony — covering own contributions.
    """

    payer: Payer
    period: date  # pierwszy dzień miesiąca rozliczeniowego
    basis_kind: Literal["preferencyjna", "ulga_na_start", "maly_zus_plus", "standard"] = "standard"
    podstawa_skladki: float | None = None  # jeśli None, wyliczany z basis_kind + GUS
    chorobowe: bool = False
    fp_fs: bool = True  # Fundusz Pracy + Solidarnościowy (zwykle TAK powyżej minimalnej)


__all__ = [
    "DraInput",
    "Insured",
    "JdgMonthlyInput",
    "Payer",
    "Program",
    "ZcnaInput",
    "ZiuaInput",
    "ZuaInput",
    "ZwuaInput",
]
