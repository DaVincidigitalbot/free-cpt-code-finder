# Real-World Impact Report Package

Status: review only. No production deployment performed.

## Available Data

- GA4: available for 90-day aggregate sessions, pageviews, event names, and internal search terms.
- Search Console: available for 90-day query/page data.
- Backend suggestion rankings: available from the public suggestion-rankings endpoint.
- Case Builder CPT-combination logs: unavailable. The production app does not currently log CPT pairs entered together in Case Builder.

## Findings

- GA4 90-day sessions: 2,577.
- GA4 90-day pageviews: 5,345.
- GA4 internal view_search_results events: 184.
- Distinct internal CPT search terms available: 57.
- Affected top searched CPT codes: 0.
- Affected internal CPT search events: 0.
- Top 100 Case Builder combinations affected: unavailable because pair-combination logging does not exist.
- Estimated percentage of Case Builder sessions with a new hard stop: unavailable from direct analytics.

## High-Frequency Proxy

Because direct pair frequency is unavailable, the high-frequency table in real-world-impact-analysis.md uses a proxy from:

- GA4 internal CPT searches.
- Search Console code interest.
- Backend suggestion clicks.

This proxy identified limited related interest, mainly:

- 44626 + 44005
- 44204 + 44005
- 35102 + 44005
- 44140 + 44005

These are directional signals only, not actual Case Builder pair occurrences.

## Recommendation

C. Deploy with release notes only.

Rationale:

- The change is calculation correctness, not a broad UX redesign.
- No affected CPTs appear in available top internal searched CPT codes.
- Direct Case Builder combination analytics are unavailable.
- The UI preserves selected work and explains payable suppression.
- A site-wide announcement banner would likely overstate observed impact.

Deployment should still use the production validation checklist and post-deployment monitoring plan from deployment-plan.md.
