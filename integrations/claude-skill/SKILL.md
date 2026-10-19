---
name: agps-account-growth-propensity
description: Score customer accounts for expansion readiness with A-GPS golf-style scoring (1 = best, 8 = worst), group them into P1-P4, explain any account, and list the accounts to focus on this week. Use when the user shares an account export (CRM, CS platform, spreadsheet) and asks which accounts to prioritize, expand, protect or review.
---

# A-GPS account growth propensity

## When to use
- The user shares an account list or CSV and asks where to focus, who's ready to expand, or who's at risk.
- Weekly or monthly account reviews, book or territory planning, or getting CS, sales and support onto one list.
- Don't use it to forecast revenue. A-GPS ranks accounts; it doesn't predict dollars.

## Setup
This skill folder should contain `src/agps/` and `config/` from the A-GPS repo. The engine needs only the Python standard library. YAML configs need PyYAML; the JSON twin works without it.

## Inputs
- A CSV with one row per account. `account_name` is required. `arr` and `days_to_next_event` (v2) or `days_to_next_renewal` (v1) are strongly recommended.
- Any of the fields listed in `config/agps.v2.json` → `fields`. Blank values score 8, and fields marked N/A are excluded. Tell the user which fields were missing from their file.
- If the user's headers differ, build a mapping `{"Their header": "agps_field"}` and pass it with `--map` (see `examples/salesforce_mapping.json`). Ordinal fields expect the labels listed under each field's `levels`.

## Run
```bash
PYTHONPATH=src python -m agps score accounts.csv --map mapping.json -o scored.csv --json
PYTHONPATH=src python -m agps explain accounts.csv "Account Name"
PYTHONPATH=src python -m agps focus accounts.csv --count 3
```
Use `--config config/agps.v1-compat.json` for the simpler v1 model, and `--cluster-method growth_arr_2x2` for the 2×2.

## Read the results
- The overall score runs from 1 (best) to 8, and lower means higher priority. Each bucket score shows where the account is strong or weak.
- Clusters are quartiles of the overall score.

| Cluster | Meaning | Play |
|---|---|---|
| P1 | Healthy, engaged, momentum | Expand now: hold an exec-aligned expansion conversation, multi-thread, bring in AE + SE, and anchor on value already delivered. |
| P2 | Solid with one or two gaps | Grow into it: run land-and-expand and enablement, and close the weakest bucket before pitching. |
| P3 | Mixed health or engagement | Protect and re-ignite: put retention first, fix support or adoption, re-map stakeholders, and find the next use case. |
| P4 | Low signal or at risk | Scale and monitor: use digital or pooled CS and automated check-ins, and watch for signals. |

When you explain an account, name its strongest and weakest bucket and its worst fields, then give the play. Say that the explanation is generated from the scores. Don't invent data the file doesn't contain.

## Tuning
The choices are in the config's `options` (renewal direction, N/A handling, size normalization, minimum closed opps, field weights). Change only what the user asks for, then re-run and report how the clusters moved.
