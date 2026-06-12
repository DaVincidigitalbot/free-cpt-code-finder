# RVUReady Analytics Dashboard Report

Date/time: 2026-06-11 23:18 EDT

## Status

RVUReady funnel analytics dashboard implementation is deployed and production-tested.

Production commits:

- `870921d2` Implement RVUReady analytics dashboard views
- `d958f082` Fix RVUReady source dashboard aggregation

No copy rewrites, no new product features, no AI feature expansion, no OCR, and no note-scoring changes were made.

## Dashboard

Admin dashboard:

```text
https://free-cpt-code-finder.onrender.com/admin/rvuready-analytics?key=<ADMIN_REPORTS_KEY>
```

Access control:

- Dashboard is protected by the existing admin key.
- Production verification without a key returns `401 Unauthorized`.

## Metrics Collected

The dashboard measures:

- CTA impressions
- CTA clicks
- RVUReady landing page visits
- Form starts
- Form submissions
- Leads
- Click-through rate
- Landing-page conversion rate
- Form completion rate
- Overall visitor-to-lead conversion rate

Privacy boundaries:

- No PHI
- No names in analytics
- No emails in analytics
- No form comments in analytics
- No visitor identifiers
- Aggregated event counts only

## Dashboard Views Implemented

### 1. Summary Cards

Cards show:

- CTA impressions
- CTA clicks
- Landing visits
- Leads
- Form submissions
- Events logged

### 2. Traffic Source Conversion

Required source categories are now reported as rows:

- Homepage
- CPT pages
- Modifier pages
- Coding-center pages
- Orthopedic-hand page

Columns:

- Traffic source
- Impressions
- Clicks
- Leads
- Conversion %
- CTR

Conversion % is calculated as:

```text
leads / CTA clicks
```

CTR is calculated as:

```text
CTA clicks / CTA impressions
```

### 3. Top-Converting Pages

Ranks source pages by:

1. Lead conversion rate
2. Leads
3. Clicks

Columns:

- Page
- Impressions
- Clicks
- Leads
- Conversion %
- CTR

### 4. Lowest-Converting Pages

Ranks source pages by lowest lead conversion rate so underperforming placements can be identified.

Columns:

- Page
- Impressions
- Clicks
- Leads
- Conversion %
- CTR

### 5. Raw Detail Tables

Still available below the business tables:

- By source context
- By source path
- By day

These are useful for debugging and deeper analysis.

## Source Attribution Fix

Before this implementation, successful leads were being attributed primarily to `/rvuready/`.

Updated attribution now sends the original referring source path through the landing page and lead submission:

```text
FreeCPT source page
-> RVUReady CTA
-> /rvuready/?source=<source_path>&context=<source_category>
-> lead submission
-> dashboard attributes lead back to original source page/category
```

Orthopedic-hand traffic now has its own source category:

```text
orthopedic-hand
```

## Production Test

Controlled test events were submitted for the required source categories.

Synthetic test coverage:

- Homepage CTA impression/click/landing/form-start
- CPT page CTA impression/click/landing/form-start/lead
- Modifier page CTA impression/click/landing/form-start
- Coding-center CTA impression/click/landing/form-start/lead
- Orthopedic-hand CTA impression/click/landing/form-start/lead

Production health after test:

```json
{
  "ctaImpressions": 5,
  "ctaClicks": 5,
  "landingPageVisits": 5,
  "formStarts": 5,
  "formSubmissions": 3,
  "leads": 3
}
```

Test leads created:

- CPT page test: https://github.com/DaVincidigitalbot/free-cpt-code-finder/issues/40
- Coding-center test: https://github.com/DaVincidigitalbot/free-cpt-code-finder/issues/41
- Orthopedic-hand test: https://github.com/DaVincidigitalbot/free-cpt-code-finder/issues/42

No PHI used.

## Current Test Data Interpretation

The current dashboard contains seeded test data only after the latest Render deploy reset runtime counters.

Do not use the seeded data for business decisions.

Use it only as proof that:

- Events are accepted.
- Leads are created.
- Source categories work.
- Original source paths are preserved.
- Dashboard conversion math works.

## How to Use the Dashboard

Weekly decision workflow:

1. Open the dashboard.
2. Review Traffic Source Conversion first.
3. Identify the source category with the highest lead conversion rate.
4. Review Top-Converting Pages.
5. Review Lowest-Converting Pages.
6. Only then decide whether to change CTA placement, page targeting, or source-specific messaging.

Decision rule:

```text
Do not optimize based on opinions. Optimize based on source-specific clicks -> leads.
```

## Recommended Baseline KPIs

Initial organic traffic baselines:

### CTA CTR

Baseline target:

```text
0.5% to 2.0%
```

Strong:

```text
>2.0%
```

Concern:

```text
<0.3%
```

### Click-to-lead conversion

Baseline target:

```text
5% to 15%
```

Strong:

```text
>15%
```

Concern:

```text
<3%
```

### Overall visitor-to-lead conversion

Baseline target:

```text
0.05% to 0.30%
```

Strong:

```text
>0.30%
```

## Recommended Monitoring Window

Use a 14-day baseline window before making another conversion decision, unless there is an obvious technical failure.

Minimum useful decision threshold:

- At least 100 CTA impressions per source category, or
- At least 25 CTA clicks for a specific source page

Below that, the data is directionally useful but too thin for hard conclusions.

## Final Recommendation

The funnel is now measurable by source category and source page.

Next decisions should be made from:

```text
Traffic source -> CTA clicks -> leads -> conversion %
```

Not from copy opinions.

