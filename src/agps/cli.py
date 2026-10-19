"""agps command line.

  agps score accounts.csv [--config cfg.yaml|json] [--map map.json] [-o scored.csv] [--json]
  agps explain accounts.csv "Account Name" [--config ...]
  agps focus accounts.csv [--count 3] [--window-days 120]
  agps convert config/agps.v2.yaml config/agps.v2.json     (needs PyYAML)
"""
from __future__ import annotations

import argparse
import json
import sys

from . import api
from .io import load_config, write_csv


def _common(p):
    p.add_argument("input", help="accounts CSV")
    p.add_argument("-c", "--config", help="config .json or .yaml (default: bundled v2)")
    p.add_argument("-m", "--map", help="JSON mapping file or 'Header=field,...'")
    p.add_argument("--cluster-method", choices=["quartile", "growth_arr_2x2"])


def main(argv=None):
    ap = argparse.ArgumentParser(prog="agps", description="A-GPS account growth propensity scoring")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score", help="score a CSV")
    _common(s)
    s.add_argument("-o", "--out", default="scored_accounts.csv")
    s.add_argument("--json", action="store_true")
    e = sub.add_parser("explain", help="explain one account")
    _common(e)
    e.add_argument("account")
    f = sub.add_parser("focus", help="focus-this-week list")
    _common(f)
    f.add_argument("--count", type=int)
    f.add_argument("--window-days", type=int)
    c = sub.add_parser("convert", help="convert a YAML config to JSON")
    c.add_argument("src")
    c.add_argument("dst")
    a = ap.parse_args(argv)

    if a.cmd == "convert":
        with open(a.dst, "w") as fh:
            json.dump(load_config(a.src), fh, indent=2)
            fh.write("\n")
        print(f"wrote {a.dst}")
        return
    try:
        if a.cmd == "explain":
            print(json.dumps(api.explain_account(a.input, a.account, a.config, a.map, a.cluster_method), indent=2))
            return
        if a.cmd == "focus":
            print(json.dumps(api.get_focus_list(a.input, a.config, a.map, a.count, a.window_days, a.cluster_method), indent=2))
            return
        res = api.score_accounts(a.input, a.config, a.map, a.cluster_method)
    except (ValueError, KeyError) as err:
        sys.exit(f"error: {err}")
    cfg = load_config(a.config or api.DEFAULT_CONFIG)
    out_cols = api.output_columns(cfg)
    write_csv(a.out, [c for c in res["_columns"] if c not in out_cols] + out_cols, res["_rows"])
    if res["missing_fields"]:
        print(f"note: {len(res['missing_fields'])} scored field(s) not in input, scored as missing: "
              f"{', '.join(res['missing_fields'])}", file=sys.stderr)
    if a.json:
        print(json.dumps({k: v for k, v in res.items() if not k.startswith("_") and k != "accounts"} | {"output": a.out}, indent=2))
        return
    print(f"Scored {res['scored']} accounts -> {a.out}\n")
    for k, v in res["clusters"].items():
        print(f"{k}: {v['accounts']:>3} accounts  ${v['total_arr']:>14,.0f} ARR  top: {', '.join(map(str, v['top']))}")
    fc = cfg.get("focus", {})
    print(f"\nFocus this week (lowest score among renewals within {fc.get('window_days', 120)} days)")
    for i, x in enumerate(res["focus_this_week"], 1):
        d = "?" if x["days_to_renewal"] is None else f"{x['days_to_renewal']:.0f}"
        print(f"  {i}. {x['account']} [{x['cluster']}] overall {x['overall_score']:.3f}, {d} days to renewal")


if __name__ == "__main__":
    main()
