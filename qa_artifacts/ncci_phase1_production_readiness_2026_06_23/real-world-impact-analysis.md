# Real-World Impact Analysis - 159-Pair NCCI Activation

Status: review only. No production deployment performed.

## Data Availability

- GA4: available.
- Search Console: available.
- Backend suggestion search/click rankings: available.
- Case Builder CPT-combination logs: unavailable. The production app does not currently log CPT pairs entered together.

## GA4 90-Day Summary

- Active users: 1676
- Sessions: 2577
- Pageviews: 5345
- view_search_results events: 184

## User Impact Analysis

- Top internal searched CPT codes available: 57
- Affected among available top searched CPT codes: 0
- Affected internal CPT search events: 0
- Affected internal CPT search event share: 0.0%
- Affected search events as share of all sessions: 0.0%
- Top 100 Case Builder combinations affected: unavailable; no Case Builder combination logs exist.
- Estimated percent of Case Builder sessions with a new hard-stop: unavailable from direct analytics.

Affected top searched CPT codes:

## High-Frequency Impact Report

Frequency is a proxy from GA4 internal searches, Search Console code interest, and backend suggestion clicks; it is not actual Case Builder pair frequency.

| CPT pair | Current behavior | New behavior | Selected wRVU change | Payable wRVU change | Estimated frequency |
|---|---|---|---:|---:|---:|
| 44626 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 6.10 |
| 44204 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 3.00 |
| 35102 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 1.90 |
| 44140 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.70 |
| 39540 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.60 |
| 35081 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.30 |
| 44625 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.30 |
| 38115 + 38101 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -19.06 | 0.20 |
| 38115 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.20 |
| 44143 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.20 |
| 44156 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.10 |
| 44205 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.10 |
| 44207 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.10 |
| 44960 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.10 |
| 45800 + 44005 | Both selected codes could contribute payable wRVU if entered together. | Column 2 visible but payable wRVU suppressed to 0.00 with hard-stop warning. | 0.00 | -18.00 | 0.10 |

## Deployment Recommendation

C. Deploy with release notes only.

Rationale: direct Case Builder pair-frequency analytics are unavailable, and affected-code search interest is low. The activation corrects payable-wRVU logic and preserves selected work visibility. A site-wide announcement banner would likely overstate the blast radius; release notes plus post-deployment monitoring are the right level.
