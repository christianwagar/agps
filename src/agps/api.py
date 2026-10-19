"""Public API: score_accounts, explain_account, get_focus_list."""
from __future__ import annotations

import os

from . import engine
from .io import load_config, read_csv

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "agps.v2.json")
REQUIRED = ["account_name"]
PLAY_LABELS = ["P1", "P2", "P3", "P4"]


def _prep(accounts, config, mapping, cluster_method):
    cfg = load_config(config or DEFAULT_CONFIG)
    if isinstance(accounts, list):
        rows = [dict(r) for r in accounts]
        if mapping:
            from .io import load_mapping
            m = load_mapping(mapping)
            rows = [{m.get(k, k): v for k, v in r.items()} for r in rows]
        cols = list(rows[0].keys()) if rows else []
    else:
        cols, rows = read_csv(accounts, mapping)
    miss = [c for c in REQUIRED if c not in cols]
    if miss:
        raise ValueError(f"missing required column(s) {miss}; map your headers with mapping=")
    engine.score_rows(cfg, rows, cluster_method)
    return cfg, cols, rows


def output_columns(cfg):
    return [f"{b}_score" for b in cfg["bucket_weights"]] + ["overall_score", "cluster"]


def _public(cfg, r, cols=None):
    keep = (cols or ["account_name", "arr"]) + output_columns(cfg)
    return {k: r.get(k) for k in dict.fromkeys(keep) if not k.startswith("_")}


def score_accounts(accounts, config=None, mapping=None, cluster_method=None, include_inputs=False):
    """Score accounts (CSV path, CSV text, or list of dicts).

    Returns {"accounts": [...sorted best first...], "clusters": {...}, "focus_this_week": [...],
    "missing_fields": [...], "config": name}.
    """
    cfg, cols, rows = _prep(accounts, config, mapping, cluster_method)
    ranked = sorted(rows, key=lambda r: (r["_overall"], r["_i"]))
    summary = {}
    for k in PLAY_LABELS:
        g = [r for r in ranked if r["cluster"] == k]
        summary[k] = {"accounts": len(g), "total_arr": sum(engine.num(r.get("arr")) or 0 for r in g),
                      "top": [r.get("account_name") for r in g[:3]], "play": cfg.get("plays", {}).get(k)}
    return {
        "config": cfg.get("name"),
        "scored": len(rows),
        "missing_fields": [f for f in cfg["fields"] if f not in cols],
        "clusters": summary,
        "focus_this_week": [_focus_item(cfg, r) for r in engine.focus_list(cfg, rows)],
        "accounts": [_public(cfg, r, cols if include_inputs else None) for r in ranked],
        "_rows": ranked,
        "_columns": cols,
    }


def _focus_item(cfg, r):
    return {"account": r.get("account_name"), "cluster": r["cluster"], "overall_score": r["overall_score"],
            "days_to_renewal": engine.renewal_days(cfg, r), "arr": engine.num(r.get("arr"))}


def explain_account(accounts, account_name, config=None, mapping=None, cluster_method=None):
    cfg, _, rows = _prep(accounts, config, mapping, cluster_method)
    for r in rows:
        if str(r.get("account_name", "")).lower() == account_name.lower():
            return engine.explain(cfg, r)
    raise KeyError(f"account {account_name!r} not found")


def get_focus_list(accounts, config=None, mapping=None, count=None, window_days=None, cluster_method=None):
    cfg, _, rows = _prep(accounts, config, mapping, cluster_method)
    return [_focus_item(cfg, r) for r in engine.focus_list(cfg, rows, count, window_days)]
