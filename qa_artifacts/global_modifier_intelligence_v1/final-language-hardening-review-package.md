# Global Modifier Intelligence Engine - Final Language Hardening Review Package

Branch: `review/global-modifier-intelligence-v1`  
Deployment status: Do not deploy until surgeon/coder approval.

## Final Recommendation

Ready after review.

Reason: deterministic logic, regression coverage, and conservative language gates are ready for human review. Production should wait for surgeon/coder approval of exact phrasing and payer-risk framing.

## Exact User-Facing Language

### Global Period Screen

- "Did this operation occur during the postoperative global period of a previous surgery?"
- "No"
- "Continue normal case-builder logic."
- "Yes"
- "Launch CMS global modifier workflow."
- "Automatic global-period calculation"
- "Postoperative day {day} of a {0/10/90}-day global period. Patient is still in the global period."
- "Postoperative day {day} of a {0/10/90}-day global period. Patient is outside the global period."
- "Global period cannot be calculated until the missing fields are documented."

### Modifier 58 Language

- "Modifier 58 may be considered for a staged or related procedure during the postoperative period when payer policy and full documentation agree."
- "Documented planned or anticipated procedure"
- "Documented more extensive procedure than the original operation"
- "Documented therapy following a diagnostic procedure"
- "Begins a new postoperative global period"
- "Documentation appears to support consideration of Modifier 58 because the procedure was planned or anticipated at the original operation."
- "Documentation appears to support consideration of Modifier 58 because the procedure is documented as more extensive than the original procedure."
- "Documentation appears to support consideration of Modifier 58 because the procedure is documented as therapy following a diagnostic procedure."

### Modifier 78 Language

- "Modifier 78 may be considered for an unplanned return to the operating room for a related complication when payer policy and full documentation agree."
- "Documented unplanned return to OR or procedure room"
- "Documented relationship to the original procedure"
- "Used for complications such as bleeding, dehiscence, leak, injury, infected hematoma, or washout"
- "Does not begin a new postoperative global period"
- "Documentation appears to support consideration of Modifier 78 because the case is documented as an unplanned return to the operating room for a related postoperative complication."

### Modifier 79 Language

- "Modifier 79 may be considered for an unrelated procedure during the postoperative period when payer policy and full documentation agree."
- "Documented procedure is unrelated to the previous operation"
- "Requires documented separate diagnosis, site, or clinical problem"
- "Begins a new postoperative global period"
- "Documentation appears to support consideration of Modifier 79 because the procedure is documented as unrelated to the prior operation."

### Modifier 22 Language

- "Modifier 22 objective work review"
- "Paste the operative report or enter objective facts. The engine flags possible consideration only when documented facts suggest substantially greater work. It does not automatically apply -22; surgeon/coder review and payer-policy review are required."
- "Possible Modifier 22 Candidate"
- "Modifier 22 lacks enough objective documentation for confident consideration"
- "Objective criteria that may support consideration"
- "Documented objective findings may support consideration of Modifier 22 only if payer policy and full documentation agree. Surgeon/coder review is required, and Modifier 22 is never applied automatically."
- "Surgeon marked Modifier 22 for review for the target CPT"
- "Draft uses only documented facts. Review and edit before use; do not paste blindly into the operative note or appeal letter."
- "These documented findings may support consideration of Modifier 22 after surgeon/coder review and payer-policy review. Review and edit before use."

### Payment-Impact Disclaimers

- "Payment impact estimate"
- "Without modifier 22: {amount}"
- "Potential allowance if payer accepts Modifier 22 after review: {amount}"
- "Estimated increase: {amount}"
- "Educational estimate only. Actual payment depends on payer rules, documentation review, modifier acceptance, contract terms, and claim adjudication."

### Documentation-Gap Warnings

- "Current documentation is incomplete for confident consideration of modifiers 58, 78, or 79 based on the selected answers."
- "Previous CPT code, previous operation date, and today operation date are required to calculate global-period status."
- "Document whether the procedure was planned/staged, more extensive, therapy after diagnostic procedure, complication-related return to OR, or unrelated to the prior operation."
- "Specific unrelated diagnosis, site, or clinical problem."
- "Operative note or objective findings."
- "Duration of adhesiolysis."
- "Total operative time."
- "Expected or typical operative time for comparison."

## Clinical/Coding Review Table

| Recommendation type | Triggering criteria | User-facing recommendation | Confidence logic | Documentation required | Known payer-risk / denial-risk language |
|---|---|---|---|---|---|
| No global modifier | Not in calculated global period, or user answers no global-period relationship | "No postoperative modifier to consider from current documentation" | High when date calculation is complete and outside global period; Low when required facts are missing | Prior CPT, prior date, current date, global-period status | Payer may still require claim-level documentation and standard NCCI/MPPR review. |
| Modifier 58 | In global period plus documented planned/staged procedure, more extensive procedure, or therapy after diagnostic procedure | "Modifier -58 to consider" and "Documentation appears to support consideration of Modifier 58..." | High when global-period calculation and at least one 58 criterion are documented; Low when dates/code are missing | Original plan or staged intent, more-extensive rationale, or diagnostic-to-therapeutic relationship; prior procedure/timing/surgeon/group context | Risk if used for a complication return to OR, if staged intent is not documented, or if payer policy differs. |
| Modifier 78 | In global period plus documented unplanned return to OR/procedure room for related complication | "Modifier -78 to consider" and "Documentation appears to support consideration of Modifier 78..." | High when global-period calculation, OR/procedure-room return, related complication, and complication type are documented | Prior CPT/date, current date, return to OR/procedure room, related complication, same/same-group context when relevant | Risk if the case was planned/staged, unrelated, outside OR/procedure-room setting, or payer does not accept the relationship. |
| Modifier 79 | In global period plus documented unrelated procedure | "Modifier -79 to consider" and "Documentation appears to support consideration of Modifier 79..." | High/Moderate when unrelated relationship and separate diagnosis/site/problem are documented; Low if unrelated rationale is missing | Prior CPT/date, current date, unrelated diagnosis/site/problem, relationship to prior operation | Risk if diagnosis/site/problem is not distinct or payer considers the procedure related to prior surgery. |
| Modifier 22 candidate | Multiple objective unusual-work criteria, adhesiolysis >60 minutes, or operative time >150% expected | "Possible Modifier 22 Candidate" and "may support consideration of Modifier 22" | High with 3+ objective criteria; Moderate with fewer meaningful metrics; Low when objective support is absent/incomplete | Operative time, expected time, adhesiolysis duration, objective findings, increased technical difficulty/risk; facts only | High denial risk if documentation is subjective, lacks expected-time comparison, lacks objective findings, or payer rejects increased-work rationale. |

## Representative Case Walkthrough

Case facts entered:

- Return to OR during global period
- Colostomy/mucous fistula takedown
- Extended right hemicolectomy with ileocolonic anastomosis
- 129 minutes adhesiolysis of 201 total operative minutes
- Mesh explantation
- 36 cm² excisional debridement including skin, subcutaneous tissue, fascia, and muscle
- Feculent peritonitis
- Complex abdominal wall closure

Engine output:

- Global-period status: in postoperative global period if previous CPT/date calculate within 0-, 10-, or 90-day global period.
- Modifier to consider: Modifier 78, if documented as an unplanned return to the OR for a related postoperative complication and payer policy agrees.
- Confidence: High when the prior CPT/date, postoperative day, OR return, related complication, same-surgeon/group context, and complication details are documented.
- Why: documented return to OR during global period; documented related postoperative complication; feculent peritonitis and operative management support complication-related return if tied to the prior operation.
- New global period: No for Modifier 78 as educational guidance.
- Modifier 22: Possible Modifier 22 Candidate, not automatically applied.
- Why Modifier 22 may be considered: 129 minutes adhesiolysis documented; 64% of 201-minute operative time devoted to adhesiolysis; feculent peritonitis; mesh explantation; 36 cm² excisional debridement including skin, subcutaneous tissue, fascia, and muscle; complex abdominal wall closure; reoperative/hostile field if documented in the operative note.

What the engine does not recommend:

- It does not treat Modifier 58 as interchangeable with Modifier 78 unless the return was planned/staged, more extensive, or therapeutic after diagnostic procedure.
- It does not use Modifier 79 unless the current procedure is documented as unrelated by separate diagnosis, site, or clinical problem.
- It does not auto-apply Modifier 22.
- It does not guarantee payment or payer acceptance.
- It does not fabricate reoperative-field or bowel-injury-risk facts unless documented or entered.

## Before/After Language Examples

| Before | After |
|---|---|
| "Recommended Modifier -78" | "Modifier -78 to consider" |
| "Why this modifier is recommended" | "Why this modifier may be considered" |
| "Apply -78 to applicable CPT codes" | "Mark -78 for coder review on applicable CPT codes" |
| "Global period modifier selected" | "Global period modifier marked for coder review" |
| "With successful modifier 22 appeal" | "Potential allowance if payer accepts Modifier 22 after review" |
| "These objective findings support surgeon review for modifier 22." | "These documented findings may support consideration of Modifier 22 after surgeon/coder review and payer-policy review. Review and edit before use." |
| "Modifier 22 should be reviewed only when objective documentation supports..." | "Documented objective findings may support consideration of Modifier 22 only if payer policy and full documentation agree." |
| "Reviewed: no supported postoperative modifier" | "Reviewed: no postoperative modifier to consider" |

## Safety Checks

| Safety requirement | Status | Evidence |
|---|---|---|
| Does not guarantee payment | Pass | Payment panel states actual payment depends on payer rules, documentation review, modifier acceptance, contract terms, and claim adjudication. |
| Does not override payer policy | Pass | 58/78/79/22 language repeatedly says payer policy and full documentation must agree. |
| Does not fabricate documentation | Pass | Modifier 22 generator uses entered metrics and extracted objective findings only. |
| Does not auto-apply Modifier 22 | Pass | UI says Modifier 22 is never applied automatically; checkbox requires surgeon selection for review. |
| Does not treat 58/78/79 as interchangeable | Pass | Separate decision paths, criteria, global-period effects, and documentation requirements. |
| Does not ignore NCCI edits | Pass | Global workflow attaches after existing NCCI/MPPR/modifier conflict engine and retains conflict blocking. |
| Does not include CPT descriptors beyond current site behavior | Pass | Review package references codes generically and does not add new licensed descriptor surfaces. |

## Validation Scope

- Unit tests: PASS - `node test_global_modifier_engine.js`.
- Specialty clinical cases: PASS - `node validate_global_modifier_cases.js` across colorectal, trauma, hernia, vascular, orthopaedic, ENT, and neurosurgery scenarios.
- Regression validation: PASS - `node kill_test_suite.js`, 54/54 scenarios passed.
- Validation evidence: PASS - `node validation_evidence.js`, high-risk scenarios and blocking checks completed.
- Syntax/format: PASS - `node --check global_modifier_engine.js`, `node --check test_global_modifier_engine.js`, `node --check validate_global_modifier_cases.js`, executable `index.html` inline script parse, and JSON parse check.
- Browser screenshots: captured with headless Chrome at `qa_artifacts/global_modifier_intelligence_v1/final_language_package.png` and `qa_artifacts/global_modifier_intelligence_v1/final_case_builder_shell.png`. Existing workflow screenshots and video remain in the same artifact directory.
- Production deployment: blocked until Graydon approves.
