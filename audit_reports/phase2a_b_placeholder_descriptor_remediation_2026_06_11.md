# Phase 2A-B Placeholder Descriptor Remediation Report

Generated: 2026-06-11

Mode: local audit branch only. No deployment performed.

Canonical descriptor source: CMS RVU26C / PPRRVU2026_Jul_nonQPP.csv descriptor column.

## Scope

Repaired:

- CPT-code placeholder descriptors.
- CMS-repairable suspicious/truncated descriptors.
- Associated generated CPT page title tags.
- Associated generated CPT page H1s.
- Associated generated CPT page meta descriptions.
- Homepage/search/Case Builder SPECS where repaired descriptors are embedded.

Excluded:

- Deleted-code remediation.
- SEO/content expansion.
- Hand-written descriptor replacement.
- Non-CMS descriptor inference.
- RVU/payment/indicator/modifier/NCCI changes.

## Counts

| Metric | Before | After | Repaired / reduced |
| --- | ---: | ---: | ---: |
| Placeholder descriptors | 72 | 13 | 59 |
| Truncated/suspicious descriptors | 85 | 16 | 69 |
| Broken title tags from placeholder descriptors | 72 | 13 | 59 |
| Broken H1s from placeholder descriptors | 72 | 13 | 59 |
| Broken meta descriptions from placeholder descriptors | 72 | 13 | 59 |

Repaired descriptor records from active CMS RVU26C: 69.

Remaining records require separate deleted-code/inactive-code review because no active CMS RVU26C descriptor row was found:

| CPT | Current descriptor | Reason retained |
| --- | --- | --- |
| 27193 | CPT 27193 | No active CMS RVU26C replacement descriptor found |
| 32405 | CPT 32405 | No active CMS RVU26C replacement descriptor found |
| 37228 | CPT 37228 | No active CMS RVU26C replacement descriptor found |
| 37230 | CPT 37230 | No active CMS RVU26C replacement descriptor found |
| 47500 | CPT 47500 | No active CMS RVU26C replacement descriptor found |
| 47511 | CPT 47511 | No active CMS RVU26C replacement descriptor found |
| 49560 | CPT 49560 | No active CMS RVU26C replacement descriptor found |
| 49561 | CPT 49561 | No active CMS RVU26C replacement descriptor found |
| 49565 | CPT 49565 | No active CMS RVU26C replacement descriptor found |
| 49570 | CPT 49570 | No active CMS RVU26C replacement descriptor found |
| 49572 | CPT 49572 | No active CMS RVU26C replacement descriptor found |
| 49655 | CPT 49655 | No active CMS RVU26C replacement descriptor found |
| 92921 | CPT 92921 | No active CMS RVU26C replacement descriptor found |

Additional suspicious descriptors retained because they already matched active CMS RVU26C:

| CPT | Descriptor | Reason retained |
| --- | --- | --- |
| 32482 | Bilobectomy | Current descriptor already matches CMS RVU26C |
| 65820 | Goniotomy | Current descriptor already matches CMS RVU26C |
| 80061 | Lipid panel | Current descriptor already matches CMS RVU26C |

## Required Before / After Examples

| CPT | Before | After |
| --- | --- | --- |
| 19318 | CPT 19318 | Breast reduction |
| 19325 | CPT 19325 | Breast augmentation w/implt |
| 19340 | CPT 19340 | Insj breast implt sm d mast |
| 19342 | CPT 19342 | Insj/rplcmt brst implt sep d |
| 19350 | CPT 19350 | Nipple/areola reconstruction |
| 19355 | CPT 19355 | Correct inverted nipple(s) |

## Pages Repaired

Generated CPT pages were regenerated for the 69 CMS-repaired descriptor records, including:

- codes/19318.html
- codes/19325.html
- codes/19340.html
- codes/19342.html
- codes/19350.html
- codes/19355.html
- codes/20206.html
- codes/22510.html
- codes/22513.html
- codes/22612.html
- codes/23472.html
- codes/23500.html
- codes/23605.html
- codes/27125.html
- codes/27130.html
- codes/27217.html
- codes/27226.html
- codes/27447.html
- codes/27487.html
- codes/27780.html
- codes/27810.html
- codes/32557.html
- codes/33362.html
- codes/33419.html
- codes/33968.html
- codes/33992.html
- codes/36558.html
- codes/36569.html
- codes/36584.html
- codes/36589.html
- codes/36590.html
- codes/36904.html
- codes/36906.html
- codes/37192.html
- codes/37211.html
- codes/37212.html
- codes/37236.html
- codes/37238.html
- codes/37241.html
- codes/44604.html
- codes/47544.html
- codes/49446.html
- codes/49450.html
- codes/50200.html
- codes/50435.html
- codes/50693.html
- codes/55250.html
- codes/60260.html
- codes/60270.html
- codes/70496.html
- codes/70498.html
- codes/71275.html
- codes/76942.html
- codes/77001.html
- codes/77012.html
- codes/82728.html
- codes/83550.html
- codes/84153.html
- codes/84450.html
- codes/84460.html
- codes/92924.html
- codes/92973.html
- codes/92978.html
- codes/92986.html
- codes/92987.html
- codes/93571.html
- codes/93580.html
- codes/93583.html

## Validation Results

Homepage/search/Case Builder SPECS:

- Command: python3 tools/validate_homepage_specs.py
- Result: homepage_specs_count 3,915; canonical_numeric_cpt_count 3,915; hard_error_count 0

Descriptor scan artifacts:

- qa_artifacts/phase2a_b_placeholder_descriptor_remediation_2026_06_11/descriptor_remediation_summary.json
- qa_artifacts/phase2a_b_placeholder_descriptor_remediation_2026_06_11/after_descriptor_page_scan.json

Data safety:

- No RVU source values were changed.
- No indicator values were changed.
- No modifier rules were changed.
- No NCCI data was changed.
- No deleted-code remediation was performed.

## Production Status

No deployment performed.
