#!/usr/bin/env python3
"""Generates config/agps.v2.yaml (commented) and its JSON twins from the field table below.

Source: the 'A-GPS Logic | Elements to Measure' sheet (column D thresholds) plus the column-E logic
review. The YAML is the file people edit; after editing YAML directly, run
`agps convert config/agps.v2.yaml config/agps.v2.json`. Re-running this script overwrites both.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = 8

def desc(*edges, floor=None):
    """Higher is better. edges = inclusive lower bounds for scores 1..n; below last -> n+1 (or floor)."""
    out, upper = [], None
    for i, lo in enumerate(edges):
        out.append({"min": lo, "max_exclusive": upper, "score": i + 1}); upper = lo
    out.append({"min": None, "max_exclusive": upper, "score": floor or len(edges) + 1})
    return out

def asc(*edges):
    """Lower is better. edges = exclusive upper bounds for scores 1..n; at/above last -> n+1."""
    out, lower = [], None
    for i, hi in enumerate(edges):
        out.append({"min": lower, "max_exclusive": hi, "score": i + 1}); lower = hi
    out.append({"min": lower, "max_exclusive": None, "score": len(edges) + 1})
    return out

def explicit(*triples):
    return [{"min": a, "max_exclusive": b, "score": s} for a, b, s in triples]

SECTIONS = {  # sheet section -> bucket (his mapping)
    "GTM": "gtm_propensity",
    "Marketing | Customer Programs Engagement": "marketing_programmatic_engagement",
    "Customer Success / Support / Services": "post_sales",
    "Product": "product",
    "Situation & Timing": "down_and_distance",
}

# (field, sheet_row, section, sheet element, spec, comment)
F = []
def add(field, row, section, element, spec, comment=None):
    spec = {"bucket": SECTIONS[section], "sheet_section": section, "sheet_row": row, "element": element, **spec}
    F.append((field, spec, comment))

WIN_LADDER = desc(100, 90, 80, 70, 60, 50, 40)  # his ladder: >=100%->1, >=90->2, >=80->3, continued by 10s
GTM_ACT = asc(11, 16, 21, 31, 46, 61, 91)       # 0-10d->1, 11-15->2, 16-20->3, 21-30, 31-45, 46-60, 61-90, >90->8
PCT_OF_ARR = desc(50, 30, 20, 10, 5, 2, 0.0001)  # % of ARR (size-normalized alternative)

add("arr", 4, "GTM", "ARR", {"type": "number", "direction": "higher_is_better", "unit": "USD",
    "bands": desc(1_000_000, 850_000, 500_000, 250_000, 150_000, 100_000, 75_000), "percentile_option": "arr_scoring"},
    "TYPO FIX: sheet says >=$850,000,000 for band 2; read as $850,000. Bands 3-8 fill in his 'and so on' using the review ladder. Split from NRR (row 4 combined ARR | NRR).")
add("nrr", 4, "GTM", "NRR", {"type": "number", "direction": "higher_is_better", "unit": "percent",
    "bands": desc(130, 120, 110, 105, 100, 95, 90)}, "Split out of row 4 'ARR | NRR'; a % can't share the $ ladder.")
add("nbec", 5, "GTM", "NBEC | NB (growth outside recurring revenue)", {"type": "number", "direction": "higher_is_better", "unit": "USD",
    "bands": desc(1_000_000, 850_000, 500_000, 250_000, 100_000, 50_000, 1),
    "normalize": {"divide_by": "arr", "multiply": 100, "bands": PCT_OF_ARR}},
    "TYPO FIX: sheet says >=$850,000.000 for band 2; read as $850,000. With size_normalization on, scored as % of ARR.")
add("opp_win_rate", 6, "GTM", "% of opportunities closed won", {"type": "number", "direction": "higher_is_better", "unit": "percent",
    "bands": WIN_LADDER, "min_count": {"field": "opp_closed_count", "option": "min_closed_opps"}},
    "His ladder (100/90/80 ...). N/A when opp_closed_count < min_closed_opps. See DECISIONS.md D6 on realistic bands.")
add("gtm_days_since_activity", 7, "GTM", "GTM activity in account (days since last)", {"type": "number", "direction": "lower_is_better", "unit": "days",
    "bands": GTM_ACT}, "Sheet bands overlapped (>10 and >15); made exclusive.")

MK = "Marketing | Customer Programs Engagement"
add("field_event_status", 8, MK, "Attending field marketing events", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"attended_3plus": 1, "attended_2": 2, "attended_1": 3, "registered_no_show": 5, "invited_not_registered": 6, "never_invited": "na"}})
add("conference_status", 9, MK, "Attending annual conference", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"in_person_2plus": 1, "in_person_1": 2, "virtual": 3, "registered_no_show": 5, "not_registered": 6, "not_invited": "na"}})
add("webinars_attended_12m", 10, MK, "Attending webinars", {"type": "number", "direction": "higher_is_better", "unit": "count",
    "bands": explicit((6, None, 1), (4, 6, 2), (3, 4, 3), (2, 3, 4), (1, 2, 5), (None, 1, 7))},
    "0 attended -> 7. The review's 'registered only -> 6' needs a registration flag the input doesn't carry yet.")
add("relationship_nps", 11, MK, "NPS score(s)", {"type": "number", "direction": "higher_is_better", "unit": "NPS -100..100",
    "bands": desc(70, 50, 30, 10, 0, -20, -40), "min_count": {"field": "nps_responses", "option": "min_survey_responses"}})
add("newsletter_subscribed_pct", 12, MK, "Subscribed to newsletter(s)", {"type": "number", "direction": "higher_is_better", "unit": "percent of contacts",
    "bands": explicit((50, None, 1), (30, 50, 2), (20, 30, 3), (10, 20, 4), (0.0001, 10, 5), (None, 0.0001, 6))},
    "His yes/no became % of contacts. 'Active unsubscribe, none left -> 7' is not encoded (needs an unsubscribe flag).")
add("newsletter_open_rate", 13, MK, "Opening newsletter(s)", {"type": "number", "direction": "higher_is_better", "unit": "percent (90d)",
    "bands": explicit((50, None, 1), (40, 50, 2), (30, 40, 3), (20, 30, 4), (10, 20, 5), (0.0001, 10, 6), (None, 0.0001, 7)),
    "overrides": [{"field": "newsletter_all_bounced", "op": "eq", "value": 1, "score": 8}]},
    "All bounced -> 8 via newsletter_all_bounced (1/0).")
add("advocacy_level", 14, MK, "Customer advocacy / positive word of mouth", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"conference_speaker": 1, "video_or_case_study": 2, "community_story": 3, "reference_or_review": 4, "agreed_not_done": 5, "none": 6, "declined_or_detractor": 8}})
add("community_champion", 15, MK, "Customer champion (Discord, community, marketplace)", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"contributor_3plus_channels": 1, "channels_4_5": 2, "channels_3": 3, "channels_2": 4, "channels_1": 5, "passive_members": 6, "none": 7}},
    "Levels as in the review; 'channels_4_5' without a contribution ranks below 'contributor + 3 channels'.")

PS = "Customer Success / Support / Services"
add("success_plan_tier", 16, PS, "Success / support plan tier and spend", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"top": 1, "second": 3, "third": 5, "standard": 7, "none": 8}})
add("csql_pipeline", 17, PS, "CSQL / PSQL pipeline $", {"type": "number", "direction": "higher_is_better", "unit": "USD (12m)",
    "bands": desc(1_000_000, 850_000, 500_000, 250_000, 150_000, 100_000, 1),
    "normalize": {"divide_by": "arr", "multiply": 100, "bands": PCT_OF_ARR}},
    "TYPO FIX: sheet says >=$850,000,000 for band 2; read as $850,000.")
add("csql_win_rate", 18, PS, "CSQL / PSQL win rate", {"type": "number", "direction": "higher_is_better", "unit": "percent",
    "bands": WIN_LADDER, "min_count": {"field": "csql_closed_count", "option": "min_closed_opps"}})
add("onboarding_delivered", 19, PS, "Onboarding delivered (if applicable)", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"fully_delivered": 1, "in_progress": 3, "partially_delivered": 5, "not_delivered": 8, "not_purchased": "na"}})
add("onboarding_completed", 20, PS, "Onboarding completed", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"completed_all_activated": 1, "completed_most_activated": 3, "partially_completed": 5, "not_started": 8}})
add("activation_pct", 21, PS, "Adoption milestones / product activation", {"type": "number", "direction": "higher_is_better", "unit": "percent",
    "bands": desc(100, 90, 80, 70, 60, 50, 25)})
add("utilization_pct", 22, PS, "Utilization benchmarks", {"type": "number", "direction": "higher_is_better", "unit": "percent",
    "bands": desc(100, 90, 80, 70, 60, 50, 30)}, "Over 100% scores 1; the review's expansion flag is not emitted yet.")
add("value_realization", 23, PS, "Value realization / value delivery", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"all_met": 1, "mostly_met": 3, "partially_met": 5, "none_met": 8, "no_success_plan": "na"}})
add("csm_pulse_rag", 24, PS, "Customer success RAG / pulse", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"green": 1, "amber": 4, "yellow": 4, "red": 8}, "weight": 2,
    "stale": {"field": "csm_pulse_days_since_update", "after_days": 30, "add": 1, "option": "stale_rag_penalty"}},
    "weight 2 ('carry a good amount of weight') only applies when use_field_weights is on.")
add("csm_days_since_activity", 25, PS, "Last CS activity (days since)", {"type": "number", "direction": "lower_is_better", "unit": "days",
    "bands": GTM_ACT}, "Same overlap fix as row 7.")
add("support_cases_12m", 26, PS, "# of support cases", {"type": "number", "direction": "lower_is_better", "unit": "count (12m)",
    "bands": asc(2, 5, 8, 11, 16, 21, 31)}, "Raw count: <=1->1, 2-4->2, 5-7, 8-10, 11-15, 16-20, 21-30, >30->8.")
add("sla_max_overrun_hours", 27, PS, "SLA adherence / breaches", {"type": "number", "direction": "lower_is_better", "unit": "hours (max overrun, 12m)",
    "bands": explicit((None, 1, 2), (1, 4, 3), (4, 8, 4), (8, 24, 5), (24, 72, 6), (72, None, 7)),
    "overrides": [{"field": "sla_breaches_12m", "op": "eq", "value": 0, "score": 1},
                  {"field": "sla_breaches_12m", "op": "gte", "value": 5, "score": 8}]},
    "0 breaches -> 1 and 5+ breaches -> 8 (overrides), via sla_breaches_12m.")
add("median_resolution_hours", 28, PS, "Time to case resolution", {"type": "number", "direction": "lower_is_better", "unit": "hours",
    "bands": [{"min": None, "max": 4, "score": 1}, {"min": None, "max": 8, "score": 2}, {"min": None, "max": 24, "score": 3},
              {"min": None, "max": 48, "score": 4}, {"min": None, "max": 72, "score": 5}, {"min": None, "max": 120, "score": 6},
              {"min": None, "max": 240, "score": 7}, {"min": None, "max": None, "score": 8}],
    "na_if": [{"field": "support_cases_12m", "op": "eq", "value": 0}]},
    "Inclusive upper edges (<=4h -> 1, >4-8h -> 2 ...). His sheet column says avg days; hours used for same-day granularity.")
add("support_csat_pct", 29, PS, "Support ticket CSAT / NPS", {"type": "number", "direction": "higher_is_better", "unit": "CSAT percent",
    "bands": desc(95, 90, 85, 80, 70, 60, 50), "min_count": {"field": "support_survey_responses", "option": "min_survey_responses"}})
add("ps_engagement", 30, PS, "Professional services engagement", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"active_12m": 1, "purchased_12_36m": 3, "purchased_over_36m": 5, "never": 6}})
add("ps_hours_used_pct", 31, PS, "% of service hours delivered vs purchased", {"type": "number", "direction": "higher_is_better", "unit": "percent",
    "bands": desc(90, 75, 60, 45, 30, 15, 0.0001),
    "na_if": [{"field": "ps_hours_purchased", "op": "eq", "value": 0}]}, "N/A when ps_hours_purchased = 0.")

add("feature_requests_12m", 32, "Product", "# of product feature requests", {"type": "number", "direction": "higher_is_better", "unit": "count",
    "bands": explicit((10, None, 1), (7, 10, 2), (5, 7, 3), (3, 5, 4), (None, 3, 5)), "missing": "na"},
    "0 requests -> 5 (neutral, 'not a big detractor'); blank = not tracked = N/A.")
add("feature_requests_delivered_pct", 33, "Product", "# of product feature requests delivered", {"type": "number", "direction": "higher_is_better", "unit": "percent (24m)",
    "bands": explicit((100, None, 1), (75, 100, 2), (50, 75, 3), (25, 50, 5), (0.0001, 25, 6), (None, 0.0001, 7)),
    "na_if": [{"field": "feature_requests_12m", "op": "eq", "value": 0}]})

ST = "Situation & Timing"
add("days_to_next_event", 34, ST, "Days to next renewal / next opp close", {"type": "number", "direction": "set by renewal_direction", "unit": "days",
    "band_option": "renewal_direction", "band_sets": {
        "sooner_is_better": explicit((None, 0, 8), (0, 90, 1), (90, 150, 2), (150, 210, 3), (210, 270, 4), (270, 365, 5), (365, 540, 6), (540, 730, 7), (730, None, 8)),
        "runway_is_better": explicit((None, 0, 8), (0, 30, 7), (30, 60, 6), (60, 90, 5), (90, 120, 4), (120, 150, 3), (150, 180, 2), (180, None, 1)),
        "sweet_spot": explicit((None, 0, 8), (0, 30, 7), (30, 60, 5), (60, 90, 3), (90, 270, 1), (270, 365, 2), (365, None, 4))}},
    "Input = min(days to renewal, days to next open opp close). Past due -> 8 in every mode. sooner_is_better matches the live v1 model.")
add("stakeholder_engagement", 35, ST, "Key stakeholder / decision-maker involvement", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"exec_engaged_90d": 1, "champion_plus_dm_identified": 3, "champion_only": 5, "passive": 6, "absent_or_champion_left": 8}})
add("tenure_years", 36, ST, "# of years as a customer", {"type": "number", "direction": "higher_is_better", "unit": "years",
    "bands": desc(10, 8, 6, 5, 4, 3, 1)})
add("financial_signal", 37, ST, "10-K / major financial news", {"type": "ordinal", "direction": "higher_is_better",
    "levels": {"strong_growth": 1, "positive": 2, "neutral": 4, "mixed": 5, "negative": 7, "severe": 8, "no_data": "na"}})

OPTIONS = [
    ("renewal_direction", "sooner_is_better", "D1. sooner_is_better | runway_is_better | sweet_spot. Default matches the live model; his sheet note prefers runway."),
    ("not_applicable", "exclude", "D2. exclude (drop N/A fields from the bucket average) | score_missing (N/A scores 8)."),
    ("empty_bucket", "renormalize", "D3. When every field in a bucket is N/A/blank-NA: renormalize (drop the bucket, reweight the rest) | score_missing (bucket = 8)."),
    ("size_normalization", False, "D4. true = score NBEC and CSQL $ as % of ARR so big accounts don't win twice."),
    ("min_closed_opps", 3, "D5. Win-rate fields are N/A below this many closed opps/CSQLs."),
    ("min_survey_responses", 3, "D5b. NPS / CSAT are N/A below this many responses."),
    ("use_field_weights", False, "D7. true = apply per-field 'weight' inside buckets (e.g. csm_pulse_rag = 2). false = straight average."),
    ("arr_scoring", "absolute", "D8. absolute ($ ladder) | percentile (octile rank within segment_field or the whole file)."),
    ("segment_field", None, "D8b. Optional column used to group accounts for percentile ARR scoring."),
    ("stale_rag_penalty", False, "D9. true = RAG not updated in 30+ days gets +1 band (needs csm_pulse_days_since_update)."),
]

def build():
    cfg = {
        "name": "A-GPS v2 (Account Growth Propensity Scoring)", "version": "2.0.0",
        "scale": {"best": 1, "worst": 8, "missing_score": M},
        "options": {k: v for k, v, _ in OPTIONS},
        "bucket_weights": {"gtm_propensity": 0.30, "post_sales": 0.25, "down_and_distance": 0.25,
                           "marketing_programmatic_engagement": 0.10, "product": 0.10},
        "section_to_bucket": SECTIONS,
        "rounding": {"bucket_scores": 2, "overall_score": 3},
        "cluster": {"method": "quartile",
                    "quartile": {"labels": ["P1", "P2", "P3", "P4"]},
                    "growth_arr_2x2": {"arr_high_max_band": 4}},
        "focus": {"count": 3, "window_days": 120, "renewal_field": "days_to_next_event"},
        "plays": {"P1": "Expand now: exec-aligned expansion, multi-thread, bring in AE + SE",
                  "P2": "Grow into it: land-and-expand, programs, close the weakest bucket first",
                  "P3": "Protect and re-ignite: retention first, fix health, find the next use case",
                  "P4": "Scale and monitor: digital or pooled CS, watch for signals"},
        "fields": {f: s for f, s, _ in F},
    }
    return cfg

def y(v):
    return json.dumps(v)  # JSON scalars/flow collections are valid YAML

def to_yaml(cfg):
    L = ["# A-GPS v2 config. Generated by tools/build_config.py from the 'A-GPS Logic | Elements to Measure' sheet.",
         "# Golf-style: 1 = best, 8 = worst, blank = 8. Bands: min (inclusive), max_exclusive or max (inclusive); null = open.",
         "# The first band that contains the value wins. Ordinal 'levels' map a label straight to a score ('na' = not applicable).",
         "# After editing, regenerate the JSON twin: agps convert config/agps.v2.yaml config/agps.v2.json", ""]
    for k in ("name", "version"):
        L.append(f"{k}: {y(cfg[k])}")
    L.append(f"scale: {y(cfg['scale'])}")
    L += ["", "# Open decisions (see DECISIONS.md). Change a value here; every option has a working default."]
    L.append("options:")
    for k, v, c in OPTIONS:
        L += [f"  # {c}", f"  {k}: {y(v)}"]
    L += ["", "# Bucket weights (sum 1.0). Kept from the live model."]
    L.append("bucket_weights:")
    L += [f"  {k}: {v}" for k, v in cfg["bucket_weights"].items()]
    L += ["", "# His sheet sections -> buckets."]
    L.append("section_to_bucket:")
    L += [f"  {y(k)}: {v}" for k, v in SECTIONS.items()]
    for k in ("rounding", "cluster", "focus", "plays"):
        L += ["", f"{k}: {y(cfg[k])}"]
    L += ["", "fields:"]
    for f, s, c in F:
        L.append("")
        if c:
            L += [f"  # {line}" for line in c.split("\n")]
        L.append(f"  {f}:")
        for k, v in s.items():
            if k in ("bands",) and isinstance(v, list):
                L.append(f"    {k}:")
                L += [f"      - {y(b)}" for b in v]
            elif k == "band_sets":
                L.append(f"    {k}:")
                for name, bs in v.items():
                    L.append(f"      {name}:")
                    L += [f"        - {y(b)}" for b in bs]
            else:
                L.append(f"    {k}: {y(v)}")
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    cfg = build()
    open(os.path.join(ROOT, "config", "agps.v2.yaml"), "w").write(to_yaml(cfg))
    for p in ("config/agps.v2.json", "src/agps/data/agps.v2.json"):
        os.makedirs(os.path.dirname(os.path.join(ROOT, p)), exist_ok=True)
        with open(os.path.join(ROOT, p), "w") as fh:
            json.dump(cfg, fh, indent=2); fh.write("\n")
    print(f"{len(F)} fields written")
