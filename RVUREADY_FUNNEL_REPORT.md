# RVUReady Funnel Report

Date/time: 2026-06-11 22:34 EDT

## Live URL

- Primary landing page: https://freecptcodefinder.com/rvuready/
- Legacy helper URL: https://freecptcodefinder.com/rvuready.html
  - Status: restored as a noindex redirect helper to `/rvuready/`
- Production commits:
  - `b962aea8` Restore RVUReady funnel and lead capture
  - `c74e07f7` Add RVUReady CTA to orthopedic hand hub

## Lead Storage Mechanism

RVUReady beta leads now submit to:

```text
POST https://free-cpt-code-finder.onrender.com/leads
```

Storage path:

1. Landing page form submits name, email, role, specialty, practice setting, documentation pain, founding-user interest, and source context.
2. Backend validates email and rejects PHI-like free-text content.
3. Backend writes a local runtime ledger at `assistant-backend/data/rvuready_leads.json`.
4. Backend creates a durable GitHub Issue when GitHub issue storage is enabled.
5. `/health` now reports lead storage state:
   - `leads: 1`
   - `leadStore: github_issues`
   - `githubIssues.durableStore: true`

Lead intake is separate from bug reports and does not reuse the report issue type taxonomy.

## Email Capture Test

Status: Passed.

Test submission:

- Lead ID: `RVU-20260612023242-8256`
- GitHub Issue: https://github.com/DaVincidigitalbot/free-cpt-code-finder/issues/37
- Test email: `graydon+rvuready-test@example.com`
- Backend response: `201 ok: true`
- Production health after test: `leads: 1`

No PHI was submitted in the test payload.

## Landing Page Contents

The restored landing page includes:

- What RVUReady does: documentation revenue check before notes are signed.
- Who it is for: surgeons, APPs, residents/fellows, coders, practice administrators, revenue-cycle leaders.
- Why documentation affects revenue: work can be real but underpaid when the note does not support complexity, modifier use, approach, laterality, MDM, or work intensity.
- Local-first/privacy messaging: signup does not collect PHI; product direction remains privacy-conscious with local-first note review where feasible.
- Beta waitlist signup.
- Founding-user interest capture.

AdSense script was intentionally not added to the RVUReady landing page.

## CTA Placement Inventory

Implemented CTA paths:

- Homepage:
  - `/`
  - Explicit `js/rvuready-cta.js` loader added.

- Top CPT pages:
  - `/codes/99214.html`
  - `/codes/99215.html`
  - `/codes/99291.html`
  - `/codes/99292.html`
  - `/codes/49591.html`
  - `/codes/49592.html`
  - `/codes/49593.html`
  - `/codes/49594.html`
  - `/codes/49595.html`
  - `/codes/49596.html`
  - `/codes/49613.html`
  - `/codes/49614.html`
  - `/codes/49615.html`
  - `/codes/49616.html`
  - `/codes/49617.html`
  - `/codes/49618.html`
  - `/codes/64721.html`
  - `/codes/26055.html`
  - `/codes/29848.html`
  - `/codes/25607.html`
  - `/codes/25609.html`
  - `/codes/47562.html`
  - `/codes/47563.html`
  - `/codes/44140.html`
  - `/codes/49000.html`

- Modifier pages:
  - Covered through live `js/site-chrome.js`, which now injects `js/rvuready-cta.js`.
  - Verified page family: `/modifiers/complete-surgeon-cpt-modifier-guide.html`

- Coding-center pages:
  - Covered through live `js/site-chrome.js`.
  - Verified page family: `/coding-centers/index.html`

- Blog articles:
  - Covered through live `js/site-chrome.js`.
  - Verified page family: `/blog/guides/cpt-code-ventral-hernia-repair.html`

- Specialty hub:
  - Orthopedic hand hub explicit CTA loader:
    - `/specialties/orthopedic-hand-surgery.html`

## Production Verification

Passed:

- `https://freecptcodefinder.com/rvuready/` returns the RVUReady landing page.
- `https://freecptcodefinder.com/rvuready.html` exists and redirects users to `/rvuready/`.
- `https://freecptcodefinder.com/js/rvuready-cta.js` returns 200.
- `https://freecptcodefinder.com/sitemap.xml` includes `https://freecptcodefinder.com/rvuready/`.
- `rvuready.html` is marked `noindex, follow` and is not the canonical sitemap target.
- Homepage and selected top CPT pages load the CTA script explicitly.
- Modifier, coding-center, and blog page families load live `site-chrome.js`, which injects the RVUReady CTA.
- Orthopedic hand specialty hub loads the CTA script explicitly.
- Backend `/health` confirms `leadStore: github_issues`.
- Live lead capture test created durable GitHub Issue #37.

## Conversion Funnel Diagram

```text
Existing FreeCPT traffic
  |
  |-- Homepage
  |-- Top CPT pages
  |-- Modifier pages
  |-- Coding-center pages
  |-- Blog articles
  |-- Orthopedic hand hub
        |
        v
RVUReady inline CTA
        |
        v
/rvuready/ landing page
        |
        v
Beta waitlist + founding-user interest form
        |
        v
POST /leads on Render backend
        |
        v
Validation + PHI-like text rejection
        |
        v
Durable GitHub Issue lead record + backend JSON ledger
        |
        v
Manual beta invite / founding-user follow-up
```

## Current Recommendation

Ready to use for traffic capture: Yes.

Next best growth move: track CTA click and form-submit conversion by source page, then prioritize RVUReady copy variants on the pages sending the most signup intent.

