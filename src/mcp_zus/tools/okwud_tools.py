"""MCP tools — OK-WUD module."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from mcp_zus.okwud.builder import build_okwud
from mcp_zus.okwud.importers import import_subjects
from mcp_zus.okwud.kody_instytucji import KODY_INSTYTUCJI
from mcp_zus.okwud.models import OkwudRequest, PodmiotUdostepnioneDane


class BuildOkwudResponse(BaseModel):
    xml: str
    podmioty_count: int


def tool_build_okwud(input: OkwudRequest) -> BuildOkwudResponse:
    xml = build_okwud(input)
    return BuildOkwudResponse(xml=xml.decode("utf-8"), podmioty_count=len(input.podmioty))


class ImportSubjectsInput(BaseModel):
    file_path: str


class ImportSubjectsResponse(BaseModel):
    podmioty: list[PodmiotUdostepnioneDane]
    count: int


def tool_import_subjects(input: ImportSubjectsInput) -> ImportSubjectsResponse:
    podmioty = import_subjects(Path(input.file_path))
    return ImportSubjectsResponse(podmioty=podmioty, count=len(podmioty))


def tool_list_kody_instytucji() -> dict[str, str]:
    return KODY_INSTYTUCJI


__all__ = [
    "tool_build_okwud",
    "tool_import_subjects",
    "tool_list_kody_instytucji",
]
