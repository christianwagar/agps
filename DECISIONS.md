# Open decisions

These are choices the sheet review flagged and that the author hasn't settled yet. Each one is a toggle under `options:` in `config/agps.v2.yaml`. The defaults below are a starting point, not a recommendation set in stone.

| # | Option | Choices | Default | Why this default |
|---|---|---|---|---|
| D1 | `renewal_direction` | `sooner_is_better` · `runway_is_better` · `sweet_spot` | `sooner_is_better` | Matches the live v1 model and the focus-this-week rule. The sheet note leans toward runway (more time = better score); switch if that's the intent. `sweet_spot` treats 90–270 days as ideal. |
| D2 | `not_applicable` | `exclude` · `score_missing` | `exclude` | An account shouldn't be penalized for something it never bought (onboarding, PS hours, feature delivery). Blank data still scores 8. |
| D3 | `empty_bucket` | `renormalize` · `score_missing` | `renormalize` | If every field in a bucket is N/A, that bucket is dropped and the others are reweighted. |
| D4 | `size_normalization` | `true` · `false` | `false` | `true` scores NBEC and CSQL $ as % of ARR, so big accounts don't win twice. Off by default to stay close to the sheet's $ ladders. |
| D5 | `min_closed_opps` | integer | `3` | Win rates from 1–2 closed deals are noise; below the minimum the field is N/A. The count columns are `opp_closed_count` and `csql_closed_count`, and the check is skipped if they're absent. |
| D5b | `min_survey_responses` | integer | `3` | The same idea for NPS and CSAT (`nps_responses`, `support_survey_responses`). |
| D6 | Win-rate bands | sheet ladder · realistic | sheet ladder (≥100%→1, ≥90→2 … ≥40→7) | Kept as written. The review notes B2B win rates usually sit at 20–50%, so most accounts will score 6–8. A realistic ladder (≥60→1, 50, 40, 30, 25, 20, 10) is a one-line change in `tools/build_config.py`. |
| D7 | `use_field_weights` | `true` · `false` | `false` | Straight average inside buckets, as in v1. `true` applies per-field `weight` (`csm_pulse_rag` is pre-set to 2, per the sheet's "carry a good amount of weight"). |
| D8 | `arr_scoring` (+ `segment_field`) | `absolute` · `percentile` | `absolute` | The sheet gives a $ ladder but its reasoning asks for scoring relative to ATR within a segment. `percentile` ranks ARR in octiles within `segment_field` (or the whole file). |
| D9 | `stale_rag_penalty` | `true` · `false` | `false` | +1 band when the RAG is more than 30 days old. Needs `csm_pulse_days_since_update`. |
| — | Bucket weights | any, summing to 1 | 0.30 / 0.25 / 0.25 / 0.10 / 0.10 | Kept from the live model. |
| — | Cluster method | `quartile` · `growth_arr_2x2` | `quartile` | Always gives equal groups. |

## Fixes applied to the sheet

- Rows 4 and 17 say `$850,000,000` for band 2, and row 5 says `$850,000.000`. All three are read as **$850,000**.
- Row 4 "ARR | NRR" is split into `arr` ($) and `nrr` (%), since one $ threshold can't score a percentage.
- Rows 7 and 25 have overlapping activity bands (">10 then 2", ">15 then 3"). These are now exclusive: 0–10, 11–15, 16–20, 21–30, 31–45, 46–60, 61–90, >90.
- Where the sheet says "and so on", the remaining bands come from the column-E logic review.

## Not encoded yet

These items from the sheet review are not in the model yet: flags (expansion on >100% utilization, contact-loss on bounces), the registration-only webinar state, the active-unsubscribe newsletter state, NPS on a 0–10 scale, support-case normalization per 100 users, and pro-rating PS hours to the elapsed SOW term.
