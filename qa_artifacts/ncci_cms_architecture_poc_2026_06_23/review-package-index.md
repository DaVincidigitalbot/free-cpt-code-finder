# CMS NCCI Coverage Review Package

Branch: review/ncci-cms-architecture-poc-20260623

Status: review only. No production deployment performed.

## Risk Quantification

CMS Q3 2026 Practitioner PTP audit scope:

- Loaded FreeCPTCodeFinder CPT codes: 3,875
- Target surgical CPT codes in requested domains: 1,279
- CMS PTP relationships in scope: 302,705
- Missing active app relationships in scope: 302,588
- Top missing modifier-0 findings ranked: 500
- Staging POC imported pair subset: 601
- Modifier-1 examples included in POC subset: 100

Primary risk: the current app is not missing one edit. It is using a tiny curated rule subset against a CMS rules universe large enough to materially overstate payable wRVUs across common operative combinations.

## Real Overstatement Examples

- 44055 + 49000: selected 37.22 wRVU, payable should be 24.99 wRVU; exploratory laparotomy is modifier-0 bundled.
- 44140 + 44005: selected 40.03 wRVU, payable should be 22.03 wRVU; enterolysis is modifier-0 bundled.
- 38100 + 49000: selected 31.29 wRVU, payable should be 19.06 wRVU; exploratory laparotomy is modifier-0 bundled in trauma splenectomy scenario.
- 44120 + 49000: selected/payable 32.53 wRVU in the POC because CMS marks this relationship modifier-1, so it requires warning/override workflow rather than automatic suppression.

## Browser Validation

Validation artifact: browser-validation.json

Screenshots:

- poc-44055-49000-hard-stop.png
- poc-44140-44005-enterolysis-hard-stop.png
- poc-44120-49000-exploratory-warning.png
- poc-44140-44603-modifier1-warning.png
- poc-49593-15734-hernia-component-separation.png
- poc-38100-49000-trauma-hard-stop.png
- poc-44120-44140-mppr.png

Observed results:

- Modifier-0 pairs suppress Column 2 payable wRVU to 0.00 and show bundled/not included.
- Modifier-1 pairs keep selected and payable wRVU included, move engine state to WARNING, and show CMS NCCI Warning cards.
- Selected and payable totals remain separated when suppression occurs.
- Existing MPPR behavior remains intact.
- Hernia + component separation remains payable and unblocked in the tested case.

## Architecture Recommendation

Recommendation: move to comprehensive CMS NCCI import architecture now, but do not flip the entire CMS PTP universe into production in one deploy.

Implementation path:

1. Build the durable CMS import/versioning pipeline.
2. Add regression tests against official CMS source files.
3. Deploy a reviewed high-value surgical subset first behind the new architecture.
4. Expand toward comprehensive coverage by quarter and specialty after warning/override telemetry is reviewed.

Reasoning:

- User safety and coding accuracy favor CMS-source coverage over hand-maintained JSON.
- The maintenance burden is lower with a deterministic quarterly importer than with curated manual rules.
- Deployment risk is high if 300k plus relationships are activated at once without reviewer workflow and audit telemetry.
- A staged rollout gives better accuracy quickly without hiding behavior changes from surgeons.

## Supporting Artifacts

- top-500-missing-modifier-0-risk.md
- top-500-missing-modifier-0-risk.json
- full-cms-ncci-architecture-plan.md
- cms_ncci_ptp_subset.json
- browser-validation.json
