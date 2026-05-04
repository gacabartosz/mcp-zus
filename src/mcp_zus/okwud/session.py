"""OK-WUD session protocol: pobierzOswiadczenie → BYO sign → openSession.

Per ZUS "Wytyczne techniczne":
    1. Wywołaj pobierzOswiadczenie → otrzymaj XML oświadczenia.
    2. Podpisz oświadczenie KWALIFIKOWANYM podpisem (po stronie usera).
    3. Wywołaj otworzSesje z podpisanym oświadczeniem → otrzymaj sessionToken.
    4. Każdy kolejny call używa sessionToken.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SessionPayload:
    """Oświadczenie XML otrzymane z ZUS — należy podpisać lokalnie."""

    oswiadczenie_xml: bytes
    correlation_id: str


@dataclass(slots=True)
class SessionToken:
    """Active OK-WUD session — pass to every subsequent SOAP call."""

    token: str
    expires_at: str  # ISO timestamp


__all__ = ["SessionPayload", "SessionToken"]
