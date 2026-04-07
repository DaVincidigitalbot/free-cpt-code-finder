# MEMORY MASTER — FreeCPTCodeFinder Recovery Memory

Last updated: 2026-04-06
Repo: /home/setup/Desktop/FreeCPTCodeFinder
Purpose: Persistent crash-safe project memory for state recovery without chat history.

## 1. Project Overview
FreeCPTCodeFinder is a live static web app for CPT lookup, ICD-10 support, surgical billing guidance, modifier logic, and case-level wRVU calculation. It has evolved from a lookup tool into a surgical billing intelligence platform with risk-aware case building and audit-defensible reasoning.

## 2. System Architecture
- Frontend: static HTML/CSS/JavaScript, no required backend
- Main shell: `index.html`
- Core data:
  - `rvu_database.json`
  - `cpt_decision_tree.json`
  - `modifier_rules.json`
  - `ncci_bundles.json`
  - `icd10_database.json`
- Engines/modules:
  - decision tree + CPT search in `index.html`
  - modifier engine in `modifier_engine.js`
  - validation engine in `index.html`
  - audit/defensibility display logic in `index.html`
  - lightweight performance profiler in `performance_profiler.js`
- Hosting: GitHub Pages, production at `https://freecptcodefinder.com`

## 3. Current Capabilities
### CPT / Search / Navigation
- decision-tree-guided CPT selection
- direct CPT search and RVU search
- structured specialty/category navigation
- inline CPT data and external JSON-backed data coexist

### Billing / Case Builder
- multi-procedure case builder
- automatic primary vs secondary ranking
- MPPR logic
- bilateral handling
- duplicate CPT detection and resolution
- modifier-aware case summary export
- copy blocking when validation errors exist

### Modifier / NCCI / Compliance
- modifier engine with payer-aware logic
- NCCI bundling detection
- conservative -59 logic, documentation-aware
- global period support (-58/-78/-79 context)
- laterality and bilateral logic
- assistant/co-surgeon role handling
- audit trail and confidence/blocking indicators

### Audit / Defensibility
- reasoning panel for modifier/ranking decisions
- case-level warnings/errors
- hernia + 15734 defensibility layer
- documentation-sensitive risk messaging

## 4. Major Work Completed
### Billing intelligence upgrade
- system upgraded into surgical billing intelligence engine
- modifier rules expanded with hierarchy, inclusion, payer, and bundling intelligence
- NCCI bundles expanded significantly
- modifier engine rewritten for hierarchy, payer, global-period, bilateral, role, and audit logic

### Billing compliance overhaul
- duplicate CPT blocking flow added
- full modifier dropdown integration
- inline NCCI warning banner in case tray
- real-time validation engine added
- copy/export blocked when errors exist

### Hernia + 15734 workflow fixes
- decision tree restored after broken refactor
- hernia repair made deterministically primary when present
- 15734 treated as adjunct reconstructive in hernia workflow, not principal procedure
- bilateral 15734 from structured decision tree normalized to one line with `-50`
- bilateral wRVU corrected to 150%
- add-on codes forced to full payment and removed from MPPR slot occupation

### Performance instrumentation
- artificial 300 ms chat delay removed
- search debounce reduced from 300 ms to 180 ms
- startup validation deferred via idle callback/fallback
- `performance_profiler.js` added for live timing capture of fetch, parse, compute, render, and workflow functions

## 5. Active Modules
- CPT engine
- modifier engine
- validation engine
- NCCI/compliance engine
- audit/defensibility engine
- search/chat UI
- performance profiler

## 6. Key Business Objectives
- make FreeCPTCodeFinder the primary monetizable medical coding property
- increase trust by behaving like expert coding logic, not prompting users to think through obvious billing decisions
- improve defensibility for higher-risk billing scenarios
- preserve production stability while shipping billing intelligence upgrades

## 7. Critical Domain Rules
- inline CPT data and `cpt_decision_tree.json` must stay synchronized
- ventral hernia uses 2023+ codes, not legacy 49560-49566
- 15734 work RVU = 20.22
- bilateral `-50` = 150% work RVU in current site logic
- add-on codes with ZZZ global = always 100%, no MPPR slot usage
- in hernia + component separation scenarios, hernia repair stays primary

## 8. Known Limitations
- static client-side architecture, no server-side persistence for user cases
- modifier engine is strong but still rule-based, not fully payer-contract specific
- 15734 defensibility is documentation-sensitive and payer-variable
- some legacy docs overstate “production-ready” status, but live behavior should always win over documentation claims
- not all performance bottlenecks are yet benchmarked from a real browser session export

## 9. Current Priorities
1. persistent memory and crash recovery documentation
2. continue hardening hernia + 15734 defensibility logic
3. use live profiler output to identify real bottlenecks
4. preserve production behavior while improving case builder speed and audit clarity

## 10. Unresolved Risks
- documentation-sensitive billing, especially 15734 with hernia repair
- payer variance for bilateral/component separation behavior
- regression risk in giant `index.html`
- sync drift between inline CPT data and external structured data
- incomplete performance evidence until a real browser session profiler export is reviewed

## 11. Living Update Rule
After every meaningful change:
- update `memory_master.md` if project state, architecture, priorities, or risks changed
- update the relevant module memory file
- update `decision_log.md` if a major product/technical decision changed
- update `system_boot.md` if recovery sequence or immediate priorities changed
- commit these updates with the code when possible

## 12. Recovery Order
1. read `system_boot.md`
2. read `memory_master.md`
3. read module memory files relevant to the current task
4. inspect live repo state and recent git commits
5. continue work without requiring chat history
