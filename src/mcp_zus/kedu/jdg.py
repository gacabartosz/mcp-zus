"""High-level builder for self-employed monthly settlement (JDG / B2B sole-trader).

Wraps KEDU `build_kedu` with sensible defaults for one-person businesses,
covering the most common case: monthly DRA with own-contributions only,
no employees, no benefits.
"""
from __future__ import annotations

from mcp_zus.kedu.builder import build_kedu
from mcp_zus.kedu.models import DraInput, JdgMonthlyInput, Program

# Stawki ustawowe — % od podstawy. Aktualne dla 2026; do utrzymania w `data/` w v0.2.
RATE_EMERYTALNE = 0.1952  # 19.52%
RATE_RENTOWE = 0.08  # 8%
RATE_CHOROBOWE = 0.0245  # 2.45%
RATE_WYPADKOWE = 0.0167  # 1.67% (stawka standardowa, można nadpisać)
RATE_FP_FS = 0.0245  # 2.45% Fundusz Pracy + Solidarnościowy
RATE_ZDROWOTNA = 0.09  # 9% — uwaga: różne podstawy w MZP

# Podstawy minimalne — APROKSYMACJA dla 2026 (w produkcji: ciągnij z GUS lub KSI).
# To są PRZYBLIŻENIA: rzeczywiste wartości muszą być pobierane z aktualnego komunikatu Prezesa GUS.
PODSTAWA_STANDARD_2026 = 4694.40  # 60% przeciętnego wynagrodzenia (przybliżenie)
PODSTAWA_PREFERENCYJNA_2026 = 1395.00  # 30% minimalnego wynagrodzenia (przybliżenie)
PODSTAWA_ZDROWOTNA_RYCZALT_NISKI_2026 = 4694.40  # podstawa zryczałtowana (przybliżenie)


def _resolve_basis(input: JdgMonthlyInput) -> float:
    if input.podstawa_skladki is not None:
        return input.podstawa_skladki

    match input.basis_kind:
        case "preferencyjna":
            return PODSTAWA_PREFERENCYJNA_2026
        case "ulga_na_start":
            return 0.0  # tylko składka zdrowotna
        case "maly_zus_plus":
            return PODSTAWA_PREFERENCYJNA_2026  # placeholder — wymaga indywidualnego wyliczenia
        case _:
            return PODSTAWA_STANDARD_2026


def build_jdg_monthly(input: JdgMonthlyInput, *, program: Program | None = None) -> bytes:
    """Generate a single-document KEDU 5.6 (DRA) for a self-employed person.

    NOTE: Składki są przybliżone — produkcyjnie wymaga aktualnych podstaw z GUS
    i indywidualnego wyliczenia dla MZP. Wynik MUSI zostać zwalidowany przez usera.
    """
    basis = _resolve_basis(input)

    if input.basis_kind == "ulga_na_start":
        skladka_emer = 0.0
        skladka_rent = 0.0
        skladka_chor = 0.0
        skladka_wyp = 0.0
        fp_fs = 0.0
    else:
        skladka_emer = round(basis * RATE_EMERYTALNE, 2)
        skladka_rent = round(basis * RATE_RENTOWE, 2)
        skladka_chor = round(basis * RATE_CHOROBOWE, 2) if input.chorobowe else 0.0
        skladka_wyp = round(basis * RATE_WYPADKOWE, 2)
        fp_fs = round(basis * RATE_FP_FS, 2) if input.fp_fs else 0.0

    skladka_zdr = round(PODSTAWA_ZDROWOTNA_RYCZALT_NISKI_2026 * RATE_ZDROWOTNA, 2)

    dra = DraInput(
        payer=input.payer,
        period=input.period.replace(day=1),
        skladka_emerytalna=skladka_emer,
        skladka_rentowa=skladka_rent,
        skladka_chorobowa=skladka_chor,
        skladka_wypadkowa=skladka_wyp,
        skladka_zdrowotna=skladka_zdr,
        skladka_fp=fp_fs,
        skladka_fgsp=0.0,
        skladka_fs=0.0,
        liczba_ubezpieczonych=1,
    )

    return build_kedu([dra], program=program)


__all__ = ["build_jdg_monthly"]
