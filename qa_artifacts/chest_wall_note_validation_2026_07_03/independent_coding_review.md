# Chest Wall Reconstruction Reference Note - Independent Coding Review

Date: 2026-07-03
Reference: de-identified operative-note image set supplied by surgeon.
Status: local validation/hardening only. Not deployed.

## Executive Finding

The operative narrative strongly supports a single-rib left 10th rib nonunion repair with thoracoscopic assistance and internal fixation. It does not support the broad template code set as billable for this case.

Primary supported CPT: 21811.

Most important discrepancy: the procedure list labels cryoablation as 64421, but the narrative describes AtriCure cryoablation/freezing of the 7th, 8th, and 9th intercostal nerves. That maps to intercostal nerve destruction review, not intercostal nerve injection/block. ClaimIQ now flags 64421 as injection, not cryoablation, and points review toward 64620.

## Independent Narrative Coding

Supported by the narrative:

- 21811 - Open treatment of rib fracture(s) with internal fixation, includes thoracoscopy, first 3 ribs. Evidence: displaced left 10th rib nonunion, thoracoscopic visualization, open exposure over fracture, fracture-end preparation, drill holes, Titan plate fixation, reduction/apposition.
- 64620 - Intercostal nerve destruction/cryoablation review. Evidence: AtriCure cryoablation of left 7th, 8th, and 9th intercostal nerves; each frozen for 1 minute then defrosted.
- 64420 - Single intercostal nerve block review, not 64461 on the current narrative. Evidence: Exparel chemical block of the left 10th intercostal nerve under direct thoracoscopic visualization.
- 32551 - Supported when the note is corrected to reflect the actual separate incision. Surgeon clarification: the chest tube was placed through a separate incision. Documentation should explicitly say separate incision, tube size, position, connection to suction/drainage, and therapeutic indication so it is not misread as routine same-incision drainage.

Not supported by the narrative:

- 21812 - no documentation of 4-6 ribs fixed.
- 21813 - no documentation of 7 or more ribs fixed.
- 32110 - no formal thoracotomy with control of traumatic hemorrhage.
- 32320 - no decortication or parietal pleurectomy; note says no adhesions.
- 32651 - no VATS pulmonary decortication.
- 64421 - the documented multi-level work is cryoablation, not anesthetic injection/block.
- 64461 - the narrative documents an intercostal block, not a thoracic paravertebral block.
- 36620 - listed, but surgeon narrative does not document arterial catheter placement steps; likely anesthesia/perioperative documentation issue.

## Supported ICD-10

- S22.32XK - Fracture of one rib, left side, subsequent encounter for fracture with nonunion. Evidence: old displaced left 10th rib fracture with nonunion causing severe chronic pain.

Additional diagnoses that may be supportable depending on coder/surgeon preference and payer requirements:

- R07.81 - Pleurodynia or R07.89 - other chest pain, if symptom coding is needed as secondary context.
- G89.21 - chronic pain due to trauma, if clinically documented and needed. Current note supports chronic severe pain/opioid use, but diagnosis selection should be coder-reviewed.

Not supported in this reference note:

- S27.331A/D/S - lung laceration codes. These must be searchable for other cases, but this operative note does not document lung laceration.

## Selected vs Payable RVU Model

Reference-case selected review set:

- Selected CPTs: 21811, 64420, 64620, 32551.
- Expected payable CPTs if 32551 distinct-service documentation is clarified: 21811, 64420, 64620, 32551.
- Supported payable line: 32551, assuming the corrected note documents the separate chest tube incision and therapeutic purpose.
- Selected work RVU: 17.35.
- Expected payable work RVU after MPPR with 32551 included: 13.94.
- Expected Medicare payment, total-RVU basis for payable CPTs: $1,019.40.

Conservative payable logic:

- 21811 is primary and paid at 100% work RVU.
- 64620 is secondary and subject to MPPR review in facility setting.
- 64420 is secondary and subject to MPPR review unless payer/anesthesia policy says otherwise.
- 32551 remains payable in the model because the surgeon clarified that a separate incision was made; the note should explicitly document that fact.

## CPT Validation Matrix

| CPT | Status for reference note | CMS/PFS metadata in repo | Documentation requirement |
| --- | --- | --- | --- |
| 21811 | Supported | 0-day global, work RVU 10.52, total RVU 16.31, assistant allowed, MP indicator 2, bilateral indicator 1 | Side, rib number/count, fracture/nonunion, fixation device, reduction, thoracoscopy |
| 21812 | Not supported | Add-on, 0-day global, work RVU 12.68, total RVU 19.62, assistant allowed | At least 4 ribs fixed; additional 3-rib increment after 21811 |
| 21813 | Not supported | 0-day global, work RVU 17.17, total RVU 26.69, assistant allowed | 7 or more ribs fixed; do not stack with 21811/21812 for same construct |
| 32110 | Not supported | 90-day global, work RVU 24.65, total RVU 41.79, assistant allowed, co-surgeon indicator 1 | Thoracotomy plus control of traumatic hemorrhage |
| 32320 | Not supported | 90-day global, work RVU 26.57, total RVU 45.89, assistant allowed, co-surgeon indicator 1 | Decortication and parietal pleurectomy with pleural peel/extent |
| 32551 | Supported after note clarification | 0-day global, work RVU 2.96, total RVU 4.28, assistant not allowed | Separate incision/site, therapeutic indication, tube size, placement, drainage connection |
| 32651 | Not supported | 90-day global, work RVU 18.31, total RVU 31.13, assistant allowed, co-surgeon indicator 1 | VATS partial pulmonary decortication |
| 64421 | Not supported for cryoablation | Add-on/ZZZ, work RVU 0.49, total RVU 1.05, assistant not allowed | Additional intercostal nerve injection/block levels with base block |
| 64620 | Supported for review | 10-day global, work RVU 2.82, total RVU 6.76, assistant not allowed | Intercostal nerve destruction/cryoablation levels, laterality, device, lesion time |

## ClaimIQ Hardening Added

ClaimIQ now generates specific findings for:

- 21812 selected with 21811 when additional ribs are not documented.
- 21813 selected without documented 7-or-more-rib fixation.
- 32110 selected without traumatic hemorrhage-control documentation.
- 32320 selected without decortication/pleurectomy documentation.
- 32651 selected without VATS pulmonary decortication documentation.
- 32551 selected with thoracic operative work, requiring distinct tube-thoracostomy support.
- 64421 selected without 64420.
- 64421 selected with 64620, forcing injection-vs-cryoablation review.
- 64461 selected where only intercostal injection is documented.

## Operative Note Quality Review

Strong documentation:

- Clear indication: severe pain from displaced left 10th rib nonunion with functional limitation and chronic opioid use.
- Clear laterality and rib level.
- Clear fixation technique, device, and reduction.
- Clear cryoablation device, levels, laterality, and freeze/defrost technique.
- Clear chest tube size, route, position, and suction.
- Clear assistant role.

Weak or missing documentation:

- Procedure list uses 64421 for cryoablation; this conflicts with the narrative.
- Procedure list uses 64461 for the Exparel block, but the narrative describes intercostal nerve block, not paravertebral block.
- 32551 is listed separately, and the surgeon clarified that it was placed through a separate incision. The note should remove the ambiguous "through this incision" wording and explicitly state "a separate incision was made for tube thoracostomy."
- Arterial line is listed, but surgeon placement is not described.
- Debridement of prior chest tube site lacks size, depth, tissue type, and medical necessity for separate debridement coding.
- Phrase "Once all ribs reduced and plated" is imprecise because only the left 10th rib is otherwise documented.

Suggested wording improvements:

- "Open treatment of chronic displaced nonunion of the left 10th rib with internal fixation using Titan EXT 60 plate. One rib was repaired."
- "AtriCure cryoablation was performed on the left 7th, 8th, and 9th intercostal nerves for postoperative analgesia; each nerve underwent a 1-minute freeze followed by thaw."
- "A single left 10th intercostal nerve block was performed under thoracoscopic visualization with Exparel/saline mixture. This was not a paravertebral block." Or, if it was paravertebral, document the paravertebral target and technique explicitly.
- For 32551 support: "A separate incision was made for tube thoracostomy. A 28 Fr chest tube was inserted through this separate incision under thoracoscopic visualization and positioned posteriorly to the apex, then connected to suction for [therapeutic indication]."
- For prior tube site: "Sharp excisional debridement of skin/subcutaneous tissue at the prior chest tube site measured X cm by Y cm by Z cm for devitalized/contaminated tissue."

## S27.33 Validation

Repo CMS compact ICD-10-CM FY2026 data contains 13 S27.33 family rows and 9 billable children:

- S27331A, S27331D, S27331S
- S27332A, S27332D, S27332S
- S27339A, S27339D, S27339S

Browser validation confirms these searches return correct rows:

- S27.331A
- S27.331D
- S27.331S
- lung laceration
- laceration of lung
- pulmonary laceration

Root cause assessment: not missing CMS source rows. The prior production symptom is consistent with diagnosis search/indexing/autocomplete behavior, especially dotted-code normalization and plain-English synonym coverage.

## Permanent Validation Suite

Added: tools/validate_chest_wall_reconstruction_suite.py

The suite validates:

- Reference left 10th rib nonunion with cryoablation and chest tube documentation review.
- Simple rib plating.
- Flail chest/seven-rib fixation.
- Lung laceration repair.
- VATS converted to thoracotomy/decortication pattern.
- Chest tube before thoracotomy.
- Chest tube through thoracotomy/operative field.
- Multiple intercostal nerve blocks.
- Cryoablation of multiple intercostal nerves.
- CPT metadata presence for requested chest wall CPTs.
- S27.33 ICD-10 family completeness.
- ClaimIQ rule text for the failure classes above.

Validation command:

\`\`\`bash
python3 tools/validate_chest_wall_reconstruction_suite.py --write-artifacts
\`\`\`

Result: PASS.

## Remaining Ambiguities Requiring Surgeon/Coder Review

- Whether 64620 should be reported per nerve/level or per session under the target payer policy.
- Whether the single Exparel intercostal block should be separately billed when performed by the surgeon during the operation versus treated as bundled/anesthesia-related by payer policy.
- Whether the final signed note explicitly documents the separate chest tube incision and therapeutic indication for 32551.
- Whether symptom/pain diagnoses should be added secondary to S22.32XK.
- Whether any facility/anesthesia documentation separately supports 36620.

## Confidence Score

Chest Wall Reconstruction pathway confidence after this hardening pass: 82/100.

Reason: CPT/ICD completeness and targeted ClaimIQ warnings are now much stronger, and the permanent suite protects the major failure classes. Remaining gap is true free-text operative-note ingestion: current ClaimIQ can reason from selected case lines and validation fixtures, but full "paste operative note and independently code it" remains a larger parser/workflow capability and should not be claimed as complete until implemented and validated.
