"""Unit tests — OK-WUD słownik kodów instytucji."""
from __future__ import annotations

from mcp_zus.okwud.kody_instytucji import KODY_INSTYTUCJI, describe_kod, is_valid_kod


def test_dictionary_has_known_codes():
    assert "KS" in KODY_INSTYTUCJI
    assert "S" in KODY_INSTYTUCJI
    assert "NFZ" in KODY_INSTYTUCJI
    assert "POLICJA" in KODY_INSTYTUCJI
    assert "KAS" in KODY_INSTYTUCJI


def test_is_valid_kod():
    assert is_valid_kod("KS")
    assert is_valid_kod("NFZ")
    assert not is_valid_kod("INVALID_CODE")


def test_describe_kod():
    assert describe_kod("KS") == "Komornik Sądowy"
    assert describe_kod("NIK") == "Najwyższa Izba Kontroli"
    assert describe_kod("UNKNOWN") is None


def test_dictionary_size():
    # 60+ kodów wg dokumentacji
    assert len(KODY_INSTYTUCJI) >= 50
