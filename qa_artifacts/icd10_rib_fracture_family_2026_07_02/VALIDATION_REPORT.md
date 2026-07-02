# ICD-10 Rib Fracture Family Validation

Date: 2026-07-02
Branch: review/icd10-rib-fracture-family
Base URL validated locally: http://127.0.0.1:8787
Deployment: not deployed

## Scope

- Added Rib fracture / chest wall trauma diagnosis family for CPT 21811, 21812, and 21813.
- Added selectable ICD-10 diagnosis pointer behavior in Case Builder.
- Added diagnosis pointer output to audit report and JSON export.
- Added 21813 to the CPT database/search source.
- Marked 21812 as an add-on code in the runtime add-on set and CPT database.

## ICD-10 Codes Added

Single rib fracture:
- S22.31XA, S22.32XA, S22.39XA
- S22.31XD, S22.32XD, S22.39XD
- S22.31XS, S22.32XS, S22.39XS

Multiple rib fractures:
- S22.41XA, S22.42XA, S22.49XA
- S22.41XD, S22.42XD, S22.49XD
- S22.41XS, S22.42XS, S22.49XS

Flail chest:
- S22.5XXA, S22.5XXD, S22.5XXS

Traumatic pneumothorax / hemothorax:
- S27.0XXA, S27.0XXD, S27.0XXS
- S27.1XXA, S27.1XXD, S27.1XXS
- S27.2XXA, S27.2XXD, S27.2XXS

Chest wall injury / blunt chest trauma:
- S29.8XXA, S29.8XXD, S29.8XXS
- S29.9XXA, S29.9XXD, S29.9XXS

## Synonyms Added

- rib fracture
- rib fractures
- multiple rib fractures
- broken ribs
- flail chest
- chest trauma
- blunt chest trauma
- rib fixation
- SSRF
- surgical stabilization of rib fractures
- chest wall trauma
- additional ribs
- seven or more ribs

## Browser Validation

Screenshots:
- screenshots/01-search-ssrf-results.png
- screenshots/02-21811-single-rib-right-initial-pointer-a.png
- screenshots/03-21812-multiple-rib-fractures-pointers-ab.png
- screenshots/04-audit-report-diagnosis-pointers.png
- screenshots/05-21813-flail-chest-exported.png

Videos:
- videos/page@0661daefb61054c8ab7fc21ea9b076b2.webm
- videos/page@3e2fc0beb129ae5e998ce84f1830305c.webm

Generated exports:
- validation-output.json
- rib-icd10-export.json

Browser checks passed:
- Search "rib fracture" returns 21811, 21812, and 21813.
- Search "multiple rib fractures" returns 21811, 21812, and 21813.
- Search "flail chest" returns 21811, 21812, and 21813.
- Search "broken ribs" returns 21811, 21812, and 21813.
- Search "SSRF" returns 21811, 21812, and 21813.
- 21811 supports laterality-specific diagnosis selection with S22.31XA pointer A.
- 21812 supports multiple diagnosis selection with S22.41XA pointer A and S22.42XA pointer B.
- 21813 supports flail chest plus traumatic hemopneumothorax pointers A/B.
- Audit report includes diagnosis pointer rows.
- JSON export includes diagnoses and line-level diagnosisPointers.

## Regression Summary

Commands run:
- node case_test_suite.js
  - Result: 110/110 passed.
- node final_hardening_validation.js
  - Result: 54/54 scenarios passing.
- node validation_evidence.js
  - Result: high-risk scenarios and failure blocking checks completed successfully.
- python3 test_modifier57_em_slice.py
  - Result: passed.
- JSON parse checks for cpt_database.json and cpt_decision_tree.json
  - Result: passed.
- Homepage JavaScript parse check
  - Result: passed.
- Targeted rib ICD-10 assertions
  - Result: passed.

Regression surfaces covered:
- MPPR
- Modifier 58/78/79
- Modifier 22
- NCCI
- ICD-10 pointer engine
- inpatient-only warnings
- Medicaid warnings
- APP mode

## Notes

- No production deployment was performed.
- Failed-run zero-byte videos were moved to trash; only successful validation videos remain in this artifact folder.
