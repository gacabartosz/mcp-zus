"""Unit tests — KEDU pydantic models (NIP/PESEL validation)."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_zus.kedu.models import Insured, Payer

# Valid Polish test NIPs (real-format checksums)
VALID_NIP = "1234563218"  # checksum-valid


def test_payer_valid_nip():
    p = Payer(nip=VALID_NIP, nazwa_skrocona="ACME Sp. z o.o.")
    assert p.nip == VALID_NIP


def test_payer_invalid_nip_length():
    with pytest.raises(ValidationError):
        Payer(nip="123", nazwa_skrocona="X")


def test_payer_invalid_nip_checksum():
    with pytest.raises(ValidationError):
        Payer(nip="1234567890", nazwa_skrocona="X")


def test_insured_valid_pesel():
    # Valid PESEL: 44051401359 (checksum-correct)
    ins = Insured(pesel="44051401359", nazwisko="Kowalski", imie_pierwsze="Jan")
    assert ins.pesel == "44051401359"


def test_insured_invalid_pesel():
    with pytest.raises(ValidationError):
        Insured(pesel="12345678901", nazwisko="X", imie_pierwsze="Y")


def test_insured_no_pesel_ok():
    ins = Insured(nazwisko="Nowak", imie_pierwsze="Anna")
    assert ins.pesel is None
