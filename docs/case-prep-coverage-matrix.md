# Case Prep coverage matrix

Updated: 2026-10-20
Production baseline: 233 rapid-prep resources, 20 categories, plus original operative guides.

Status vocabulary:

- Coverage: Existing / Partial overlap / Genuine gap / Duplicate / Mislabel
- Evidence: Not started / Sources identified / Independently reviewed / Surgeon approved
- Content: Not started / Draft / Surgeon revision / Production-ready
- QA: Not started / Editorial / Search-schema-links / Clinical QA / Passed

| Resource | Specialty | Existing/overlap | Coverage | Priority | Rationale | Evidence | Owner | Content | QA |
|---|---|---|---|---|---|---|---|---|---|
| Robotic TAPP inguinal hernia repair | Hernia | Dedicated production resource | Existing | Complete | Distinct transabdominal posterior groin approach | Independently reviewed | Case Prep | Production | Passed |
| Robotic eTEP inguinal hernia repair | Hernia | Dedicated resource, but content is superficial and includes unsafe/overgeneralized wording | Partial overlap | P0 safety review | eTEP is a modification of TEP; it is not ventral eTEP | Sources identified | Hernia surgeon | Surgeon revision | Not started |
| Robotic eTEP ventral hernia repair | Hernia | rTAR and inguinal eTEP are not substitutes | Genuine gap | P0 required | Direct retrorectus access, crossover, midline reconstruction, and selective—not routine—TAR | Sources identified | Abdominal-wall surgeon | Evidence-supported draft held outside the static publish tree; Graydon review required | Editorial complete; surgeon review pending |
| Robotic TAR | Hernia | `robotic-ventral-hernia-repair` currently conflates umbrella robotic repair with rTAR | Mislabel | P0 safety review | TAR is a posterior component release, not every robotic ventral repair | Sources identified | Abdominal-wall surgeon | Surgeon revision | Not started |
| Open Rives-Stoppa retrorectus repair | Hernia | Ventral and TAR resources do not substitute | Genuine gap | P1 | Foundational non-TAR retrorectus reconstruction | Sources identified | Abdominal-wall surgeon | Not started | Not started |
| Open posterior component separation with TAR | Hernia | Robotic rTAR does not substitute | Genuine gap | P1 | Access, wound burden, release, and postoperative issues differ materially | Sources identified | Abdominal-wall surgeon | Not started | Not started |
| Laparoscopic TEP inguinal hernia repair | Hernia | Referenced by related links; absent | Genuine gap | P1 | Standard posterior approach with distinct access and peritoneal-tear bailouts | Sources identified | MIS/hernia surgeon | Not started | Not started |
| Open Lichtenstein inguinal hernia repair | Hernia | Shouldice is not a synonym | Genuine gap | P1 | Core anterior mesh operation and comparator to TEP/TAPP | Sources identified | Hernia surgeon | Not started | Not started |
| Adhesiolysis for adhesive SBO | Acute Care Surgery | Exploratory laparotomy only partially overlaps | Genuine gap | P1 | Common emergency operation with distinct entry, viability, enterotomy, and conversion decisions | Sources identified | ACS surgeon | Not started | Not started |
| Small-bowel resection with anastomosis | General/ACS | Ileocecectomy and colectomy are not substitutes | Genuine gap | P1 | Core small-intestine curriculum omission | Sources identified | ACS/colorectal surgeon | Not started | Not started |
| PEG tube placement | Endoscopy/Critical Care | EGD resources only partially overlap | Genuine gap | P1 | Common enteral-access procedure with distinct contraindications and complication management | Sources identified | Surgical endoscopist | Not started | Not started |
| Pediatric inguinal hernia repair/high ligation | Pediatric Surgery | Adult repairs are not substitutes | Genuine gap | P1-P2 | Different anatomy, sac handling, contralateral evaluation, and gonadal risk | Sources identified | Pediatric surgeon | Not started | Not started |
| Hemithyroidectomy + hemithyroidectomy-lobectomy | Endocrine | Near-identical resources | Duplicate | P0 cleanup | Merge while preserving aliases and stable redirects | Existing content | Endocrine reviewer | Not started | Not started |
| TAH-BSO duplicate IDs | Gynecology | Near-identical resources | Duplicate | P0 cleanup | Merge while preserving aliases | Existing content | Gynecology reviewer | Not started | Not started |
| `fissurectomy` titled Lateral Internal Sphincterotomy | Colorectal | Different operations conflated | Mislabel | P0 safety | Correct ID/title or split after specialty review | Sources needed | Colorectal surgeon | Not started | Not started |
| Open Shouldice repair | Hernia | Production description calls it tension-free | Partial/inaccurate | P0 safety | Nomenclature and principles require hernia review | Sources identified | Hernia surgeon | Surgeon revision | Not started |
| Related-procedure references | All | 519 unresolved references affecting 222/233 records | Partial integrity | P1 | Normalize aliases, add true gaps, or document unavailable targets | Audit complete | Data/editorial | Not started | Not started |

## Batch discipline

The first implementation batch ships independently verified search, readability, printing, fetch-recovery, modal-accessibility, and importer-precedence fixes. The new ventral eTEP resource remains a reviewable clinical draft until the listed surgeon decisions are resolved. Subsequent clinical additions should proceed one manageable specialty-owned batch at a time; authors may not approve their own work.
