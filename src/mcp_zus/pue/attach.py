"""Connect to the user's already-logged-in Chrome via CDP.

The user runs Chrome like this:

    open -na "Google Chrome" --args \\
        --remote-debugging-port=9222 \\
        --user-data-dir="$HOME/.chrome-pue-mcp"

Then logs in manually to PUE ZUS (login + SMS). MCP attaches to that
running browser; it does not launch its own Chrome and does not handle
credentials.
"""
from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mcp_zus.pue import PUE_HOST
from mcp_zus.pue.selectors import LoginCheck

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, Page


class PueNotAttachedError(RuntimeError):
    """Chrome with --remote-debugging-port is not running, or no PUE tab open."""


class PueNotLoggedInError(RuntimeError):
    """User is not logged in to PUE — please log in manually first."""


@dataclass(slots=True)
class PueSession:
    """Active PUE session attached to the user's browser."""

    context: BrowserContext
    page: Page
    cdp_url: str

    async def whoami(self) -> dict:
        """Detect current PUE role / NIP / user name from the open page."""
        await self.page.bring_to_front()
        url = self.page.url
        title = await self.page.title()
        return {
            "url": url,
            "title": title,
            "is_logged_in": await self.is_logged_in(),
        }

    async def is_logged_in(self) -> bool:
        try:
            await self.page.wait_for_selector(LoginCheck.LOGGED_IN_INDICATOR, timeout=2000)
            return True
        except Exception:
            return False


@asynccontextmanager
async def attach(cdp_url: str | None = None) -> AsyncIterator[PueSession]:
    """Attach to user's running Chrome via CDP and find a PUE-bearing tab.

    Raises:
        PueNotAttachedError: if Chrome with CDP isn't running.
        PueNotLoggedInError: if no PUE tab is logged in.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError(
            "playwright not installed. Install with: uv pip install 'mcp-zus[pue]'"
        ) from exc

    cdp_url = cdp_url or os.getenv("PUE_CDP_URL", "http://localhost:9222")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(cdp_url)
        except Exception as exc:
            raise PueNotAttachedError(
                f"Cannot connect to Chrome at {cdp_url}. Start Chrome with "
                f"--remote-debugging-port=9222 and log in to {PUE_HOST} manually."
            ) from exc

        context = browser.contexts[0] if browser.contexts else await browser.new_context()

        page: Page | None = None
        for p_ in context.pages:
            if PUE_HOST in p_.url or "pue.zus.pl" in p_.url:
                page = p_
                break

        if page is None:
            raise PueNotLoggedInError(
                f"No PUE tab found in your Chrome. Open {PUE_HOST}/portal/ and log in first."
            )

        session = PueSession(context=context, page=page, cdp_url=cdp_url)

        if not await session.is_logged_in():
            raise PueNotLoggedInError(
                "Found a PUE tab but you don't appear to be logged in. "
                "Log in manually (login + SMS), then retry."
            )

        try:
            yield session
        finally:
            # We do NOT close the browser — it's the user's running session.
            pass


__all__ = ["PueNotAttachedError", "PueNotLoggedInError", "PueSession", "attach"]
