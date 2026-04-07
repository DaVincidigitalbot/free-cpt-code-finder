# CPT ENGINE MEMORY

Last updated: 2026-04-06

## What exists
- decision tree workflow embedded in `index.html`
- CPT search for categories, branch endpoints, and code descriptions
- RVU search against `RVU_DATA.codes`
- inline and external CPT data dependencies
- case-builder add flow from search and decision tree

## How it works
- `index.html` is the main orchestrator
- decision tree guides specialty → branch → CPT endpoint selection
- `addAndContinue()` supports structured guided selections
- `addToRVUCalculator()` routes selections into case builder logic
- CPT search scans category names, branches, options, and ICD data context
- RVU search scans `RVU_DATA.codes`

## Dependencies
- `index.html`
- `cpt_decision_tree.json`
- inline `CPT_DATA`
- `rvu_database.json`
- related case-builder functions in `index.html`

## Current state
- decision tree was previously broken by a v2 refactor, then restored from `index-legacy.html`
- structured hernia workflow is live again
- bilateral structured selections now pass explicit flags into case builder
- search debounce has been reduced from 300 ms to 180 ms
- profiler instrumentation added around search/render paths

## Key rules
- inline CPT_DATA and `cpt_decision_tree.json` must stay in sync
- structured selection should avoid raw duplicate CPT creation unless truly unexpected
- guided workflow should feel deterministic and expert-led

## Known limitations
- `index.html` is monolithic and easy to break
- search is still broad/iterative, not fully indexed
- large inline logic increases maintenance risk

## What to update after changes
- if decision-tree flow changes, update this file
- if search behavior, CPT source structure, or add flow changes, update this file
