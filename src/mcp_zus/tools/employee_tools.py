"""MCP tools — high-level employee orchestrators (KEDU + EWD)."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from mcp_zus.kedu.builder import build_kedu
from mcp_zus.kedu.models import (
    Insured,
    Payer,
    ZcnaInput,
    ZiuaInput,
    ZuaInput,
    ZwuaInput,
)


class RegisterEmployeeInput(BaseModel):
    payer: Payer
    employee: Insured
    kod_tytulu: str
    data_powstania: date
    chorobowe: bool = True


class EmployeeOpResponse(BaseModel):
    xml: str
    document_kind: str
    note: str


def tool_register_employee(input: RegisterEmployeeInput) -> EmployeeOpResponse:
    """Generate ZUA (registration) for a new employee."""
    doc = ZuaInput(
        payer=input.payer,
        insured=input.employee,
        kod_tytulu_ubezpieczenia=input.kod_tytulu,
        data_powstania_obowiazku=input.data_powstania,
        ubezpieczenie_chorobowe=input.chorobowe,
    )
    xml = build_kedu([doc])
    return EmployeeOpResponse(
        xml=xml.decode("utf-8"),
        document_kind="ZUA",
        note="Zgłoszenie wymaga podpisu kwalifikowanego płatnika i wysyłki przez EWD lub PUE.",
    )


class DeregisterEmployeeInput(BaseModel):
    payer: Payer
    employee: Insured
    kod_tytulu: str
    data_wyrejestrowania: date
    kod_przyczyny: str  # 100, 600, 800 — patrz słowniki ZUS


def tool_deregister_employee(input: DeregisterEmployeeInput) -> EmployeeOpResponse:
    doc = ZwuaInput(
        payer=input.payer,
        insured=input.employee,
        kod_tytulu_ubezpieczenia=input.kod_tytulu,
        data_wyrejestrowania=input.data_wyrejestrowania,
        kod_przyczyny_wyrejestrowania=input.kod_przyczyny,
    )
    xml = build_kedu([doc])
    return EmployeeOpResponse(
        xml=xml.decode("utf-8"),
        document_kind="ZWUA",
        note="Wyrejestrowanie wymaga podpisu kwalifikowanego płatnika.",
    )


class UpdateEmployeeInput(BaseModel):
    payer: Payer
    old: Insured
    new: Insured


def tool_update_employee(input: UpdateEmployeeInput) -> EmployeeOpResponse:
    doc = ZiuaInput(payer=input.payer, old=input.old, new=input.new)
    xml = build_kedu([doc])
    return EmployeeOpResponse(
        xml=xml.decode("utf-8"),
        document_kind="ZIUA",
        note="Zmiana danych ubezpieczonego — wymaga podpisu kwalifikowanego.",
    )


class AddFamilyMemberInput(BaseModel):
    payer: Payer
    employee: Insured
    family_member: Insured
    stopien_pokrewienstwa: str
    data_powstania_uprawnienia: date


def tool_add_family_member(input: AddFamilyMemberInput) -> EmployeeOpResponse:
    doc = ZcnaInput(
        payer=input.payer,
        insured=input.employee,
        family_member=input.family_member,
        stopien_pokrewienstwa=input.stopien_pokrewienstwa,
        data_powstania_uprawnienia=input.data_powstania_uprawnienia,
    )
    xml = build_kedu([doc])
    return EmployeeOpResponse(
        xml=xml.decode("utf-8"),
        document_kind="ZCNA",
        note="Zgłoszenie członka rodziny do ubezpieczenia zdrowotnego.",
    )


__all__ = [
    "tool_add_family_member",
    "tool_deregister_employee",
    "tool_register_employee",
    "tool_update_employee",
]
