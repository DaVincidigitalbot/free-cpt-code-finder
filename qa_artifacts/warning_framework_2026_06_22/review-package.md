# Case Builder Warning Framework Review Package

Date: 2026-06-22
Branch: fix/case-builder-warning-framework-review
Base: origin/fix/iatrogenic-splenectomy-bundling-review
Status: Review package only. Not deployed.

## Objective

Standardize Case Builder warnings into one readable educational framework before adding more separate-procedure rules.

## Warning Classes

### Class A: NCCI Hard Stop

- Color: red
- Trigger: non-bypassable NCCI modifier-indicator-0 relationships
- Example validated: 44207 + 44180
- Default display: NCCI Hard Stop; CPT XXXX is bundled into CPT YYYY under an NCCI edit that cannot be bypassed. Payable estimate adjusted accordingly.
- Expanded Learn More: NCCI explanation, Column 1 / Column 2 logic, modifier restrictions, documentation discussion.

### Class B: Separate Procedure

- Color: orange
- Trigger: separate-procedure payable suppression or review-required separate-procedure context
- Examples validated:
  - 44005 + 49000
  - 44140 + 38100 with splenicIndication=iatrogenic_splenic_injury
- Default display: Separate Procedure; CPT XXXX is generally not separately reportable in this clinical context. Payable estimate adjusted accordingly.
- Expanded Learn More: separate-procedure explanation, clinical examples, documentation considerations, modifier discussion.

### Class C: Documentation Opportunity

- Color: blue
- Trigger: documentation-sensitive warnings where payable suppression is not the issue
- Example validated: 99214 + 44140 with same-day major surgery context and modifier 25 selected
- Default display: Documentation Opportunity; Documentation may support additional review.
- Expanded Learn More: modifier/documentation discussion and suggestions.

## UI Behavior

- Bundled lines now show code, description, selected wRVU, payable wRVU, and one warning card.
- Duplicate warning paragraphs are removed.
- Long educational text is hidden under Learn More.
- The old inline bundled paragraph is no longer rendered.
- Modifier-denial/caution details are folded into the standardized warning cards for active line warnings.

## Validation

Command:

- NODE_PATH=/tmp/fccf-pw/node_modules node scripts/capture_warning_framework_validation.js

Validation result:

- Status: pass
- Console messages: []
- No duplicate warning validation: pass
- Desktop overflow validation: pass
- Mobile overflow validation: pass

Artifacts:

- qa_artifacts/warning_framework_2026_06_22/warning-framework-browser-validation.json
- qa_artifacts/warning_framework_2026_06_22/desktop-ncci-hard-stop-44207-44180.png
- qa_artifacts/warning_framework_2026_06_22/desktop-separate-procedure-44005-49000.png
- qa_artifacts/warning_framework_2026_06_22/desktop-separate-procedure-38100-iatrogenic.png
- qa_artifacts/warning_framework_2026_06_22/desktop-documentation-opportunity-99214-44140.png
- qa_artifacts/warning_framework_2026_06_22/mobile-separate-procedure-44005-49000.png

## Changed Files

- index.html
- scripts/capture_warning_framework_validation.js
- qa_artifacts/warning_framework_2026_06_22/*

## Deployment Status

Not deployed. Main was not touched.
