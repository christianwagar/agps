# A-GPS MCP server

This is a minimal stdio MCP server with three tools. All three take `csv` (CSV text) or `csv_path` (a local file), plus an optional `config` path and `mapping` dict.

| Tool | Returns |
|---|---|
| `score_accounts` | cluster summaries (P1–P4), the focus list, the scored accounts (best first, capped at `limit`), and missing fields |
| `explain_account` | bucket scores, the strongest and weakest bucket, the best and worst fields, N/A fields, and the cluster play |
| `get_focus_list` | the lowest overall scores among accounts renewing within `window_days` (default 120) |

## Install
```bash
cd <repo>
python -m venv .venv && . .venv/bin/activate
pip install -e ".[mcp]"          # or: pip install "mcp>=1.2,<2"
python integrations/mcp-server/smoke_test.py   # optional check
```
`server.py` adds `../../src` to the path, so it also runs from a plain checkout. Set the `AGPS_CONFIG` environment variable to use your own config by default. The bundled v2 config is used otherwise.

## Claude Desktop
Edit `claude_desktop_config.json` (Settings → Developer → Edit Config):
```json
{
  "mcpServers": {
    "agps": {
      "command": "/absolute/path/to/repo/.venv/bin/python",
      "args": ["/absolute/path/to/repo/integrations/mcp-server/server.py"]
    }
  }
}
```
Restart Claude Desktop.

## Cursor
Add this to `.cursor/mcp.json` in a project, or to `~/.cursor/mcp.json` for all projects:
```json
{
  "mcpServers": {
    "agps": {
      "command": "/absolute/path/to/repo/.venv/bin/python",
      "args": ["/absolute/path/to/repo/integrations/mcp-server/server.py"]
    }
  }
}
```

## Grok Bot
Grok Bot can run the package directly on its box using `integrations/grok-skill/SKILL.md`, which needs no MCP. If you want the tools exposed over MCP, add a custom MCP server in Grok Bot's connector settings with the same command and args. A stdio server has to run on a machine Grok Bot can reach. If your setup only accepts remote (HTTP) servers, run it behind an MCP stdio-to-HTTP bridge, or change `mcp.run()` to `mcp.run(transport="streamable-http")` and host it.

## Notes
- The server is stateless and keeps no account data between calls.
- It's pinned to the `mcp` 1.x Python SDK (`FastMCP`). The SDK's 2.x release renamed that API.
