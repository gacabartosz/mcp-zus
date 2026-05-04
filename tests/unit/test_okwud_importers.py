"""Unit tests — OK-WUD importers (CSV, XLSX, XML, ODS, XLS)."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from mcp_zus.okwud.importers import (
    import_from_csv,
    import_from_xml,
    import_subjects,
)


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "podmioty.csv"
    with p.open("w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            [
                "LP",
                "SYGNATURA_SPRAWY",
                "NAZWA_SKROCONA",
                "NIP",
                "PESEL",
                "IMIE",
                "NAZWISKO",
            ]
        )
        writer.writerow(["1", "I C 100/26", "ACME", "1234563218", "", "", ""])
        writer.writerow(["2", "I C 101/26", "", "", "44051401359", "Jan", "Kowalski"])
    return p


def test_import_from_csv_basic(sample_csv: Path):
    podmioty = import_from_csv(sample_csv)
    assert len(podmioty) == 2
    assert podmioty[0].nazwa_skrocona == "ACME"
    assert podmioty[0].nip == "1234563218"
    assert podmioty[1].pesel == "44051401359"
    assert podmioty[1].imie == "Jan"
    assert podmioty[1].nazwisko == "Kowalski"


def test_import_subjects_auto_detects(sample_csv: Path):
    podmioty = import_subjects(sample_csv)
    assert len(podmioty) == 2


def test_import_subjects_unsupported_raises(tmp_path: Path):
    bad = tmp_path / "x.txt"
    bad.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported"):
        import_subjects(bad)


def test_import_from_xml(tmp_path: Path):
    xml_doc = tmp_path / "podmioty.xml"
    xml_doc.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<podmioty>
  <podmiot>
    <nip>1234563218</nip>
    <nazwa_skrocona>ACME</nazwa_skrocona>
  </podmiot>
  <podmiot>
    <pesel>44051401359</pesel>
    <imie>Jan</imie>
    <nazwisko>Kowalski</nazwisko>
  </podmiot>
</podmioty>
""",
        encoding="utf-8",
    )
    podmioty = import_from_xml(xml_doc)
    assert len(podmioty) == 2


def test_import_from_xlsx_using_zus_template():
    """If ZUS template exists in docs/source, smoke-test importing from it."""
    template = Path(__file__).parents[2] / "docs" / "source" / "zus-bartosz-materials" / "Szablony - import" / "OK-WUD_szablon_importu_XLSX.xlsx"
    if not template.exists():
        pytest.skip("ZUS XLSX template not in docs/source")
    from mcp_zus.okwud.importers import import_from_xlsx
    podmioty = import_from_xlsx(template)
    # Template likely has 0 data rows but valid headers
    assert isinstance(podmioty, list)
