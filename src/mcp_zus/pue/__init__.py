"""PUE Browser Companion — Playwright + Chrome DevTools Protocol attach.

EXPERIMENTAL. Operates on the user's already-logged-in Chrome session.
Never handles credentials, never logs in. The user logs in manually
(login + SMS) and starts Chrome with `--remote-debugging-port=9222`.
"""
from __future__ import annotations

PUE_HOST = "https://www.zus.pl"
PUE_PORTAL = "https://www.zus.pl/portal/"

__all__ = ["PUE_HOST", "PUE_PORTAL"]
