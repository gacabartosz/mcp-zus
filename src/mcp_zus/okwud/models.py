"""Pydantic models for OK-WUD inputs."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from mcp_zus.okwud.kody_instytucji import is_valid_kod

RodzajDokumentuTozsamosci = Literal[1, 2]  # 1 = dowód osobisty, 2 = paszport


class DaneIdentyfikacyjneWnioskodawcy(BaseModel):
    """Identifying data of the requesting institution."""

    nazwa_skrocona: str = Field(max_length=128)
    nip: str | None = Field(default=None, max_length=10)
    regon: str | None = Field(default=None)


class DaneAdresoweWnioskodawcy(BaseModel):
    kod_pocztowy: str
    miejscowosc: str = Field(max_length=26)
    numer_domu: str = Field(max_length=10)
    ulica: str | None = Field(default=None, max_length=65)
    numer_lokalu: str | None = Field(default=None, max_length=7)
    panstwo: str = "Polska"


class RodzajWnioskodawcy(BaseModel):
    """One of the institution codes from kody_instytucji.py."""

    rodzaj_kod: str | None = None  # np. KS, S, NFZ, OPS — patrz kody_instytucji
    rodzaj_inny: str | None = None  # gdy nie pasuje żaden kod

    @field_validator("rodzaj_kod")
    @classmethod
    def _check_kod(cls, v: str | None) -> str | None:
        if v is not None and not is_valid_kod(v):
            raise ValueError(
                f"Unknown kod instytucji '{v}'. Valid: see okwud.kody_instytucji.KODY_INSTYTUCJI"
            )
        return v


class PodmiotUdostepnioneDane(BaseModel):
    """Subject whose data is requested (osoba fizyczna lub firma)."""

    sygnatura_sprawy: str | None = Field(default=None, max_length=128)
    # Osoba fizyczna
    imie: str | None = Field(default=None, max_length=22)
    nazwisko: str | None = Field(default=None, max_length=31)
    pesel: str | None = Field(default=None, max_length=11)
    rodzaj_dokumentu_tozsamosci: RodzajDokumentuTozsamosci | None = None
    numer_dokumentu_tozsamosci: str | None = Field(default=None, max_length=15)
    data_urodzenia: date | None = None
    # Firma
    nazwa_skrocona: str | None = Field(default=None, max_length=128)
    nazwa_pelna: str | None = Field(default=None, max_length=100)
    nip: str | None = Field(default=None, max_length=10)
    regon: str | None = Field(default=None, max_length=14)
    # Adres
    kod_pocztowy: str | None = None
    miejscowosc: str | None = Field(default=None, max_length=26)
    ulica: str | None = Field(default=None, max_length=65)
    nr_domu: str | None = Field(default=None, max_length=10)
    nr_lokalu: str | None = Field(default=None, max_length=7)


class ZakresZadanychDanych(BaseModel):
    """What categories of data are requested."""

    dane_identyfikacyjne: bool = False
    okresy_ubezpieczenia: bool = False
    podstawy_wymiaru: bool = False
    swiadczenia: bool = False
    skladki: bool = False
    inne: str | None = None


class OkwudRequest(BaseModel):
    """Full OK-WUD application input."""

    cid: str = Field(max_length=64)  # unikalny identyfikator wniosku
    wnioskodawca_dane: DaneIdentyfikacyjneWnioskodawcy
    wnioskodawca_adres: DaneAdresoweWnioskodawcy
    rodzaj_wnioskodawcy: RodzajWnioskodawcy
    przeznaczenie_danych: str
    podstawa_prawna: list[str] = Field(default_factory=list)
    podmioty: list[PodmiotUdostepnioneDane]
    zakres: ZakresZadanychDanych
    data_wniosku: date


__all__ = [
    "DaneAdresoweWnioskodawcy",
    "DaneIdentyfikacyjneWnioskodawcy",
    "OkwudRequest",
    "PodmiotUdostepnioneDane",
    "RodzajDokumentuTozsamosci",
    "RodzajWnioskodawcy",
    "ZakresZadanychDanych",
]
