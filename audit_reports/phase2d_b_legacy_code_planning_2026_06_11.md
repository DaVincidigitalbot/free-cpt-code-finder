# Phase 2D-B Legacy Code Planning Report

Date: 2026-06-11
Branch: phase2d-deleted-hernia-remediation-2026-06-11
Scope: 27193, 32405, 37228, 37230, 47500, 47511, 92921
Deployment status: report only; not deployed

## Summary

All seven scoped Phase 2D-B codes remain in the active site data today as 0.00 RVU placeholder records. None has an active CMS RVU26C July 2026 row in the site's canonical RVU baseline.

This does not prove every code is deleted. Several may be active CPT codes that are missing from the current site import, contractor-priced, non-payable in the CMS RVU source, or otherwise mishandled by the generation pipeline. Phase 2D-B should therefore start with source-status confirmation before remediation.

## Current Site Status

| CPT | Site active record | Site descriptor | Work RVU | Total RVU | Active CMS RVU26C row present? | Current classification | Recommended action |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| 27193 | Yes | CPT 27193 | 0.00 | 0.00 | No | Legacy placeholder / missing CMS baseline row | Manual source review before remediation |
| 32405 | Yes | CPT 32405 | 0.00 | 0.00 | No | Legacy placeholder / missing CMS baseline row | Determine whether deleted/replaced before active removal |
| 37228 | Yes | CPT 37228 | 0.00 | 0.00 | No | Potential active-code import defect | Verify against CMS MPFS/CPT before removal |
| 37230 | Yes | CPT 37230 | 0.00 | 0.00 | No | Potential active-code import defect | Verify against CMS MPFS/CPT before removal |
| 47500 | Yes | CPT 47500 | 0.00 | 0.00 | No | Legacy placeholder / missing CMS baseline row | Manual source review before remediation |
| 47511 | Yes | CPT 47511 | 0.00 | 0.00 | No | Legacy placeholder / missing CMS baseline row | Manual source review before remediation |
| 92921 | Yes | CPT 92921 | 0.00 | 0.00 | No | Potential active add-on/import defect | Verify against CMS MPFS/CPT before removal |

## Data Locations

All seven currently appear in:

- cpt_database.json
- modifier_rules.json
- index.html active homepage/search metadata
- codes/index.html active code cards
- generated code pages under /codes/

## Planning Recommendations

Recommended next workflow:

1. Confirm each CPT status against the current authoritative CPT/CMS source.
2. Split the seven into two remediation groups:
   - Confirmed deleted/inactive: remove from active data and retain URL with deleted-code education.
   - Active but missing/misclassified: repair canonical descriptor/RVU provenance instead of deleting.
3. Rebuild homepage/search and Case Builder metadata only after classification is complete.
4. Do not remove 37228, 37230, or 92921 without explicit confirmation; these look higher risk for import defects than deleted-code artifacts.

## Deployment Recommendation

Do not deploy Phase 2D-B changes yet. This phase is planning only.

