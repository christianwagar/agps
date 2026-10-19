<p align="center"><img src="docs/assets/banner.svg" alt="A-GPS | Account Growth Propensity Scoring" width="100%"></p>

<p align="center">
<a href="https://26-w.com/notes/account-growth-propensity/"><img src="https://img.shields.io/badge/LIVE_DEMO-26--W.COM-000000?style=flat-square" alt="Live demo"></a>
<img src="https://img.shields.io/badge/TESTS-46_PASSING-000000?style=flat-square" alt="Tests">
<img src="https://img.shields.io/badge/PYTHON-3.9+-666666?style=flat-square" alt="Python">
<img src="https://img.shields.io/badge/MCP-READY-666666?style=flat-square" alt="MCP">
<a href="LICENSE"><img src="https://img.shields.io/badge/LICENSE-MIT-e5e5e5?style=flat-square&labelColor=000000" alt="MIT"></a>
</p>

<p align="center"><b>[ <a href="https://26-w.com/notes/account-growth-propensity/">READ THE WRITEUP</a> ]</b> &nbsp; <b>[ <a href="METHODOLOGY.md">METHODOLOGY</a> ]</b> &nbsp; <b>[ <a href="integrations/">SKILLS + MCP</a> ]</b></p>

---

# A-GPS: Account Growth Propensity Scoring

A-GPS ranks a book of customer accounts by how ready each one is to grow. It turns CRM and customer-success signals into one score per account, groups accounts into P1–P4, and suggests which few to focus on this week.

It was designed by **Christian Wagar**. Live demo with 40 fictional accounts: **https://26-w.com/notes/account-growth-propensity/**

> [!IMPORTANT]
> **This is a framework, not a one-size-fits-all answer.** The bands and weights here (ARR thresholds, win rates, renewal timing, bucket weights) were tuned for one book of business. Dial them in for yours: your customer spend levels, deal sizes, risk appetite, sales motion, and how clean your data is. A $250K account is "big" for some companies and "small" for others.

### How to tune it

All the settings live in one file: [`config/agps.v2.yaml`](config/agps.v2.yaml). Work through this list:

1. **ARR and $ bands.** Move the ARR, NBEC and pipeline ladders so your biggest customers land in bands 1–2 and your smallest in 7–8.
2. **Win rates.** If a 40% win rate is great in your world, shift the win-rate bands down.
3. **Renewal timing.** Pick `renewal_direction`: `sooner_is_better`, `runway_is_better`, or `sweet_spot`.
4. **Bucket weights.** Change `bucket_weights` to match what drives growth for you (they should add up to 1.0).
5. **Data quality.** If a signal is patchy or self-reported, give its bucket less weight or leave the field blank.
6. **Check the result.** Rescore and ask: do the P1s look like accounts your team would actually bet on? If not, adjust and repeat.

Using an LLM instead of code? Just tell it your thresholds in plain English (see [the universal prompt](integrations/any-llm/PROMPT.md)).

## Start here

| You are… | Start with | What you get |
|---|---|---|
| **CS / RevOps leader** | [METHODOLOGY.md](METHODOLOGY.md) · [DECISIONS.md](DECISIONS.md) | Every signal, band, and weight in plain English. Tune it in a spreadsheet. |
| **Using Claude, ChatGPT, Gemini, Grok or any LLM** | [integrations/any-llm/PROMPT.md](integrations/any-llm/PROMPT.md) | One copy-paste prompt. Paste it plus your account CSV, get scores, P1–P4, and the why. |
| **Claude or Grok power user** | [integrations/claude-skill](integrations/claude-skill/) · [integrations/grok-skill](integrations/grok-skill/) | Installable skills that do the same thing. |
| **Developer / builder** | [Quickstart](#quickstart) · [MCP server](integrations/mcp-server/) | Zero-dependency Python package, CLI, and an MCP server. |

---

## How the scoring works

A-GPS scores like golf: **lower is better**.

1. Every signal gets a band score from **1 (best) to 8 (worst)**. A blank value scores 8, so missing data never gets a free pass. A signal that doesn't apply (for example, onboarding was never purchased) is marked N/A and left out by default.
2. Signals roll up into five buckets. Each bucket score is the average of its signals.
3. The overall score is a weighted average of the buckets.
4. Accounts are split into quartiles: **P1** = best 25%, down to **P4**. A growth × ARR 2×2 is also available.
5. **Focus this week** = the lowest overall scores among accounts with a renewal or opportunity close within 120 days.

| Bucket | Weight | What it covers |
|---|---|---|
| GTM propensity | 30% | ARR, NRR, expansion pipeline, win rate, sales activity |
| Post-sales | 25% | Success plan, CSQLs, onboarding, adoption, value, CSM pulse, support, services |
| Down-and-distance | 25% | Timing and context: next renewal/close, stakeholders, tenure, financial news |
| Marketing & programs | 10% | Events, conference, webinars, NPS, newsletters, advocacy, community |
| Product | 10% | Feature requests submitted and delivered |

The full field-by-field table is in [METHODOLOGY.md](METHODOLOGY.md), and the open choices are in [DECISIONS.md](DECISIONS.md).

## Quickstart

```bash
pip install -e .                       # no runtime dependencies; add [yaml] to read YAML configs
agps score examples/v2_small_accounts.csv -o scored.csv
agps explain examples/v2_small_accounts.csv Northwind
agps focus examples/v2_small_accounts.csv

# The model behind the live demo (v1):
agps score examples/demo_accounts.csv --config config/agps.v1-compat.json

# Your own CRM export, with a header map:
agps score my_export.csv --map examples/salesforce_mapping.json
```

Without installing: `PYTHONPATH=src python -m agps score ...`

```python
from agps import score_accounts, explain_account, get_focus_list
res = score_accounts("accounts.csv", config="config/agps.v2.yaml", mapping={"Account Name": "account_name"})
res["clusters"]["P1"], res["focus_this_week"]
explain_account("accounts.csv", "Northwind")
```

## Repo layout

```
config/          agps.v2.yaml (edit this) + agps.v2.json twin, agps.v1-compat.json (live demo model)
src/agps/        engine, CLI, Python API (stdlib only)
tests/           pytest: v1 exact-match, band edges, N/A handling, option toggles
examples/        fictional demo CSVs, Salesforce mapping, sample scored output
integrations/    claude-skill/, grok-skill/, mcp-server/ (stdio)
tools/           build_config.py (sheet → config), gen_methodology.py
```

## Use it from an assistant

- **Claude:** copy `integrations/claude-skill/` together with `src/` and `config/` into a skill folder.
- **Grok Bot:** add `integrations/grok-skill/SKILL.md` as a skill, or connect the MCP server.
- **MCP (Claude Desktop, Cursor, Grok Bot, others):** see [integrations/mcp-server/README.md](integrations/mcp-server/README.md). It provides the tools `score_accounts`, `explain_account` and `get_focus_list`.

## Tuning

Edit `config/agps.v2.yaml`, run `agps convert config/agps.v2.yaml config/agps.v2.json`, then re-score. Check how much the cluster mix moved and gut-check a few accounts you know well.

---

## License

MIT. See [LICENSE](LICENSE). All sample data is fictional.

---

<p align="center"><sub>BUILT BY <a href="https://26-w.com">CHRISTIAN WAGAR</a> · 26-W</sub></p>
