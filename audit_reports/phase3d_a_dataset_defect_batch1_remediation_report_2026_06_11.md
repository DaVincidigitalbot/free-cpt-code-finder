# DATASET DEFECT BATCH 1 REMEDIATION REPORT

Date: 2026-06-11
Branch: phase3d-a-dataset-defect-batch1-2026-06-11
Scope: only the 28 Phase 3C records classified as should be inactive/deleted.
Production status: no deployment performed.

## Codes Remediated

49566, 49568, 49580, 49582, 49585, 49587, 49590, 49652, 49653, 49654, 49656, 49657, 99218, 99219, 99220, 99224, 99225, 99226, 99241, 99251, 99343, 99354, 99355, 99356, 99357, 99441, 99442, 99443

## Summary

- Before active CPT count: 3902
- After active CPT count: 3874
- Active records removed: 28
- URLs preserved: 28
- Homepage SPECS count: 3874
- Canonical numeric CPT count: 3874
- Homepage SPECS count matches canonical numeric CPT count: yes

## Files Changed

- codes/49566.html
- codes/49568.html
- codes/49580.html
- codes/49582.html
- codes/49585.html
- codes/49587.html
- codes/49590.html
- codes/49652.html
- codes/49653.html
- codes/49654.html
- codes/49656.html
- codes/49657.html
- codes/99218.html
- codes/99219.html
- codes/99220.html
- codes/99224.html
- codes/99225.html
- codes/99226.html
- codes/99241.html
- codes/99251.html
- codes/99343.html
- codes/99354.html
- codes/99355.html
- codes/99356.html
- codes/99357.html
- codes/99441.html
- codes/99442.html
- codes/99443.html
- codes/index.html
- cpt_database.json
- cpt_decision_tree.json
- index.html
- modifier_rules.json
- ncci_bundles.json
- rvu_database.json
- specialty_hierarchy.json
- tools/platform_hardening_audit.py
- tools/remediate_phase3d_a_dataset_defects.py

## Workflow Changes

- Removed the 28 codes from cpt_database.json.
- Removed the 28 codes from rvu_database.json active codes.
- Removed the 28 codes from modifier_rules.json.
- Removed legacy references from cpt_decision_tree.json.
- Removed legacy references from specialty_hierarchy.json.
- Removed stale NCCI reason references and records tied to the 28 codes where applicable.
- Regenerated homepage SPECS from cpt_database.json.
- Removed active code index cards from codes/index.html.
- Rewrote each affected /codes/{code}.html page as an inactive/deleted/not-supported informational page.
- Added the Phase 3D-A banner marker to the hardening audit inactive-code classifier.

## Warning Banner

This code is inactive, deleted, or not supported by the current CMS RVU26C dataset and should not be used for current billing.

## Validation Results

- python3 tools/validate_homepage_specs.py: PASS, hard_error_count 0.
- homepage_specs_count: 3874
- canonical_numeric_cpt_count: 3874
- Direct reference scan across active datasets: PASS; no references to the 28 codes remain in cpt_database.json, rvu_database.json, cpt_decision_tree.json, specialty_hierarchy.json, modifier_rules.json, ncci_bundles.json, index.html, or codes/index.html.
- HTTP validation: 28/28 pages returned HTTP 200.
- Warning banner validation: 28/28 pages contain the warning banner.
- Phase 3A hardening score after Batch 1: 335 hard errors remaining, integrity score 91.35.
- Remaining hard errors are outside this batch scope: {'page_metadata': 6, 'rvu': 329}

## Before / After Hardening Delta

- Before Batch 1: 368 Phase 3A hard errors, including 357 zero-RVU active records and 11 metadata mismatches.
- After Batch 1: 335 hard errors, including 329 zero-RVU active records and 6 metadata mismatches.
- Net reduction: 33 hard errors. This equals 28 removed zero-RVU dataset defects plus 5 metadata mismatches on the remediated old hernia pages.

## Screenshot / Example Evidence

- Representative page examples validated by HTTP/banner checks: 49566, 49652, 99218, 99441.
- Screenshot capture was attempted with local Google Chrome headless and failed because Chrome hung with shared-memory descriptor error before writing PNG output. Evidence log: qa_artifacts/phase3d_a_dataset_defect_batch1_2026_06_11/screenshot_capture_blocker.log.
- No screenshot files were fabricated.

## Deliverable Artifacts

- qa_artifacts/phase3d_a_dataset_defect_batch1_2026_06_11/dataset_defect_batch1_archive.json
- qa_artifacts/phase3d_a_dataset_defect_batch1_2026_06_11/http_warning_validation.csv
- qa_artifacts/phase3d_a_dataset_defect_batch1_2026_06_11/platform_hardening_after_batch1_scorecard.json
- qa_artifacts/phase3d_a_dataset_defect_batch1_2026_06_11/screenshot_capture_blocker.log
- tools/remediate_phase3d_a_dataset_defects.py

## Deployment Recommendation

Proceed to staging review only after human review of this package. Do not deploy production until staging verifies that the 28 codes are absent from active search/Case Builder and the retained pages show the warning banner.

## Exclusions

- Did not remediate the 43 re-import candidates.
- Did not remediate the 46 specialty-review candidates.
- Did not remediate carrier-priced, anesthesia, bundled, technical-only, or other zero-RVU categories.
- No redirects created.
- No production deployment performed.
