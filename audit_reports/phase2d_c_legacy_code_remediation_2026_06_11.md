# Phase 2D-C Legacy Code Remediation Report

Date: 2026-06-11
Branch: phase2d-c-legacy-code-remediation-2026-06-11
Deployment status: not deployed
Scope: 27193, 32405, 37228, 37230, 47500, 47511, 92921

## Summary

The seven scoped legacy/deleted codes were removed from active searchable/payable data while their public URLs were retained as informational inactive/deleted pages.

No redirects were created. No replacement-code mapping was added.

## Files Changed

- cpt_database.json
- modifier_rules.json
- specialty_hierarchy.json
- index.html
- codes/index.html
- codes/27193.html
- codes/32405.html
- codes/37228.html
- codes/37230.html
- codes/47500.html
- codes/47511.html
- codes/92921.html
- tools/remediate_phase2d_c_legacy_codes.py
- audit_reports/phase2d_c_legacy_code_remediation_2026_06_11.md
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/legacy_code_archive.json
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/validation.json
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/http_validation.json
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/screenshots/

## Codes Affected

| CPT | Active data action | URL action | Special note |
| --- | --- | --- | --- |
| 27193 | Removed from active CPT/search/Case Builder data | Retained with inactive/deleted banner | No redirect |
| 32405 | Removed from active CPT/search/Case Builder data | Retained with inactive/deleted banner | No redirect |
| 37228 | Removed from active CPT/search/Case Builder data | Retained with inactive/deleted banner | Replacement-family review pending |
| 37230 | Removed from active CPT/search/Case Builder data | Retained with inactive/deleted banner | Replacement-family review pending |
| 47500 | Removed from active CPT/search/Case Builder data | Retained with inactive/deleted banner | No redirect |
| 47511 | Removed from active CPT/search/Case Builder data | Retained with inactive/deleted banner | No redirect |
| 92921 | Removed from active CPT/search/Case Builder data | Retained with inactive/deleted banner | Replacement-family review pending |

## Warning Banner

Each retained page displays:

> This code is inactive/deleted and should not be used for current billing.

Each page also states that the code is excluded from active search, Case Builder selection, payable RVU estimates, and current CPT datasets.

## Search and Case Builder Behavior

The seven codes were removed from:

- cpt_database.json
- modifier_rules.json
- homepage/search metadata in index.html
- active browse cards in codes/index.html

This excludes them from active search results, Case Builder selection, and payable CPT workflows.

## Specialty/NCCI Cleanup

- specialty_hierarchy.json: removed 37228 from the active Endovascular hierarchy list.
- ncci_bundles.json: no scoped-code references remained after Phase 2D-B review; no NCCI data change was required for these seven.

## Validation

Commands run:

- python3 tools/remediate_phase2d_c_legacy_codes.py
- python3 scripts/build_homepage_specs.py
- python3 tools/validate_homepage_specs.py

Results:

- active homepage/search codes: 3902
- homepage_specs_count: 3902
- canonical_numeric_cpt_count: 3902
- hard_error_count: 0

Direct file validation found no scoped-code references remaining in:

- cpt_database.json
- modifier_rules.json
- ncci_bundles.json
- specialty_hierarchy.json
- index.html
- codes/index.html

Local HTTP validation:

- /codes/27193.html: HTTP 200, warning banner visible
- /codes/32405.html: HTTP 200, warning banner visible
- /codes/37228.html: HTTP 200, warning banner visible
- /codes/37230.html: HTTP 200, warning banner visible
- /codes/47500.html: HTTP 200, warning banner visible
- /codes/47511.html: HTTP 200, warning banner visible
- /codes/92921.html: HTTP 200, warning banner visible

## Screenshots

Screenshots captured:

- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/screenshots/code_27193_inactive_deleted.jpg
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/screenshots/code_32405_inactive_deleted.jpg
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/screenshots/code_37228_inactive_deleted.jpg
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/screenshots/code_37230_inactive_deleted.jpg
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/screenshots/code_47500_inactive_deleted.jpg
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/screenshots/code_47511_inactive_deleted.jpg
- qa_artifacts/phase2d_c_legacy_code_remediation_2026_06_11/screenshots/code_92921_inactive_deleted.jpg

Visual sample check confirmed the 37228 screenshot is not blank and shows the inactive/deleted warning page.

## Production Deployment Recommendation

Recommend staging validation before production.

Required staging checks:

1. Confirm all seven URLs return HTTP 200.
2. Confirm warning banner visible on all seven pages.
3. Confirm none of the seven appear in homepage active search.
4. Confirm none can be added to Case Builder.
5. Confirm no redirects exist for 37228, 37230, or 92921.

Production deployment should proceed only after staging review approval.
