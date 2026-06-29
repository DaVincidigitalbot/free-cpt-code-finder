# Global Surgery Modifier Intelligence Engine Review Package

Branch: review/global-modifier-intelligence-v1

Production deployment: not performed.

Review purpose: surgeon/coder approval of user-facing language, coding logic, payer-risk framing, and production readiness.

## Exact User-Facing Language

### Workflow And Global-Period Language

- "Global Surgery Review"
- "Not reviewed"
- "Ask after the case is built: did this operation occur during the postoperative global period of a previous surgery?"
- "Finish case"
- "Global Surgery Modifier Assistant"
- "Postoperative modifier review"
- "Did this operation occur during the postoperative global period of a previous surgery?"
- "No"
- "Continue normal case-builder logic."
- "Yes"
- "Launch CMS global modifier workflow."
- "Previous operation"
- "Previous CPT code"
- "Previous operation date"
- "Today operation date"
- "Previous surgeon"
- "Same surgeon?"
- "Same group?"
- "Calculate global period"
- "Continue"
- "Back"
- "Automatic global-period calculation"
- "Postoperative day {N} of a {0|10|90}-day global period. Patient is still in the global period."
- "Postoperative day {N} of a {0|10|90}-day global period. Patient is outside the global period."
- "Global period cannot be calculated until the missing fields are documented."
- "Missing: {fields}"
- "Reviewed: no global period"
- "Standard NCCI, MPPR, modifier 51/59/80, and APP mode logic continues normally."
- "Reviewed: no supported postoperative modifier"
- "Documentation may not support 58, 78, or 79."

### Modifier 58 Language

- "Modifier 58"
- "Staged or related procedure during the postoperative period."
- "Planned or anticipated procedure"
- "More extensive procedure than the original operation"
- "Therapy following a diagnostic procedure"
- "Begins a new postoperative global period"
- "Modifier 58 applies to staged, more extensive, or therapeutic procedures during the postoperative period and begins a new global period."
- "Planned or anticipated at the original operation."
- "More extensive than the original procedure."
- "Therapy following a diagnostic procedure."
- "CMS Medicare Claims Processing Manual — modifier 58 identifies a staged, more extensive, or therapeutic procedure during the postoperative period and starts a new global period"

### Modifier 78 Language

- "Modifier 78"
- "Unplanned return to the operating room for a related complication."
- "Unplanned return to OR or procedure room"
- "Related to the original procedure"
- "Used for complications such as bleeding, dehiscence, leak, injury, infected hematoma, or washout"
- "Does not begin a new postoperative global period"
- "Modifier 78 applies to an unplanned return to the OR/procedure room for a related complication and does not begin a new global period."
- "Unplanned return to the operating room for a related postoperative complication."
- "CMS Medicare Claims Processing Manual — modifier 78 identifies an unplanned return to the operating/procedure room for a related complication during the postoperative period and does not start a new global period"

### Modifier 79 Language

- "Modifier 79"
- "Unrelated procedure during the postoperative period."
- "Procedure is unrelated to the previous operation"
- "Requires a separate diagnosis, site, or clinical problem"
- "Begins a new postoperative global period"
- "Modifier 79 applies to an unrelated procedure during the postoperative period and begins a new global period."
- "Procedure is unrelated to the prior operation."
- "CMS Medicare Claims Processing Manual — modifier 79 identifies an unrelated procedure during the postoperative period and starts a new global period"

### Modifier 22 Language

- "Modifier 22 objective work review"
- "Paste the operative report or enter objective facts. The engine flags candidates only when documented facts suggest substantially greater work. It does not automatically apply -22."
- "Target CPT"
- "Expected minutes"
- "Actual minutes"
- "Total operative minutes"
- "Adhesiolysis minutes"
- "Blood loss mL"
- "Operative report"
- "Paste objective operative findings here"
- "Objective findings"
- "Analyze modifier 22"
- "Possible Modifier 22 Candidate"
- "Modifier 22 not strongly supported by objective criteria entered"
- "Surgeon selected modifier 22 for the target CPT"
- "Documentation generator"
- "Copy justification"
- "Modifier 22 justification copied"
- "CMS/AMA modifier 22 guidance — increased procedural services require objective documentation of substantially greater work"
- "Surgeon-selected modifier 22 candidate. Do not submit unless the operative report contains objective facts supporting substantially greater work."
- "Modifier 22 should be reviewed only when objective documentation supports substantially greater work than typical for the CPT code."
- "This procedure required substantially greater work than typically required for CPT XXXXX because the documented operative findings increased technical difficulty, operative time, and operative risk."
- "These objective findings support surgeon review for modifier 22."

### Confidence / Why-Panel Language

- "Confidence: High"
- "Confidence: Moderate"
- "Confidence: Low"
- "Why this modifier is recommended"
- "Facts extracted from the case"
- "No objective case facts documented yet."
- "Educational guidance"
- "No additional guidance."
- "Documentation gaps"

### Payment-Impact Disclaimers

- "Payment impact estimate"
- "Without modifier 22: {amount}"
- "With successful modifier 22 appeal: {amount}"
- "Estimated increase: {amount}"
- "Educational estimate only. Actual payer allowance depends on documentation, contract, and appeal review."
- "Estimated APP Productivity is not the same as compensation, reimbursement, or guaranteed employer wRVU credit. Actual attribution depends on payer rules, documentation, modifier acceptance, scope of practice, supervision requirements, and employer compensation policy."
- "Educational estimate only. Not legal or billing advice."
- "Automated coding support. Requires coder review prior to claim submission. CPT © AMA."

### Documentation-Gap Warnings

- "Previous CPT code, previous operation date, and today operation date are required to calculate global-period status."
- "Specific unrelated diagnosis, site, or clinical problem."
- "Document whether the procedure was planned/staged, more extensive, therapy after diagnostic procedure, complication-related return to OR, or unrelated to the prior operation."
- "Operative note or objective findings."
- "Duration of adhesiolysis."
- "Total operative time."
- "Expected or typical operative time for comparison."
- "Documentation may not support modifiers 58, 78, or 79 based on the selected answers."

## Clinical / Coding Review Table

| Recommendation type | Triggering criteria | User-facing recommendation | Confidence level logic | Documentation required | Known payer-risk / denial-risk language |
|---|---|---|---|---|---|
| No global modifier | Current case is outside prior CPT global period, or user reports no global-period context | "No postoperative global modifier indicated"; standard NCCI/MPPR logic continues | High when dates/code allow calculation outside global; otherwise Low if missing required fields | Prior CPT code, prior operation date, current operation date | Avoids unnecessary postop modifier. Still requires payer-specific review. |
| Modifier 58 | In global period plus documented planned/staged operation, more extensive procedure, or therapy after diagnostic procedure | "Recommended Modifier -58"; staged/related procedure; begins new global period | High when global-period calculation and at least one 58 criterion are documented; Low if dates/code missing | Original plan/anticipation, staged intent, more-extensive rationale, or diagnostic-to-therapeutic relationship | Risk if used for a complication return to OR, or if staged intent is not documented. |
| Modifier 78 | In global period plus documented unplanned return to OR/procedure room for related complication | "Recommended Modifier -78"; unplanned related complication; does not begin new global period | High when global-period calculation, return-to-OR status, related complication, and complication type are documented | Prior CPT/date, current date, return to OR/procedure room, related complication, same/same-group context when relevant | Risk if the case is planned/staged, unrelated, or not clearly in OR/procedure-room setting. |
| Modifier 79 | In global period plus documented unrelated procedure | "Recommended Modifier -79"; unrelated procedure; begins new global period | High/Moderate when unrelated relationship and separate diagnosis/site/problem are documented; gap if unrelated rationale missing | Prior CPT/date, current date, unrelated diagnosis/site/problem, relationship to prior operation | Risk if diagnosis/site/problem is not distinct or payer considers the procedure related to prior surgery. |
| Modifier 22 candidate | Multiple objective unusual-work criteria, adhesiolysis >60 min, or operative time >150% expected | "Possible Modifier 22 Candidate"; surgeon review only | High with 3+ objective criteria; Moderate with fewer but meaningful objective metrics; Low when objective support is absent/incomplete | Operative time, expected time, adhesiolysis duration, objective findings, increased technical difficulty/risk, and no embellishment | High denial risk if documentation is subjective, unsupported, missing expected-time comparison, or payer rejects increased-work appeal. |

## Representative Case Walkthrough

### Case Facts Entered

- Return to OR during global period.
- Previous CPT assumed for global-period calculation: 44140, 90-day global.
- Previous operation date: 2026-06-10.
- Current operation date: 2026-06-29.
- Postoperative day: 19.
- Patient is still in the prior 90-day global period.
- Current case: colostomy/mucous fistula takedown; extended right hemicolectomy with ileocolonic anastomosis.
- 129 minutes adhesiolysis of 201 total operative minutes.
- Mesh explantation.
- 36 cm2 excisional debridement including skin, subcutaneous tissue, fascia, and muscle.
- Feculent peritonitis.
- Complex abdominal wall closure.

### What The Engine Recommends

Global modifier recommendation: Modifier 78

Confidence: High

User-facing reason:

"Unplanned return to the operating room for a related postoperative complication."

Facts extracted from the case:

- "Postoperative day 19 of a 90-day global period. Patient is still in the global period."
- "Same surgeon: yes."
- "Same group: yes."
- "Documented unplanned return to the operating room for a related postoperative complication."
- "Complication documented: feculent peritonitis / contaminated return to OR."

Educational guidance:

- "Modifier 78 applies to an unplanned return to the OR/procedure room for a related complication and does not begin a new global period."

Modifier 22 review: Possible Modifier 22 Candidate

Confidence: High

Important: the engine does not automatically apply modifier 22. It flags the case for surgeon review.

Objective criteria supporting review:

- "Feculent peritonitis documented."
- "Major contamination documented."
- "Mesh explantation documented."
- "Large abdominal wall reconstruction documented."
- "Difficult exposure documented."
- "Debridement depth and size documented."
- "129 minutes of adhesiolysis documented."
- "64% of operative time devoted to adhesiolysis."
- "Operative time was 168% of expected."

Generated justification text:

"This procedure required substantially greater work than typically required for CPT 44160 because the documented operative findings increased technical difficulty, operative time, and operative risk. Total operative time was 201 minutes; expected time was 120 minutes; 129 minutes were spent performing adhesiolysis; 64% of operative time was adhesiolysis. Objective findings included: Feculent peritonitis documented. Major contamination documented. Mesh explantation documented. Large abdominal wall reconstruction documented. Difficult exposure documented. Debridement depth and size documented. 129 minutes of adhesiolysis documented. 64% of operative time devoted to adhesiolysis. Operative time was 168% of expected. These objective findings support surgeon review for modifier 22."

### What The Engine Does Not Recommend

- Does not recommend 58 unless the user documents planned/staged status, more extensive procedure, or therapy after diagnostic procedure.
- Does not recommend 79 unless the user documents that the current procedure is unrelated to the prior operation, with a separate diagnosis, site, or clinical problem.
- Does not auto-apply 22.
- Does not treat 58, 78, and 79 as interchangeable.
- Does not suppress NCCI/MPPR/multiple-procedure logic.

## Safety Checks

| Safety check | Status | Evidence |
|---|---|---|
| Does not guarantee payment | Pass | Uses "Educational estimate only. Actual payer allowance depends on documentation, contract, and appeal review." |
| Does not override payer policy | Pass | Explicitly references payer allowance, payer rules, documentation, and coder review. |
| Does not fabricate documentation | Pass | Modifier 22 generator uses entered objective findings and metrics only. Documentation gaps are surfaced instead of filled in. |
| Does not auto-apply modifier 22 | Pass | UI says "It does not automatically apply -22"; checkbox requires surgeon selection. |
| Does not treat 58/78/79 as interchangeable | Pass | Each modifier has separate trigger criteria, global-period effect, and recommendation path. |
| Does not ignore NCCI edits | Pass | Existing NCCI/modifier 59 smoke and regression gates remain active and passed. |
| Does not include CPT descriptors beyond current site behavior | Pass | Review package references only site behavior and example codes; CPT descriptors remain within existing site data behavior and notices. |

## Validation Evidence

- Refined unit tests: PASS 12/12.
- Specialty case validation: PASS 9/9.
- Existing kill suite: PASS 54/54.
- Validation evidence: PASS 10/10 high-risk scenarios.
- Browser smoke: PASS MPPR, APP mode, modifier 80, NCCI/modifier 59.
- Browser workflow: PASS auto global detection, confidence panel, documentation gaps, operative-note extraction.

## Deployment Recommendation

Recommendation: Ready after language edits

Reason: the deterministic logic and regression gates are clean, but this is a clinically sensitive billing feature. Surgeon/coder review should approve or edit the exact wording above before production deployment, especially:

- modifier 22 justification wording
- expected-time comparison language
- payer-risk language for modifier 22 appeals
- modifier 78 wording for contaminated return-to-OR cases
- modifier 79 unrelated-procedure documentation requirements
