# MODIFIER ENGINE MEMORY

Last updated: 2026-04-06

## What exists
- advanced rules-based modifier engine in `modifier_engine.js`
- supporting rule datasets in `modifier_rules.json` and `ncci_bundles.json`
- UI integration in `index.html`
- validation and audit linkage

## How it works
- global instance auto-initializes on DOM load
- loads modifier and NCCI JSON data
- `ModifierEngine.analyze(caseItems, context)` applies:
  - hierarchy checks
  - ranking
  - payer-aware logic
  - global-period logic
  - modifier -51 logic
  - bilateral logic
  - NCCI/bundle logic
  - laterality logic
  - surgeon role modifiers
  - return-to-OR logic
  - reduced/incomplete service logic
  - auto-suggestion logic
  - adjusted wRVU calculation
  - audit output/confidence/blocking output

## Dependencies
- `modifier_engine.js`
- `modifier_rules.json`
- `ncci_bundles.json`
- case builder data from `index.html`
- UI hooks in modifier panel and validation tray

## Current state
- modifier engine rewritten into surgical billing intelligence layer
- 559 CPT rules enhanced with hierarchy/payer/bundle metadata
- NCCI coverage expanded materially
- profiler instrumentation added around initialize and analyze phases
- conservative documentation-dependent behavior remains intentional

## Hernia + 15734 current logic
- in combined hernia/component separation cases, hernia repair remains principal procedure
- 15734 is treated as adjunct reconstructive work in that workflow
- bilateral 15734 from structured selection becomes one line with `-50`
- bilateral work RVU currently treated as 150% in site logic
- add-on codes always get full credit and do not consume MPPR ranking positions

## Known limitations
- payer-specific nuance is not exhaustive
- documentation-heavy modifiers still need caution
- some older docs may describe 15734 ranking differently than current live behavior, so live code and this file take precedence

## What to update after changes
- any rule change to modifier assignment, ranking, bilateral handling, global period logic, or bundle logic
- any JSON schema/data expansion
