"""OK-WUD — Wnioski Uprawnionych Instytucji o Udostępnienie Danych ZUS.

SOAP endpoint (production): https://pue.zus.pl:8100/ws/zus.channel.pub:wsdlPub
XSD: http://crd.gov.pl/wzor/2020/12/29/10229/schemat.xsd
"""
from __future__ import annotations

OKWUD_NS = "http://crd.gov.pl/wzor/2020/12/29/10229/"
OKWUD_PROD_WSDL = "https://pue.zus.pl:8100/ws/zus.channel.pub:wsdlPub"

__all__ = ["OKWUD_NS", "OKWUD_PROD_WSDL"]
