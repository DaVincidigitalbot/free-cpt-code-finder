# AUTHORITATIVE RE-IMPORT REPORT

Date: 2026-06-11
Branch: phase3d-b-authoritative-reimport-review-2026-06-11
Scope: investigation only; no fixes and no deployment.

## Scope

- Included only the 43 Phase 3C records classified as should be re-imported from authoritative source.
- Excluded the 28 inactive/deleted Batch 1 records, 46 specialty-review records, carrier-priced, anesthesia, bundled, and technical-only categories.

## Summary

- Records reviewed: 43
- Found in CMS RVU26C main PPRRVU file: 0
- Found in other CSV files inside the CMS RVU26C package: 0
- Can be restored automatically from current local CMS package: 0
- Requires specialty review: 43
- Should be inactive/deleted instead based on current evidence: 0
- Expected hard-error reduction if all 43 are resolved later: 43

## Counts By Authoritative Source

- no approved authoritative source found in local artifacts: 41
- specialty dataset candidate: ABOS hand source URL: 2

## Counts By Likely Source

- specialty import: 43

## Counts By Specialty

- ophthalmology: 11
- orthopedic_surgery: 7
- pulmonology: 7
- orthopedics: 5
- radiology: 5
- pain_management: 4
- radiation_oncology: 3
- ent: 1

## Recommended Disposition

- requires specialty review: 43

## Review Table

| CPT | Specialty | wRVU | total RVU | current source | authoritative source | disposition | effort |
|---|---|---:|---:|---|---|---|---|
| 20926 | orthopedic_surgery | 3.45 | 0 | abos_hand_source_url: https://ebhmc.com/cptabos/ | specialty dataset candidate: ABOS hand source URL | requires specialty review | medium - specialty source validation required |
| 22851 | orthopedic_surgery | 6.78 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 26261 | orthopedic_surgery | 12.78 | 0 | abos_hand_source_url: https://ebhmc.com/cptabos/ | specialty dataset candidate: ABOS hand source URL | requires specialty review | medium - specialty source validation required |
| 27194 | orthopedics | 6.55 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 27445 | orthopedic_surgery | 20.89 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 27468 | orthopedic_surgery | 15.67 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 28440 | orthopedics | 2.15 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 29020 | orthopedic_surgery | 5.89 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 29025 | orthopedics | 3.55 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 29582 | orthopedics | 1.05 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 29583 | orthopedics | 0.85 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 29715 | orthopedic_surgery | 1.56 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 64402 | pain_management | 1.34 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 64410 | pain_management | 1.34 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 64412 | pain_management | 1.34 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 64413 | pain_management | 1.56 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65455 | ophthalmology | 1.4 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65470 | ophthalmology | 4.2 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65471 | ophthalmology | 4.6 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65472 | ophthalmology | 3.2 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65473 | ophthalmology | 3.3 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65474 | ophthalmology | 4.8 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65480 | ophthalmology | 2.5 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65485 | ophthalmology | 5.5 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65490 | ophthalmology | 4 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65491 | ophthalmology | 6.6 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 65897 | ophthalmology | 6.3 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 69605 | ent | 14 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 72010 | radiology | 0.75 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 73500 | radiology | 0.22 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 76001 | radiology | 2.34 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 76101 | radiology | 0.78 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 76102 | radiology | 0.34 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 77385 | radiation_oncology | 0.85 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 77386 | radiation_oncology | 1.25 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 77401 | radiation_oncology | 0.2 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 94250 | pulmonology | 0.23 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 94400 | pulmonology | 0.89 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 94620 | pulmonology | 1.42 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 94662 | pulmonology | 1.34 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 94720 | pulmonology | 0.56 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 94750 | pulmonology | 0.89 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |
| 94770 | pulmonology | 0.23 | 0 | none stored | no approved authoritative source found in local artifacts | requires specialty review | medium - specialty source validation required |

Full 43-record CSV: qa_artifacts/phase3d_b_authoritative_reimport_review_2026_06_11/authoritative_reimport_43_review.csv

## Detailed Record Appendix

| CPT | Descriptor | work RVU | total RVU | payment estimate | source label | disposition |
|---|---|---:|---:|---:|---|---|
| 20926 | Tissue grafts other; fat, dermis, fascia | 3.45 | 0 | 0 | abos_hand_source_url: https://ebhmc.com/cptabos/ | requires specialty review |
| 22851 | Application of intervertebral biomechanical device to vertebral defect | 6.78 | 0 | 0.0 | none stored | requires specialty review |
| 26261 | Radical resection proximal or middle phalanx with autograft | 12.78 | 0 | 0 | abos_hand_source_url: https://ebhmc.com/cptabos/ | requires specialty review |
| 27194 | Closed tx pelvic ring fx; with manipulation | 6.55 | 0 | 0.0 | none stored | requires specialty review |
| 27445 | Arthroplasty knee hinge prosthesis | 20.89 | 0 | 0.0 | none stored | requires specialty review |
| 27468 | Lengthening of long bone tibia | 15.67 | 0 | 0.0 | none stored | requires specialty review |
| 28440 | Closed tx tarsal bone fx (excl talus/calcaneus); without manipulation | 2.15 | 0 | 0.0 | none stored | requires specialty review |
| 29020 | Application of turnbuckle jacket body cast | 5.89 | 0 | 0.0 | none stored | requires specialty review |
| 29025 | Application of body cast, shoulder to hips, Minerva type | 3.55 | 0 | 0.0 | none stored | requires specialty review |
| 29582 | Application of multi-layer compression; thigh and leg | 1.05 | 0 | 0.0 | none stored | requires specialty review |
| 29583 | Application of multi-layer compression; upper arm and forearm | 0.85 | 0 | 0.0 | none stored | requires specialty review |
| 29715 | Removal or bivalving of turnbuckle jacket body cast | 1.56 | 0 | 0.0 | none stored | requires specialty review |
| 64402 | Injection anesthetic agent facial nerve | 1.34 | 0 | 0.0 | none stored | requires specialty review |
| 64410 | Injection anesthetic agent phrenic nerve | 1.34 | 0 | 0.0 | none stored | requires specialty review |
| 64412 | Injection anesthetic agent spinal accessory nerve | 1.34 | 0 | 0.0 | none stored | requires specialty review |
| 64413 | Injection anesthetic agent cervical plexus | 1.56 | 0 | 0.0 | none stored | requires specialty review |
| 65455 | Removal of corneal epithelium; with chelation | 1.4 | 0 | 0.0 | none stored | requires specialty review |
| 65470 | Fistulectomy of cornea | 4.2 | 0 | 0.0 | none stored | requires specialty review |
| 65471 | Fistulectomy of sclera | 4.6 | 0 | 0.0 | none stored | requires specialty review |
| 65472 | Treatment of recurrent corneal erosion by laser | 3.2 | 0 | 0.0 | none stored | requires specialty review |
| 65473 | Corneal relaxing incision for refractive correction | 3.3 | 0 | 0.0 | none stored | requires specialty review |
| 65474 | Phototherapeutic keratectomy | 4.8 | 0 | 0.0 | none stored | requires specialty review |
| 65480 | Destruction of lesion of sclera | 2.5 | 0 | 0.0 | none stored | requires specialty review |
| 65485 | Translation or repositioning of corneal transplant | 5.5 | 0 | 0.0 | none stored | requires specialty review |
| 65490 | Removal of implanted material, anterior segment | 4 | 0 | 0.0 | none stored | requires specialty review |
| 65491 | Removal of implanted material, posterior segment | 6.6 | 0 | 0.0 | none stored | requires specialty review |
| 65897 | Aqueous drainage device revision without extraocular reservoir | 6.3 | 0 | 0.0 | none stored | requires specialty review |
| 69605 | Mastoidectomy, complete, modified radical | 14 | 0 | 0.0 | none stored | requires specialty review |
| 72010 | XR spine, entire survey | 0.75 | 0 | 0.0 | none stored | requires specialty review |
| 73500 | Radiologic examination hip unilateral with pelvis when performed 1 view | 0.22 | 0 | 0.0 | none stored | requires specialty review |
| 76001 | Fluoroscopy physician or other qualified health care professional time more than 1 hour | 2.34 | 0 | 0.0 | none stored | requires specialty review |
| 76101 | Radiologic examination complex motion body section other than with urography | 0.78 | 0 | 0.0 | none stored | requires specialty review |
| 76102 | Radiologic examination complex motion body section other than with urography each additional section | 0.34 | 0 | 0.0 | none stored | requires specialty review |
| 77385 | Intensity modulated radiation treatment delivery; simple | 0.85 | 0 | 0.0 | none stored | requires specialty review |
| 77386 | Intensity modulated radiation treatment delivery; complex | 1.25 | 0 | 0.0 | none stored | requires specialty review |
| 77401 | Radiation treatment delivery, superficial and/or ortho voltage | 0.2 | 0 | 0.0 | none stored | requires specialty review |
| 94250 | Expired gas collection quantitative single procedure | 0.23 | 0 | 0.0 | none stored | requires specialty review |
| 94400 | Breathing response to CO2 | 0.89 | 0 | 0.0 | none stored | requires specialty review |
| 94620 | Pulmonary stress testing (cardiopulmonary exercise) | 1.42 | 0 | 0.0 | none stored | requires specialty review |
| 94662 | Continuous negative pressure ventilation CNP initiation and management | 1.34 | 0 | 0.0 | none stored | requires specialty review |
| 94720 | Carbon monoxide diffusing capacity DLCO | 0.56 | 0 | 0.0 | none stored | requires specialty review |
| 94750 | Pulmonary compliance study lung or thorax | 0.89 | 0 | 0.0 | none stored | requires specialty review |
| 94770 | Carbon dioxide expired gas determination by infrared analyzer | 0.23 | 0 | 0.0 | none stored | requires specialty review |

## Interpretation

- None of the 43 can be safely auto-restored from CMS RVU26C because none appear in the CMS RVU26C package files available in this repository.
- Two records, 20926 and 26261, carry a specialty dataset source URL; that source is not enough by itself to restore RVU/payment values into CMS-governed billing workflows without review approval.
- The remaining 41 records have no durable source label in the active CPT record and should not be restored without a specialty or CPT-source review.

## Metadata Review After Phase 3D-A Cleanup

| CPT | active record present | inactive warning page | defect remains? | status | recommendation |
|---|---|---|---|---|---|
| 37220 | Yes | No | Yes | still active metadata defect | Regenerate page metadata from canonical descriptor after source/RVU disposition is decided. |
| 37221 | Yes | No | Yes | still active metadata defect | Regenerate page metadata from canonical descriptor after source/RVU disposition is decided. |
| 37224 | Yes | No | Yes | still active metadata defect | Regenerate page metadata from canonical descriptor after source/RVU disposition is decided. |
| 37226 | Yes | No | Yes | still active metadata defect | Regenerate page metadata from canonical descriptor after source/RVU disposition is decided. |
| 47510 | Yes | No | Yes | still active metadata defect | Regenerate page metadata from canonical descriptor after source/RVU disposition is decided. |
| 49652 | No | Yes | No | resolved by Phase 3D-A inactive page cleanup | No metadata remediation needed for active workflow; page retained as inactive warning page. |
| 49653 | No | Yes | No | resolved by Phase 3D-A inactive page cleanup | No metadata remediation needed for active workflow; page retained as inactive warning page. |
| 49654 | No | Yes | No | resolved by Phase 3D-A inactive page cleanup | No metadata remediation needed for active workflow; page retained as inactive warning page. |
| 49656 | No | Yes | No | resolved by Phase 3D-A inactive page cleanup | No metadata remediation needed for active workflow; page retained as inactive warning page. |
| 49657 | No | Yes | No | resolved by Phase 3D-A inactive page cleanup | No metadata remediation needed for active workflow; page retained as inactive warning page. |
| 92929 | Yes | No | Yes | still active metadata defect | Regenerate page metadata from canonical descriptor after source/RVU disposition is decided. |

Requested metadata set remaining defects: 6 of 11.

## Estimated Remediation Effort

- 0 low-effort automatic CMS restores.
- 43 medium-effort specialty/CPT-source reviews before any re-import or inactive/deleted decision.
- Expected hard-error reduction after final disposition of all 43: 43 fewer zero-RVU hard errors.

## Production Status

No fixes were made. No deployment was performed.
