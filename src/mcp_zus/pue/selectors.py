"""All CSS/XPath selectors for PUE in one place.

Selectors break with every UI revision — when a tool fails, fix here and
the rest of the codebase keeps working.

NOTE: These are EDUCATED GUESSES based on common PUE patterns. Calibrate
against a real logged-in PUE session (DevTools → copy selector) before relying.
"""
from __future__ import annotations


class LoginCheck:
    LOGGED_IN_INDICATOR = "#header-user, [data-testid='user-menu'], .user-info"
    LOGOUT_BUTTON = "a[href*='logout'], button[aria-label*='Wyloguj']"
    LOGIN_FORM = "input[name='username'], input[name='login']"


class Navigation:
    ROLE_SWITCHER = "[data-testid='role-switcher'], .role-selector"
    ROLE_PLATNIK = "text=Płatnik"
    ROLE_UBEZPIECZONY = "text=Ubezpieczony"
    ROLE_SWIADCZENIOBIORCA = "text=Świadczeniobiorca"


class Platnik:
    DOKUMENTY_MENU = "a[href*='dokumenty'], text=Dokumenty"
    UBEZPIECZENI_MENU = "a[href*='ubezpieczeni'], text=Ubezpieczeni"
    KORESPONDENCJA_MENU = "a[href*='korespondencja'], text=Korespondencja"
    PLATNIK_NIP = "[data-field='nip'], .platnik-nip"


class Ubezpieczeni:
    LIST_TABLE = "table.ubezpieczeni-list, [data-testid='ubezpieczeni-table']"
    LIST_ROW = "tbody > tr"
    SEARCH_INPUT = "input[placeholder*='Szukaj']"


class Dokumenty:
    LIST_TABLE = "table.dokumenty, [data-testid='dokumenty-table']"
    LIST_ROW = "tbody > tr"
    STATUS_CELL = "td.status, [data-field='status']"
    UPO_DOWNLOAD_LINK = "a[href*='UPO'], a[download*='UPO']"
    UPLOAD_FORM = "form[action*='upload'], [data-testid='upload-form']"
    UPLOAD_FILE_INPUT = "input[type='file']"
    UPLOAD_SUBMIT = "button[type='submit'], button:has-text('Wyślij')"


class Korespondencja:
    LIST_TABLE = "table.pisma, [data-testid='pisma-table']"
    LIST_ROW = "tbody > tr"
    PISMO_TITLE = "td.tytul, [data-field='tytul']"
    PISMO_DATE = "td.data, [data-field='data']"
    OPEN_BUTTON = "a, button"


__all__ = [
    "Dokumenty",
    "Korespondencja",
    "LoginCheck",
    "Navigation",
    "Platnik",
    "Ubezpieczeni",
]
