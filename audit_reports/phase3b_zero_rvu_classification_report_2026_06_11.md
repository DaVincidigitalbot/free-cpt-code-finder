# ZERO-RVU CLASSIFICATION REPORT

Date: 2026-06-11
Branch: phase3b-zero-rvu-classification-2026-06-11
Scope: classification only; no fixes and no deployment.

## Source Inputs

- CMS baseline: /home/setup/.openclaw/workspace/staging/freecpt-phase1c-b-cms-reversion/qa_artifacts/phase2d_b_source_review_2026_06_11/cms/rvu26c.zip
- Flagged population: active CPT records with total_rvu = 0.00 and no inactive/deleted page classification from Phase 3A.
- Search / Case Builder source: index.html SPECS payload.
- Active CPT field in the CSV means the current site treats the code as active. CMS RVU26C presence/status is reported separately because AMA CPT status is not bundled in the local repository.

## Summary

- Total flagged records: 357
- Records appearing in homepage search: 357
- Records appearing in Case Builder: 357
- Metadata/descriptor mismatches reviewed: 11

## Counts By Category

- dataset defect: 117
- carrier-priced code: 83
- technical-only code: 58
- anesthesia/base-unit code: 47
- deleted/inactive code: 30
- bundled/non-payable code: 22
- legitimate zero-RVU code: 0
- CMS import defect: 0
- unknown: 0

## Counts By CMS Status Indicator

- ABSENT (No row in CMS RVU26C baseline): 150
- C (Carrier-priced by Medicare contractor): 83
- X (Statutory exclusion/non-MPFS payment path): 58
- J (Anesthesia service; base-unit/payment methodology, no RVU total): 44
- N (Non-covered/non-payable under MPFS): 11
- B (Bundled/non-payable under MPFS): 5
- E (Excluded from MPFS by regulation): 3
- R (Restricted coverage/special rules): 2
- I (Not valid for Medicare purposes): 1

## Classification Rules Used

- Anesthesia specialty rows or CMS status J were classified as anesthesia/base-unit codes.
- CMS status C rows were classified as carrier-priced codes.
- CMS status X rows were classified as technical-only / non-MPFS payment-path codes.
- CMS status B, N, E, R, and I rows were classified as bundled/non-payable codes.
- Codes absent from CMS RVU26C with site work RVU greater than 0 were classified as dataset defects because the site has a work RVU but no total/payment RVU path.
- Codes absent from CMS RVU26C with site work RVU equal to 0 were classified as deleted/inactive candidates.

## Remediation Recommendations By Category

- anesthesia/base-unit code: Keep active only if anesthesia base-unit workflow is intentional; classify as anesthesia/base-unit and prevent RVU/payment display as zero-dollar surgical CPT.
- carrier-priced code: Classify as carrier-priced; keep searchable only with warning that Medicare payment is contractor-priced and not estimated by RVU formula.
- deleted/inactive code: Move to inactive/deleted handling: remove from active search/Case Builder, keep URL with warning or redirect after replacement-family review.
- dataset defect: High priority: source-row mismatch or legacy specialty-import artifact. Verify current CPT/CMS status, then either restore CMS total/payment or reclassify inactive/deleted.
- bundled/non-payable code: Classify as non-payable/bundled; keep informational page if useful, exclude from payable workflows unless a supported payer-specific path exists.
- technical-only code: Classify as non-MPFS/statutory-exclusion or technical/lab-only; remove from payable surgical Case Builder unless separate fee-schedule logic exists.

## Top 50 Highest-Risk Records

| CPT | Category | Specialty | CMS status | Site wRVU | Site total RVU | Search | Case Builder | Descriptor |
|---|---|---|---|---:|---:|---|---|---|
| 47136 | dataset defect | gastroenterology | ABSENT | 52.34 | 0 | Yes | Yes | Liver allotransplantation heterotopic partial or whole from cadaver or living donor any ag |
| 57112 | dataset defect | obgyn | ABSENT | 35.4 | 0 | Yes | Yes | Exenteration of vagina; complete |
| 34802 | dataset defect | vascular | ABSENT | 27.54 | 0 | Yes | Yes | Endovascular AAA repair, aorto-bi-iliac graft |
| 34800 | dataset defect | vascular | ABSENT | 25 | 0 | Yes | Yes | Endovascular AAA repair, aorto-aortic tube graft |
| 47802 | dataset defect | gastroenterology | ABSENT | 24.56 | 0 | Yes | Yes | U-tube hepaticoenterostomy |
| 49654 | dataset defect | general_surgery | ABSENT | 22.85 | 0 | Yes | Yes | Laparoscopy, surgical; repair ventral hernia >10 cm |
| 27445 | dataset defect | orthopedic_surgery | ABSENT | 20.89 | 0 | Yes | Yes | Arthroplasty knee hinge prosthesis |
| 19272 | dataset defect | general_surgery | ABSENT | 20.42 | 0 | Yes | Yes | Excision of chest wall tumor, including ribs, with mesh/prosthesis |
| 49653 | dataset defect | general_surgery | ABSENT | 20.28 | 0 | Yes | Yes | Laparoscopy, surgical; repair ventral hernia 3-10 cm |
| 43324 | dataset defect | general_surgery | ABSENT | 19.06 | 0 | Yes | Yes | Esophagogastric fundoplasty (eg, Nissen, Belsey IV, Hill procedures) |
| 19271 | dataset defect | general_surgery | ABSENT | 18.55 | 0 | Yes | Yes | Excision of chest wall tumor including ribs, with reconstruction |
| 49203 | dataset defect | general_surgery | ABSENT | 16.76 | 0 | Yes | Yes | Excision or destruction, open, intra-abdominal tumors, cysts or endometriomas, 1 or more p |
| 49657 | dataset defect | general_surgery | ABSENT | 16 | 0 | Yes | Yes | Laparoscopy, repair recurrent ventral hernia; 3-10 cm or larger |
| 27468 | dataset defect | orthopedic_surgery | ABSENT | 15.67 | 0 | Yes | Yes | Lengthening of long bone tibia |
| 32020 | dataset defect | general_surgery | ABSENT | 12.85 | 0 | Yes | Yes | Thoracotomy, with or without pleural biopsy |
| 26261 | dataset defect | orthopedic_surgery | ABSENT | 12.78 | 0 | Yes | Yes | Radical resection proximal or middle phalanx with autograft |
| 37229 | dataset defect | vascular | ABSENT | 12.64 | 0 | Yes | Yes | Revascularization, tibial/peroneal, atherectomy |
| 19260 | dataset defect | general_surgery | ABSENT | 12.53 | 0 | Yes | Yes | Excision of chest wall tumor including ribs |
| 49656 | dataset defect | general_surgery | ABSENT | 12.5 | 0 | Yes | Yes | Laparoscopy, repair recurrent ventral hernia; <3 cm |
| 52647 | dataset defect | urology | ABSENT | 10.89 | 0 | Yes | Yes | Laser vaporization of prostate including control of postoperative bleeding with coagulatio |
| 15732 | dataset defect | plastic_surgery | ABSENT | 18.86 | 0 | Yes | Yes | Muscle/myocutaneous flap, head and neck |
| 35450 | dataset defect | vascular | ABSENT | 9.84 | 0 | Yes | Yes | Transluminal balloon angioplasty, renal or visceral artery |
| 19304 | dataset defect | general_surgery | ABSENT | 8.95 | 0 | Yes | Yes | Mastectomy, subcutaneous |
| 49652 | dataset defect | general_surgery | ABSENT | 8.86 | 0 | Yes | Yes | Laparoscopy, surgical; repair initial ventral hernia |
| 37221 | dataset defect | vascular | ABSENT | 8.72 | 0 | Yes | Yes | Iliac artery stent placement |
| 37226 | dataset defect | vascular | ABSENT | 8.72 | 0 | Yes | Yes | Femoral/popliteal stent placement |
| 49590 | dataset defect | general_surgery | ABSENT | 7.83 | 0 | Yes | Yes | Spigelian hernia repair, reducible |
| 49566 | dataset defect | hernia_repair | ABSENT | 15.53 | 0 | Yes | Yes | Repair recurrent incisional or ventral hernia; incarcerated or strangulated (legacy/delete |
| 37220 | dataset defect | vascular | ABSENT | 7.16 | 0 | Yes | Yes | Iliac artery angioplasty |
| 37224 | dataset defect | vascular | ABSENT | 7.16 | 0 | Yes | Yes | Femoral/popliteal angioplasty |
| 22851 | dataset defect | orthopedic_surgery | ABSENT | 6.78 | 0 | Yes | Yes | Application of intervertebral biomechanical device to vertebral defect |
| 47561 | dataset defect | gastroenterology | ABSENT | 6.78 | 0 | Yes | Yes | Laparoscopy surgical with guided transhepatic cholangiography with biopsy |
| 92944 | dataset defect | interventional_cardiology | ABSENT | 6.12 | 0 | Yes | Yes | Percutaneous transluminal revascularization of chronic total occlusion each additional cor |
| 69605 | dataset defect | ent | ABSENT | 14 | 0 | Yes | Yes | Mastoidectomy, complete, modified radical |
| 29020 | dataset defect | orthopedic_surgery | ABSENT | 5.89 | 0 | Yes | Yes | Application of turnbuckle jacket body cast |
| 47560 | dataset defect | gastroenterology | ABSENT | 5.89 | 0 | Yes | Yes | Laparoscopy surgical with guided transhepatic cholangiography without biopsy |
| 92934 | dataset defect | interventional_cardiology | ABSENT | 5.89 | 0 | Yes | Yes | Percutaneous transluminal coronary atherectomy with intracoronary stent each additional ve |
| 39400 | dataset defect | cardiothoracic_surgery | ABSENT | 5.85 | 0 | Yes | Yes | Mediastinoscopy; includes biopsy(ies), when performed |
| 49582 | dataset defect | general_surgery | ABSENT | 5.58 | 0 | Yes | Yes | Umbilical hernia repair, <5 years, incarcerated |
| 47510 | dataset defect | general_surgery | ABSENT | 5.5 | 0 | Yes | Yes | Percutaneous biliary drainage, external |
| 92938 | dataset defect | vascular | ABSENT | 5.34 | 0 | Yes | Yes | Percutaneous transluminal revascularization of or through coronary artery bypass graft eac |
| 32602 | dataset defect | general_surgery | ABSENT | 5.3 | 0 | Yes | Yes | Thoracoscopy, with biopsy |
| 92925 | dataset defect | interventional_cardiology | ABSENT | 5.23 | 0 | Yes | Yes | Percutaneous transluminal coronary atherectomy with coronary angioplasty each additional v |
| 92929 | dataset defect | general_surgery | ABSENT | 4.63 | 0 | Yes | Yes | PCI with coronary stent; each additional branch (add-on) |
| 47530 | dataset defect | gastroenterology | ABSENT | 3.56 | 0 | Yes | Yes | Revision and/or reinsertion of transhepatic tube |
| 20926 | dataset defect | orthopedic_surgery | ABSENT | 3.45 | 0 | Yes | Yes | Tissue grafts other; fat, dermis, fascia |
| 92977 | dataset defect | interventional_cardiology | ABSENT | 3.12 | 0 | Yes | Yes | Thrombolysis coronary by intravenous infusion |
| 55700 | dataset defect | urology | ABSENT | 2.96 | 0 | Yes | Yes | Prostate biopsy, any approach |
| 47525 | dataset defect | gastroenterology | ABSENT | 2.34 | 0 | Yes | Yes | Change of percutaneous biliary drainage catheter |
| 92975 | dataset defect | interventional_cardiology | ABSENT | 1.9 | 0 | Yes | Yes | Thrombolysis coronary by intracoronary infusion |

Full 357-record classification is in qa_artifacts/phase3b_zero_rvu_classification_2026_06_11/zero_rvu_classification.csv.

## Search And Case Builder Exposure

- All 357 flagged records appear in the current homepage search payload.
- All 357 flagged records appear in the current Case Builder payload.
- This does not mean all should be deleted; it means every zero-RVU row needs an explicit active/non-payable classification before the Phase 3A gate can pass.

## Metadata Mismatch Appendix

| CPT | Page URL | Title mismatch | H1 mismatch | Descriptor/meta mismatch | Recommended correction |
|---|---|---|---|---|---|
| 37220 | codes/37220.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 37221 | codes/37221.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 37224 | codes/37224.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 37226 | codes/37226.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 47510 | codes/47510.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 49652 | codes/49652.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 49653 | codes/49653.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 49654 | codes/49654.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 49656 | codes/49656.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 49657 | codes/49657.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |
| 92929 | codes/92929.html | Yes | Yes | Yes | Regenerate page metadata from canonical descriptor. |

Detailed metadata mismatch data is in qa_artifacts/phase3b_zero_rvu_classification_2026_06_11/metadata_mismatch_appendix.csv.

## Deployment Status

No fixes were made. No deployment was performed.
