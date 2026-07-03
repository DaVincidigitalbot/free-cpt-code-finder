# Chest Wall Reconstruction Production Readiness Report

## CPT Completeness
- 21811: cpt=True rvu=True modifiers=True search/casebuilder=True page=True wRVU=10.52 totalRVU=16.31 global=0
- 21812: cpt=True rvu=True modifiers=True search/casebuilder=True page=True wRVU=12.68 totalRVU=19.62 global=0
- 21813: cpt=True rvu=True modifiers=True search/casebuilder=True page=True wRVU=17.17 totalRVU=26.69 global=0
- 32110: cpt=True rvu=True modifiers=True search/casebuilder=True page=True wRVU=24.65 totalRVU=41.79 global=90
- 32320: cpt=True rvu=True modifiers=True search/casebuilder=True page=True wRVU=26.57 totalRVU=45.89 global=90
- 32551: cpt=True rvu=True modifiers=True search/casebuilder=True page=True wRVU=2.96 totalRVU=4.28 global=0
- 32651: cpt=True rvu=True modifiers=True search/casebuilder=True page=True wRVU=18.31 totalRVU=31.13 global=90
- 64421: cpt=True rvu=True modifiers=True search/casebuilder=True page=True wRVU=0.49 totalRVU=1.05 global=0
- 64620: cpt=True rvu=True modifiers=True search/casebuilder=True page=True wRVU=2.82 totalRVU=6.76 global=10

## Missing CPTs Identified
- 21813 lacked full RVU database, modifier rules, standalone code page, code index entry, and sitemap entry.

## CPTs Added Or Corrected
- 21813 full CMS RVU/indicator metadata and standalone code page
- stale cpt_decision_tree wRVU/global values corrected for 21811, 21812, 32110, 32551, 32651
- platform integrity gate repair: 44213 RVU/modifier metadata and 44139/44213 CMS indicators added from CMS RVU26C

## ICD-10 Audit
- Missing billable chest-trauma ICD-10 diagnoses identified: 0
- Search terms added: pulmonary contusion, lung contusion, hemothorax, pneumothorax, hemopneumothorax, pleural injury, respiratory failure

## ClaimIQ Coverage
- selected vs expected payable RVU summary
- 21813 vs 21811/21812 mutually exclusive warning
- 21812 parent/base warning
- adjunct thoracic procedure documentation warning
- intercostal block/cryoablation documentation warning
- NCCI pair evidence when detected
- existing inpatient-only, MPPR, diagnosis pointer, APP mode and modifier checks

## Validation Screenshots
- validation/chest_wall_2026_07_03/local_chest_wall_pathway.png
- validation/chest_wall_2026_07_03/local_chest_wall_claimiq.png
- validation/chest_wall_2026_07_03/local_chest_wall_7plus_appmode.png

## Local Gates
- json_validation: passed
- homepage_specs_validation: passed
- platform_integrity: 0 hard errors, 0 warnings
- source_internal_link_audit: 0 missing internal links, 0 missing source links; pre-existing non-root source-link warning remains for app-productivity.html -> /app-resources.html
