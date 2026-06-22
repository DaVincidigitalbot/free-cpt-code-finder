# Iatrogenic Splenectomy Bundling Rule Review Package

Date: 2026-06-22
Branch: fix/iatrogenic-splenectomy-bundling-review
Status: Review package only. Not deployed.

## Objective

Add conservative separate-procedure handling for CPT 38100 and 38101 when splenectomy is performed only to manage an iatrogenic splenic injury during another related abdominal operation.

## Proposed JSON Rule Entries

Two entries were added to separate_procedure_rules.json:

- iatrogenic-splenic-injury-total-splenectomy: secondary CPT 38100
- iatrogenic-splenic-injury-partial-splenectomy: secondary CPT 38101

Both rules use:

- rule: bundled_when_context_matches
- relationship: iatrogenic_complication_treatment
- requires_context: true
- suppress_when.splenic_indication: iatrogenic_splenic_injury
- modifier_risk: never_bypass_for_iatrogenic_complication
- status: review_package

Payment suppression is not triggered by CPT pairing alone. The splenectomy line is suppressed only when the clinical context explicitly marks the splenic indication as iatrogenic_splenic_injury.

## Abdominal Parent CPT Families Included

- Gastric: 43620, 43621, 43622, 43631, 43632, 43633, 43634, 43635, 43840
- Small bowel / colorectal: 44120, 44121, 44140, 44143, 44155, 44202, 44203, 44204, 44205, 44206, 44207, 44208, 44210, 44212
- Pancreas: 48140, 48150, 48153
- Exploratory abdominal access: 49000

Note: distal pancreatectomy 48140 suppresses 38100 only when the splenectomy is specifically marked as iatrogenic splenic injury. It does not suppress for planned oncologic splenectomy or distinct splenic pathology.

## Excluded / Distinct Splenic Indications

The rule does not suppress for:

- traumatic_splenic_injury
- pre_existing_splenic_pathology
- splenic_mass
- hypersplenism
- abscess
- planned_oncologic_splenectomy
- separate_encounter
- clinically_independent_splenic_indication

## UI Warning Behavior

- Explicit iatrogenic splenic injury context: CPT 38100/38101 remains visible as selected/performed, but payable wRVU and payable reimbursement are set to 0.00 with a bundled warning.
- Unknown splenic context with a related abdominal parent: no automatic suppression. Case Builder shows a review-required warning and keeps the splenectomy payable.
- Distinct splenic indication context: no suppression and no separate-procedure warning from this rule.
- Existing NCCI relationships still apply independently. Example: trauma laparotomy + splenectomy keeps 38100 payable, but existing logic may bundle 49000 into the organ-specific splenectomy.

Warning text:

> CPT 38100/38101 is a separate-procedure splenectomy code. When splenectomy is performed only to manage an iatrogenic splenic injury during another abdominal operation, it is generally not separately reportable. If the splenectomy was performed for trauma, pre-existing splenic disease, malignancy, abscess, hypersplenism, or a distinct indication, separate reporting may be supportable with documentation.

## Positive Test Cases

- 44140 + 38100 with splenicIndication=iatrogenic_splenic_injury: 38100 suppressed; payable wRVU 22.03; selected wRVU 41.09.
- 43620 + 38100 with splenicIndication=iatrogenic_splenic_injury: 38100 suppressed; payable wRVU 33.19; selected wRVU 52.25.
- 48140 + 38100 with splenicIndication=iatrogenic_splenic_injury: 38100 suppressed; payable wRVU 25.66; selected wRVU 44.72.
- 44140 + 38101 with splenicIndication=iatrogenic_splenic_injury: 38101 suppressed; payable wRVU 22.03; selected wRVU 41.09.

## Negative / Do-Not-Suppress Test Cases

- 49000 + 38100 with splenicIndication=traumatic_splenic_injury: 38100 remains payable. Existing NCCI may still bundle 49000 into 38100.
- 38100 alone with splenicIndication=splenic_mass: 38100 remains payable.
- 44140 + 38100 with splenicIndication=pre_existing_splenic_pathology: 38100 remains payable.
- 44140 + 38100 with splenicIndication=separate_encounter: 38100 remains payable.
- 44140 + 38100 with no splenic context: 38100 remains payable and shows review-required warning.

## Before / After Payable wRVU Examples

- Colectomy 44140 + total splenectomy 38100, unknown context: selected/payable wRVU 41.09 with review warning.
- Colectomy 44140 + total splenectomy 38100, iatrogenic context: selected wRVU 41.09; payable wRVU 22.03; 38100 contributes 0.00 payable wRVU.
- Gastrectomy 43620 + total splenectomy 38100, iatrogenic context: selected wRVU 52.25; payable wRVU 33.19; 38100 contributes 0.00 payable wRVU.
- Distal pancreatectomy 48140 + total splenectomy 38100, iatrogenic context: selected wRVU 44.72; payable wRVU 25.66; 38100 contributes 0.00 payable wRVU.

## Validation

Commands run:

- node --check modifier_engine.js
- inline index.html script parsed with new Function(...)
- node --check scripts/validate_iatrogenic_splenectomy_rule.js
- node --check scripts/capture_iatrogenic_splenectomy_validation.js
- node scripts/validate_iatrogenic_splenectomy_rule.js
- local browser validation via scripts/capture_iatrogenic_splenectomy_validation.js

Browser validation:

- Status: pass
- Console messages: []
- JSON: qa_artifacts/iatrogenic_splenectomy_2026_06_22/browser-validation.json
- Rule validation JSON: qa_artifacts/iatrogenic_splenectomy_2026_06_22/rule-validation.json
- Screenshots:
  - qa_artifacts/iatrogenic_splenectomy_2026_06_22/colectomy-38100-iatrogenic-suppressed.png
  - qa_artifacts/iatrogenic_splenectomy_2026_06_22/colectomy-38100-review-required.png

## Changed Files

- index.html
- modifier_engine.js
- separate_procedure_rules.json
- scripts/validate_iatrogenic_splenectomy_rule.js
- scripts/capture_iatrogenic_splenectomy_validation.js
- qa_artifacts/iatrogenic_splenectomy_2026_06_22/browser-validation.json
- qa_artifacts/iatrogenic_splenectomy_2026_06_22/rule-validation.json
- qa_artifacts/iatrogenic_splenectomy_2026_06_22/colectomy-38100-iatrogenic-suppressed.png
- qa_artifacts/iatrogenic_splenectomy_2026_06_22/colectomy-38100-review-required.png

## Deployment Status

Not deployed. This branch is ready for review only.
