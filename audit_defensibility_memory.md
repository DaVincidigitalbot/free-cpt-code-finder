# AUDIT DEFENSIBILITY MEMORY

Last updated: 2026-04-06

## What exists
- audit-style reasoning in modifier analysis output
- validation warnings/errors in case tray
- confidence indicator and blocking-status logic
- hernia + 15734 risk/defensibility messaging in UI
- copy/export blocking on unsafe cases

## How it works
- modifier analysis generates explanations, warnings, and summary state
- validation engine flags duplicates, NCCI issues, and laterality concerns
- UI surfaces risk cues, questions, and blocking conditions
- hernia-specific risk profile explains confidence, risk, bundling sensitivity, MPPR ambiguity, and documentation needs

## Dependencies
- `modifier_engine.js`
- validation functions in `index.html`
- ranking audit functions in `index.html`
- confidence/blocking UI in `index.html`

## Current state
- defensibility is baked into workflow, not bolted on later
- 15734 logic is explicitly documentation-sensitive
- audit trail exists to explain why procedures/modifiers were chosen
- copy is blocked when validation errors exist
- high-risk scenarios should be surfaced, not hidden

## Known limitations
- not a substitute for payer policy or operative note review
- some risk scoring is heuristic rather than claims-derived
- legal/compliance posture depends on documentation quality outside the app

## Unresolved risks
- 15734 with hernia repair may be challenged if operative note is weak
- bilateral reconstructive work remains payer-variable
- conservative warnings may still under-capture unusual regional payer behavior

## What to update after changes
- any change to audit trail structure, confidence, blocking logic, or defensibility messaging
