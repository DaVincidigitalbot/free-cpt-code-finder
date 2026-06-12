# GROWTH SPRINT 2 ROADMAP

Generated: 2026-06-11 EDT

Scope:
- Traffic and monetization only.
- No specialty expansion.
- No new CPT imports.
- No audit work.

## Priority 1: Top 100 CPT Enrichment

Goal:
- Turn thin, high-intent CPT pages into monetizable search landing pages.

First 25 pages:
- 99214
- 99215
- 99291
- 99292
- 49591
- 49592
- 49593
- 49594
- 49595
- 49596
- 49613
- 49614
- 49615
- 49616
- 49617
- 49618
- 64721
- 26055
- 29848
- 25607
- 25609
- 47562
- 47563
- 44140
- 49000

Page enrichment template:
- Plain-language CPT use case.
- Common ICD-10 pairings.
- Documentation checklist.
- Modifier traps.
- Related CPT comparisons.
- wRVU/payment interpretation.
- FAQ schema.
- Links to coding-center, specialty hub, and source page.

## Priority 2: 9 Orphaned Pages

Pages:
- `blog/guides/carpal-tunnel-cpt-wrvu-guide.html`
- `blog/guides/cpt-code-peg-tube-placement.html`
- `blog/guides/distal-radius-orif-cpt-wrvu-guide.html`
- `blog/guides/inpatient-vs-observation-coding.html`
- `blog/guides/learn-cpt-coding-medical-student.html`
- `blog/guides/most-common-hand-surgery-cpt-codes.html`
- `blog/guides/orthopedic-hand-surgery-cpt-codes.html`
- `blog/guides/trigger-finger-cpt-wrvu-guide.html`
- `blog/rvu/highest-rvu-hand-surgery-procedures.html`

Internal-link plan:
- Add a Hand Surgery guide cluster to `specialties/orthopedic-hand-surgery.html`.
- Add hand surgery guide cards to `blog/index.html`.
- Link carpal tunnel guide from `codes/64721.html` and `codes/29848.html`.
- Link trigger finger guide from `codes/26055.html`.
- Link distal radius ORIF guide from `codes/25607.html` and `codes/25609.html`.
- Link PEG guide from `codes/43246.html`, `codes/49440.html`, and relevant endoscopy/GI pages.
- Link inpatient vs observation and medical student guide from academy/documentation pages.

## Priority 3: ICD-10 -> CPT Clusters

First clusters:
- Appendicitis: `K35.*`, `K36`, `K37` -> 44970, 44960, 44979, 99291 when septic/critical.
- Gallbladder disease: `K80.*`, `K81.*` -> 47562, 47563, 47564, 47600, 47605, 47490.
- Hernias: `K40.*`, `K42.*`, `K43.*`, `K46.*` -> 49591-49618, 49650, 49651, 15734.
- Bowel obstruction/ischemia: `K56.*`, `K55.*` -> 44005, 44120, 44140, 44143, 44205.
- Soft tissue infection/wounds: `L02.*`, `L03.*`, `M72.6`, `T81.4*` -> 10060, 10061, 11042-11047, 97605, 97606.
- GI bleeding/endoscopy: `K92.2`, `K25-K28`, `D12.*` -> 43235, 43239, 45378, 45380, 45385.
- Hand nerve/tendon disorders: `G56.0*`, `M65.3*`, `S66.*` -> 64721, 29848, 26055, 26356, 26418.
- Distal radius/hand fractures: `S52.5*`, `S62.*` -> 25607, 25609, 26600, 26720, 26770.
- Critical care/trauma: `S36.*`, `S27.*`, `R57.*`, `J96.*` -> 99291, 99292, 49000, 32551, 31600.
- Vascular access: `Z45.2`, `T82.*`, `N18.6` -> 36556, 36561, 36590, 77001, 76942.

Execution order:
1. Fix orphan internal links.
2. Enrich the first 25 CPT pages.
3. Build ICD-10 cluster copy into the enriched CPT pages.
4. Add cluster navigation blocks to related guides/hubs.
