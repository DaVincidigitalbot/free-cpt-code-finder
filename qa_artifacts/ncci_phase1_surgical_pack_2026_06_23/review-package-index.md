# Phase 1 Surgical NCCI Activation Review Package

Status: review only. No production deployment performed.

Branch: review/ncci-phase1-surgical-pack-20260623

## Deliverables

- Architecture package: architecture-package.md
- Import workflow documentation: docs/ncci-import-workflow.md
- Activation candidate list: activation-candidate-list.md and activation-candidate-list.json
- Behavior-change list: data/ncci/versions/2026-Q3/surgical-modifier0-behavior-change-list.json
- Versioned activation pack: data/ncci/versions/2026-Q3/surgical-modifier0-activation-pack.json
- Active runtime pack: data/ncci/active/cms_ncci_ptp_active.json
- Audit log: data/ncci/versions/2026-Q3/import-audit.json
- Regression validation: regression-validation.json
- Browser validation: browser-validation.json plus screenshots

## Phase 1 Summary

- CMS source: Q3 2026 Practitioner PTP files.
- Eligible missing surgical modifier-0 pairs found by importer: 7,700.
- Phase 1 active pack: 500 pairs.
- Estimated surgeon-facing behavior changes: 500 CPT pairs.
- Modifier-1 edits: disabled.

## Behavior Change

Previous behavior:

- Missing CMS modifier-0 pairs could allow both selected CPT lines to contribute payable wRVUs.

New behavior:

- Column 2 remains visible as selected/performed.
- Column 2 payable wRVU becomes 0.00.
- Total shows payable wRVU and selected wRVU separately.
- NCCI hard-stop warning card explains suppression and no modifier bypass.

## Browser Validation Results

- Enterolysis/colectomy: 44140 + 44005, BLOCKED, 40.03 selected -> 22.03 payable.
- Exploratory laparotomy: 44055 + 49000, BLOCKED, 37.22 selected -> 24.99 payable.
- Small bowel resection: 44120 + 44005, BLOCKED, 38.30 selected -> 20.30 payable.
- Ostomy reversal: 44620 + 44005, BLOCKED, 32.07 selected -> 14.07 payable.
- Ostomy creation: 44310 + 44005, BLOCKED, 35.15 selected -> 17.15 payable.
- TAR/component separation: 49593 + 15734, CLEAN, 32.43 selected -> 32.43 payable.
- Trauma splenectomy/ex lap: 38100 + 49000, BLOCKED, 31.29 selected -> 19.06 payable.

## Screenshots

- phase1-enterolysis-colectomy-44140-44005.png
- phase1-exlap-44055-49000.png
- phase1-small-bowel-enterolysis-44120-44005.png
- phase1-ostomy-reversal-enterolysis-44620-44005.png
- phase1-ostomy-creation-enterolysis-44310-44005.png
- phase1-tar-component-separation-49593-15734.png
- phase1-trauma-splenectomy-exlap-38100-49000.png

## Production Deployment Plan

1. Graydon reviews this package and the candidate list.
2. If approved, merge this review branch.
3. Deploy through the normal GitHub Pages path.
4. Validate live with the same browser cases.
5. Monitor reported Case Builder issues and behavior-change feedback.

## Rollback Plan

Preferred rollback:

- Revert the Phase 1 deployment commit from main and push the revert.

Data-only rollback:

- Replace data/ncci/active/cms_ncci_ptp_active.json with an empty ptp_pairs dataset and set manifest pair count to 0.

## Risk Assessment

Recommendation: Phase 1 is suitable for review, not automatic production deployment.

Accuracy risk without Phase 1 is high because known CMS modifier-0 edits can overstate payable wRVUs.

Deployment risk is moderate because 500 CPT pairs will change behavior. The risk is controlled by keeping modifier-1 disabled, limiting the pack to modifier-0 hard stops, providing a full behavior-change list, and preserving rollback.
