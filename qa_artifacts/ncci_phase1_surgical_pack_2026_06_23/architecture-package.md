# Phase 1 CMS NCCI Architecture Package

Status: review only. No production deployment performed.

## Scope

Phase 1 builds permanent CMS NCCI infrastructure and activates a review candidate pack for high-value surgical modifier-0 edits only.

Modifier-1 edits are intentionally disabled for Phase 1. The runtime schema can represent modifier-1 rows, but the active dataset contains only modifier-0 rows.

## Runtime Architecture

index.html loads two NCCI sources:

- ncci_bundles.json: existing curated rules.
- data/ncci/active/cms_ncci_ptp_active.json: Phase 1 active CMS-derived modifier-0 pack.

The CMS-derived file uses ptp_pairs, which preserves pair-specific modifier indicators. This avoids the old grouped JSON limitation where one Column 1 code could not safely represent mixed modifier indicators.

## Versioning

Active pointer:

- data/ncci/active/cms_ncci_ptp_active.json
- data/ncci/active/manifest.json

Versioned 2026-Q3 dataset:

- data/ncci/versions/2026-Q3/surgical-modifier0-activation-pack.json
- data/ncci/versions/2026-Q3/surgical-modifier0-behavior-change-list.json
- data/ncci/versions/2026-Q3/import-audit.json

## Audit Logging

import-audit.json records CMS version, source directory, source zip files, import mode, eligible missing pairs, activated pair count, modifier-1 activation status, and import timestamp.

## Phase 1 Activation Summary

- CMS version: 2026-Q3.
- Active pairs: 500.
- Modifier indicator: 0 only.
- Modifier-1 active: false.
- Estimated surgeon-facing behavior changes: 500 CPT pairs.

## User Experience

Modifier-0 behavior:

- Column 2 line remains visible as selected/performed.
- Payable wRVU becomes 0.00.
- Case total separates selected and payable wRVUs.
- Warning card explains the CMS NCCI hard stop.
- NCCI rationale is included when CMS provides one.
- Modifier 59/X bypass is not allowed.

Modifier-1 behavior:

- Not activated in Phase 1.
- Infrastructure remains available for later warning/override workflow.

## Review Artifacts

- activation-candidate-list.md
- activation-candidate-list.json
- browser-validation.json
- regression-validation.json
- Browser screenshots for required workflows.
