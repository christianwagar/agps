"""Regenerate parity fixtures from the Python reference engine: python3 test/make_fixtures.py"""
import copy, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
import agps
from agps.io import load_config

V1 = load_config(os.path.join(ROOT, "config", "agps.v1-compat.json"))
V2 = load_config(os.path.join(ROOT, "config", "agps.v2.json"))
def merged(base, over):
    c = copy.deepcopy(base)
    def m(t, s):
        for k, v in s.items():
            if isinstance(v, dict) and isinstance(t.get(k), dict): m(t[k], v)
            else: t[k] = v
    m(c, over); return c
W2515 = {"bucket_weights": {"gtm_propensity": 0.25, "marketing_programmatic_engagement": 0.15}}
CASES = [
  ("v1_demo", "config/agps.v1-compat.json", None, "examples/demo_accounts.csv", None),
  ("v1_demo_25_15", "config/agps.v1-compat.json", W2515, "examples/demo_accounts.csv", None),
  ("v1_demo_2x2", "config/agps.v1-compat.json", None, "examples/demo_accounts.csv", "growth_arr_2x2"),
  ("v2_sample", "config/agps.v2.json", None, "examples/sample_accounts.csv", None),
  ("v2_small", "config/agps.v2.json", None, "examples/v2_small_accounts.csv", None),
  ("v2_small_options", "config/agps.v2.json", {"options": {"renewal_direction": "runway_is_better", "not_applicable": "score_missing",
      "use_field_weights": True, "arr_scoring": "percentile", "stale_rag_penalty": True, "size_normalization": True}}, "examples/v2_small_accounts.csv", None),
  ("v2_small_2x2", "config/agps.v2.json", W2515, "examples/v2_small_accounts.csv", "growth_arr_2x2"),
]
out = []
for name, cfgp, over, csvp, method in CASES:
    cfg = merged(load_config(os.path.join(ROOT, cfgp)), over or {})
    path = os.path.join(ROOT, csvp)
    res = agps.score_accounts(path, config=cfg, cluster_method=method, include_inputs=False)
    res = {k: v for k, v in res.items() if not k.startswith("_")}
    names = [a["account_name"] for a in res["accounts"]]
    out.append({"name": name, "config": cfgp, "settings": over, "csv": csvp, "cluster_method": method,
                "score": res,
                "explain": {n: agps.explain_account(path, n, config=cfg, cluster_method=method) for n in names},
                "focus_5_60": agps.get_focus_list(path, config=cfg, count=5, window_days=60, cluster_method=method)})
json.dump(out, open(os.path.join(HERE, "fixtures.json"), "w"), indent=1)
print("wrote", len(out), "cases")
