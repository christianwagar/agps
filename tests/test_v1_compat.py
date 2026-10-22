"""The v1-compat config must reproduce the live (Supabase / 26-w.com) scores exactly."""
import csv
import os

import pytest

from agps import get_focus_list, score_accounts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1 = os.path.join(ROOT, "config", "agps.v1-compat.json")
DEMO = os.path.join(ROOT, "examples", "demo_accounts.csv")
EXPECTED = os.path.join(ROOT, "tests", "expected_v1_scores.csv")
COLS = ["gtm_propensity_score", "marketing_programmatic_engagement_score", "post_sales_score",
        "product_score", "down_and_distance_score", "overall_score"]


@pytest.fixture(scope="module")
def result():
    # Legacy quartile split kept for exact parity with the original live site.
    return score_accounts(DEMO, config=V1, cluster_method="quartile")


def test_all_40_scores_match_exactly(result):
    expected = {r["account_name"]: r for r in csv.DictReader(open(EXPECTED))}
    got = {r["account_name"]: r for r in result["accounts"]}
    assert set(expected) == set(got) and len(got) == 40
    for name, e in expected.items():
        for c in COLS:
            assert got[name][c] == pytest.approx(float(e[c]), abs=1e-9), (name, c)
        assert got[name]["cluster"] == e["cluster"], name


def test_clusters_are_quartiles(result):
    assert {k: v["accounts"] for k, v in result["clusters"].items()} == {"P1": 10, "P2": 10, "P3": 10, "P4": 10}
    assert result["accounts"][0]["account_name"] == "Stripe"


def test_focus_matches_live_site_quartile():
    assert [x["account"] for x in get_focus_list(DEMO, config=V1, cluster_method="quartile")] == ["Delta", "Coca-Cola", "Canva"]


def test_default_is_median_2x2_matching_preview():
    res = score_accounts(DEMO, config=V1)
    assert {k: v["accounts"] for k, v in res["clusters"].items()} == {"P1": 14, "P2": 6, "P3": 6, "P4": 14}
    c = {a["account_name"]: a["cluster"] for a in res["accounts"]}
    assert c["Airbnb"] == "P2" and c["iPhone"] == "P3" and c["Tesla"] == "P4" and c["Stripe"] == "P1"


def test_watch_floor_defaults_and_config():
    from agps import explain_account
    watch = sorted(n for n in ["Tesla", "Liquid Death", "Starbucks", "Spotify", "Sonos", "Salesforce", "Stripe"]
                   if explain_account(DEMO, n, config=V1)["watch"])
    assert watch == ["Liquid Death", "Salesforce", "Sonos", "Spotify", "Starbucks", "Tesla"]
    import copy, json
    cfg = json.load(open(V1)); cfg["cluster"]["watch"] = {"nrr_below": 0, "growth_worse_than": 7.0}
    assert explain_account(DEMO, "Spotify", config=cfg)["watch"] is False
    assert explain_account(DEMO, "Salesforce", config=cfg)["watch"] is True


def test_indicator_wording():
    from agps import explain_account
    e = explain_account(DEMO, "Tesla", config=V1)
    assert e["indicator"].startswith("Best signal: ") and "Strong" not in e["indicator"]
    p1 = explain_account(DEMO, "Stripe", config=V1)
    assert p1["growth_score"] < 4.3 and not p1["indicator"].startswith("Best signal")
