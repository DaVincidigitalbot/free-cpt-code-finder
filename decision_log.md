# DECISION LOG — FreeCPTCodeFinder

Last updated: 2026-04-06

## Decision 1: FreeCPTCodeFinder is the primary focus
- Direction: prioritize FreeCPTCodeFinder over Avenyx for near-term product work
- Why: more traffic, easier monetization, simpler delivery model
- Tradeoff: Avenyx remains important but secondary

## Decision 2: Keep architecture static/client-side for now
- Direction: continue as static HTML/JS app without backend dependency
- Why: faster deployment, GitHub Pages compatibility, lower operational risk
- Tradeoff: less persistent user-state capability, heavier frontend logic

## Decision 3: Modifier logic must be conservative
- Direction: avoid auto-applying documentation-sensitive modifiers blindly, especially -59
- Why: billing risk is worse than friction
- Tradeoff: some scenarios still require confirmation or warnings

## Decision 4: Hernia repair remains primary over 15734 in combined cases
- Direction: in hernia + component separation scenarios, hernia repair is principal and 15734 is adjunct reconstructive work
- Why: matches intended site behavior and expert-coder style workflow for this product
- Tradeoff: some alternative interpretations exist, so defensibility messaging is necessary

## Decision 5: Bilateral structured selections normalize to one line with -50
- Direction: decision-tree bilateral workflow should create one line with modifier -50, not duplicate entries
- Why: duplicate lines created billing confusion and incorrect UX
- Tradeoff: payer-specific exceptions still exist outside current site logic

## Decision 6: Add-on codes should never occupy MPPR ranking slots
- Direction: ZZZ/add-on codes always get full value and do not demote regular procedures
- Why: aligns with intended billing logic and prevents undercounting
- Tradeoff: requires explicit guardrails in ranking logic

## Decision 7: Case builder should think for the user
- Direction: remove interruptive primary-procedure confirmation in normal workflow and use deterministic ranking
- Why: Graydon explicitly wants expert-coder behavior, not user-driven ranking decisions
- Tradeoff: manual override still needed for exceptions

## Decision 8: Validation should block unsafe export
- Direction: if validation errors exist, do not allow copy/export as if case is clean
- Why: prevents avoidable downstream billing errors
- Tradeoff: may frustrate users in edge cases, but safer

## Decision 9: Defensibility is a product feature, not an afterthought
- Direction: include audit trail, warnings, confidence signals, and documentation-sensitive guidance in UI
- Why: user trust comes from explainable logic under audit scrutiny
- Tradeoff: more UI complexity and more logic maintenance

## Decision 10: Performance work must be evidence-based
- Direction: instrument real workflow timing before claiming bottlenecks
- Why: guesses waste time and create fake optimization work
- Tradeoff: requires profiler plumbing before deeper tuning

## Decision 11: Persistent recovery memory belongs in the project repo
- Direction: store crash recovery memory docs inside `/home/setup/Desktop/FreeCPTCodeFinder`
- Why: repo-local state survives resets and travels with project history
- Tradeoff: must keep docs updated or they rot
