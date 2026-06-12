# RVUReady Analytics Report

Date/time: 2026-06-11 22:52 EDT

## Status

RVUReady funnel analytics are implemented, deployed, and production-tested.

Production commit:

- `7e43feb6` Add RVUReady funnel analytics

## Metrics Collected

The funnel now tracks these aggregate events:

- `cta_impression`
  - Fired when the inline RVUReady CTA becomes visible.
- `cta_click`
  - Fired when a visitor clicks the inline RVUReady CTA.
- `landing_visit`
  - Fired when `/rvuready/` loads.
- `form_start`
  - Fired on the first focus/input interaction with the RVUReady form.
- `form_submit`
  - Fired server-side when a lead is successfully created through `POST /leads`.

Derived conversion metrics:

- Click-through rate:
  - `cta_click / cta_impression`
- Landing-page conversion rate:
  - `form_submit / landing_visit`
- Form completion rate:
  - `form_submit / form_start`
- Overall visitor-to-lead conversion rate:
  - `form_submit / cta_impression`

## Implementation Details

### Client-side tracking

Files changed:

- `js/rvuready-cta.js`
- `rvuready/index.html`

The inline CTA script sends:

- CTA impression
- CTA click
- Source page path
- Source context/page family

The RVUReady landing page sends:

- Landing visit
- First form start
- GA4 event for successful form submit

The lead endpoint records successful form submissions server-side, which keeps `form_submit` tied to actual lead creation rather than button clicks.

### Backend tracking

File changed:

- `assistant-backend/server.js`

New endpoint:

```text
POST https://free-cpt-code-finder.onrender.com/rvuready-analytics
```

New admin dashboard:

```text
GET https://free-cpt-code-finder.onrender.com/admin/rvuready-analytics?key=<ADMIN_REPORTS_KEY>
```

New backend health summary field:

```json
{
  "rvureadyAnalytics": {
    "ctaImpressions": 1,
    "ctaClicks": 1,
    "landingPageVisits": 1,
    "formStarts": 1,
    "formSubmissions": 1,
    "leads": 1
  }
}
```

Storage:

- Backend aggregate store:
  - `assistant-backend/data/rvuready_analytics.json`
- GA4 custom events:
  - `rvuready_cta_impression`
  - `rvuready_cta_click`
  - `rvuready_landing_visit`
  - `rvuready_form_start`
  - `rvuready_form_submit`
  - `rvuready_beta_signup`

## Privacy / Safety

Analytics are aggregate-only.

Stored fields:

- Event type
- Source path
- Source context
- Day/date bucket
- Aggregate counters

Not stored in analytics:

- Names
- Emails
- Documentation pain text
- Free-text form content
- PHI
- Visitor identifiers
- Cookies
- IP-derived identity

The analytics endpoint rejects unsupported event names and only accepts the predefined RVUReady funnel events.

## Production Test

Controlled production test completed.

Events submitted:

- `cta_impression`
- `cta_click`
- `landing_visit`
- `form_start`
- `form_submit` through a real test lead

Test lead:

- Lead ID: `RVU-20260612024935-0A10`
- GitHub Issue: https://github.com/DaVincidigitalbot/free-cpt-code-finder/issues/38
- Test email: `graydon+rvuready-analytics-test@example.com`
- No PHI used

Production health after test:

```json
{
  "ctaImpressions": 1,
  "ctaClicks": 1,
  "landingPageVisits": 1,
  "formStarts": 1,
  "formSubmissions": 1,
  "leads": 1
}
```

Dashboard protection verified:

- `/admin/rvuready-analytics` returns `401 Unauthorized` without the admin key.
- Use `?key=<ADMIN_REPORTS_KEY>` to view the dashboard.

## How to Monitor Conversions

### Backend dashboard

Use:

```text
https://free-cpt-code-finder.onrender.com/admin/rvuready-analytics?key=<ADMIN_REPORTS_KEY>
```

Dashboard shows:

- CTA impressions
- CTA clicks
- Landing page visits
- Form starts
- Form submissions
- Leads
- CTR
- Landing-page conversion rate
- Form completion rate
- Overall visitor-to-lead conversion rate
- Breakdown by source context
- Breakdown by source path
- Breakdown by day

### Backend health quick check

Use:

```text
https://free-cpt-code-finder.onrender.com/health
```

This exposes aggregate RVUReady funnel counts only.

### GA4

In GA4, review custom events:

- `rvuready_cta_impression`
- `rvuready_cta_click`
- `rvuready_landing_visit`
- `rvuready_form_start`
- `rvuready_form_submit`
- `rvuready_beta_signup`

Recommended GA4 dimensions:

- `source_path`
- `source_context`

Recommended GA4 conversions:

- Mark `rvuready_form_submit` as a key event.
- Optionally mark `rvuready_beta_signup` as a key event if using it as the business conversion.

## Recommended Baseline KPIs

For the first 30 days, use conservative baselines because traffic is existing organic CPT intent, not paid acquisition.

### CTA click-through rate

Target baseline:

```text
0.5% to 2.0%
```

Strong signal:

```text
>2.0%
```

Concern:

```text
<0.3%
```

Interpretation:

- Low CTR means the inline CTA copy or placement is not matching page intent.
- Segment by CPT page, modifier page, blog, coding center, homepage.

### Landing-page conversion rate

Target baseline:

```text
5% to 15%
```

Strong signal:

```text
>15%
```

Concern:

```text
<3%
```

Interpretation:

- Low landing conversion means headline/form/offer friction is the issue.
- Since users clicked a high-intent CTA, the landing page should convert materially better than cold traffic.

### Form completion rate

Target baseline:

```text
50% to 80%
```

Concern:

```text
<40%
```

Interpretation:

- Low completion means form burden is too high or PHI/privacy anxiety is stopping users.
- If form starts are high but submissions are low, reduce required fields further.

### Overall visitor-to-lead conversion rate

Target baseline:

```text
0.05% to 0.30%
```

Strong signal:

```text
>0.30%
```

Interpretation:

- This is the full path from CTA impression to lead.
- Early goal should be learning by page family, not maximizing the blended number.

## Highest-Value Monitoring Questions

Review weekly:

1. Which page family produces the highest CTA CTR?
2. Which source path produces actual leads?
3. Are CPT pages or modifier pages producing better intent?
4. Do users start the form but fail to submit?
5. Does the new founding-user copy improve landing conversion?
6. Which CPT codes should get stronger RVUReady-specific CTA copy?

## Recommendation

Use the first 2 weeks as a baseline period.

Do not add product features yet. Watch:

```text
CTA CTR -> landing conversion -> form completion -> leads by source path
```

If CTR is weak, rewrite CTAs by page family.

If landing conversion is weak, simplify the form and push the founding-user offer harder.

If form completion is weak, make email-only capture the primary path and move all other fields to optional post-submit enrichment.

