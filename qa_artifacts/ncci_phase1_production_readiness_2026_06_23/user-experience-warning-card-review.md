# User Experience Warning Card Review

Scope: 159-pair Phase 1 CMS NCCI modifier-0 release candidate.

## Findings

The warning-card UX is acceptable for production rollout of the 159-pair set.

Answers:

- Is the explanation understandable to a practicing surgeon? Yes. The card states that the secondary CPT is bundled into the primary CPT under an NCCI edit and that the payable estimate was adjusted.
- Does it explain why the code was suppressed? Yes. The line-level card says the code is bundled under a non-bypassable NCCI edit, and the expanded details cite Column 1 / Column 2 logic.
- Does it explain whether a modifier could ever bypass the edit? Yes. Modifier-0 relationships are shown as hard stops; the text states modifier 59, XE, XS, XP, and XU should not be used to bypass modifier-indicator-0 relationships.
- Does it clearly distinguish selected work and payable work? Yes. The bundled line remains visible with Selected wRVU and Payable wRVU 0.00, and the case total shows payable wRVU with selected wRVU in the subtitle.

## Screenshot Evidence

Representative screenshots:

- top25_workflow_screenshots/01-colectomy_enterolysis.png
- top25_workflow_screenshots/03-ostomy_reversal_enterolysis.png
- top25_workflow_screenshots/05-small_bowel_resection_enterolysis.png
- top25_workflow_screenshots/06-ladd_exploratory_laparotomy.png
- top25_workflow_screenshots/08-splenectomy_enterolysis.png
- top25_workflow_screenshots/22-tar_component_separation_control.png
- top25_workflow_screenshots/23-thyroid_parathyroid_control.png
- top25_workflow_screenshots/25-rib_fixation_chest_tube_control.png

## Residual UX Risk

The main risk is not mysterious disappearing wRVUs. The UI keeps selected work visible.

The residual risk is surgeon disagreement with CMS payment policy for real adhesiolysis work. That risk is managed by:

- Keeping the selected line visible.
- Showing payable wRVU as 0.00, not deleting the line.
- Explaining NCCI modifier-0 hard-stop behavior.
- Preserving an issue-report button for disputed cases.
