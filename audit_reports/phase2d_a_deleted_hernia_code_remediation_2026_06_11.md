# Phase 2D-A Deleted Hernia Code Remediation Report

Date: 2026-06-11
Branch: phase2d-deleted-hernia-remediation-2026-06-11
Scope: 49560, 49561, 49565, 49570, 49572, 49655
Deployment status: not deployed

## Summary

The six scoped legacy hernia codes were removed from the active searchable/payable data path while their public code-page URLs were retained with deleted-code education.

These codes are absent from the CMS RVU26C July 2026 active RVU baseline used by the site and were previously represented as 0.00 RVU placeholder records.

## Codes Affected

| CPT | Prior site descriptor | Prior work RVU | Prior total RVU | Remediation |
| --- | --- | ---: | ---: | --- |
| 49560 | CPT 49560 | 0.00 | 0.00 | Removed from active data; URL retained with deleted-code banner |
| 49561 | CPT 49561 | 0.00 | 0.00 | Removed from active data; URL retained with deleted-code banner |
| 49565 | CPT 49565 | 0.00 | 0.00 | Removed from active data; URL retained with deleted-code banner |
| 49570 | CPT 49570 | 0.00 | 0.00 | Removed from active data; URL retained with deleted-code banner |
| 49572 | CPT 49572 | 0.00 | 0.00 | Removed from active data; URL retained with deleted-code banner |
| 49655 | CPT 49655 | 0.00 | 0.00 | Removed from active data; URL retained with deleted-code banner |

## Files Changed

- cpt_database.json
- modifier_rules.json
- ncci_bundles.json
- specialty_hierarchy.json
- index.html
- codes/index.html
- codes/49560.html
- codes/49561.html
- codes/49565.html
- codes/49570.html
- codes/49572.html
- codes/49655.html
- tools/remediate_deleted_hernia_codes.py
- audit_reports/phase2d_a_deleted_hernia_code_remediation_2026_06_11.md
- qa_artifacts/phase2d_a_deleted_hernia_2026_06_11/deleted_hernia_archive.json
- qa_artifacts/phase2d_a_deleted_hernia_2026_06_11/validation.json

## Deleted-Code Page Handling

The six URLs remain live as standalone reference pages:

- /codes/49560.html
- /codes/49561.html
- /codes/49565.html
- /codes/49570.html
- /codes/49572.html
- /codes/49655.html

Each page now displays:

> ⚠️ This CPT code is inactive/deleted and should not be used for current billing. See current ventral/incisional hernia coding guidance.

Each page links to:

- /blog/guides/cpt-code-ventral-hernia-repair.html
- /coding-centers/hernia-coding-center.html
- Current hernia family code pages: 49591, 49593, 49595, 49596, 49613, 49615, 49617, 49618, 49621, 49622

No redirects were created.

## Search Behavior

The scoped codes are no longer present in the homepage active CPT metadata.

Validation:

- Homepage specs before Phase 2D-A: 3,915 active codes
- Homepage specs after Phase 2D-A: 3,909 active codes
- validate_homepage_specs.py hard errors: 0

## Case Builder Behavior

The scoped codes are no longer present in cpt_database.json or index.html active specs, so Case Builder cannot select them from the active CPT lookup.

The retained code pages explicitly state that the code is excluded from active search, Case Builder selection, payable RVU estimates, and current CPT datasets.

## Active Dataset Cleanup

Validation found no scoped-code references remaining in:

- cpt_database.json
- modifier_rules.json
- ncci_bundles.json
- specialty_hierarchy.json
- index.html
- codes/index.html

## 49655 Reference Audit

49655 was audited across NCCI datasets, modifier datasets, bundle logic, and search datasets.

Prior 49655 active references:

- cpt_database.json placeholder 0.00 RVU record
- modifier_rules.json placeholder modifier metadata
- ncci_bundles.json top-level bundle entry: 49655 -> 49320
- homepage/search metadata generated from cpt_database.json
- codes/index.html active card
- codes/49655.html placeholder page

After remediation:

- 49655 has no active references in cpt_database.json.
- 49655 has no active references in modifier_rules.json.
- 49655 has no active references in ncci_bundles.json.
- 49655 has no active references in homepage/search metadata.
- 49655 is removed from codes/index.html active cards.
- /codes/49655.html remains live with deleted-code education.

NCCI cleanup removed five deleted-code-linked NCCI records/entries. Archived copies are preserved in qa_artifacts/phase2d_a_deleted_hernia_2026_06_11/deleted_hernia_archive.json.

## Validation Results

Commands run:

- python3 tools/remediate_deleted_hernia_codes.py
- python3 scripts/build_homepage_specs.py
- python3 tools/validate_homepage_specs.py

Result:

- specialties: 53
- active homepage/search codes: 3909
- homepage_specs_count: 3909
- canonical_numeric_cpt_count: 3909
- hard_error_count: 0

Additional validation artifact:

- qa_artifacts/phase2d_a_deleted_hernia_2026_06_11/validation.json

## Production Status

No production deployment was performed for Phase 2D-A.

