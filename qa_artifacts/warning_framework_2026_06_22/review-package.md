# Case Builder Warning Framework Deployment Package

Date: 2026-06-22
Branch: deploy/warning-framework-202606222205
Base: origin/main
Status: Scoped warning-framework deployment package.

## Objective

Standardize Case Builder warnings into a readable educational framework without changing payment logic or adding new separate-procedure rules.

## Scope Included

- NCCI Hard Stop warning card
- Separate Procedure warning card
- Documentation Opportunity warning card
- Duplicate warning removal
- Collapsible Learn More educational content
- Browser validation script and screenshot artifacts

## Scope Excluded

- No new separate-procedure suppression rules
- No iatrogenic splenectomy rule deployment
- No payment-engine logic changes
- No changes to separate_procedure_rules.json

## Warning Classes

### Class A: NCCI Hard Stop

- Color: red
- Trigger: non-bypassable NCCI modifier-indicator-0 relationships
- Example validated: 44207 + 44180
- Default display: NCCI Hard Stop; CPT XXXX is bundled into CPT YYYY under an NCCI edit that cannot be bypassed. Payable estimate adjusted accordingly.
- Expanded Learn More: NCCI explanation, Column 1 / Column 2 logic, modifier restrictions, documentation discussion.

### Class B: Separate Procedure

- Color: orange
- Trigger: currently deployed separate-procedure payable suppression
- Example validated: 44005 + 49000
- Default display: Separate Procedure; CPT XXXX is generally not separately reportable in this clinical context. Payable estimate adjusted accordingly.
- Expanded Learn More: separate-procedure explanation, clinical examples, documentation considerations, modifier discussion.

### Class C: Documentation Opportunity

- Color: blue
- Trigger: documentation-sensitive warnings where payable suppression is not the issue
- Example validated: 99214 + 44140 with same-day major surgery context and modifier 25 selected
- Default display: Documentation Opportunity; Documentation may support additional review.
- Expanded Learn More: modifier/documentation discussion and suggestions.

## UI Behavior

- Bundled lines show code, description, selected wRVU, payable wRVU, and one warning card.
- Duplicate warning paragraphs are removed.
- Long educational text is hidden under Learn More.
- Old inline bundled paragraphs no longer render.
- Modifier-denial and caution details are folded into standardized warning cards for active line warnings.

## Validation

Command:

- NODE_PATH=/tmp/fccf-pw/node_modules node scripts/capture_warning_framework_validation.js

Validation requirements:

- NCCI example renders one red NCCI Hard Stop card.
- Separate-procedure example renders one orange Separate Procedure card.
- Documentation example renders one blue Documentation Opportunity card.
- Duplicate warning validation passes.
- Desktop overflow validation passes.
- Mobile overflow validation passes.
- Console error validation passes.

Artifacts:

- qa_artifacts/warning_framework_2026_06_22/warning-framework-browser-validation.json
- qa_artifacts/warning_framework_2026_06_22/desktop-ncci-hard-stop-44207-44180.png
- qa_artifacts/warning_framework_2026_06_22/desktop-separate-procedure-44005-49000.png
- qa_artifacts/warning_framework_2026_06_22/desktop-documentation-opportunity-99214-44140.png
- qa_artifacts/warning_framework_2026_06_22/mobile-separate-procedure-44005-49000.png

## Changed Files

- index.html
- scripts/capture_warning_framework_validation.js
- qa_artifacts/warning_framework_2026_06_22/*

## Deployment Guardrails

- Deploy from clean branch based on current origin/main.
- Preserve current production changes.
- Do not include unrelated dirty files.
- Confirm separate_procedure_rules.json is unchanged.
- Confirm browser validation has no console errors and no mobile overflow.
