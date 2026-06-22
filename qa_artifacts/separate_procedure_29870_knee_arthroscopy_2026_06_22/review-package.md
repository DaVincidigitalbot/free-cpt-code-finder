# CPT 29870 Same-Knee Surgical Arthroscopy Review Package

Date: 2026-06-22
Branch: review/separate-procedure-29870-knee-arthroscopy-202606222240
Base: origin/main at 150ae6544eade14bd89e0162c88e574372af3ec2
Status: Approved deployment package.

## Objective

Add a conservative separate-procedure rule package for CPT 29870 diagnostic knee arthroscopy when performed in the same knee and same encounter as a definitive surgical knee arthroscopy.

## Proposed Rule

- Secondary CPT: 29870
- Rule: bundled_when_context_matches
- Relationship: same_joint_diagnostic_integral
- Category: separate_procedure
- Status: active
- Suppression requires explicit same-knee same-encounter context.

## Parent CPT Family Included

Same-knee surgical arthroscopy parent CPTs:

- 29850, 29851, 29855, 29856
- 29866, 29867, 29868
- 29871, 29873, 29874, 29875, 29876, 29877, 29879
- 29880, 29881, 29882, 29883, 29884, 29885, 29886, 29887, 29888, 29889

## Context Gate

Suppress 29870 only when one of these is true:

- CPT 29870 context has sameKnee=true
- CPT 29870 context has same_anatomic_site=true
- CPT 29870 and the surgical arthroscopy parent have matching RT or LT side context

Do not suppress when context indicates:

- contralateral_knee
- different_joint
- separate_encounter
- separate_session
- staged_diagnostic_only
- diagnostic_arthroscopy_alone
- clinically_independent_diagnostic_indication

Unknown same-knee context remains payable and shows a review-required Separate Procedure card using the summary: Coder review required before payable adjustment.

## Suggested Warning Language

CPT 29870 is a separate-procedure diagnostic knee arthroscopy code. When diagnostic knee arthroscopy is performed in the same knee and same encounter as a definitive surgical knee arthroscopy, it is generally not separately payable. If the diagnostic arthroscopy was performed on the contralateral knee, at a separate encounter/session, or for a clinically independent diagnostic indication, separate reporting may be supportable with documentation.

## Positive Suppression Tests

- 29881 + 29870 with sameKnee=true: selected wRVU 11.91; payable wRVU 6.85; 29870 suppressed 5.06 wRVU.
- 29888 + 29870 with both sides RT: selected wRVU 19.00; payable wRVU 13.94; 29870 suppressed 5.06 wRVU.
- 29871 + 29870 with same_anatomic_site=true: selected wRVU 11.58; payable wRVU 6.52; 29870 suppressed 5.06 wRVU.

## Negative / Escape-Hatch Tests

- 29881 RT + 29870 LT with contralateral_knee: 29870 remains payable.
- 29881 + 29870 with separate_encounter: 29870 remains payable.
- 29870 alone with diagnostic_arthroscopy_alone: 29870 remains payable.
- 29881 + 29870 with unknown same-knee context: 29870 remains payable and review-required card appears.

## Browser Validation

Command:

- BASE_URL=http://127.0.0.1:8793 NODE_PATH=/tmp/fccf-pw/node_modules node scripts/capture_29870_knee_arthroscopy_validation.js

Result:

- Status: pass
- Console messages: []
- Overflow: none
- Same-knee suppressed screenshot captured
- Unknown-context review-required screenshot captured

Artifacts:

- qa_artifacts/separate_procedure_29870_knee_arthroscopy_2026_06_22/browser-validation.json
- qa_artifacts/separate_procedure_29870_knee_arthroscopy_2026_06_22/rule-validation.json
- qa_artifacts/separate_procedure_29870_knee_arthroscopy_2026_06_22/meniscectomy-29870-same-knee-suppressed.png
- qa_artifacts/separate_procedure_29870_knee_arthroscopy_2026_06_22/meniscectomy-29870-review-required.png

## Regression Validation

- Existing 44005 + 49000 validation remains PASS.
- Existing iatrogenic splenectomy validation remains PASS.
- Existing warning-framework validation remains PASS.
- separate-procedure audit now reports 79 relationships, including 24 context-gated 29870 parent relationships.

## Changed Files

- index.html
- modifier_engine.js
- separate_procedure_rules.json
- separate-procedure-audit.json
- scripts/validate_29870_knee_arthroscopy_rule.js
- scripts/capture_29870_knee_arthroscopy_validation.js
- qa_artifacts/separate_procedure_29870_knee_arthroscopy_2026_06_22/*

## Deployment Status

Approved for deployment. Deploy only this 29870 rule package.
