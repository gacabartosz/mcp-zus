"""KEDU 5.6 XSD validator (lxml)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from lxml import etree
from pydantic import BaseModel

_SCHEMAS_DIR = Path(__file__).parent / "schemas"
_XSD_PATH = _SCHEMAS_DIR / "kedu_5_6.xsd"
_XMLDSIG_LOCAL = _SCHEMAS_DIR / "xmldsig-core-schema.xsd"

# Map remote schema URLs to local cached copies — avoids network during validation.
_LOCAL_SCHEMA_MAP = {
    "http://www.w3.org/TR/xmldsig-core/xmldsig-core-schema.xsd": _XMLDSIG_LOCAL,
    "http://www.w3.org/TR/2002/REC-xmldsig-core-20020212/xmldsig-core-schema.xsd": _XMLDSIG_LOCAL,
    "http://www.w3.org/2001/XMLSchema.dtd": None,  # ignore DTD references
}


class KeduValidationError(ValueError):
    """Raised when KEDU XML fails XSD validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(f"KEDU validation failed with {len(errors)} error(s):\n" + "\n".join(errors))


class ValidationReport(BaseModel):
    valid: bool
    errors: list[str]


class _LocalSchemaResolver(etree.Resolver):
    """Redirect remote schema imports (xmldsig) to local cached copies."""

    def resolve(self, system_url, public_id, context):  # type: ignore[override]
        if system_url in _LOCAL_SCHEMA_MAP:
            local = _LOCAL_SCHEMA_MAP[system_url]
            if local is None:
                return self.resolve_string("", context)
            return self.resolve_filename(str(local), context)
        return None


@lru_cache(maxsize=1)
def _load_schema() -> etree.XMLSchema:
    """Load and cache compiled XSD schema with local xmldsig resolution."""
    if not _XSD_PATH.exists():
        raise FileNotFoundError(
            f"KEDU XSD not found at {_XSD_PATH}. Run: "
            f"curl -fsSL https://bip.zus.pl/documents/493361/11959946/kedu_5_6.xsd -o {_XSD_PATH}"
        )
    parser = etree.XMLParser(load_dtd=False, no_network=True)
    parser.resolvers.add(_LocalSchemaResolver())
    schema_doc = etree.parse(str(_XSD_PATH), parser)
    return etree.XMLSchema(schema_doc)


def validate_kedu(xml: bytes | str | etree._Element, *, raise_on_error: bool = False) -> ValidationReport:
    """Validate KEDU XML against the official XSD schema.

    Args:
        xml: raw bytes, decoded string, or already-parsed lxml Element.
        raise_on_error: if True, raises KeduValidationError on failure;
            otherwise returns a ValidationReport.

    Returns:
        ValidationReport with `valid` flag and list of error strings.
    """
    if isinstance(xml, etree._Element):
        doc = etree.ElementTree(xml)
    elif isinstance(xml, bytes):
        doc = etree.fromstring(xml).getroottree()
    else:
        doc = etree.fromstring(xml.encode("utf-8")).getroottree()

    schema = _load_schema()
    if schema.validate(doc):
        return ValidationReport(valid=True, errors=[])

    errors = [f"line {e.line}: {e.message}" for e in schema.error_log]
    if raise_on_error:
        raise KeduValidationError(errors)
    return ValidationReport(valid=False, errors=errors)


__all__ = ["KeduValidationError", "ValidationReport", "validate_kedu"]
