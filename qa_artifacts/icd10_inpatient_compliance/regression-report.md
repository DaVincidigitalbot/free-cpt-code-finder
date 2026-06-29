# ICD-10 Intelligence + Inpatient-Only Compliance Regression Report

Branch: `review/icd10-inpatient-compliance-engine`  
Production deployed: No

## Database Statistics

- ICD-10-CM version: FY2026
- ICD-10-CM rows: 98,186
- Billable ICD-10-CM codes: 74,719
- Non-billable ICD-10-CM hierarchy rows: 23,467
- Inpatient-only version: CY2026
- Inpatient-only codes: 1,438

## Implemented

- Versioned ICD-10-CM data from CMS FY2026 code descriptions in tabular order.
- Versioned inpatient-only data from CY2026 OPPS Addendum E.
- ICD-10 search by code, description, synonym, and abbreviation.
- Suggested diagnoses panel ranked ahead of full search.
- Diagnosis selection with CMS-1500 style pointers A, B, C, etc.
- Many-to-many CPT to diagnosis pointer support.
- Manual diagnosis entry.
- Educational warnings for missing diagnosis, non-billable diagnosis, retired/replaced diagnosis, and CPT/diagnosis mismatch.
- Inpatient-only line warning card.
- Active Case inpatient-only summary warning.
- Audit report and JSON export now include selected diagnoses, diagnosis pointers, diagnosis validation warnings, and inpatient-only warnings.
- Dataset version metadata is included in export.

## Validation

| Check | Result |
|---|---|
| Full ICD-10-CM database loads | Pass |
| Inpatient-only database loads | Pass |
| Search: diverticulitis | Pass |
| Search: hernia | Pass |
| Search: gallstones | Pass |
| Search: abscess | Pass |
| Search: SBO | Pass |
| Search: bowel obstruction | Pass |
| Colorectal diagnosis pointers | Pass |
| Many-to-many diagnosis pointers | Pass |
| Non-billable ICD-10 warning | Pass |
| Inpatient-only warning | Pass |
| JSON export shape | Pass |
| Inline JS syntax | Pass |
| Global modifier engine | Pass |
| Global modifier specialty cases | Pass |
| MPPR regression | Pass |
| Medicaid modifier warning regression | Pass |
| validation_evidence.js | Pass |
| final_hardening_validation.js | Pass |
| kill_test_suite.js | 50/54 pass; same 4 baseline failures reproduced on origin/main |
| source audit | Same pre-existing non-root source-link warning reproduced on origin/main |

## Artifacts

- `qa_artifacts/icd10_inpatient_compliance/01_colorectal_dx_pointers.png`
- `qa_artifacts/icd10_inpatient_compliance/02_inpatient_only_warning.png`
- `qa_artifacts/icd10_inpatient_compliance/03_many_to_many_dx.png`
- `qa_artifacts/icd10_inpatient_compliance/clinical_workflow_video.mp4`
- `qa_artifacts/icd10_inpatient_compliance/icd10_inpatient_validation.json`
- `qa_artifacts/icd10_inpatient_compliance/database-statistics.json`
- `qa_artifacts/icd10_inpatient_compliance/sample_cases.json`

## Final Recommendation

Ready after review.

