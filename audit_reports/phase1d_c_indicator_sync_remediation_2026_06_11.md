# Phase 1D-C Indicator Synchronization Remediation Report

Generated: 2026-06-11

Mode: local remediation branch only. No deployment performed.

CMS baseline: CMS RVU26C / PPRRVU2026_Jul_nonQPP.csv

## Branch

- Branch: audit/phase1d-c-indicator-sync-2026-06-11
- Rollback baseline: f7004b2131f28a28d87c7a9ad66d452d74f22f11
- Production deployment: not performed

## Root Causes Fixed

- Assistant surgeon, co-surgeon, bilateral, and team surgeon indicators defaulting to 0 instead of preserving raw CMS RVU26C values.
- Multiple-procedure indicators defaulting to 2 instead of preserving raw CMS RVU26C values.
- Global-period symbolic indicators such as XXX, YYY, ZZZ, and MMM being represented only as normalized numeric days.

## Implementation

- Added repeatable sync tool: tools/sync_cms_indicators.py
- Loaded matched base CPT rows from PPRRVU2026_Jul_nonQPP.csv.
- Synchronized raw CMS indicator fields into cpt_database.json:
  - assistant_surgeon_indicator
  - cosurgeon_indicator
  - bilateral_indicator
  - multiple_procedure_indicator
  - team_surgeon_indicator
  - global_period_indicator
- Preserved numeric global_period_days for UI compatibility while storing raw CMS global_period_indicator.
- Derived modifier_rules.json from corrected CPT indicator fields.
- Regenerated affected CPT pages.
- Regenerated homepage/search/Case Builder SPECS.

## Files Changed

- cpt_database.json
- modifier_rules.json
- index.html
- codes/*.html for 3,752 regenerated affected CPT pages
- tools/sync_cms_indicators.py
- audit_reports/phase1d_c_indicator_sync_remediation_2026_06_11.md

QA package files:

- qa_artifacts/phase1d_c_indicator_sync_2026_06_11/indicator_sync_summary.json
- qa_artifacts/phase1d_c_indicator_sync_2026_06_11/before_indicator_mismatches.csv
- qa_artifacts/phase1d_c_indicator_sync_2026_06_11/after_indicator_mismatches.csv
- qa_artifacts/phase1d_c_indicator_sync_2026_06_11/manual_review_exceptions.csv
- qa_artifacts/phase1d_c_indicator_sync_2026_06_11/indicator_before_values_changed.csv
- qa_artifacts/phase1d_c_indicator_sync_2026_06_11/indicator_after_values_changed.csv
- qa_artifacts/phase1d_c_indicator_sync_2026_06_11/screenshots/*.png

## Mismatch Reduction

| Metric | Count |
| --- | ---: |
| Total mismatches before | 7,231 |
| Total mismatches after | 2 |
| Mismatch reduction | 7,229 |
| Remaining mismatches | 2 |

## Before Counts By Indicator

| Indicator | Before |
| --- | ---: |
| assistant_surgeon | 2,253 |
| co_surgeon | 1,160 |
| bilateral | 1,418 |
| multiple_procedure | 1,194 |
| team_surgeon | 204 |
| global_period | 1,002 |

## After Counts By Indicator

| Indicator | After |
| --- | ---: |
| assistant_surgeon | 1 |
| co_surgeon | 1 |
| bilateral | 0 |
| multiple_procedure | 0 |
| team_surgeon | 0 |
| global_period | 0 |

## Remaining Exceptions

| CPT | Field | Current site value | CMS RVU26C value | Reason |
| --- | --- | ---: | ---: | --- |
| 38120 | assistant_surgeon | 0 | 2 | Manual-override provenance; held out for explicit human review. |
| 38120 | co_surgeon | 0 | 1 | Manual-override provenance; held out for explicit human review. |

## Validation

Homepage/search/Case Builder SPECS:

- Command: python3 tools/validate_homepage_specs.py
- Result: homepage_specs_count 3,915; canonical_numeric_cpt_count 3,915; hard_error_count 0

Representative code validation:

| CPT | Category | Assistant | Co-surgeon | Bilateral | Multiple | Team | Global indicator | Remaining mismatch |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 19364 | General Surgery sample | 2 | 1 | 1 | 2 | 0 | 90 | No |
| 60545 | General Surgery sample | 2 | 1 | 1 | 2 | 0 | 90 | No |
| 15734 | General Surgery sample | 2 | 1 | 0 | 2 | 0 | 90 | No |
| 43280 | Trauma/ACS sample | 2 | 1 | 0 | 2 | 0 | 90 | No |
| 44970 | Trauma/ACS sample | 2 | 2 | 0 | 2 | 0 | 90 | No |
| 47133 | High-impact/top-list sample | 9 | 9 | 9 | 9 | 9 | XXX | No |
| 48160 | High-impact/top-list sample | 9 | 9 | 9 | 9 | 9 | XXX | No |
| 47579 | High-impact/top-list sample | 2 | 1 | 1 | 2 | 1 | YYY | No |
| 00100 | Indicator-9 sample | 9 | 9 | 9 | 9 | 9 | XXX | No |
| 49505 | Previously reviewed code | 2 | 1 | 1 | 2 | 0 | 90 | No |
| 38120 | Manual-review exception | 0 | 0 | 0 | 2 | 0 | 90 | assistant_surgeon, co_surgeon |

Screenshots/examples captured with wkhtmltoimage:

- homepage_desktop.png
- homepage_mobile_375.png
- code_19364_desktop.png
- code_43280_desktop.png
- code_44970_desktop.png
- code_47133_desktop.png
- code_00100_desktop.png
- code_38120_exception_desktop.png
- code_49505_desktop.png

Note: Playwright was unavailable in this checkout, so browser console validation could not be run through Playwright. Static homepage seed validation and local rendered screenshot capture completed.

## No-Deployment Confirmation

No production deployment was performed.
No staging deployment was performed.
No deleted-code, descriptor, or RVU remediation was performed.
