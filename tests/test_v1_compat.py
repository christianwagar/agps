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
    return score_accounts(DEMO, config=V1)


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


def test_focus_matches_live_site():
    assert [x["account"] for x in get_focus_list(DEMO, config=V1)] == ["Delta", "Coca-Cola", "Canva"]
