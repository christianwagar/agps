import json
import os

import pytest

from agps import engine, explain_account, get_focus_list, score_accounts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = os.path.join(ROOT, "config", "agps.v2.json")
V2_SMALL = os.path.join(ROOT, "examples", "v2_small_accounts.csv")


def cfg(**opts):
    c = json.load(open(V2))
    c["options"].update(opts)
    return c


def fs(c, field, row):
    return engine.field_score(c, engine.options(c), field, c["fields"][field], row)


@pytest.mark.parametrize("arr,expected", [
    (1_000_000, 1), (999_999.99, 2), (850_000, 2), (849_999, 3), (500_000, 3),
    (250_000, 4), (150_000, 5), (100_000, 6), (75_000, 7), (74_999, 8), (0, 8)])
def test_arr_band_edges_desc(arr, expected):
    assert fs(cfg(), "arr", {"arr": arr}) == expected


@pytest.mark.parametrize("days,expected", [(0, 1), (10, 1), (11, 2), (15, 2), (16, 3), (30, 4), (31, 5), (90, 7), (91, 8)])
def test_activity_band_edges_asc_no_overlap(days, expected):
    assert fs(cfg(), "gtm_days_since_activity", {"gtm_days_since_activity": days}) == expected


@pytest.mark.parametrize("hours,expected", [(4, 1), (4.01, 2), (8, 2), (24, 3), (240, 7), (241, 8)])
def test_inclusive_upper_edges(hours, expected):
    assert fs(cfg(), "median_resolution_hours", {"median_resolution_hours": hours, "support_cases_12m": 3}) == expected


def test_missing_scores_8():
    assert fs(cfg(), "nrr", {}) == 8
    assert fs(cfg(), "advocacy_level", {"advocacy_level": "unknown_label"}) == 8


def test_currency_and_percent_strings():
    assert fs(cfg(), "arr", {"arr": "$1,200,000"}) == 1
    assert fs(cfg(), "nrr", {"nrr": "131%"}) == 1


@pytest.mark.parametrize("mode", ["exclude", "score_missing"])
def test_not_applicable_handling(mode):
    c = cfg(not_applicable=mode)
    want = engine.NA if mode == "exclude" else 8
    assert fs(c, "onboarding_delivered", {"onboarding_delivered": "not_purchased"}) == want
    assert fs(c, "ps_hours_used_pct", {"ps_hours_used_pct": "", "ps_hours_purchased": 0}) == want
    assert fs(c, "feature_requests_12m", {}) == want  # not tracked
    assert fs(c, "opp_win_rate", {"opp_win_rate": 100, "opp_closed_count": 1}) == want  # tiny sample


def test_na_excluded_from_bucket_average():
    base = {"account_name": "X", "arr": 1, "onboarding_completed": "completed_all_activated"}
    excl = engine.score_rows(cfg(), [dict(base, onboarding_delivered="not_purchased")])[0]
    s8 = engine.score_rows(cfg(not_applicable="score_missing"), [dict(base, onboarding_delivered="not_purchased")])[0]
    assert excl["_fields"]["onboarding_delivered"] == engine.NA
    assert excl["_buckets"]["post_sales"] < s8["_buckets"]["post_sales"]


def test_empty_bucket_renormalizes_or_scores_8():
    row = {"account_name": "X", "arr": 1_000_000, "feature_requests_delivered_pct": "n/a"}
    r = engine.score_rows(cfg(), [dict(row)])[0]
    assert r["_buckets"]["product"] is None  # both product fields N/A
    r8 = engine.score_rows(cfg(empty_bucket="score_missing"), [dict(row)])[0]
    assert r8["_buckets"]["product"] == 8


def test_min_closed_opps_toggle():
    row = {"opp_win_rate": 100, "opp_closed_count": 2}
    assert fs(cfg(min_closed_opps=3), "opp_win_rate", row) == engine.NA
    assert fs(cfg(min_closed_opps=2), "opp_win_rate", row) == 1


def test_renewal_direction_toggle():
    row = {"days_to_next_event": 20}
    assert fs(cfg(renewal_direction="sooner_is_better"), "days_to_next_event", row) == 1
    assert fs(cfg(renewal_direction="runway_is_better"), "days_to_next_event", row) == 7
    assert fs(cfg(renewal_direction="sweet_spot"), "days_to_next_event", {"days_to_next_event": 180}) == 1
    assert fs(cfg(), "days_to_next_event", {"days_to_next_event": -5}) == 8


def test_size_normalization_toggle():
    row = {"nbec": 100_000, "arr": 200_000}  # 50% of ARR
    assert fs(cfg(), "nbec", row) == 5
    assert fs(cfg(size_normalization=True), "nbec", row) == 1


def test_field_weights_toggle():
    row = {"account_name": "X", "csm_pulse_rag": "red", "onboarding_completed": "completed_all_activated"}
    off = engine.score_rows(cfg(), [dict(row)])[0]["_buckets"]["post_sales"]
    on = engine.score_rows(cfg(use_field_weights=True), [dict(row)])[0]["_buckets"]["post_sales"]
    assert on > off


def test_sla_overrides():
    c = cfg()
    assert fs(c, "sla_max_overrun_hours", {"sla_breaches_12m": 0, "sla_max_overrun_hours": 99}) == 1
    assert fs(c, "sla_max_overrun_hours", {"sla_breaches_12m": 6, "sla_max_overrun_hours": 0.5}) == 8
    assert fs(c, "sla_max_overrun_hours", {"sla_breaches_12m": 2, "sla_max_overrun_hours": 5}) == 4


def test_stale_rag_penalty():
    row = {"csm_pulse_rag": "green", "csm_pulse_days_since_update": 45}
    assert fs(cfg(), "csm_pulse_rag", row) == 1
    assert fs(cfg(stale_rag_penalty=True), "csm_pulse_rag", row) == 2


def test_arr_percentile_mode():
    rows = [{"account_name": str(i), "arr": i * 1000} for i in range(1, 9)]
    out = engine.score_rows(cfg(arr_scoring="percentile"), rows)
    assert sorted(r["_fields"]["arr"] for r in out) == list(range(1, 9))


def test_v2_end_to_end_and_api():
    res = score_accounts(V2_SMALL)
    assert res["scored"] == 8 and res["missing_fields"] == []
    assert res["accounts"][0]["account_name"] == "Northwind"
    assert res["accounts"][-1]["account_name"] == "Adatum"
    assert sum(v["accounts"] for v in res["clusters"].values()) == 8
    ex = explain_account(V2_SMALL, "fabrikam")
    assert "onboarding_delivered" in ex["not_applicable"] and ex["cluster"] in {"P3", "P4"}
    assert len(get_focus_list(V2_SMALL, count=2)) == 2


def test_two_by_two():
    res = score_accounts(V2_SMALL, cluster_method="growth_arr_2x2")
    assert {a["cluster"] for a in res["accounts"]} <= {"P1", "P2", "P3", "P4"}


def test_mapping_renames_headers():
    text = "Account Name,Annual Recurring Revenue\nAcme,2000000\n"
    res = score_accounts(text, mapping={"Account Name": "account_name", "Annual Recurring Revenue": "arr"})
    assert res["accounts"][0]["account_name"] == "Acme"


def test_yaml_and_json_twins_match():
    yaml = pytest.importorskip("yaml")
    assert yaml.safe_load(open(os.path.join(ROOT, "config", "agps.v2.yaml"))) == json.load(open(V2))
