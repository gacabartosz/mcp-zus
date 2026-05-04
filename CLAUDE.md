# CLAUDE.md — mcp-zus

Pierwsze publiczne MCP dla **polskiego ZUS / PUE ZUS**. Pokrywa cztery kanały komunikacji + tryb "browser companion" do działającej sesji PUE.

## Build & Run

```bash
# Setup
uv sync --all-extras

# Run MCP server (stdio)
uv run mcp-zus

# Dev — MCP Inspector
uv run mcp dev src/mcp_zus/server.py

# Tests
uv run pytest tests/unit -v
uv run pytest tests/integration -v -m integration

# Lint + types
uv run ruff check src/ tests/
uv run mypy src/

# Verify tools list
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | uv run mcp-zus
```

## Architecture

`mcp-zus` jest **modular**: każdy kanał komunikacji to osobny pakiet z dedykowanymi narzędziami MCP. LLM widzi płaską listę tooli (`kedu.*`, `ewd.*`, `okwud.*`, `epuap.*`, `pue.*`, `employee.*`, `crypto.*`).

```
src/mcp_zus/
├── server.py               # MCP entrypoint, agreguje wszystkie tools
├── kedu/                   # KEDU 5.6 XML — builder/parser/validator (offline)
├── ewd/                    # Elektroniczna Wymiana Dokumentów (SOAP, payer channel)
├── okwud/                  # Wnioski uprawnionych instytucji o dane (SOAP, pue.zus.pl:8100)
├── epuap/                  # Skrzynka /ZUS/esp via WS-Skrytka SOAP
├── pue/                    # Browser companion — Playwright + CDP attach
├── crypto/                 # XAdES (BYO key — never on server)
└── tools/                  # MCP tool definitions per module
```

Wspólne pakiety (`crypto/`, oddzielnie schematy w `kedu/schemas/`, `okwud/schemas/`).

## Code Conventions

- **Python 3.11+**, `from __future__ import annotations` ON.
- **Type hints** wszędzie gdzie się da (pydantic v2 dla I/O kontraktów MCP).
- **`lxml`** do XML (nie ElementTree — XSD validation, namespacing).
- **`zeep`** do SOAP. WS-Security plugin.
- **`signxml`** do XAdES — NIGDY własna implementacja kryptografii.
- **BYO key**: MCP **nigdy** nie wczytuje klucza prywatnego. Wszystkie funkcje `crypto.*` zwracają payload do podpisu, user podpisuje lokalnie, my embeddujemy podpis.
- **Logi do stderr** (stdio MCP wymaga czystego stdout dla JSON-RPC).
- **Sekrety nigdy w response'ach** ani w logach — masking on default.
- **`pydantic.BaseModel`** dla input schemas tooli; konwersja na MCP `inputSchema` przez `.model_json_schema()`.
- **PEP 621** — `pyproject.toml`, `hatchling`, `uv` jako manager.
- **Tool naming**: `<moduł>.<akcja>` (np. `kedu.build_dra`, `pue.list_ubezpieczeni`).

## Adding a New Tool

1. Dopisz funkcję / metodę w odpowiednim module (`kedu/`, `okwud/`, …).
2. Stwórz pydantic model wejścia w `src/mcp_zus/tools/<module>_tools.py`.
3. Dodaj `@mcp.tool()` handler tam.
4. Tool jest auto-rejestrowany przez `import` w `server.py`.
5. Test: `tests/unit/test_<module>_<action>.py`.

## Channels — what each module does

| Moduł | Kanał | Wymaga | Auth | Sandbox |
|-------|-------|--------|------|---------|
| `kedu` | offline XML | XSD validator | — | — |
| `ewd` | SOAP do ZUS | KEDU + XAdES + akredytacja | cert kwalifikowany + Basic | brak publicznego |
| `okwud` | SOAP `pue.zus.pl:8100` | WSDL + XAdES + cert ZUS + Basic + sesja | wszystko powyższe + uprawniona instytucja | brak publicznego |
| `epuap` | SOAP WS-Skrytka | cert MAC/MC + PZ albo kwalifikowany | per ePUAP | tak (test.epuap.gov.pl) |
| `pue` | browser-attached | Chrome z CDP, user zalogowany manualnie | sesja usera | — |
| `crypto` | wspólny | klucz prywatny po stronie usera | — | — |

## Non-goals (NIGDY)

- ❌ Server-side klucze prywatne. Klucz zostaje u usera.
- ❌ Auto-login do PUE (SMS, hasło, biometria) — credentials zawsze user-side.
- ❌ Masowy scraping PUE / ZUS.
- ❌ RPA na desktop Płatniku.
- ❌ Emisja certyfikatów / deepfake podpisu / cokolwiek omijającego CA.

## Compliance / Legal Disclaimer

- ZUS oficjalnie nie publikuje SDK. Specyfikacje na BIP ZUS są publiczne, ale produkcyjne EWD/OK-WUD wymaga indywidualnej akredytacji u ZUS.
- Moduł `pue` używa publicznego UI portalu — kruche, podlega regulaminowi PUE. Nie do masowych operacji.
- Wszystkie testy E2E na produkcji wymagają realnego certyfikatu kwalifikowanego usera.
- Patrz `docs/source/` — kopie publicznych docs ZUS (BIP, public domain) używane jako source of truth.

## Owner

Bartosz Gaca — projekt **prywatny**, NIE BeeCommerce. Repo: `github.com/gacabartosz/mcp-zus`.
