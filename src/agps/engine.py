"""A-GPS scoring engine. Standard library only.

Golf-style scoring: every field gets a band score from 1 (best) to 8 (worst). Bucket score is the
weighted average of its fields, overall is the weighted average of the buckets, lower = higher priority.
Works with both the v1 config (agps_config.json, the live 26-w.com model) and v2 (config/agps.v2.yaml).
"""
from __future__ import annotations

import math
import statistics

NA = "n/a"  # sentinel: field does not apply to this account
DEFAULT_OPTIONS = {
    "not_applicable": "exclude",     # exclude | score_missing
    "empty_bucket": "renormalize",   # renormalize | score_missing
    "use_field_weights": False,
    "size_normalization": False,
    "min_closed_opps": 3,
    "min_survey_responses": 3,
    "renewal_direction": "sooner_is_better",
    "arr_scoring": "absolute",       # absolute | percentile
    "segment_field": None,
    "stale_rag_penalty": False,
}
_NA_TOKENS = {"n/a", "na", "not applicable", "not_applicable"}
_OPS = {
    "eq": lambda a, b: a == b, "ne": lambda a, b: a != b, "lt": lambda a, b: a < b,
    "lte": lambda a, b: a <= b, "gt": lambda a, b: a > b, "gte": lambda a, b: a >= b,
}


def options(cfg: dict) -> dict:
    out = dict(DEFAULT_OPTIONS)
    out.update({k: (v["value"] if isinstance(v, dict) and "value" in v else v)
                for k, v in (cfg.get("options") or {}).items()})
    return out


def num(v):
    if v is None or isinstance(v, bool):
        return None if v is None else float(v)
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "").replace("$", "").replace("%", "")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _blank(v) -> bool:
    return v is None or str(v).strip() == ""


def _cond(row, c) -> bool:
    v = num(row.get(c["field"]))
    return v is not None and _OPS[c.get("op", "eq")](v, c["value"])


def band_score(bands, val, missing):
    """Bands: {min (inclusive), max_exclusive | max (inclusive), score}; null = open-ended.
    The first band (in listed order) that contains val wins."""
    for b in bands:
        lo, hi_x, hi_i = b.get("min"), b.get("max_exclusive"), b.get("max")
        if lo is not None and val < lo:
            continue
        if hi_x is not None and val >= hi_x:
            continue
        if hi_i is not None and val > hi_i:
            continue
        return b["score"]
    return missing


def field_score(cfg, opts, name, spec, row):
    """Return an int 1..8, or NA when the field does not apply."""
    missing = cfg["scale"]["missing_score"]
    na_result = NA if opts["not_applicable"] == "exclude" else missing
    raw = row.get(name)

    for c in spec.get("na_if", []):
        if _cond(row, c):
            return na_result
    mc = spec.get("min_count")
    if mc and not _blank(row.get(mc["field"])):
        n = num(row.get(mc["field"]))
        if n is not None and n < opts[mc["option"]]:
            return na_result
    for o in spec.get("overrides", []):
        if _cond(row, o):
            return o["score"]
    if _blank(raw):
        return na_result if spec.get("missing") == "na" else missing
    s = str(raw).strip().lower()
    if s in _NA_TOKENS and spec.get("type") != "ordinal":
        return na_result

    t = spec.get("type", "number")
    if t == "ordinal" and "levels" in spec:  # v2: label -> score (or "na")
        lv = {k.lower(): v for k, v in spec["levels"].items()}
        if s not in lv:
            return missing
        return na_result if lv[s] == "na" else _modify(cfg, opts, spec, row, lv[s])
    if t == "ordinal":  # v1: label -> number, then bands
        val = {k.lower(): v for k, v in spec["ordinal_map"].items()}.get(s)
    elif t == "boolean":
        bv = cfg.get("boolean_values", {"true": ["true", "t", "yes", "y", "1"], "false": ["false", "f", "no", "n", "0"]})
        val = 1 if s in bv["true"] else 0 if s in bv["false"] else None
    else:
        val = num(raw)
        pct = spec.get("transform", {}).get("percent_of")
        if pct:
            base = num(row.get(pct)) or 0
            val = 100.0 * (val or 0) / base if base > 0 else None
    if val is None:
        return missing

    bands = spec.get("bands")
    if "band_sets" in spec:
        bands = spec["band_sets"][opts[spec["band_option"]]]
    norm = spec.get("normalize")
    if norm and opts["size_normalization"]:
        base = num(row.get(norm["divide_by"]))
        if not base:
            return missing
        val, bands = val / base * norm.get("multiply", 1), norm["bands"]
    return _modify(cfg, opts, spec, row, band_score(bands, val, missing))


def _modify(cfg, opts, spec, row, score):
    st = spec.get("stale")
    if st and opts.get(st["option"]):
        age = num(row.get(st["field"]))
        if age is not None and age > st["after_days"]:
            score = min(cfg["scale"]["missing_score"], score + st.get("add", 1))
    return score


def _percentile_scores(rows, field, seg_field):
    """Octile rank within segment (or all rows): top 12.5% -> 1 ... bottom 12.5% -> 8."""
    groups = {}
    for r in rows:
        if num(r.get(field)) is not None:
            groups.setdefault(r.get(seg_field) if seg_field else None, []).append(r)
    out = {}
    for g in groups.values():
        g = sorted(g, key=lambda r: -num(r[field]))
        for i, r in enumerate(g):
            out[id(r)] = min(8, 1 + math.floor(8 * i / len(g)))
    return out


def _wavg(pairs):
    tw = sum(w for _, w in pairs)
    return sum(s * w for s, w in pairs) / tw if tw else None


def score_rows(cfg: dict, rows: list[dict], method: str | None = None) -> list[dict]:
    """Score rows in place and return them. Adds <bucket>_score, overall_score, cluster
    plus private keys _fields, _buckets, _overall, _growth_ex_arr."""
    opts = options(cfg)
    W = cfg["bucket_weights"]
    missing = cfg["scale"]["missing_score"]
    rd = cfg.get("rounding", {"bucket_scores": 2, "overall_score": 3})
    v1 = "options" not in cfg
    pct = {}
    for f, spec in cfg["fields"].items():
        po = spec.get("percentile_option")
        if po and opts.get(po) == "percentile":
            pct[f] = _percentile_scores(rows, f, opts.get("segment_field"))
    for i, r in enumerate(rows):
        r["_i"] = i
        fs = {}
        for f, spec in cfg["fields"].items():
            fs[f] = pct[f].get(id(r), missing) if f in pct else field_score(cfg, opts, f, spec, r)
        r["_fields"] = fs
        b, bx = {}, {}
        for bk in W:
            def w(spec):
                return spec.get("weight", 1) if (v1 or opts["use_field_weights"]) else 1
            pairs = [(fs[f], w(s)) for f, s in cfg["fields"].items() if s["bucket"] == bk and fs[f] != NA]
            ex = [(fs[f], w(s)) for f, s in cfg["fields"].items() if s["bucket"] == bk and fs[f] != NA and f != "arr"]
            b[bk] = _wavg(pairs)
            if b[bk] is None and opts["empty_bucket"] == "score_missing":
                b[bk] = float(missing)
            bx[bk] = _wavg(ex) if ex else b[bk]
        r["_buckets"] = b
        for bk in W:
            r[f"{bk}_score"] = "" if b[bk] is None else round(b[bk], rd["bucket_scores"])
        live = [(b[k], wt) for k, wt in W.items() if b[k] is not None]
        r["_overall"] = _wavg(live) if live else float(missing)
        gx = [(bx[k], W[k]) for k in W if bx[k] is not None]
        r["_growth_ex_arr"] = _wavg(gx) if gx else float(missing)
        r["overall_score"] = round(r["_overall"], rd["overall_score"])
    assign_clusters(cfg, rows, method)
    return rows


def assign_clusters(cfg, rows, method=None):
    cl = cfg["cluster"]
    method = method or cl["method"]
    if method == "quartile":
        labels = cl.get("quartile", {}).get("labels", ["P1", "P2", "P3", "P4"])
        ranked = sorted(rows, key=lambda r: (r["_overall"], -(num(r.get("arr")) or 0), r["_i"]))
        size, rem = divmod(len(ranked), 4)
        i = 0
        for q in range(4):  # same split as Postgres ntile(4)
            for _ in range(size + (1 if q < rem else 0)):
                ranked[i]["cluster"] = labels[q]
                i += 1
    elif method == "growth_arr_2x2":
        c = cl["growth_arr_2x2"]
        med = statistics.median(r["_growth_ex_arr"] for r in rows)
        for r in rows:
            g = r["_growth_ex_arr"] <= med
            a = r["_fields"].get("arr") not in (None, NA) and r["_fields"]["arr"] <= c["arr_high_max_band"]
            r["cluster"] = {(True, True): "P1", (True, False): "P2", (False, True): "P3", (False, False): "P4"}[(g, a)]
    else:
        raise ValueError(f"unknown cluster method {method!r}")


def renewal_days(cfg, r):
    return num(r.get(cfg.get("focus", {}).get("renewal_field", "days_to_next_renewal")))


def focus_list(cfg, rows, count=None, window_days=None):
    f = cfg.get("focus", {})
    n = count or f.get("count", 3)
    win = window_days if window_days is not None else f.get("window_days", 120)
    ren = lambda r: renewal_days(cfg, r)
    key = lambda r: (r["overall_score"], ren(r), str(r.get("account_name", "")))
    inw = sorted([r for r in rows if ren(r) is not None and ren(r) <= win], key=key)
    if len(inw) >= n:
        return inw[:n]
    later = sorted([r for r in rows if ren(r) is not None and ren(r) > win], key=lambda r: (ren(r),) + key(r))
    return (inw + later)[:n]


def explain(cfg, r):
    W = cfg["bucket_weights"]
    live = [k for k in W if r["_buckets"][k] is not None]
    ranked = sorted(live, key=lambda k: (r["_buckets"][k], -W[k]))
    scored = [(k, v) for k, v in r["_fields"].items() if v != NA]
    return {
        "account": r.get("account_name"),
        "cluster": r["cluster"],
        "overall_score": r["overall_score"],
        "bucket_scores": {k: (None if r["_buckets"][k] is None else round(r["_buckets"][k], 2)) for k in W},
        "strongest_bucket": ranked[0] if ranked else None,
        "weakest_bucket": ranked[-1] if ranked else None,
        "best_fields": [{"field": k, "score": v} for k, v in sorted(scored, key=lambda kv: kv[1])[:3]],
        "weakest_fields": [{"field": k, "score": v} for k, v in sorted(scored, key=lambda kv: -kv[1])[:3]],
        "not_applicable": [k for k, v in r["_fields"].items() if v == NA],
        "play": cfg.get("plays", {}).get(r["cluster"]),
        "note": "Generated from the scores; not an AI judgement.",
    }
