"""A-GPS MCP server (stdio). Exposes score_accounts, explain_account, get_focus_list.

Run:  python server.py        (needs: pip install "mcp>=1.2" and the agps package, or run from the repo)
Every tool takes the accounts as CSV text (csv) or a local file path (csv_path), plus optional
config path, header mapping and cluster method. Stateless: nothing is stored between calls.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))  # run from a repo checkout without installing

from mcp.server.fastmcp import FastMCP  # noqa: E402

import agps  # noqa: E402

mcp = FastMCP("agps")
DEFAULT_CONFIG = os.environ.get("AGPS_CONFIG")  # optional: point at your own config


def _source(csv, csv_path):
    if csv_path:
        return csv_path
    if csv:
        return csv
    raise ValueError("pass csv (CSV text) or csv_path (a file path)")


@mcp.tool()
def score_accounts(csv: str = "", csv_path: str = "", config: str = "", mapping: dict | None = None,
                   cluster_method: str = "", limit: int = 50) -> dict:
    """Score accounts with A-GPS (golf-style: 1 = best, 8 = worst) and group them into P1-P4.
    Returns cluster summaries, the focus-this-week list, and the top `limit` scored accounts."""
    res = agps.score_accounts(_source(csv, csv_path), config or DEFAULT_CONFIG, mapping, cluster_method)
    out = {k: v for k, v in res.items() if not k.startswith("_")}
    out["accounts"] = out["accounts"][:limit]
    return out


@mcp.tool()
def explain_account(account_name: str, csv: str = "", csv_path: str = "", config: str = "",
                    mapping: dict | None = None) -> dict:
    """Explain one account: bucket scores, strongest/weakest bucket, best and worst fields, cluster play."""
    return agps.explain_account(_source(csv, csv_path), account_name, config or DEFAULT_CONFIG, mapping)


@mcp.tool()
def get_focus_list(csv: str = "", csv_path: str = "", config: str = "", mapping: dict | None = None,
                   count: int = 3, window_days: int = 120) -> list:
    """Accounts to focus on this week: lowest overall score among renewals within window_days."""
    return agps.get_focus_list(_source(csv, csv_path), config or DEFAULT_CONFIG, mapping, count, window_days)


if __name__ == "__main__":
    mcp.run()
