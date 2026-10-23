"""The stdio MCP server's tools, called by name, plus their annotations. Skipped if the mcp package isn't installed."""
import asyncio
import json
import os
import sys

import pytest

pytest.importorskip("mcp")
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "integrations", "mcp-server"))
import server  # noqa: E402

DEMO = os.path.abspath(os.path.join(ROOT, "examples", "demo_accounts.csv"))
V1 = os.path.abspath(os.path.join(ROOT, "config", "agps.v1-compat.json"))


def _call(name, args):
    """Call a tool by name the way a client would and decode its JSON text content."""
    res = asyncio.run(server.mcp.call_tool(name, args))
    content = res[0] if isinstance(res, tuple) else res
    return [json.loads(c.text) for c in content]


def test_tools_listed_with_readonly_annotations():
    tools = asyncio.run(server.mcp.list_tools())
    assert sorted(t.name for t in tools) == ["explain_account", "get_focus_list", "score_accounts"]
    for t in tools:
        a = t.annotations
        assert (a.readOnlyHint, a.destructiveHint, a.idempotentHint, a.openWorldHint) == (True, False, True, False)


def test_score_accounts():
    d = _call("score_accounts", {"csv_path": DEMO, "config": V1, "limit": 3})[0]
    assert d["scored"] == 40 and len(d["accounts"]) == 3


def test_explain_account():
    assert _call("explain_account", {"csv_path": DEMO, "config": V1, "account_name": "Stripe"})[0]["account"] == "Stripe"


def test_get_focus_list():
    assert len(_call("get_focus_list", {"csv_path": DEMO, "config": V1, "count": 2})) == 2
