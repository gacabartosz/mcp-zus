# mcp-zus

> **Pierwsze publiczne MCP (Model Context Protocol) dla polskiego ZUS / PUE ZUS.**
> Pokrywa KEDU, EWD, OK-WUD, ePUAP oraz tryb "browser companion" do zalogowanej sesji PUE.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)]()

## Co to jest

`mcp-zus` to serwer MCP, który pozwala LLM-owi (Claude, GPT, dowolnemu klientowi MCP) operować na ZUS:

- **KEDU 5.6** — generować, parsować i walidować dokumenty XML (DRA, RCA, RSA, ZUA, ZWUA, ZIUA, ZCNA, ...) **offline**, bez akredytacji.
- **EWD** — wysyłać KEDU do ZUS przez oficjalny SOAP po stronie płatnika (po akredytacji).
- **OK-WUD** — wnioski o udostępnienie danych dla **uprawnionych instytucji** (sądy, komornicy, NFZ, KRUS, banki, ...) przez `pue.zus.pl:8100`.
- **ePUAP** — wysyłka pism na skrzynkę ZUS (`/ZUS/esp`) przez WS-Skrytka.
- **PUE Browser Companion** — pragmatyczny tryb: logujesz się ręcznie w Chrome (login + SMS), MCP doczepia się do sesji przez CDP i robi czytanie + nieinwazyjne operacje. **Bez akredytacji ZUS.**

## Status modułów

| Moduł | Status | Co działa 100% | Czego wymaga |
|-------|--------|----------------|--------------|
| `kedu` envelope | ✅ | XSD-valid envelope: `<KEDU wersja_schematu="1">` + `<naglowek.KEDU>` z `program`/`ID_KEDU`/`data_utworzenia_KEDU`. Walidator (lxml + XSD), parser, SHA-256 digest. | offline |
| `kedu` inner sections | 🟡 WIP | Generuje `ZUSDRA`/`ZUSZUA`/`ZUSZWUA`/`ZUSZIUA`/`ZUSZCNA` z payerem i podstawowymi danymi. **Sekcje I-XIV z polami pozycyjnymi `<p1>...<pN>` zgodnie z formularzem Płatnika to iterative roadmap (v0.2).** | offline |
| `okwud` builder + importers | ✅ | Pełny XML wg `crd.gov.pl/wzor/2020/12/29/10229`, 60+ kodów instytucji, 5 formatów importu (XLSX/XLS/CSV/ODS/XML) | offline |
| `okwud` SOAP client | 🟡 scaffold | WSDL endpoint stały, struktura sesji `pobierzOswiadczenie` znana | cert kwalifikowany + uprawnienia uprawnionej instytucji |
| `crypto` BYO key | ✅ | `prepare_signing_payload` (C14N + SHA-256 digest), `attach_signature` (osadza `<ds:Signature>`); server NIGDY nie czyta klucza | klucz po stronie usera |
| `pue` browser companion | 🟡 alpha | Playwright + CDP attach do running Chrome'a, page-object pattern, MCP nigdy nie obsługuje credentials | Chrome `--remote-debugging-port=9222` + ręczne login + kalibracja selektorów na żywej sesji |
| `ewd` (płatnik SOAP) | 🟡 scaffold | Interfejs i sygnatury gotowe | akredytacja u ZUS dla produkcji |
| `epuap` (WS-Skrytka) | 🟡 scaffold | Interfejs gotowy | cert MAC dla SOD |
| `employee` orchestrator | ✅ | High-level `register/deregister/update/add_family_member` opakowuje KEDU builder | offline |
| MCP server (stdio) | ✅ | 30 tooli zarejestrowanych przez FastMCP, smoke-tested po stdio JSON-RPC | offline |

## Quickstart

```bash
# 1. Klon
git clone https://github.com/gacabartosz/mcp-zus.git && cd mcp-zus

# 2. Instalacja (uv recommended)
uv sync --all-extras

# 3. Uruchom MCP server
uv run mcp-zus

# 4. Zarejestruj w Claude Code (~/.claude.json) lub Claude Desktop:
# {
#   "mcpServers": {
#     "zus": {
#       "command": "uv",
#       "args": ["--directory", "/sciezka/do/mcp-zus", "run", "mcp-zus"],
#       "env": { "PUE_CDP_URL": "http://localhost:9222" }
#     }
#   }
# }
```

## Przykład — KEDU offline (Faza 1)

```bash
# W Claude:
> Zbuduj DRA na maj 2026 dla NIP 1234563218, samozatrudniony JDG, podstawa preferencyjna
# → kedu.build_jdg_monthly()
# → zwraca walidowany XML KEDU 5.6 gotowy do podpisu kwalifikowanego u Ciebie lokalnie
```

## Przykład — PUE Browser Companion (Faza 1.5)

```bash
# 1. Uruchom Chrome z CDP enabled:
open -na "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.chrome-pue-mcp"

# 2. Zaloguj się ręcznie na pue.zus.pl (login + SMS)

# 3. W Claude:
> Sprawdź status moich ostatnich 5 zestawów dokumentów wysłanych do ZUS
# → pue.attach() → pue.list_dokumenty() → pue.get_zestaw_status() x 5
```

## Lista narzędzi MCP

Patrz [`docs/tools.md`](docs/tools.md) dla pełnej dokumentacji 40+ tooli.

## Bezpieczeństwo

- **MCP nigdy nie wczytuje klucza prywatnego.** Wszystkie operacje podpisu zwracają payload do podpisu lokalnego u usera (Szafir, Certum, `signxml` lokalnie).
- **MCP nigdy nie loguje się sam do PUE.** Login + SMS pozostaje 100% po stronie usera; tryb `pue` jedynie *attachuje się* do otwartej sesji Chrome.
- **Sekrety w env** — patrz `.env.example`. **Nigdy** nie commituj `.env`, certyfikatów, kluczy.
- **Logi** maskują NIP/PESEL na poziomie INFO/WARN.

## Prawne ramy

- Ustawa o systemie ubezpieczeń społecznych — [`isap.sejm.gov.pl/.../WDU20250000350`](https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20250000350).
- eIDAS (Rozporządzenie 910/2014) — wymóg podpisu kwalifikowanego dla EWD.
- Regulamin PUE ZUS — moduł `pue` jest narzędziem ergonomicznym dla pojedynczego usera, **nie batch-processorem**. Używaj zgodnie z regulaminem.
- ZUS oficjalnie nie publikuje SDK; produkcyjne EWD/OK-WUD wymaga indywidualnej akredytacji u ZUS.

## Status: Alpha v0.1.0

Projekt jest w fazie alpha. **Nie używaj produkcyjnie bez własnych testów na własnych danych.** Jeśli znajdziesz błąd — issue. Jeśli chcesz pomóc — PR welcome.

### Co wymaga jeszcze pracy w v0.2

1. **KEDU inner section mapping** — dla pełnej XSD-walidacji DRA/ZUA/RCA każda sekcja (I, II, ..., XIV) musi mapować pola pozycyjne `<p1>...<pN>` dokładnie wg `Załącznik 1 — Zakres informacyjny dokumentów ubezpieczeniowych ZUS` (BIP ZUS). Aktualne builders generują strukturę uproszczoną — envelope jest XSD-valid, inner sekcje są nazwane semantycznie ale nie pozycyjnie.
2. **PUE selector calibration** — selektory w `src/mcp_zus/pue/selectors.py` to educated guesses; finalna kalibracja po pierwszym `pue.attach()` na zalogowanej sesji (DevTools → Copy Selector → wklej do `selectors.py`).
3. **EWD/OK-WUD live calls** — wymaga akredytacji u ZUS; interfejsy i WSDL gotowe.
4. **JDG monthly DRA: aktualne podstawy z GUS** — obecnie zaszyte w `kedu/jdg.py`; w v0.2 czytane z aktualnego komunikatu Prezesa GUS.

## License

MIT © 2026 Bartosz Gaca
