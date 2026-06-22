# CPT 49255 Omentectomy Separate-Procedure Review Package

Date: 2026-06-22
Branch: review/separate-procedure-49255-omentectomy-202606222330
Base: origin/main at 6224499982578f7d7066ea4d5f11d241edcc840b
Status: Review only. Not deployed.

## Objective

Add conservative, context-gated handling for CPT 49255 when omentectomy is performed for cytoreduction/debulking, to accomplish the primary abdominal oncologic operation, or as an incidental/integral part of the same abdominal operation.

## Proposed Rule

- Secondary CPT: 49255
- Rule: bundled_when_context_matches
- Relationship: abdominal_oncologic_debulking_integral
- Category: separate_procedure
- Status: review_package
- Suppression requires explicit omentectomy context. CPT pairing alone does not suppress payable wRVU.

## Parent CPT Family Included

Explicit parent family only:

- 45126: pelvic exenteration for colorectal malignancy
- 49203: open intra-abdominal tumor/peritoneal/mesenteric/retroperitoneal tumor excision
- 58240: pelvic exenteration for gynecologic malignancy
- 58943: oophorectomy for ovarian malignancy
- 58952: BSO with omentectomy and TAH for malignancy
- 58956: BSO with total omentectomy for malignancy

## Suppression Contexts

Suppress CPT 49255 only when the 49255 line explicitly has one of:

- cytoreduction_debulking
- included_in_parent_operation
- accomplish_primary_abdominal_oncologic_operation
- incidental_integral_same_abdominal_operation

## Escape Hatches

Do not suppress CPT 49255 when context indicates:

- isolated_omental_infarction
- omental_torsion
- omental_mass
- omental_abscess
- distinct_omental_biopsy_resection
- trauma_related_omental_injury
- separate_encounter
- clinically_independent_omental_indication

Unknown context remains payable and shows a coder-review Separate Procedure card.

## Warning Language

CPT 49255 is a separate-procedure omentectomy code. When omentectomy is performed for cytoreduction/debulking, to accomplish the primary abdominal oncologic operation, or as an incidental/integral part of the same abdominal operation, it is generally not separately payable. If the omentectomy was performed for isolated omental infarction or torsion, omental mass, abscess, distinct omental biopsy/resection, trauma-related omental injury, separate encounter, or another clinically independent omental indication, separate reporting may be supportable with documentation.

## Positive Suppression Tests

- 58952 + 49255 with omentectomyContext=cytoreduction_debulking: selected wRVU 38.86; payable wRVU 26.61; 49255 suppressed 12.25 wRVU.
- 58956 + 49255 with omentectomyContext=included_in_parent_operation: selected wRVU 34.48; payable wRVU 22.23; 49255 suppressed 12.25 wRVU.
- 49203 + 49255 with omentectomyContext=incidental_integral_same_abdominal_operation: selected wRVU 29.01; payable wRVU 16.76; 49255 suppressed 12.25 wRVU.

## Negative / Escape-Hatch Tests

- 49255 alone with omentalIndication=omental_mass: 49255 remains payable.
- 58952 + 49255 with unknown context: 49255 remains payable and shows coder-review card.
- 58952 + 49255 with omentalIndication=omental_mass: 49255 remains payable.
- 58952 + 49255 with encounter=separate_encounter: 49255 remains payable.

## Browser Validation

Command:

- BASE_URL=http://127.0.0.1:8795 NODE_PATH=/tmp/fccf-pw/node_modules node scripts/capture_49255_omentectomy_validation.js

Result:

- Status: pass
- Console messages: []
- Overflow: none
- Suppressed debulking screenshot captured
- Unknown-context review-required screenshot captured

Artifacts:

- qa_artifacts/separate_procedure_49255_omentectomy_2026_06_22/browser-validation.json
- qa_artifacts/separate_procedure_49255_omentectomy_2026_06_22/rule-validation.json
- qa_artifacts/separate_procedure_49255_omentectomy_2026_06_22/bso-hysterectomy-49255-debulking-suppressed.png
- qa_artifacts/separate_procedure_49255_omentectomy_2026_06_22/bso-hysterectomy-49255-review-required.png

## Regression Validation

- Existing 44005 + 49000 validation remains PASS.
- Existing iatrogenic splenectomy validation remains PASS.
- Existing 29870 same-knee arthroscopy validation remains PASS.
- Existing warning-framework validation remains PASS.
- separate-procedure audit now reports 85 relationships, including 6 context-gated 49255 parent relationships.

## Recommendation

Recommend review approval before deployment, with one explicit clinical review point: confirm whether parent family should remain limited to loaded malignancy/debulking/tumor-resection codes only, or whether future gynecologic oncology codes not currently loaded should be added later. Do not broaden this package before review.

## Changed Files

- index.html
- modifier_engine.js
- separate_procedure_rules.json
- separate-procedure-audit.json
- scripts/validate_49255_omentectomy_rule.js
- scripts/capture_49255_omentectomy_validation.js
- qa_artifacts/separate_procedure_49255_omentectomy_2026_06_22/*

## Deployment Status

Not deployed. This package is ready for review.
