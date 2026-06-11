# Phase 2D-B Final Legacy Code Status Report

Date: 2026-06-11
Branch: phase2d-b-expanded-source-review-2026-06-11
Production baseline deployed before this report: e5d6bfc647169571d399290fab11e6b8fad23111
Deployment status: no deployment performed for Phase 2D-B
Scope: 27193, 32405, 37228, 37230, 47500, 47511, 92921

## Sources Checked

- CMS PFS Relative Value Files page: https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files
- CMS RVU26C download: https://www.cms.gov/files/zip/rvu26c.zip
- RVU26C files inspected:
  - PPRRVU2026_Jul_nonQPP.csv
  - PPRRVU2026_Jul_QPP.csv
- CMS PFS Look-Up Tool overview: https://www.cms.gov/medicare/physician-fee-schedule/search/overview
- Secondary CPT-status probe:
  - AAPC Codify public CPT code pages for each scoped code
  - Used only as non-canonical support for current/deleted status because AMA CPT source is not stored in this repository.

## High-Level Finding

All seven scoped codes are absent from the official CMS RVU26C July 2026 PPRRVU files, both non-QPP and QPP.

All seven also canonicalize on AAPC Codify to deleted CPT-code URLs:

- /codes/cpt_code/deleted_cpt_code/27193
- /codes/cpt_code/deleted_cpt_code/32405
- /codes/cpt_code/deleted_cpt_code/37228
- /codes/cpt_code/deleted_cpt_code/37230
- /codes/cpt_code/deleted_cpt_code/47500
- /codes/cpt_code/deleted_cpt_code/47511
- /codes/cpt_code/deleted_cpt_code/92921

The current site still carries all seven as active 0.00 RVU placeholder records. This is most consistent with legacy/specialty-import artifacts, not active CMS import omissions.

## Status Table

| CPT | Current CPT status | Current CPT source presence | CMS RVU26C presence | MPFS presence | Site classification | Recommended disposition |
| --- | --- | --- | --- | --- | --- | --- |
| 27193 | Likely deleted/inactive | No accessible current-source evidence; AAPC canonical = deleted_cpt_code | No | No RVU26C/MPFS row found | Specialty-import artifact / legacy placeholder | Warning banner + remove from active search/Case Builder |
| 32405 | Likely deleted/inactive | No accessible current-source evidence; AAPC canonical = deleted_cpt_code | No | No RVU26C/MPFS row found | Legacy placeholder | Warning banner + remove from active search/Case Builder |
| 37228 | Likely deleted/inactive in current CPT set | No accessible current-source evidence; AAPC canonical = deleted_cpt_code | No | No RVU26C/MPFS row found | Specialty-import artifact / legacy vascular placeholder | Warning banner + remove from active search/Case Builder; manual CPT confirmation recommended before redirect |
| 37230 | Likely deleted/inactive in current CPT set | No accessible current-source evidence; AAPC canonical = deleted_cpt_code | No | No RVU26C/MPFS row found | Specialty-import artifact / legacy vascular placeholder | Warning banner + remove from active search/Case Builder; manual CPT confirmation recommended before redirect |
| 47500 | Deleted/inactive likely | No accessible current-source evidence; AAPC canonical = deleted_cpt_code; web snippet also identifies deleted historical code | No | No RVU26C/MPFS row found | Legacy biliary placeholder | Warning banner + remove from active search/Case Builder |
| 47511 | Likely deleted/inactive | No accessible current-source evidence; AAPC canonical = deleted_cpt_code | No | No RVU26C/MPFS row found | Legacy biliary/interventional placeholder | Warning banner + remove from active search/Case Builder |
| 92921 | Likely deleted/inactive | No accessible current-source evidence; AAPC canonical = deleted_cpt_code | No | No RVU26C/MPFS row found | Specialty-import artifact / legacy cardiology add-on placeholder | Warning banner + remove from active search/Case Builder; manual CPT confirmation recommended before redirect |

## Evidence Details

### CMS RVU26C / MPFS Presence

The official CMS RVU26C archive was downloaded from:

https://www.cms.gov/files/zip/rvu26c.zip

Files searched:

- PPRRVU2026_Jul_nonQPP.csv
- PPRRVU2026_Jul_QPP.csv

No rows were found for:

- 27193
- 32405
- 37228
- 37230
- 47500
- 47511
- 92921

Interpretation: these codes are not present in the CMS RVU26C July 2026 physician fee schedule source used by the site.

### Current Site State

All seven currently exist in active site data as 0.00 RVU placeholder records:

- cpt_database.json
- modifier_rules.json
- index.html homepage/search metadata
- codes/index.html active code cards
- generated /codes/*.html pages

This means they can still surface as active site records unless remediated.

### CPT Status Evidence

The repository does not contain a licensed current AMA CPT source file that can independently prove active/deleted CPT status.

Secondary public CPT-status probe:

- All seven AAPC Codify pages returned canonical links under deleted_cpt_code.
- This is consistent with CMS RVU26C absence.
- Because AAPC is not the canonical source for this project, destructive remediation should still preserve URLs with warning banners rather than deleting or redirecting immediately.

## Recommended Remediation Plan

Recommended batch behavior for all seven:

1. Remove from active searchable/payable CPT generation pipeline.
2. Remove from Case Builder active selection.
3. Remove from modifier_rules.json active modifier metadata.
4. Remove from codes/index.html active browse cards.
5. Keep each page URL alive.
6. Add deleted/inactive warning banner.
7. Link to relevant current family guidance where available:
   - 27193: orthopedic fracture/pelvis coding guidance or manual review page.
   - 32405: current lung biopsy coding guidance.
   - 37228/37230: current lower-extremity revascularization/endovascular coding guidance, if replacement family is confirmed.
   - 47500/47511: current biliary/interventional radiology coding guidance.
   - 92921: current PCI/cardiology add-on guidance.
8. Do not create redirects until replacement/current-family targets are confirmed.

## Risk Levels

- High risk if left active: all seven are 0.00 RVU placeholders that can mislead search and Case Builder users.
- Moderate remediation risk: removing from active data is low-risk if URLs are retained with warnings.
- Higher manual-review risk: 37228, 37230, and 92921 should receive explicit clinical coding review before any redirect is chosen because they belong to high-complexity vascular/cardiology families.

## Final Recommendations

| CPT | Recommendation |
| --- | --- |
| 27193 | Remove from active data; retain URL with warning banner; manual replacement guidance optional |
| 32405 | Remove from active data; retain URL with warning banner; link to current lung biopsy guidance |
| 37228 | Remove from active data; retain URL with warning banner; manual vascular replacement review before redirect |
| 37230 | Remove from active data; retain URL with warning banner; manual vascular replacement review before redirect |
| 47500 | Remove from active data; retain URL with warning banner; link to current biliary guidance |
| 47511 | Remove from active data; retain URL with warning banner; link to current biliary/interventional guidance |
| 92921 | Remove from active data; retain URL with warning banner; manual PCI/add-on replacement review before redirect |

## Deployment Recommendation

No Phase 2D-B deployment should occur from this report.

Next recommended implementation phase:

Phase 2D-C: apply deleted/inactive handling to the seven scoped legacy codes using the same URL-retention pattern used in Phase 2D-A, with specialty-specific links added only where the current family target is confirmed.
