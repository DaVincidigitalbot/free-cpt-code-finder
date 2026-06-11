# Phase 1D-D 38120 Final Exception Resolution Report

Generated: 2026-06-11

Mode: local remediation branch only after approved Phase 1D-C production deploy. No Phase 1D-D deployment performed.

CMS baseline: CMS RVU26C / PPRRVU2026_Jul_nonQPP.csv

## Production Deployment Verification For Phase 1D-C

Approved production commit:

- 4e1152e177d96e88b30479a23e8bb706c34ef64d

Render production service verification:

- Service: free-cpt-code-finder / srv-d7ep88n7f7vs73daplig
- Live deploy: dep-d8ljbm3eo5us73fat7gg
- Live deploy commit: 4e1152e177d96e88b30479a23e8bb706c34ef64d
- Direct Render service artifact: https://free-cpt-code-finder.onrender.com/staging-frontend/index.html
- Direct Render artifact SHA256: 6e984c447b89aa938edfa97ff7693cda63b63d3c16a4cb593cb7764eb3d6a10a
- Local 4e1152e index.html SHA256: 6e984c447b89aa938edfa97ff7693cda63b63d3c16a4cb593cb7764eb3d6a10a

Note: the apex custom-domain root was still serving the prior cached/static root artifact during verification. The Render backend service route above confirmed the approved Phase 1D-C commit was live on the Render production service.

## Branch

- Branch: phase1d-d-38120-final-exception-2026-06-11
- Base commit: 4e1152e177d96e88b30479a23e8bb706c34ef64d
- Production deployment: not performed for this remediation

## 38120 Indicator Remediation

| Field | Before site value | CMS RVU26C value | After site value |
| --- | ---: | ---: | ---: |
| assistant_surgeon_indicator | 0 | 2 | 2 |
| cosurgeon_indicator | 0 | 1 | 1 |

Other 38120 CMS indicator fields remained aligned:

| Field | CMS / site value |
| --- | ---: |
| bilateral_indicator | 0 |
| multiple_procedure_indicator | 2 |
| team_surgeon_indicator | 0 |
| global_period_indicator | 90 |

## Implementation

- Removed the 38120 manual-review holdout from tools/sync_cms_indicators.py.
- Re-ran the CMS RVU26C indicator synchronization tool.
- Updated 38120 in cpt_database.json.
- Re-derived 38120 modifier rules in modifier_rules.json.
- Regenerated codes/38120.html.
- Rebuilt homepage/search/Case Builder SPECS through scripts/build_homepage_specs.py.

## Files Changed

- cpt_database.json
- modifier_rules.json
- codes/38120.html
- tools/sync_cms_indicators.py
- audit_reports/phase1d_d_38120_final_exception_resolution_2026_06_11.md
- audit_reports/phase2a_placeholder_descriptor_planning_2026_06_11.md
- qa_artifacts/phase1d_d_38120_final_exception_2026_06_11/*
- qa_artifacts/phase2a_placeholder_descriptor_planning_2026_06_11/*

## Validation Results

Indicator validation:

| Metric | Count |
| --- | ---: |
| Indicator mismatches before | 2 |
| Indicator mismatches after | 0 |
| Expected target | 0 |

38120 post-remediation values:

| CPT | Assistant | Co-surgeon | Bilateral | Multiple | Team | Global |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 38120 | 2 | 1 | 0 | 2 | 0 | 90 |

Homepage/search/Case Builder seed validation:

- Command: python3 tools/validate_homepage_specs.py
- Result: homepage_specs_count 3,915; canonical_numeric_cpt_count 3,915; hard_error_count 0

Full validation engine:

- Command: node validation_engine.js
- Result: pre-existing global database/hierarchy issues remain; no cpt_database to modifier_rules field mismatches were introduced. Existing known issues include hierarchy placeholder/zero-RVU rows and modifier_rules-only legacy rows outside this task scope.

Browser validation:

- Local browser run through Playwright using the real generated files.
- CPT page rendered with assistant surgeon indicator 2 and co-surgeon indicator 1.
- Homepage search found 38120.
- Case Builder added 38120 as a clean single line.
- Case Builder displayed 16.64 wRVU and $998.69 estimate.
- Browser console material issues: only local-test CORS/404 noise from backend analytics endpoints under localhost; no 38120 rendering or Case Builder errors.

Screenshots:

- qa_artifacts/phase1d_d_38120_final_exception_2026_06_11/screenshots/38120_cpt_page_desktop.png
- qa_artifacts/phase1d_d_38120_final_exception_2026_06_11/screenshots/38120_homepage_search_desktop.png
- qa_artifacts/phase1d_d_38120_final_exception_2026_06_11/screenshots/38120_case_builder_desktop.png
- qa_artifacts/phase1d_d_38120_final_exception_2026_06_11/screenshots/38120_mobile_375_homepage_case_builder.png

## Production Status

Phase 1D-C production deploy completed for commit 4e1152e177d96e88b30479a23e8bb706c34ef64d.

Phase 1D-D was not deployed.
