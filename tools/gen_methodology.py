#!/usr/bin/env python3
"""Regenerates METHODOLOGY.md from config/agps.v2.json."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(ROOT, "config", "agps.v2.json")))

def fmt(v):
    if v is None: return ""
    if isinstance(v, float) and v == 0.0001: return ">0"
    if isinstance(v, (int, float)) and abs(v) >= 1000: return f"{v:,.0f}"
    return f"{v:g}" if isinstance(v, float) else str(v)

def bands(bs):
    out = []
    for b in bs:
        lo, hx, hi = b.get("min"), b.get("max_exclusive"), b.get("max")
        if hi is not None: r = f"≤{fmt(hi)}"
        elif lo is None and hx is None: r = "else"
        elif lo is None: r = f"<{fmt(hx)}"
        elif hx is None: r = f"≥{fmt(lo)}"
        else: r = f"{fmt(lo)}–<{fmt(hx)}"
        out.append(f"{r}→{b['score']}")
    return ", ".join(out)

L = ["# Methodology", "", "Generated from `config/agps.v2.json` by `tools/gen_methodology.py`. Do not edit by hand.", "", "> **This is a framework, not a one-size-fits-all answer.** Every band and weight below must be dialed in for your business: customer spend levels, deal sizes, risk appetite, sales motion, and data quality. Tune them in `config/agps.v2.yaml` (see the How to tune it checklist in the README).", "",
     "## Scale", "", "- Every field scores 1 (best) to 8 (worst), like strokes in golf. Blank = 8.",
     "- N/A (the field doesn't apply, e.g. no onboarding purchased) is excluded from the bucket average by default (`not_applicable: exclude`).",
     "- Bucket score = average of its fields (per-field weights only if `use_field_weights: true`).",
     "- Overall = weighted average of buckets.",
     "- Clusters (default `median_2x2`): growth potential = the A-GPS score with ARR taken out (GTM without ARR = (7 × GTM − ARR band) / 6, then the weighted buckets), so size never counts twice. Split the book at the median growth score and the median ARR: P1 = high growth + high spend, P2 = high growth + lower spend, P3 = lower growth + high spend, P4 = lower on both. The split rebalances every time the data changes. Legacy `quartile` and `growth_arr_2x2` remain available.",
     "- WATCH flag (separate guardrail): NRR under 90% or growth score worse than 6.0, wherever the account lands. Both thresholds are configurable under `cluster.watch`.",
     "- Focus this week (median 2×2): P1 and P3 accounts renewing within 120 days, best growth score first (WATCH accounts only from P3); next-soonest P1/P3 renewals fill in if fewer than 3. Other methods: lowest overall within 120 days.", "",
     "## Buckets", "", "| Bucket | Weight | Sheet section |", "|---|---|---|"]
inv = {v: k for k, v in cfg["section_to_bucket"].items()}
for b, w in cfg["bucket_weights"].items():
    L.append(f"| `{b}` | {w:.0%} | {inv.get(b, '').replace('|', chr(92) + '|')} |")
L += ["", "## Options (defaults)", "", "| Option | Default |", "|---|---|"]
L += [f"| `{k}` | `{json.dumps(v)}` |" for k, v in cfg["options"].items()]
for b in cfg["bucket_weights"]:
    L += ["", f"## {b}", "", "| Field | Sheet row | Element | Type / unit | Scoring | Notes |", "|---|---|---|---|---|---|"]
    for f, s in cfg["fields"].items():
        if s["bucket"] != b: continue
        if "levels" in s:
            sc = ", ".join(f"{k}→{v}" for k, v in s["levels"].items())
        elif "band_sets" in s:
            sc = "<br>".join(f"*{k}*: {bands(v)}" for k, v in s["band_sets"].items())
        else:
            sc = bands(s["bands"])
        notes = []
        if s.get("missing") == "na": notes.append("blank = N/A")
        for c in s.get("na_if", []): notes.append(f"N/A if {c['field']} {c['op']} {c['value']}")
        if s.get("min_count"): notes.append(f"N/A if {s['min_count']['field']} < {s['min_count']['option']}")
        for o in s.get("overrides", []): notes.append(f"→{o['score']} if {o['field']} {o['op']} {o['value']}")
        if s.get("normalize"): notes.append(f"size_normalization: % of {s['normalize']['divide_by']} ({bands(s['normalize']['bands'])})")
        if s.get("weight", 1) != 1: notes.append(f"weight {s['weight']} (if use_field_weights)")
        if s.get("stale"): notes.append(f"+1 if {s['stale']['field']} > {s['stale']['after_days']} (if stale_rag_penalty)")
        if s.get("percentile_option"): notes.append("percentile mode via arr_scoring")
        L.append(f"| `{f}` | {s['sheet_row']} | {s['element'].replace('|', chr(92) + '|')} | {s['type']}{' / ' + s['unit'] if s.get('unit') else ''} | {sc} | {'; '.join(notes)} |")
L += ["", "## v1 compatibility", "", "`config/agps.v1-compat.json` is the model behind the live demo (33 simpler fields, booleans, sooner-is-better renewal). "
      "The test suite checks it reproduces the 40 demo scores exactly."]
open(os.path.join(ROOT, "METHODOLOGY.md"), "w").write("\n".join(L) + "\n")
print("METHODOLOGY.md written")
