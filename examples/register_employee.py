"""Example: generate ZUA for a new employee."""
from __future__ import annotations

from datetime import date

from mcp_zus.kedu.builder import build_kedu
from mcp_zus.kedu.models import Insured, Payer, ZuaInput


def main() -> None:
    payer = Payer(nip="1234563218", nazwa_skrocona="ACME Sp. z o.o.")
    employee = Insured(
        pesel="44051401359",
        nazwisko="Nowak",
        imie_pierwsze="Anna",
        data_urodzenia=date(1985, 3, 12),
    )
    zua = ZuaInput(
        payer=payer,
        insured=employee,
        kod_tytulu_ubezpieczenia="0110",  # umowa o pracę
        data_powstania_obowiazku=date(2026, 5, 1),
        ubezpieczenie_chorobowe=True,
    )
    xml = build_kedu([zua])
    print(xml.decode("utf-8"))


if __name__ == "__main__":
    main()
