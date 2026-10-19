---
name: agps-account-growth-propensity
description: Rank a book of customer accounts with A-GPS golf-style scoring (1 = best, 8 = worst), produce P1-P4 clusters and a focus-this-week list, and explain any account. Use when someone uploads an account CSV or asks which accounts to prioritize.
---

# A-GPS for Grok Bot

## When to use
- Someone uploads an account export, or points to one in Drive or email, and asks for priorities, expansion candidates or risk.
- A recurring routine: "Every Monday, score the latest account export and send the P1 list and focus accounts."

## How to run
1. Put the uploaded CSV on the box. If the A-GPS repo isn't there yet, clone it or unzip it into the workspace.
2. Check the headers against `config/agps.v2.json` → `fields`. If they don't match, write a mapping JSON (`{"Their header": "agps_field"}`) and show it to the user before you score.
3. Run `PYTHONPATH=src python3 -m agps score <file> --map <mapping> -o scored.csv --json`.
4. For a single account, run `python3 -m agps explain <file> "<name>"`. For the weekly list, run `python3 -m agps focus <file>`.
5. Alternatively, connect `integrations/mcp-server` and call `score_accounts`, `explain_account` and `get_focus_list` directly.

## Report back
- Show the counts per cluster and the total ARR, the top three accounts in P1, and the focus list with days to renewal.
- List the fields the file didn't have, since they scored 8 or were treated as N/A.
- For each cluster, give the play: P1 expand now, P2 grow into it, P3 protect and re-ignite, P4 scale and monitor.
- Hand back the scored CSV as a file.

## Guardrails
- Treat account data as confidential. Don't post it or send it anywhere unless the user asks.
- The explanations are generated from the scores. Label them that way.
- Change config options only when the user asks. See DECISIONS.md for what each one does.
