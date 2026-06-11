# Modifier Denial Guidance Report

Generated: 2026-06-11

Branch: `feature/modifier-denial-guidance`

Deployment: not performed.

## Scope

Improve Case Builder modifier-denial messaging only. No reimbursement calculation, NCCI decision, modifier decision, RVU, MPPR, code-pairing, or Case Builder math behavior was intentionally changed.

## Implementation Approach

Added a reusable denial education framework in `index.html` that renders four surgeon-facing sections whenever a modifier denial occurs:

- What happened
- Why it happened
- Modifiers affected
- What to consider next

The framework is display-only. Existing denial branches still determine whether a line is blocked. The new code changes the language shown after the block and adds an expandable `Why?` / `Learn more` explanation.

## Modifier-Denial Inventory

| Scenario identified | Previous message | Proposed / implemented message pattern |
| --- | --- | --- |
| User selects modifier 59 but no NCCI conditional edit exists for the secondary/primary pair | `Modifier -59 blocked because no NCCI conditional edit exists for this code pair.` | Explains that the selected modifier was requested, no conditional NCCI edit exists in the current rule set, distinct-service modifiers should not be substituted without support, and documentation/modifier 22 review may be more appropriate when the issue is increased work. |
| User selects modifier 59 where RT/LT laterality already resolves the distinction | `Modifier -59 blocked because RT/LT laterality already resolves distinctness.` | Explains that RT/LT is the more specific side-based distinction and -59 is not stacked when side is the reason for separation. |
| NCCI pair exists and modifier is not allowed | `Fully bundled pair is non-payable. Modifier cannot rescue payment.` | Explains Column 1/Column 2-style bundling in plain English, states modifier indicator 0 means modifier 59/XS/XE/XP/XU cannot bypass the edit, and suggests documentation review/modifier 22 consideration when appropriate. |
| Conditional NCCI pair remains conflicted because both lines share the same side | `Conditional NCCI pair remains conflicted because both procedures are on the same side. Laterality alone does not establish distinctness.` | Explains that same-side laterality does not establish a distinct procedural service and points the surgeon to separate structure/site/session/practitioner documentation review. |
| Distinct-service modifier attempted on add-on code | `Distinct service modifier blocked on add-on code without explicit CPT support.` | Explains add-on codes are reported with the parent/base procedure and usually do not need 59/X modifiers simply because additional work is listed. |
| Modifier 50 conflicts with RT/LT on same line | `Blocked conflicting use of -50 with RT/LT on the same line.` | Explains that -50 means bilateral while RT/LT identify a single side, and they should not be combined on the same line. |
| Invalid bilateral modifier use | `Blocked invalid bilateral modifier. Code/case structure does not support defensible use of -50.` | Explains that some procedures are unilateral, inherently bilateral, midline, or otherwise not paid with -50, and recommends CPT/CMS/payer review. |

## NCCI Documentation Note

The current CMS NCCI PTP verification for CPT 44207 / 44180 remains documentation-only in this task. This branch does not add or change NCCI pair data. If a non-bypassable NCCI pair is already present in the Case Builder rule set, the new messaging will describe the modifier-indicator-0 consequence. Adding 44207 / 44180 as a live rule would be a separate code-pairing logic change and is intentionally out of scope here.

## Screenshots / Mockups

Captured in `qa_artifacts/modifier_denial_guidance_2026_06_11/screenshots/`:

- `before_modifier_59_denial.png`
- `after_modifier_59_denial.png`

Scenario used: CPT 15734 primary + CPT 43280 secondary with user-selected modifier 59. This exercises the existing no-conditional-NCCI-edit denial path without adding new NCCI data.

## Validation

Browser validation file: `qa_artifacts/modifier_denial_guidance_2026_06_11/modifier_denial_browser_validation.json`

HTTP browser validation file: `qa_artifacts/modifier_denial_guidance_2026_06_11/http_validation.json`

Before and after totals for the same denied-modifier scenario:

| Metric | Before | After |
| --- | ---: | ---: |
| Total wRVU | 40.08 | 40.08 |
| Estimated payment | $1,892.84 | $1,892.84 |
| Case status | BLOCKED | BLOCKED |

Result: calculations unchanged. The after state adds the expandable denial education panel.

HTTP browser console validation captured no warnings or errors.

## Files Changed

- `index.html`
- `audit_reports/modifier_denial_guidance_2026_06_11.md`

## Edge Cases Discovered

- The Case Builder currently has an empty inline `NCCI` object with commented examples. This task did not populate NCCI pairs because that would change pairing behavior.
- The add-on-code primary-rank block still uses the existing generic conflict text because it is not a modifier-denial attempt; it is a case composition/ranking block.
- Local screenshot validation through `file://` produces missing-resource console noise for site assets, but the Case Builder script executed and the before/after totals matched.

## Final Status

Ready for review. No deployment, merge, or production change was performed.

## Addendum: Modifier Caution State

Added after additional review request on 2026-06-11.

### New User-Facing State

The Case Builder now supports three distinct user-facing modifier states:

- Modifier allowed without warning when clearly routine/valid.
- Modifier allowed with caution when documentation-dependent.
- Modifier blocked when rules prohibit it.

The new caution state is used when the existing rule set allows a distinct-service modifier but the modifier is documentation-dependent, for example an NCCI edit with `modAllowed: true` / modifier indicator 1.

### Caution Message

When an NCCI modifier-indicator-1 edit is present and the surgeon selects modifier 59 or an X-modifier, the Case Builder now shows a documentation-required panel:

> Modifier may be allowed for this code pair only when documentation supports a distinct procedural service, separate site, separate encounter, separate lesion, separate organ/structure, or other payer-recognized distinction. Do not append modifier 59/XS automatically.

The exact rendered framework includes:

- What happened: the selected modifier may be allowed only when documentation supports a distinct procedural service.
- Why it matters: modifier indicator 1 allows bypass only when clinically and payer-supported; it is not automatic.
- Modifiers affected: modifier 59, XS, XE, XP, and XU.
- What to document: separate site, encounter, lesion, organ/structure, practitioner, or payer-recognized distinction.

### Validation

Validation artifacts:

- `qa_artifacts/modifier_caution_guidance_2026_06_11/three_state_validation.json`
- `qa_artifacts/modifier_caution_guidance_2026_06_11/screenshots/01_allowed_without_warning_routine_rt.png`
- `qa_artifacts/modifier_caution_guidance_2026_06_11/screenshots/02_allowed_with_caution_indicator_1.png`
- `qa_artifacts/modifier_caution_guidance_2026_06_11/screenshots/03_blocked_indicator_0.png`

| State | Test | Result |
| --- | --- | --- |
| Allowed without warning | 43280-RT | CLEAN, modifier RT applied, no caution/denial panel, total wRVU 17.65, payment $1,012.05 |
| Allowed with caution | Runtime NCCI indicator 1 test: 15734 / 43280 with selected -59 | WARNING, modifier 59 applied, caution panel shown, total wRVU 40.08, payment $1,892.84 |
| Blocked | Runtime NCCI indicator 0 test: 44207 / 44180 with selected -59 | BLOCKED, modifier removed, denial panel shown, total wRVU 46.01, payment $2,081.55 |

### Guardrail Confirmation

No changes were made to modifier logic, calculations, NCCI pair handling, RVU values, MPPR logic, or code selection. The new state is educational display only. Runtime NCCI test pairs were used only in browser validation and were not added to the repository.
