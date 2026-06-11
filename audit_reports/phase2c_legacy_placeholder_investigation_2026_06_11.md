# Phase 2C Legacy / Placeholder Investigation Report

Generated: 2026-06-11

Mode: report only. No fixes, redirects, deletions, or deployment performed.

Canonical descriptor/RVU baseline: CMS RVU26C / PPRRVU2026_Jul_nonQPP.csv.

## Summary

Remaining placeholder pages reviewed: 13

All 13:

- Are absent from active CMS RVU26C July 2026 non-QPP rows.
- Have 0.00 work RVU, 0.00 total RVU, and $0.00 Medicare estimate in cpt_database.json.
- Overlap the prior CMS-missing/0.00 RVU findings from the Claude/data-integrity audit.
- Appear to come from legacy expansion/import scripts or older specialty page generation rather than the current CMS RVU26C import.

No remaining page has an active CMS RVU26C descriptor row that can be used for automatic descriptor repair.

## Findings By CPT

| CPT | Current page title | Current descriptor value | Active CMS RVU26C row present? | Classification | Audit overlap | Recommended action |
| --- | --- | --- | --- | --- | --- | --- |
| 27193 | CPT 27193: Closed treatment of pelvic ring fracture | CPT 27193 | No | inactive CPT / legacy orthopedic import artifact | 0.00 RVU page; missing from CMS RVU26C; legacy expand_cpt orthopedic source | Requires manual review. If not supported by current CPT/CMS source, remove from generation pipeline or retain with explicit inactive-code warning. |
| 32405 | CPT 32405: Biopsy, lung or mediastinum, percutaneous needle | CPT 32405 | No | inactive CPT / legacy thoracic import artifact | 0.00 RVU page; missing from CMS RVU26C; legacy expansion source | Requires manual review. If retired/replaced, redirect to current image-guided lung biopsy code family or remove from generated active-code set. |
| 37228 | CPT 37228: Revascularization, endovascular, open or percutaneous, tibial, peroneal artery, | CPT 37228 | No | inactive CPT / legacy vascular import artifact | 0.00 RVU page; missing from CMS RVU26C; legacy vascular source | Requires manual review against current CPT/CMS MPFS. Do not populate descriptor unless an authoritative current row/source is supplied. |
| 37230 | CPT 37230: Revascularization, endovascular, open or percutaneous, tibial, peroneal artery, | CPT 37230 | No | inactive CPT / legacy vascular import artifact | 0.00 RVU page; missing from CMS RVU26C; legacy vascular source | Requires manual review against current CPT/CMS MPFS. Do not populate descriptor unless an authoritative current row/source is supplied. |
| 47500 | CPT 47500: Injection procedure for percutaneous transhepatic cholangiography | CPT 47500 | No | inactive CPT / legacy HPB-interventional radiology import artifact | 0.00 RVU page; missing from CMS RVU26C; legacy expansion source | Requires manual review. Likely remove from active generation pipeline if no current CMS row exists. |
| 47511 | CPT 47511: Introduction of percutaneous transhepatic stent for internal and external biliar | CPT 47511 | No | inactive CPT / legacy HPB-interventional radiology import artifact | 0.00 RVU page; missing from CMS RVU26C; legacy expansion source | Requires manual review. Current page title/meta already carry a legacy descriptor, but canonical DB does not; do not repair without current authoritative source. |
| 49560 | CPT 49560: CPT 49560 | CPT 49560 | No | deleted CPT / legacy hernia code | 0.00 RVU page; missing from CMS RVU26C; known legacy ventral hernia code family superseded by 2023+ hernia codes | Remove from active generation pipeline or redirect to current ventral/incisional hernia coding guide. |
| 49561 | CPT 49561: Repair initial incisional or ventral hernia; incarcerated or strangulated | CPT 49561 | No | deleted CPT / legacy hernia code | 0.00 RVU page; missing from CMS RVU26C; known legacy ventral hernia code family superseded by 2023+ hernia codes | Remove from active generation pipeline or redirect to current ventral/incisional hernia coding guide. |
| 49565 | CPT 49565: CPT 49565 | CPT 49565 | No | deleted CPT / legacy hernia code | 0.00 RVU page; missing from CMS RVU26C; known legacy ventral hernia code family superseded by 2023+ hernia codes | Remove from active generation pipeline or redirect to current ventral/incisional hernia coding guide. |
| 49570 | CPT 49570: CPT 49570 | CPT 49570 | No | deleted CPT / legacy hernia code | 0.00 RVU page; missing from CMS RVU26C; known legacy ventral/epigastric hernia code family superseded by 2023+ hernia codes | Remove from active generation pipeline or redirect to current ventral/incisional hernia coding guide. |
| 49572 | CPT 49572: CPT 49572 | CPT 49572 | No | deleted CPT / legacy hernia code | 0.00 RVU page; missing from CMS RVU26C; known legacy ventral/epigastric hernia code family superseded by 2023+ hernia codes | Remove from active generation pipeline or redirect to current ventral/incisional hernia coding guide. |
| 49655 | CPT 49655: CPT 49655 | CPT 49655 | No | deleted CPT / legacy laparoscopic hernia code | 0.00 RVU page; missing from CMS RVU26C; listed in local deleted hernia code guardrail; NCCI audit also found deleted CMS edit retained for 49655/49320 | Remove from active generation pipeline; also clean related NCCI/bundle references in the deleted-code remediation phase. |
| 92921 | CPT 92921: Percutaneous transluminal coronary angioplasty; each additional branch of a majo | CPT 92921 | No | inactive CPT / legacy cardiology import artifact | 0.00 RVU page; missing from CMS RVU26C; legacy cardiology expansion source | Requires manual review. If inactive/deleted, remove from active generation pipeline or redirect to current PCI code family guidance. |

## Overlap Review

### Deleted-Code Findings

- Strong overlap: 49560, 49561, 49565, 49570, 49572, 49655.
- 49655 also overlaps the NCCI data-integrity audit as a deleted CMS edit retained in the site NCCI dataset: 49655/49320.
- The remaining seven non-hernia placeholders are absent from active CMS RVU26C and should be treated as inactive/manual-review until a current authoritative CPT/CMS source confirms active status.

### 0.00 RVU Pages

All 13 remaining placeholders are 0.00 RVU pages:

- work_rvu = 0
- total_rvu = 0
- estimated_medicare_payment = 0

### Legacy Imported Specialty Datasets

Evidence of legacy import/expansion origin:

- 27193: legacy orthopedic expansion scripts.
- 32405: legacy thoracic/general surgery expansion.
- 37228, 37230: legacy vascular expansion.
- 47500, 47511: legacy HPB/interventional radiology expansion.
- 49560, 49561, 49565, 49570, 49572, 49655: legacy hernia datasets predating the 2023+ hernia code migration.
- 92921: legacy cardiology expansion.

## Recommended Remediation Plan

Batch 1 - deleted hernia cleanup:

- Codes: 49560, 49561, 49565, 49570, 49572, 49655.
- Recommended action: remove from active CPT generation/search/Case Builder pipeline or redirect to the current hernia coding guide/current 2023+ hernia code families.
- Also audit related NCCI and modifier references, especially 49655/49320.
- Estimated effort: 0.5 day.

Batch 2 - inactive/non-CMS manual review:

- Codes: 27193, 32405, 37228, 37230, 47500, 47511, 92921.
- Recommended action: verify against current CPT/MPFS source outside RVU26C. If still inactive or absent from MPFS, remove from active generation pipeline or retain only with an inactive-code warning banner.
- Estimated effort: 0.5-1 day depending on source availability.

Batch 3 - generation hardening:

- Add a generator guardrail preventing CPT-code placeholders from becoming active pages unless:
  - an active CMS RVU26C row exists, or
  - the page is explicitly marked inactive/deleted with a warning banner and excluded from payable Case Builder use.
- Estimated effort: 0.5 day.

## Deployment Recommendation

Do not deploy the remaining 13 placeholders as repaired descriptor pages.

Recommended next step:

1. Open a deleted/inactive-code remediation branch.
2. Remove or redirect confirmed deleted hernia pages first.
3. Separately manual-review the seven non-hernia inactive candidates.
4. Add generator guardrails so placeholder descriptors cannot silently re-enter active CPT pages.

No fixes, redirects, page deletions, or deployments were performed in Phase 2C.
