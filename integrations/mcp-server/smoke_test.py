"""Starts server.py over stdio as a real MCP client would, lists tools, and calls each one."""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
DEMO = os.path.abspath(os.path.join(ROOT, "examples", "demo_accounts.csv"))
V1 = os.path.abspath(os.path.join(ROOT, "config", "agps.v1-compat.json"))


async def main():
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(HERE, "server.py")])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = sorted(t.name for t in (await s.list_tools()).tools)
            print("tools:", tools)
            res = await s.call_tool("score_accounts", {"csv_path": DEMO, "config": V1, "limit": 3})
            d = json.loads(res.content[0].text)
            print("score_accounts:", d["scored"], "scored; top:", [a["account_name"] for a in d["accounts"]])
            res = await s.call_tool("explain_account", {"csv_path": DEMO, "config": V1, "account_name": "Stripe"})
            d = json.loads(res.content[0].text)
            print("explain_account:", d["account"], d["cluster"], d["overall_score"])
            res = await s.call_tool("get_focus_list", {"csv_path": DEMO, "config": V1})
            print("get_focus_list:", [json.loads(c.text)["account"] for c in res.content])
            assert tools == ["explain_account", "get_focus_list", "score_accounts"]
            for t in (await s.list_tools()).tools:
                a = t.annotations
                assert (a.readOnlyHint, a.destructiveHint, a.idempotentHint, a.openWorldHint) == (True, False, True, False), t.name


asyncio.run(main())
