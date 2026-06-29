# Global Surgery Modifier Intelligence Engine

FreeCPTCodeFinder uses this workflow as educational coding support for postoperative surgical modifiers. It does not replace AMA CPT, CMS manuals, NCCI policy, payer rules, or certified coder review.

## Workflow

1. After the surgeon finishes the case, ask whether today's operation occurred during the postoperative global period of a previous surgery.
2. If no, continue standard Case Builder logic: NCCI, MPPR, modifier 51, modifier 59/X-modifiers, modifier 80 examples, APP productivity, and payment estimates.
3. If yes, collect the previous CPT code, operation date, previous surgeon, same-surgeon status, and same-group status.
4. Automatically calculate the previous CPT global period as 0, 10, or 90 days. The engine uses CPT database metadata when available and a conservative code-class fallback only when metadata is absent.
5. Display the postoperative day and whether today's operation remains within the calculated global period.
6. Apply the CMS decision sequence:
   - Planned or anticipated at the original operation: recommend modifier 58.
   - More extensive than the original procedure: recommend modifier 58.
   - Therapy following a diagnostic procedure: recommend modifier 58.
   - Unplanned return to the operating room for a related complication: recommend modifier 78.
   - Completely unrelated procedure during the postoperative period: recommend modifier 79.
   - If none fit, warn that documentation may not support 58, 78, or 79.
7. Let the user apply 58, 78, or 79 to all applicable payable non-add-on CPT lines, or manually override.
8. Show the original operation, global period, today's operation, recommended modifier, and whether a new global period begins.

## Confidence Scoring

Every recommendation displays High, Moderate, or Low confidence.

Confidence is based on objective documented criteria:

- calculated global-period status
- postoperative day
- previous CPT global-period length
- documented staged/planned status
- documented more extensive procedure
- documented therapy after diagnostic procedure
- documented return to OR for complication
- documented unrelated diagnosis, site, or clinical problem
- operative-note findings for modifier 22

The interface separates:

- facts extracted from the case
- educational guidance
- documentation gaps

If documentation is incomplete, the engine identifies the missing fields or relationship facts instead of forcing a modifier.

## Modifier 58

Modifier 58 is used for a staged or related procedure during the postoperative period when the subsequent procedure was planned, is more extensive than the original procedure, or is therapy following a diagnostic procedure.

FreeCPTCodeFinder labels modifier 58 as beginning a new global period.

## Modifier 78

Modifier 78 is used for an unplanned return to the operating room or procedure room for a related postoperative complication.

Examples surfaced in the workflow:

- postoperative bleeding
- fascial dehiscence
- anastomotic leak
- bowel injury
- infected hematoma
- wound washout

FreeCPTCodeFinder labels modifier 78 as not beginning a new global period.

## Modifier 79

Modifier 79 is used for an unrelated procedure or service during the postoperative period. Documentation should support that the new procedure is unrelated to the prior operation, commonly by separate diagnosis, site, or clinical problem.

FreeCPTCodeFinder labels modifier 79 as beginning a new global period.

## Modifier 22 Intelligence

Modifier 22 is never applied automatically. The engine only flags possible candidates when objective facts suggest substantially greater work.

Objective indicators include:

- operative time
- adhesiolysis greater than 60 minutes
- high percentage of operative time spent on adhesiolysis
- dense vascular adhesions
- prior multiple laparotomies
- hostile or reoperative field
- severe inflammation
- feculent peritonitis
- major contamination
- morbid obesity
- radiation fibrosis
- mesh explantation
- infected mesh
- large abdominal wall reconstruction
- difficult exposure
- debridement depth and size
- bowel injury risk
- unexpected anatomy
- major blood loss
- operative time greater than 150% of expected

If modifier 22 is selected by the user, the documentation generator uses only entered objective findings and measured operative metrics. It avoids adjectives that are not tied to facts and avoids AI-style language.

## Payment Impact

The modifier 22 payment impact panel displays:

- estimated reimbursement without modifier 22
- estimated reimbursement with a successful modifier 22 appeal
- estimated increase

This is labeled as an educational estimate only. Actual payment depends on payer policy, contract, documentation, and appeal review.

## Implementation Owner

Core logic lives in global_modifier_engine.js. The homepage Case Builder wires the workflow into index.html. Unit coverage lives in test_global_modifier_engine.js.
