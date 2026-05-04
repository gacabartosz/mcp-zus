"""Example: generate monthly DRA for a self-employed JDG.

Run:
    uv run python examples/jdg_monthly_dra.py

Output: walidowany KEDU 5.6 XML wypisany na stdout. Podpisz lokalnie i
prześlij przez PUE/EWD.
"""
from __future__ import annotations

from datetime import date

from mcp_zus.kedu.jdg import build_jdg_monthly
from mcp_zus.kedu.models import JdgMonthlyInput, Payer


def main() -> None:
    payer = Payer(
        nip="1234563218",
        nazwa_skrocona="Bartosz Gaca JDG",
    )
    inp = JdgMonthlyInput(
        payer=payer,
        period=date(2026, 5, 1),
        basis_kind="standard",
        chorobowe=True,
    )
    xml = build_jdg_monthly(inp)
    print(xml.decode("utf-8"))


if __name__ == "__main__":
    main()
