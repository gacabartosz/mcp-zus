"""MCP server — entrypoint registering all tools across modules.

Run via:
    uv run mcp-zus              # stdio transport (Claude Desktop / Code)
    uv run mcp dev src/mcp_zus/server.py    # MCP Inspector for dev
"""
from __future__ import annotations

import logging
import os
import sys

from mcp.server.fastmcp import FastMCP

from mcp_zus import __version__
from mcp_zus.tools import (
    crypto_tools,
    employee_tools,
    epuap_tools,
    ewd_tools,
    kedu_tools,
    okwud_tools,
    pue_tools,
)

# stdio MCP wymaga czystego stdout dla JSON-RPC — logi idą na stderr
logging.basicConfig(
    level=os.getenv("MCP_ZUS_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("mcp-zus")

mcp = FastMCP("mcp-zus")


# ---- KEDU ----
mcp.tool(name="kedu.build_dra")(kedu_tools.tool_build_kedu_dra)
mcp.tool(name="kedu.build_zua")(kedu_tools.tool_build_kedu_zua)
mcp.tool(name="kedu.build_zwua")(kedu_tools.tool_build_kedu_zwua)
mcp.tool(name="kedu.build_ziua")(kedu_tools.tool_build_kedu_ziua)
mcp.tool(name="kedu.build_zcna")(kedu_tools.tool_build_kedu_zcna)
mcp.tool(name="kedu.build_jdg_monthly")(kedu_tools.tool_build_jdg_monthly)
mcp.tool(name="kedu.validate")(kedu_tools.tool_validate_kedu)
mcp.tool(name="kedu.parse")(kedu_tools.tool_parse_kedu)

# ---- OK-WUD ----
mcp.tool(name="okwud.build_request")(okwud_tools.tool_build_okwud)
mcp.tool(name="okwud.import_subjects")(okwud_tools.tool_import_subjects)
mcp.tool(name="okwud.list_kody_instytucji")(okwud_tools.tool_list_kody_instytucji)

# ---- Crypto ----
mcp.tool(name="crypto.prepare_signing_payload")(crypto_tools.tool_prepare_signing_payload)
mcp.tool(name="crypto.attach_signature")(crypto_tools.tool_attach_signature)

# ---- Employee (high-level) ----
mcp.tool(name="employee.register")(employee_tools.tool_register_employee)
mcp.tool(name="employee.deregister")(employee_tools.tool_deregister_employee)
mcp.tool(name="employee.update")(employee_tools.tool_update_employee)
mcp.tool(name="employee.add_family_member")(employee_tools.tool_add_family_member)

# ---- PUE Browser Companion ----
mcp.tool(name="pue.attach")(pue_tools.tool_attach)
mcp.tool(name="pue.list_dokumenty")(pue_tools.tool_list_dokumenty)
mcp.tool(name="pue.list_ubezpieczeni")(pue_tools.tool_list_ubezpieczeni)
mcp.tool(name="pue.list_korespondencja")(pue_tools.tool_list_korespondencja)
mcp.tool(name="pue.read_pismo")(pue_tools.tool_read_pismo)
mcp.tool(name="pue.download_upo")(pue_tools.tool_download_upo)
mcp.tool(name="pue.upload_kedu")(pue_tools.tool_upload_kedu)

# ---- EWD (skeleton, requires accreditation) ----
mcp.tool(name="ewd.send")(ewd_tools.tool_ewd_send)
mcp.tool(name="ewd.get_status")(ewd_tools.tool_ewd_status)
mcp.tool(name="ewd.fetch_upo")(ewd_tools.tool_ewd_fetch_upo)

# ---- ePUAP ----
mcp.tool(name="epuap.send_to_zus")(epuap_tools.tool_epuap_send_to_zus)
mcp.tool(name="epuap.fetch_upp")(epuap_tools.tool_epuap_fetch_upp)
mcp.tool(name="epuap.list_inbox")(epuap_tools.tool_epuap_list_inbox)


def main() -> None:
    log.info("starting mcp-zus v%s on stdio transport", __version__)
    mcp.run()


if __name__ == "__main__":
    main()
