"""OK-WUD SOAP client — zeep + WS-Security + HTTP Basic.

Endpoint (production): https://pue.zus.pl:8100/ws/zus.channel.pub:wsdlPub
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from mcp_zus.okwud import OKWUD_PROD_WSDL
from mcp_zus.okwud.session import SessionPayload, SessionToken


@dataclass(slots=True)
class OkwudClientConfig:
    wsdl_url: str
    basic_user: str
    basic_pass: str
    cert_path: str | None = None  # opcjonalny cert ZUS dla mTLS

    @classmethod
    def from_env(cls) -> OkwudClientConfig:
        return cls(
            wsdl_url=os.getenv("ZUS_OKWUD_WSDL_URL", OKWUD_PROD_WSDL),
            basic_user=os.getenv("ZUS_OKWUD_BASIC_USER", ""),
            basic_pass=os.getenv("ZUS_OKWUD_BASIC_PASS", ""),
            cert_path=os.getenv("ZUS_OKWUD_CERT_PATH"),
        )


class OkwudClient:
    """SOAP client for `pue.zus.pl:8100/ws/zus.channel.pub`.

    NOTE: Production calls require:
      - HTTPS with valid TLS,
      - HTTP Basic auth (login/pass issued by ZUS),
      - WS-Security envelope signed with cert ZUS,
      - kwalifikowany podpis on each document and on the session oświadczenie.

    This implementation is a SCAFFOLD — fill in `_make_zeep_client()` once
    you have ZUS-issued credentials.
    """

    def __init__(self, config: OkwudClientConfig | None = None) -> None:
        self.config = config or OkwudClientConfig.from_env()
        self._client = None

    def _make_zeep_client(self):
        from requests import Session
        from requests.auth import HTTPBasicAuth
        from zeep import Client
        from zeep.transports import Transport

        session = Session()
        session.auth = HTTPBasicAuth(self.config.basic_user, self.config.basic_pass)
        if self.config.cert_path:
            session.cert = self.config.cert_path
        transport = Transport(session=session, timeout=30)
        return Client(self.config.wsdl_url, transport=transport)

    def pobierz_oswiadczenie(self) -> SessionPayload:
        """Step 1: fetch XML oświadczenia to be signed by user."""
        raise NotImplementedError(
            "Production WSDL operations require ZUS-issued credentials. "
            "Wire up `_make_zeep_client()` and call client.service.pobierzOswiadczenie()."
        )

    def otworz_sesje(self, signed_oswiadczenie: bytes) -> SessionToken:
        """Step 2: open session with signed oświadczenie."""
        raise NotImplementedError(
            "Wire up zeep client and call client.service.otworzSesje(signed_oswiadczenie)."
        )

    def wyslij_wniosek(self, signed_okwud_xml: bytes, session: SessionToken) -> dict:
        """Step 3: send signed OK-WUD request within an active session."""
        raise NotImplementedError(
            "Wire up zeep and call client.service.wyslijWniosek(xml, sessionToken)."
        )


__all__ = ["OkwudClient", "OkwudClientConfig"]
