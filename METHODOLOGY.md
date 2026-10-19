# Methodology

Generated from `config/agps.v2.json` by `tools/gen_methodology.py`. Do not edit by hand.

## Scale

- Every field scores 1 (best) to 8 (worst), like strokes in golf. Blank = 8.
- N/A (the field doesn't apply, e.g. no onboarding purchased) is excluded from the bucket average by default (`not_applicable: exclude`).
- Bucket score = average of its fields (per-field weights only if `use_field_weights: true`).
- Overall = weighted average of buckets. Clusters: quartiles of overall (P1 = best 25%), ties to higher ARR. Optional growth × ARR 2×2.
- Focus this week: lowest overall among accounts with the next commercial event within 120 days; next-soonest fill in if fewer than 3.

## Buckets

| Bucket | Weight | Sheet section |
|---|---|---|
| `gtm_propensity` | 30% | GTM |
| `post_sales` | 25% | Customer Success / Support / Services |
| `down_and_distance` | 25% | Situation & Timing |
| `marketing_programmatic_engagement` | 10% | Marketing \| Customer Programs Engagement |
| `product` | 10% | Product |

## Options (defaults)

| Option | Default |
|---|---|
| `renewal_direction` | `"sooner_is_better"` |
| `not_applicable` | `"exclude"` |
| `empty_bucket` | `"renormalize"` |
| `size_normalization` | `false` |
| `min_closed_opps` | `3` |
| `min_survey_responses` | `3` |
| `use_field_weights` | `false` |
| `arr_scoring` | `"absolute"` |
| `segment_field` | `null` |
| `stale_rag_penalty` | `false` |

## gtm_propensity

| Field | Sheet row | Element | Type / unit | Scoring | Notes |
|---|---|---|---|---|---|
| `arr` | 4 | ARR | number / USD | ≥1,000,000→1, 850,000–<1,000,000→2, 500,000–<850,000→3, 250,000–<500,000→4, 150,000–<250,000→5, 100,000–<150,000→6, 75,000–<100,000→7, <75,000→8 | percentile mode via arr_scoring |
| `nrr` | 4 | NRR | number / percent | ≥130→1, 120–<130→2, 110–<120→3, 105–<110→4, 100–<105→5, 95–<100→6, 90–<95→7, <90→8 |  |
| `nbec` | 5 | NBEC \| NB (growth outside recurring revenue) | number / USD | ≥1,000,000→1, 850,000–<1,000,000→2, 500,000–<850,000→3, 250,000–<500,000→4, 100,000–<250,000→5, 50,000–<100,000→6, 1–<50,000→7, <1→8 | size_normalization: % of arr (≥50→1, 30–<50→2, 20–<30→3, 10–<20→4, 5–<10→5, 2–<5→6, >0–<2→7, <>0→8) |
| `opp_win_rate` | 6 | % of opportunities closed won | number / percent | ≥100→1, 90–<100→2, 80–<90→3, 70–<80→4, 60–<70→5, 50–<60→6, 40–<50→7, <40→8 | N/A if opp_closed_count < min_closed_opps |
| `gtm_days_since_activity` | 7 | GTM activity in account (days since last) | number / days | <11→1, 11–<16→2, 16–<21→3, 21–<31→4, 31–<46→5, 46–<61→6, 61–<91→7, ≥91→8 |  |

## post_sales

| Field | Sheet row | Element | Type / unit | Scoring | Notes |
|---|---|---|---|---|---|
| `success_plan_tier` | 16 | Success / support plan tier and spend | ordinal | top→1, second→3, third→5, standard→7, none→8 |  |
| `csql_pipeline` | 17 | CSQL / PSQL pipeline $ | number / USD (12m) | ≥1,000,000→1, 850,000–<1,000,000→2, 500,000–<850,000→3, 250,000–<500,000→4, 150,000–<250,000→5, 100,000–<150,000→6, 1–<100,000→7, <1→8 | size_normalization: % of arr (≥50→1, 30–<50→2, 20–<30→3, 10–<20→4, 5–<10→5, 2–<5→6, >0–<2→7, <>0→8) |
| `csql_win_rate` | 18 | CSQL / PSQL win rate | number / percent | ≥100→1, 90–<100→2, 80–<90→3, 70–<80→4, 60–<70→5, 50–<60→6, 40–<50→7, <40→8 | N/A if csql_closed_count < min_closed_opps |
| `onboarding_delivered` | 19 | Onboarding delivered (if applicable) | ordinal | fully_delivered→1, in_progress→3, partially_delivered→5, not_delivered→8, not_purchased→na |  |
| `onboarding_completed` | 20 | Onboarding completed | ordinal | completed_all_activated→1, completed_most_activated→3, partially_completed→5, not_started→8 |  |
| `activation_pct` | 21 | Adoption milestones / product activation | number / percent | ≥100→1, 90–<100→2, 80–<90→3, 70–<80→4, 60–<70→5, 50–<60→6, 25–<50→7, <25→8 |  |
| `utilization_pct` | 22 | Utilization benchmarks | number / percent | ≥100→1, 90–<100→2, 80–<90→3, 70–<80→4, 60–<70→5, 50–<60→6, 30–<50→7, <30→8 |  |
| `value_realization` | 23 | Value realization / value delivery | ordinal | all_met→1, mostly_met→3, partially_met→5, none_met→8, no_success_plan→na |  |
| `csm_pulse_rag` | 24 | Customer success RAG / pulse | ordinal | green→1, amber→4, yellow→4, red→8 | weight 2 (if use_field_weights); +1 if csm_pulse_days_since_update > 30 (if stale_rag_penalty) |
| `csm_days_since_activity` | 25 | Last CS activity (days since) | number / days | <11→1, 11–<16→2, 16–<21→3, 21–<31→4, 31–<46→5, 46–<61→6, 61–<91→7, ≥91→8 |  |
| `support_cases_12m` | 26 | # of support cases | number / count (12m) | <2→1, 2–<5→2, 5–<8→3, 8–<11→4, 11–<16→5, 16–<21→6, 21–<31→7, ≥31→8 |  |
| `sla_max_overrun_hours` | 27 | SLA adherence / breaches | number / hours (max overrun, 12m) | <1→2, 1–<4→3, 4–<8→4, 8–<24→5, 24–<72→6, ≥72→7 | →1 if sla_breaches_12m eq 0; →8 if sla_breaches_12m gte 5 |
| `median_resolution_hours` | 28 | Time to case resolution | number / hours | ≤4→1, ≤8→2, ≤24→3, ≤48→4, ≤72→5, ≤120→6, ≤240→7, else→8 | N/A if support_cases_12m eq 0 |
| `support_csat_pct` | 29 | Support ticket CSAT / NPS | number / CSAT percent | ≥95→1, 90–<95→2, 85–<90→3, 80–<85→4, 70–<80→5, 60–<70→6, 50–<60→7, <50→8 | N/A if support_survey_responses < min_survey_responses |
| `ps_engagement` | 30 | Professional services engagement | ordinal | active_12m→1, purchased_12_36m→3, purchased_over_36m→5, never→6 |  |
| `ps_hours_used_pct` | 31 | % of service hours delivered vs purchased | number / percent | ≥90→1, 75–<90→2, 60–<75→3, 45–<60→4, 30–<45→5, 15–<30→6, >0–<15→7, <>0→8 | N/A if ps_hours_purchased eq 0 |

## down_and_distance

| Field | Sheet row | Element | Type / unit | Scoring | Notes |
|---|---|---|---|---|---|
| `days_to_next_event` | 34 | Days to next renewal / next opp close | number / days | *sooner_is_better*: <0→8, 0–<90→1, 90–<150→2, 150–<210→3, 210–<270→4, 270–<365→5, 365–<540→6, 540–<730→7, ≥730→8<br>*runway_is_better*: <0→8, 0–<30→7, 30–<60→6, 60–<90→5, 90–<120→4, 120–<150→3, 150–<180→2, ≥180→1<br>*sweet_spot*: <0→8, 0–<30→7, 30–<60→5, 60–<90→3, 90–<270→1, 270–<365→2, ≥365→4 |  |
| `stakeholder_engagement` | 35 | Key stakeholder / decision-maker involvement | ordinal | exec_engaged_90d→1, champion_plus_dm_identified→3, champion_only→5, passive→6, absent_or_champion_left→8 |  |
| `tenure_years` | 36 | # of years as a customer | number / years | ≥10→1, 8–<10→2, 6–<8→3, 5–<6→4, 4–<5→5, 3–<4→6, 1–<3→7, <1→8 |  |
| `financial_signal` | 37 | 10-K / major financial news | ordinal | strong_growth→1, positive→2, neutral→4, mixed→5, negative→7, severe→8, no_data→na |  |

## marketing_programmatic_engagement

| Field | Sheet row | Element | Type / unit | Scoring | Notes |
|---|---|---|---|---|---|
| `field_event_status` | 8 | Attending field marketing events | ordinal | attended_3plus→1, attended_2→2, attended_1→3, registered_no_show→5, invited_not_registered→6, never_invited→na |  |
| `conference_status` | 9 | Attending annual conference | ordinal | in_person_2plus→1, in_person_1→2, virtual→3, registered_no_show→5, not_registered→6, not_invited→na |  |
| `webinars_attended_12m` | 10 | Attending webinars | number / count | ≥6→1, 4–<6→2, 3–<4→3, 2–<3→4, 1–<2→5, <1→7 |  |
| `relationship_nps` | 11 | NPS score(s) | number / NPS -100..100 | ≥70→1, 50–<70→2, 30–<50→3, 10–<30→4, 0–<10→5, -20–<0→6, -40–<-20→7, <-40→8 | N/A if nps_responses < min_survey_responses |
| `newsletter_subscribed_pct` | 12 | Subscribed to newsletter(s) | number / percent of contacts | ≥50→1, 30–<50→2, 20–<30→3, 10–<20→4, >0–<10→5, <>0→6 |  |
| `newsletter_open_rate` | 13 | Opening newsletter(s) | number / percent (90d) | ≥50→1, 40–<50→2, 30–<40→3, 20–<30→4, 10–<20→5, >0–<10→6, <>0→7 | →8 if newsletter_all_bounced eq 1 |
| `advocacy_level` | 14 | Customer advocacy / positive word of mouth | ordinal | conference_speaker→1, video_or_case_study→2, community_story→3, reference_or_review→4, agreed_not_done→5, none→6, declined_or_detractor→8 |  |
| `community_champion` | 15 | Customer champion (Discord, community, marketplace) | ordinal | contributor_3plus_channels→1, channels_4_5→2, channels_3→3, channels_2→4, channels_1→5, passive_members→6, none→7 |  |

## product

| Field | Sheet row | Element | Type / unit | Scoring | Notes |
|---|---|---|---|---|---|
| `feature_requests_12m` | 32 | # of product feature requests | number / count | ≥10→1, 7–<10→2, 5–<7→3, 3–<5→4, <3→5 | blank = N/A |
| `feature_requests_delivered_pct` | 33 | # of product feature requests delivered | number / percent (24m) | ≥100→1, 75–<100→2, 50–<75→3, 25–<50→5, >0–<25→6, <>0→7 | N/A if feature_requests_12m eq 0 |

## v1 compatibility

`config/agps.v1-compat.json` is the model behind the live demo (33 simpler fields, booleans, sooner-is-better renewal). The test suite checks it reproduces the 40 demo scores exactly.
