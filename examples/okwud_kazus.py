"""Example: build an OK-WUD wniosek (court asking ZUS for data on a defendant)."""
from __future__ import annotations

from datetime import date

from mcp_zus.okwud.builder import build_okwud
from mcp_zus.okwud.models import (
    DaneAdresoweWnioskodawcy,
    DaneIdentyfikacyjneWnioskodawcy,
    OkwudRequest,
    PodmiotUdostepnioneDane,
    RodzajWnioskodawcy,
    ZakresZadanychDanych,
)


def main() -> None:
    req = OkwudRequest(
        cid="WNIO/2026/05/0042",
        wnioskodawca_dane=DaneIdentyfikacyjneWnioskodawcy(
            nazwa_skrocona="Sąd Rejonowy Wrocław-Krzyki",
            regon="000123456",
        ),
        wnioskodawca_adres=DaneAdresoweWnioskodawcy(
            kod_pocztowy="50-040",
            miejscowosc="Wrocław",
            numer_domu="12",
            ulica="Podwale",
        ),
        rodzaj_wnioskodawcy=RodzajWnioskodawcy(rodzaj_kod="S"),
        przeznaczenie_danych="Postępowanie sądowe — sygn. akt I C 123/26",
        podstawa_prawna=["art. 50 ust. 5 ustawy o systemie ubezpieczeń społecznych"],
        podmioty=[
            PodmiotUdostepnioneDane(
                imie="Jan",
                nazwisko="Kowalski",
                pesel="44051401359",
                kod_pocztowy="00-001",
                miejscowosc="Warszawa",
                ulica="Marszałkowska",
                nr_domu="1",
            ),
        ],
        zakres=ZakresZadanychDanych(
            okresy_ubezpieczenia=True,
            podstawy_wymiaru=True,
        ),
        data_wniosku=date(2026, 5, 4),
    )
    xml = build_okwud(req)
    print(xml.decode("utf-8"))


if __name__ == "__main__":
    main()
