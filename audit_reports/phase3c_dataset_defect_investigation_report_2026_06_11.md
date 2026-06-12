# DATASET DEFECT INVESTIGATION REPORT

Date: 2026-06-11
Branch: phase3c-dataset-defect-investigation-2026-06-11
Scope: investigation only; no fixes and no deployment.

## Scope Control

- Included only the 117 Phase 3B records classified as dataset defect.
- Excluded carrier-priced, anesthesia/base-unit, bundled/non-payable, technical-only, and deleted/inactive candidate buckets.

## Summary

- Dataset-defect records investigated: 117
- Active CMS RVU26C row present: 0
- Records appearing in homepage search: 117
- Records appearing in Case Builder: 117
- General Surgery / hernia records: 22
- Trauma/ACS-relevant records by local proxy: 28

## Counts By Likely Source

- specialty import: 75
- legacy import: 32
- unknown: 10

## Counts By Recommended Disposition

- requires specialty review: 46
- should be re-imported from authoritative source: 43
- should be inactive/deleted: 28

## Highest-Traffic Records If Known

No live GA4/Search Console/search-log export exists in this checkout. The priority list below is a proxy based on surgical relevance, specialty, homepage/Case Builder exposure, and current work RVU.

## Top 50 Priority Proxy Records

| CPT | Specialty | wRVU | Source | First commit | Recommendation | Descriptor |
|---|---|---:|---|---|---|---|
| 47136 | gastroenterology | 52.34 | specialty import | f472fb5c | requires specialty review | Liver allotransplantation heterotopic partial or whole from cadaver or living donor any ag |
| 57112 | obgyn | 35.4 | unknown | 99200a28 | requires specialty review | Exenteration of vagina; complete |
| 34802 | vascular | 27.54 | specialty import | 6ca3c7dc | requires specialty review | Endovascular AAA repair, aorto-bi-iliac graft |
| 34800 | vascular | 25 | specialty import | 6ca3c7dc | requires specialty review | Endovascular AAA repair, aorto-aortic tube graft |
| 47802 | gastroenterology | 24.56 | specialty import | f472fb5c | requires specialty review | U-tube hepaticoenterostomy |
| 19272 | general_surgery | 20.42 | unknown | da31a1ad | requires specialty review | Excision of chest wall tumor, including ribs, with mesh/prosthesis |
| 43324 | general_surgery | 19.06 | legacy import | 6ca3c7dc | requires specialty review | Esophagogastric fundoplasty (eg, Nissen, Belsey IV, Hill procedures) |
| 19271 | general_surgery | 18.55 | unknown | da31a1ad | requires specialty review | Excision of chest wall tumor including ribs, with reconstruction |
| 49203 | general_surgery | 16.76 | legacy import | 6ca3c7dc | requires specialty review | Excision or destruction, open, intra-abdominal tumors, cysts or endometriomas, 1 or more p |
| 32020 | general_surgery | 12.85 | legacy import | 6ca3c7dc | requires specialty review | Thoracotomy, with or without pleural biopsy |
| 49654 | general_surgery | 22.85 | legacy import | 6ca3c7dc | should be inactive/deleted | Laparoscopy, surgical; repair ventral hernia >10 cm |
| 37229 | vascular | 12.64 | specialty import | 6ca3c7dc | requires specialty review | Revascularization, tibial/peroneal, atherectomy |
| 19260 | general_surgery | 12.53 | unknown | da31a1ad | requires specialty review | Excision of chest wall tumor including ribs |
| 52647 | urology | 10.89 | specialty import | f472fb5c | requires specialty review | Laser vaporization of prostate including control of postoperative bleeding with coagulatio |
| 49653 | general_surgery | 20.28 | legacy import | 6ca3c7dc | should be inactive/deleted | Laparoscopy, surgical; repair ventral hernia 3-10 cm |
| 35450 | vascular | 9.84 | specialty import | 6ca3c7dc | requires specialty review | Transluminal balloon angioplasty, renal or visceral artery |
| 19304 | general_surgery | 8.95 | legacy import | 6ca3c7dc | requires specialty review | Mastectomy, subcutaneous |
| 15732 | plastic_surgery | 18.86 | legacy import | 6ca3c7dc | requires specialty review | Muscle/myocutaneous flap, head and neck |
| 37221 | vascular | 8.72 | specialty import | 6ca3c7dc | requires specialty review | Iliac artery stent placement |
| 37226 | vascular | 8.72 | specialty import | 6ca3c7dc | requires specialty review | Femoral/popliteal stent placement |
| 37220 | vascular | 7.16 | specialty import | 6ca3c7dc | requires specialty review | Iliac artery angioplasty |
| 37224 | vascular | 7.16 | specialty import | 6ca3c7dc | requires specialty review | Femoral/popliteal angioplasty |
| 47561 | gastroenterology | 6.78 | specialty import | f472fb5c | requires specialty review | Laparoscopy surgical with guided transhepatic cholangiography with biopsy |
| 92944 | interventional_cardiology | 6.12 | specialty import | f472fb5c | requires specialty review | Percutaneous transluminal revascularization of chronic total occlusion each additional cor |
| 49657 | general_surgery | 16 | legacy import | 6ca3c7dc | should be inactive/deleted | Laparoscopy, repair recurrent ventral hernia; 3-10 cm or larger |
| 27445 | orthopedic_surgery | 20.89 | specialty import | f472fb5c | should be re-imported from authoritative source | Arthroplasty knee hinge prosthesis |
| 47560 | gastroenterology | 5.89 | specialty import | f472fb5c | requires specialty review | Laparoscopy surgical with guided transhepatic cholangiography without biopsy |
| 92934 | interventional_cardiology | 5.89 | specialty import | f472fb5c | requires specialty review | Percutaneous transluminal coronary atherectomy with intracoronary stent each additional ve |
| 39400 | cardiothoracic_surgery | 5.85 | legacy import | 6ca3c7dc | requires specialty review | Mediastinoscopy; includes biopsy(ies), when performed |
| 47510 | general_surgery | 5.5 | legacy import | 6ca3c7dc | requires specialty review | Percutaneous biliary drainage, external |
| 92938 | vascular | 5.34 | specialty import | f472fb5c | requires specialty review | Percutaneous transluminal revascularization of or through coronary artery bypass graft eac |
| 32602 | general_surgery | 5.3 | unknown | da31a1ad | requires specialty review | Thoracoscopy, with biopsy |
| 92925 | interventional_cardiology | 5.23 | specialty import | f472fb5c | requires specialty review | Percutaneous transluminal coronary atherectomy with coronary angioplasty each additional v |
| 92929 | general_surgery | 4.63 | legacy import | 6ca3c7dc | requires specialty review | PCI with coronary stent; each additional branch (add-on) |
| 47530 | gastroenterology | 3.56 | specialty import | f472fb5c | requires specialty review | Revision and/or reinsertion of transhepatic tube |
| 92977 | interventional_cardiology | 3.12 | specialty import | f472fb5c | requires specialty review | Thrombolysis coronary by intravenous infusion |
| 55700 | urology | 2.96 | specialty import | 6ca3c7dc | requires specialty review | Prostate biopsy, any approach |
| 49656 | general_surgery | 12.5 | legacy import | 6ca3c7dc | should be inactive/deleted | Laparoscopy, repair recurrent ventral hernia; <3 cm |
| 47525 | gastroenterology | 2.34 | specialty import | f472fb5c | requires specialty review | Change of percutaneous biliary drainage catheter |
| 92975 | interventional_cardiology | 1.9 | specialty import | f472fb5c | requires specialty review | Thrombolysis coronary by intracoronary infusion |
| 64508 | vascular | 1.85 | specialty import | e19bfce9 | requires specialty review | Injection, anesthetic agent; carotid sinus (separate procedure) |
| 91122 | gastroenterology | 1.56 | specialty import | f472fb5c | requires specialty review | Anorectal manometry |
| 47505 | gastroenterology | 1.23 | specialty import | f472fb5c | requires specialty review | Injection procedure for cholangiography through an existing catheter |
| 91120 | gastroenterology | 1.23 | specialty import | f472fb5c | requires specialty review | Rectal sensation tone and compliance test |
| 27468 | orthopedic_surgery | 15.67 | specialty import | f472fb5c | should be re-imported from authoritative source | Lengthening of long bone tibia |
| 69605 | ent | 14 | specialty import | da31a1ad | should be re-imported from authoritative source | Mastoidectomy, complete, modified radical |
| 49652 | general_surgery | 8.86 | legacy import | 6ca3c7dc | should be inactive/deleted | Laparoscopy, surgical; repair initial ventral hernia |
| 93532 | diagnostic_cardiology | 8.34 | specialty import | f472fb5c | requires specialty review | Combined right heart catheterization and transseptal left heart catheterization through in |
| 93531 | diagnostic_cardiology | 7.89 | specialty import | f472fb5c | requires specialty review | Combined right heart catheterization and retrograde left heart catheterization for congeni |
| 49590 | general_surgery | 7.83 | unknown | da31a1ad | should be inactive/deleted | Spigelian hernia repair, reducible |

Full 117-record investigation is in qa_artifacts/phase3c_dataset_defect_investigation_2026_06_11/dataset_defect_117_investigation.csv.

## General Surgery Records

| CPT | wRVU | Recommendation | Descriptor |
|---|---:|---|---|
| 19260 | 12.53 | requires specialty review | Excision of chest wall tumor including ribs |
| 19271 | 18.55 | requires specialty review | Excision of chest wall tumor including ribs, with reconstruction |
| 19272 | 20.42 | requires specialty review | Excision of chest wall tumor, including ribs, with mesh/prosthesis |
| 19304 | 8.95 | requires specialty review | Mastectomy, subcutaneous |
| 32020 | 12.85 | requires specialty review | Thoracotomy, with or without pleural biopsy |
| 32602 | 5.3 | requires specialty review | Thoracoscopy, with biopsy |
| 43324 | 19.06 | requires specialty review | Esophagogastric fundoplasty (eg, Nissen, Belsey IV, Hill procedures) |
| 47510 | 5.5 | requires specialty review | Percutaneous biliary drainage, external |
| 49203 | 16.76 | requires specialty review | Excision or destruction, open, intra-abdominal tumors, cysts or endometriomas, 1 or more peritoneal, mesenteri |
| 49566 | 15.53 | should be inactive/deleted | Repair recurrent incisional or ventral hernia; incarcerated or strangulated (legacy/deleted 2023) |
| 49568 | 4.88 | should be inactive/deleted | Implantation of mesh or other prosthesis for open incisional or ventral hernia repair (add-on) |
| 49580 | 2.46 | should be inactive/deleted | Repair umbilical hernia, younger than age 5 years; reducible |
| 49582 | 5.58 | should be inactive/deleted | Umbilical hernia repair, <5 years, incarcerated |
| 49585 | 4.8 | should be inactive/deleted | Repair umbilical hernia, age 5 years or older; reducible |
| 49587 | 9.13 | should be inactive/deleted | Repair umbilical hernia, age 5 years or older; incarcerated or strangulated |
| 49590 | 7.83 | should be inactive/deleted | Spigelian hernia repair, reducible |
| 49652 | 8.86 | should be inactive/deleted | Laparoscopy, surgical; repair initial ventral hernia |
| 49653 | 20.28 | should be inactive/deleted | Laparoscopy, surgical; repair ventral hernia 3-10 cm |
| 49654 | 22.85 | should be inactive/deleted | Laparoscopy, surgical; repair ventral hernia >10 cm |
| 49656 | 12.5 | should be inactive/deleted | Laparoscopy, repair recurrent ventral hernia; <3 cm |
| 49657 | 16 | should be inactive/deleted | Laparoscopy, repair recurrent ventral hernia; 3-10 cm or larger |
| 92929 | 4.63 | requires specialty review | PCI with coronary stent; each additional branch (add-on) |

## Trauma/ACS-Relevant Records

| CPT | Specialty | wRVU | Recommendation | Descriptor |
|---|---|---:|---|---|
| 19260 | general_surgery | 12.53 | requires specialty review | Excision of chest wall tumor including ribs |
| 19271 | general_surgery | 18.55 | requires specialty review | Excision of chest wall tumor including ribs, with reconstruction |
| 19272 | general_surgery | 20.42 | requires specialty review | Excision of chest wall tumor, including ribs, with mesh/prosthesis |
| 19304 | general_surgery | 8.95 | requires specialty review | Mastectomy, subcutaneous |
| 32020 | general_surgery | 12.85 | requires specialty review | Thoracotomy, with or without pleural biopsy |
| 32602 | general_surgery | 5.3 | requires specialty review | Thoracoscopy, with biopsy |
| 39400 | cardiothoracic_surgery | 5.85 | requires specialty review | Mediastinoscopy; includes biopsy(ies), when performed |
| 43324 | general_surgery | 19.06 | requires specialty review | Esophagogastric fundoplasty (eg, Nissen, Belsey IV, Hill procedures) |
| 47510 | general_surgery | 5.5 | requires specialty review | Percutaneous biliary drainage, external |
| 47525 | gastroenterology | 2.34 | requires specialty review | Change of percutaneous biliary drainage catheter |
| 47560 | gastroenterology | 5.89 | requires specialty review | Laparoscopy surgical with guided transhepatic cholangiography without biopsy |
| 47561 | gastroenterology | 6.78 | requires specialty review | Laparoscopy surgical with guided transhepatic cholangiography with biopsy |
| 47802 | gastroenterology | 24.56 | requires specialty review | U-tube hepaticoenterostomy |
| 49203 | general_surgery | 16.76 | requires specialty review | Excision or destruction, open, intra-abdominal tumors, cysts or endometriomas, 1 or more peritoneal, mesenteri |
| 49566 | hernia_repair | 15.53 | should be inactive/deleted | Repair recurrent incisional or ventral hernia; incarcerated or strangulated (legacy/deleted 2023) |
| 49568 | hernia_repair | 4.88 | should be inactive/deleted | Implantation of mesh or other prosthesis for open incisional or ventral hernia repair (add-on) |
| 49580 | hernia_repair | 2.46 | should be inactive/deleted | Repair umbilical hernia, younger than age 5 years; reducible |
| 49582 | general_surgery | 5.58 | should be inactive/deleted | Umbilical hernia repair, <5 years, incarcerated |
| 49585 | hernia_repair | 4.8 | should be inactive/deleted | Repair umbilical hernia, age 5 years or older; reducible |
| 49587 | hernia_repair | 9.13 | should be inactive/deleted | Repair umbilical hernia, age 5 years or older; incarcerated or strangulated |
| 49590 | general_surgery | 7.83 | should be inactive/deleted | Spigelian hernia repair, reducible |
| 49652 | general_surgery | 8.86 | should be inactive/deleted | Laparoscopy, surgical; repair initial ventral hernia |
| 49653 | general_surgery | 20.28 | should be inactive/deleted | Laparoscopy, surgical; repair ventral hernia 3-10 cm |
| 49654 | general_surgery | 22.85 | should be inactive/deleted | Laparoscopy, surgical; repair ventral hernia >10 cm |
| 49656 | general_surgery | 12.5 | should be inactive/deleted | Laparoscopy, repair recurrent ventral hernia; <3 cm |
| 49657 | general_surgery | 16 | should be inactive/deleted | Laparoscopy, repair recurrent ventral hernia; 3-10 cm or larger |
| 55700 | urology | 2.96 | requires specialty review | Prostate biopsy, any approach |
| 92929 | general_surgery | 4.63 | requires specialty review | PCI with coronary stent; each additional branch (add-on) |

## Remediation Recommendations

- should be inactive/deleted: move out of active datasets/search/Case Builder/payable workflows and keep informational URL with deleted/inactive warning when useful.
- should be re-imported from authoritative source: verify against current CPT/CMS or another approved authoritative source, then regenerate canonical RVU/payment fields or reclassify.
- requires specialty review: do not guess. These are high clinical or specialty-impact rows absent from CMS RVU26C despite current work RVU values in the site.

## Metadata Mismatch Recommendations

| CPT | Metadata-only fix? | Descriptor-source issue remains? | Recommendation |
|---|---|---|---|
| 37220 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 37221 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 37224 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 37226 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 47510 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 49652 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 49653 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 49654 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 49656 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 49657 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |
| 92929 | Yes | Yes | Metadata regeneration alone fixes the page mismatch, but source/RVU disposition still remains because this code is in the dataset-defect population. |

## Deliverable Files

- audit_reports/phase3c_dataset_defect_investigation_report_2026_06_11.md
- qa_artifacts/phase3c_dataset_defect_investigation_2026_06_11/dataset_defect_117_investigation.csv
- qa_artifacts/phase3c_dataset_defect_investigation_2026_06_11/dataset_defect_top50_priority_proxy.csv
- qa_artifacts/phase3c_dataset_defect_investigation_2026_06_11/metadata_mismatch_source_review.csv
- qa_artifacts/phase3c_dataset_defect_investigation_2026_06_11/dataset_defect_investigation_summary.json

## Production Status

No fixes were made. No deployment was performed.
