"""EWD SOAP client (skeleton — production requires ZUS accreditation)."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class EwdClientConfig:
    wsdl_url: str
    basic_user: str
    basic_pass: str
    cert_path: str | None = None

    @classmethod
    def from_env(cls) -> EwdClientConfig:
        return cls(
            wsdl_url=os.getenv("ZUS_EWD_WSDL_URL", ""),
            basic_user=os.getenv("ZUS_EWD_BASIC_USER", ""),
            basic_pass=os.getenv("ZUS_EWD_BASIC_PASS", ""),
            cert_path=os.getenv("ZUS_EWD_CERT_PATH"),
        )


class EwdClient:
    """SOAP client for ZUS EWD.

    Specification: BIP ZUS — `EWD_Specyfikacja_We_Wy_2.16.pdf`.
    """

    def __init__(self, config: EwdClientConfig | None = None) -> None:
        self.config = config or EwdClientConfig.from_env()
        if not self.config.wsdl_url:
            raise ValueError(
                "ZUS_EWD_WSDL_URL not set. EWD requires accreditation — "
                "ZUS issues the WSDL URL together with the certificate."
            )

    def send(self, signed_kedu_xml: bytes) -> dict:
        """Send a signed KEDU XML zestaw to ZUS. Returns reference + initial status."""
        raise NotImplementedError(
            "EWD send() requires production ZUS accreditation. "
            "Wire up zeep transport with WS-Security and certificate-bound TLS."
        )

    def get_status(self, reference: str) -> dict:
        raise NotImplementedError("Implement after accreditation.")

    def fetch_upo(self, reference: str) -> bytes:
        raise NotImplementedError("Implement after accreditation.")


__all__ = ["EwdClient", "EwdClientConfig"]
