"""ePUAP SOAP client (skeleton).

Spec: epuap.gov.pl/wps/wcm/connect/epuap2/.../specyfikacja_interfejsow_wsdl
Skrzynka ZUS: `/ZUS/esp`
"""
from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_ZUS_ESP = "/ZUS/esp"


@dataclass(slots=True)
class EpuapClientConfig:
    wsdl_url: str
    podmiot_id: str
    target_esp: str = DEFAULT_ZUS_ESP
    cert_path: str | None = None

    @classmethod
    def from_env(cls) -> EpuapClientConfig:
        return cls(
            wsdl_url=os.getenv("ZUS_EPUAP_WSDL_URL", ""),
            podmiot_id=os.getenv("ZUS_EPUAP_PODMIOT_ID", ""),
            target_esp=os.getenv("ZUS_EPUAP_TARGET_ESP", DEFAULT_ZUS_ESP),
            cert_path=os.getenv("ZUS_EPUAP_CERT_PATH"),
        )


class EpuapClient:
    """ePUAP transport — sends signed XMLs to /ZUS/esp via WS-Skrytka."""

    def __init__(self, config: EpuapClientConfig | None = None) -> None:
        self.config = config or EpuapClientConfig.from_env()

    def send_to_zus(self, signed_xml: bytes, document_kind: str) -> dict:
        """Send a signed XML to ZUS via ePUAP. Returns message id + UPP id."""
        raise NotImplementedError(
            "Wire up zeep with WS-Security + MAC-issued certificate. "
            "See ePUAP integration guide in docs/source/."
        )

    def fetch_upp(self, message_id: str) -> bytes:
        raise NotImplementedError("Implement after configuring MAC certificate.")

    def list_inbox(self) -> list[dict]:
        raise NotImplementedError("Implement after configuring MAC certificate.")


__all__ = ["EpuapClient", "EpuapClientConfig"]
