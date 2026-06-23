# NCCI Coverage Audit - Surgical PTP Pairs

Generated: 2026-06-23T14:32:06.377Z
Source: CMS NCCI 2026 Q3 Practitioner PTP files v322r0

## Scope

- Compared current FreeCPT active ncci_bundles.json and separate_procedure_rules.json against CMS Practitioner PTP Q3 2026 v322r0.
- Limited to loaded FreeCPT CPT codes relevant to General Surgery, Acute Care Surgery, Trauma Surgery, Colorectal Surgery, Foregut Surgery, Hernia Surgery, HPB Surgery, Endocrine Surgery, and Surgical Oncology.
- Ranking heuristic: use/frequency proxy + Column 2 wRVU impact + estimated payment impact + modifier indicator severity.

## Summary

- Loaded CPT codes: 3875
- Target surgical CPT codes: 1203
- CMS relevant active PTP pairs in scope: 294769
- Active NCCI relationships in app: 145
- Active separate-procedure relationships in app: 85
- Total missing in app rule set: 294655
- Missing modifier-0 edits: 61427
- Missing modifier-1 edits: 229917
- Missing separate-procedure suppressions: 3311

## Focused Finding

- 44055 -> 49000 is present in this review branch active rule set.

Official CMS row:

44055    49000    effective 19970101    deletion *    modifier 0    CPT Separate procedure definition

## Top Missing Findings

| Rank | Category | Column 1 | Column 2 | Mod | Rationale | wRVU Impact | Revenue Impact | Score |
|---:|---|---|---|---:|---|---:|---:|---:|
| 1 | missing_modifier_0_edit | 44140 Colectomy, partial; with anastomosis | 44211 Laparoscopic colectomy, total, with IPAA | 0 | More extensive procedure | 36.15 | $1927.23 | 346.30 |
| 2 | missing_modifier_0_edit | 44140 Colectomy, partial; with anastomosis | 44212 Laparoscopy, surgical; colectomy, total, abdominal, with pro | 0 | More extensive procedure | 33.72 | $1862.10 | 341.44 |
| 3 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 44211 Laparoscopic colectomy, total, with IPAA | 0 | More extensive procedure | 36.15 | $1927.23 | 340.30 |
| 4 | missing_modifier_0_edit | 44140 Colectomy, partial; with anastomosis | 44208 Laparoscopic colectomy, partial, with IPAA | 0 | More extensive procedure | 33.14 | $1801.98 | 340.28 |
| 5 | missing_modifier_0_edit | 44140 Colectomy, partial; with anastomosis | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 6 | missing_modifier_0_edit | 44141 Colectomy, partial with skin level cecostomy or colostomy | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 7 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 8 | missing_modifier_0_edit | 44144 Colectomy, partial, with resection and colostomy | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 9 | missing_modifier_0_edit | 44145 Colectomy, partial, with creation of ileostomy | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 10 | missing_modifier_0_edit | 44146 Colectomy, partial, with coloproctostomy | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 11 | missing_modifier_0_edit | 44147 Colectomy, partial, with low colorectal anastomosis | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 12 | missing_modifier_0_edit | 44150 Colectomy, total, abdominal, without proctectomy; with ileos | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 13 | missing_modifier_0_edit | 44151 Colectomy, total, with continent ileostomy | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 14 | missing_modifier_0_edit | 44155 Colectomy, total, abdominal, with proctectomy; with ileostom | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 15 | missing_modifier_0_edit | 44156 Colectomy, total, with continent ileostomy + proctectomy | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 16 | missing_modifier_0_edit | 44157 Colectomy, total, with ileal pouch anal anastomosis | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 17 | missing_modifier_0_edit | 44158 Colectomy, total, with IPAA without proctectomy | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 18 | missing_modifier_0_edit | 44160 Colectomy, partial, with removal of terminal ileum | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 19 | missing_modifier_0_edit | 44208 Laparoscopic colectomy, partial, with IPAA | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 20 | missing_modifier_0_edit | 44210 Laparoscopy, surgical; colectomy, total, abdominal, without  | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 21 | missing_modifier_0_edit | 44211 Laparoscopic colectomy, total, with IPAA | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 22 | missing_modifier_0_edit | 44212 Laparoscopy, surgical; colectomy, total, abdominal, with pro | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | More extensive procedure | 31.12 | $1649.34 | 340.24 |
| 23 | missing_modifier_0_edit | 45395 Laparoscopy, surgical; proctectomy, complete, combined abdom | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 0 | Mutually exclusive procedures | 31.12 | $1649.34 | 340.24 |
| 24 | missing_modifier_0_edit | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 44206 Laparoscopy, surgical; colectomy, partial, with end colostom | 0 | Mutually exclusive procedures | 29.05 | $1600.57 | 336.10 |
| 25 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 44212 Laparoscopy, surgical; colectomy, total, abdominal, with pro | 0 | More extensive procedure | 33.72 | $1862.10 | 335.44 |
| 26 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 44208 Laparoscopic colectomy, partial, with IPAA | 0 | More extensive procedure | 33.14 | $1801.98 | 334.28 |
| 27 | missing_modifier_0_edit | 44140 Colectomy, partial; with anastomosis | 44210 Laparoscopy, surgical; colectomy, total, abdominal, without  | 0 | More extensive procedure | 29.34 | $1627.63 | 332.68 |
| 28 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 45395 Laparoscopy, surgical; proctectomy, complete, combined abdom | 0 | More extensive procedure | 32.18 | $1799.31 | 332.36 |
| 29 | missing_modifier_0_edit | 44140 Colectomy, partial; with anastomosis | 44206 Laparoscopy, surgical; colectomy, partial, with end colostom | 0 | More extensive procedure | 29.05 | $1600.57 | 332.10 |
| 30 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 44210 Laparoscopy, surgical; colectomy, total, abdominal, without  | 0 | More extensive procedure | 29.34 | $1627.63 | 326.68 |
| 31 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 44206 Laparoscopy, surgical; colectomy, partial, with end colostom | 0 | More extensive procedure | 29.05 | $1600.57 | 326.10 |
| 32 | missing_modifier_0_edit | 44204 Laparoscopic colectomy, partial | 44206 Laparoscopy, surgical; colectomy, partial, with end colostom | 0 | Mutually exclusive procedures | 29.05 | $1600.57 | 326.10 |
| 33 | missing_modifier_0_edit | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 44204 Laparoscopic colectomy, partial | 0 | HCPCS/CPT procedure code definition | 25.76 | $1413.19 | 320.18 |
| 34 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 44145 Colectomy, partial, with creation of ileostomy | 0 | Mutually exclusive procedures | 27.87 | $1515.40 | 319.51 |
| 35 | missing_modifier_0_edit | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 45402 Lap proctopexy w/sig resect | 0 | Misuse of Column Two code with Column One code | 25.85 | $1392.82 | 319.34 |
| 36 | missing_modifier_0_edit | 44141 Colectomy, partial with skin level cecostomy or colostomy | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | Mutually exclusive procedures | 27.10 | $1530.76 | 318.74 |
| 37 | missing_modifier_0_edit | 44144 Colectomy, partial, with resection and colostomy | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | Mutually exclusive procedures | 27.10 | $1530.76 | 318.74 |
| 38 | missing_modifier_0_edit | 44146 Colectomy, partial, with coloproctostomy | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | Mutually exclusive procedures | 27.10 | $1530.76 | 318.74 |
| 39 | missing_modifier_0_edit | 44147 Colectomy, partial, with low colorectal anastomosis | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | Mutually exclusive procedures | 27.10 | $1530.76 | 318.74 |
| 40 | missing_modifier_0_edit | 44150 Colectomy, total, abdominal, without proctectomy; with ileos | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | More extensive procedure | 27.10 | $1530.76 | 318.74 |
| 41 | missing_modifier_0_edit | 44151 Colectomy, total, with continent ileostomy | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | HCPCS/CPT procedure code definition | 27.10 | $1530.76 | 318.74 |
| 42 | missing_modifier_0_edit | 44155 Colectomy, total, abdominal, with proctectomy; with ileostom | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | HCPCS/CPT procedure code definition | 27.10 | $1530.76 | 318.74 |
| 43 | missing_modifier_0_edit | 44156 Colectomy, total, with continent ileostomy + proctectomy | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | HCPCS/CPT procedure code definition | 27.10 | $1530.76 | 318.74 |
| 44 | missing_modifier_0_edit | 44157 Colectomy, total, with ileal pouch anal anastomosis | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | More extensive procedure | 27.10 | $1530.76 | 318.74 |
| 45 | missing_modifier_0_edit | 44158 Colectomy, total, with IPAA without proctectomy | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | More extensive procedure | 27.10 | $1530.76 | 318.74 |
| 46 | missing_modifier_0_edit | 58240 Pelvic exenteration for gynecologic malignancy | 44143 Colectomy, partial; with end colostomy and closure of distal | 0 | Standards of medical/surgical practice | 27.10 | $1530.76 | 318.74 |
| 47 | missing_modifier_0_edit | 58952 Bilateral salpingo-oophorectomy with omentectomy, total abdo | 58210 Radical abdominal hysterectomy with lymph node dissection | 0 | Misuse of Column Two code with Column One code | 30.14 | $1677.73 | 318.28 |
| 48 | missing_modifier_0_edit | 44140 Colectomy, partial; with anastomosis | 44204 Laparoscopic colectomy, partial | 0 | Sequential procedure | 25.76 | $1413.19 | 316.18 |
| 49 | missing_modifier_1_edit | 44140 Colectomy, partial; with anastomosis | 45397 Laparoscopy, surgical; proctectomy, combined abdominoperinea | 1 | More extensive procedure | 35.59 | $1941.93 | 310.18 |
| 50 | missing_modifier_0_edit | 44141 Colectomy, partial with skin level cecostomy or colostomy | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 51 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 52 | missing_modifier_0_edit | 44144 Colectomy, partial, with resection and colostomy | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 53 | missing_modifier_0_edit | 44145 Colectomy, partial, with creation of ileostomy | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 54 | missing_modifier_0_edit | 44146 Colectomy, partial, with coloproctostomy | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 55 | missing_modifier_0_edit | 44147 Colectomy, partial, with low colorectal anastomosis | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 56 | missing_modifier_0_edit | 44150 Colectomy, total, abdominal, without proctectomy; with ileos | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 57 | missing_modifier_0_edit | 44151 Colectomy, total, with continent ileostomy | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 58 | missing_modifier_0_edit | 44155 Colectomy, total, abdominal, with proctectomy; with ileostom | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 59 | missing_modifier_0_edit | 44156 Colectomy, total, with continent ileostomy + proctectomy | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 60 | missing_modifier_0_edit | 44157 Colectomy, total, with ileal pouch anal anastomosis | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 61 | missing_modifier_0_edit | 44158 Colectomy, total, with IPAA without proctectomy | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 62 | missing_modifier_0_edit | 44160 Colectomy, partial, with removal of terminal ileum | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 63 | missing_modifier_0_edit | 44208 Laparoscopic colectomy, partial, with IPAA | 44204 Laparoscopic colectomy, partial | 0 | HCPCS/CPT procedure code definition | 25.76 | $1413.19 | 310.18 |
| 64 | missing_modifier_0_edit | 44210 Laparoscopy, surgical; colectomy, total, abdominal, without  | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 65 | missing_modifier_0_edit | 44211 Laparoscopic colectomy, total, with IPAA | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 66 | missing_modifier_0_edit | 44212 Laparoscopy, surgical; colectomy, total, abdominal, with pro | 44204 Laparoscopic colectomy, partial | 0 | More extensive procedure | 25.76 | $1413.19 | 310.18 |
| 67 | missing_modifier_0_edit | 58956 Bilateral salpingo-oophorectomy with total omentectomy for m | 58952 Bilateral salpingo-oophorectomy with omentectomy, total abdo | 0 | Misuse of Column Two code with Column One code | 26.61 | $1519.74 | 307.21 |
| 68 | missing_separate_procedure_suppression | 44120 Enterectomy, resection of small intestine; single resection  | 44316 Continent ileostomy | 0 | CPT Separate procedure definition | 23.00 | $1324.35 | 306.22 |
| 69 | missing_separate_procedure_suppression | 44140 Colectomy, partial; with anastomosis | 44316 Continent ileostomy | 0 | CPT Separate procedure definition | 23.00 | $1324.35 | 306.22 |
| 70 | missing_modifier_1_edit | 45397 Laparoscopy, surgical; proctectomy, combined abdominoperinea | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 1 | Mutually exclusive procedures | 31.12 | $1649.34 | 305.24 |
| 71 | missing_modifier_1_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 45397 Laparoscopy, surgical; proctectomy, combined abdominoperinea | 1 | More extensive procedure | 35.59 | $1941.93 | 304.18 |
| 72 | missing_modifier_0_edit | 44120 Enterectomy, resection of small intestine; single resection  | 44202 Laparoscopy, surgical; enterectomy, resection of small intes | 0 | Sequential procedure | 22.81 | $1288.94 | 304.07 |
| 73 | missing_modifier_0_edit | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 304.07 |
| 74 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 45550 Repair rectum/remove sigmoid | 0 | Misuse of Column Two code with Column One code | 24.18 | $1352.40 | 303.98 |
| 75 | missing_modifier_1_edit | 44140 Colectomy, partial; with anastomosis | 45395 Laparoscopy, surgical; proctectomy, complete, combined abdom | 1 | More extensive procedure | 32.18 | $1799.31 | 303.36 |
| 76 | missing_modifier_0_edit | 44150 Colectomy, total, abdominal, without proctectomy; with ileos | 44140 Colectomy, partial; with anastomosis | 0 | More extensive procedure | 22.03 | $1250.20 | 300.57 |
| 77 | missing_modifier_0_edit | 44151 Colectomy, total, with continent ileostomy | 44140 Colectomy, partial; with anastomosis | 0 | HCPCS/CPT procedure code definition | 22.03 | $1250.20 | 300.57 |
| 78 | missing_modifier_0_edit | 44155 Colectomy, total, abdominal, with proctectomy; with ileostom | 44140 Colectomy, partial; with anastomosis | 0 | HCPCS/CPT procedure code definition | 22.03 | $1250.20 | 300.57 |
| 79 | missing_modifier_0_edit | 44156 Colectomy, total, with continent ileostomy + proctectomy | 44140 Colectomy, partial; with anastomosis | 0 | HCPCS/CPT procedure code definition | 22.03 | $1250.20 | 300.57 |
| 80 | missing_modifier_0_edit | 44157 Colectomy, total, with ileal pouch anal anastomosis | 44140 Colectomy, partial; with anastomosis | 0 | More extensive procedure | 22.03 | $1250.20 | 300.57 |
| 81 | missing_modifier_0_edit | 44158 Colectomy, total, with IPAA without proctectomy | 44140 Colectomy, partial; with anastomosis | 0 | More extensive procedure | 22.03 | $1250.20 | 300.57 |
| 82 | missing_separate_procedure_suppression | 44143 Colectomy, partial; with end colostomy and closure of distal | 44316 Continent ileostomy | 0 | CPT Separate procedure definition | 23.00 | $1324.35 | 300.22 |
| 83 | missing_modifier_0_edit | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 44316 Continent ileostomy | 0 | Misuse of Column Two code with Column One code | 23.00 | $1324.35 | 300.22 |
| 84 | missing_modifier_0_edit | 44140 Colectomy, partial; with anastomosis | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 300.07 |
| 85 | missing_separate_procedure_suppression | 44120 Enterectomy, resection of small intestine; single resection  | 44130 Bowel to bowel fusion | 0 | CPT Separate procedure definition | 21.56 | $1230.82 | 298.66 |
| 86 | missing_modifier_1_edit | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 44227 Laparoscopy, surgical, closure of enterostomy, large or smal | 1 | Mutually exclusive procedures | 27.90 | $1519.41 | 294.77 |
| 87 | missing_modifier_1_edit | 44055 Correction of malrotation by lysis of duodenal bands and/or  | 44603 Suture small intestine | 1 | Standards of medical/surgical practice | 27.46 | $1484.34 | 294.14 |
| 88 | missing_modifier_0_edit | 44141 Colectomy, partial with skin level cecostomy or colostomy | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 294.07 |
| 89 | missing_modifier_0_edit | 44143 Colectomy, partial; with end colostomy and closure of distal | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 294.07 |
| 90 | missing_modifier_0_edit | 44144 Colectomy, partial, with resection and colostomy | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 294.07 |
| 91 | missing_modifier_0_edit | 44145 Colectomy, partial, with creation of ileostomy | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 294.07 |
| 92 | missing_modifier_0_edit | 44146 Colectomy, partial, with coloproctostomy | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 294.07 |
| 93 | missing_modifier_0_edit | 44147 Colectomy, partial, with low colorectal anastomosis | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 294.07 |
| 94 | missing_modifier_0_edit | 44150 Colectomy, total, abdominal, without proctectomy; with ileos | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | More extensive procedure | 22.38 | $1226.15 | 294.07 |
| 95 | missing_modifier_0_edit | 44151 Colectomy, total, with continent ileostomy | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | More extensive procedure | 22.38 | $1226.15 | 294.07 |
| 96 | missing_modifier_0_edit | 44155 Colectomy, total, abdominal, with proctectomy; with ileostom | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | More extensive procedure | 22.38 | $1226.15 | 294.07 |
| 97 | missing_modifier_0_edit | 44156 Colectomy, total, with continent ileostomy + proctectomy | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | More extensive procedure | 22.38 | $1226.15 | 294.07 |
| 98 | missing_modifier_0_edit | 44157 Colectomy, total, with ileal pouch anal anastomosis | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | More extensive procedure | 22.38 | $1226.15 | 294.07 |
| 99 | missing_modifier_0_edit | 44158 Colectomy, total, with IPAA without proctectomy | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | More extensive procedure | 22.38 | $1226.15 | 294.07 |
| 100 | missing_modifier_0_edit | 44160 Colectomy, partial, with removal of terminal ileum | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Sequential procedure | 22.38 | $1226.15 | 294.07 |
| 101 | missing_modifier_0_edit | 44204 Laparoscopic colectomy, partial | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Mutually exclusive procedures | 22.38 | $1226.15 | 294.07 |
| 102 | missing_modifier_0_edit | 44206 Laparoscopy, surgical; colectomy, partial, with end colostom | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 294.07 |
| 103 | missing_modifier_0_edit | 44208 Laparoscopic colectomy, partial, with IPAA | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | Misuse of Column Two code with Column One code | 22.38 | $1226.15 | 294.07 |
| 104 | missing_modifier_0_edit | 44210 Laparoscopy, surgical; colectomy, total, abdominal, without  | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | More extensive procedure | 22.38 | $1226.15 | 294.07 |
| 105 | missing_modifier_0_edit | 44211 Laparoscopic colectomy, total, with IPAA | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | More extensive procedure | 22.38 | $1226.15 | 294.07 |
| 106 | missing_modifier_0_edit | 44212 Laparoscopy, surgical; colectomy, total, abdominal, with pro | 44205 Laparoscopy, surgical; colectomy, partial, with anastomosis | 0 | More extensive procedure | 22.38 | $1226.15 | 294.07 |
| 107 | missing_separate_procedure_suppression | 43633 Gastrectomy, partial, distal; with Roux-en-Y reconstruction | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 108 | missing_separate_procedure_suppression | 43644 Laparoscopy, surgical, gastric restrictive procedure; Roux-e | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 109 | missing_separate_procedure_suppression | 43800 Pyloroplasty | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 110 | missing_separate_procedure_suppression | 43820 Gastrojejunostomy without vagotomy | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 111 | missing_separate_procedure_suppression | 43825 Gastrojejunostomy with vagotomy | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 112 | missing_separate_procedure_suppression | 43843 Gastric restrictive procedure other than vertical-banded gas | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 113 | missing_separate_procedure_suppression | 43845 Gastroplasty with duodenal switch | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 114 | missing_separate_procedure_suppression | 43846 Gastric restrictive procedure with short-limb Roux-en-Y gast | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 115 | missing_separate_procedure_suppression | 43847 Gastric restrictive procedure with small intestine reconstru | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 116 | missing_separate_procedure_suppression | 43860 Revision of gastrojejunal anastomosis without vagotomy | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 117 | missing_separate_procedure_suppression | 43865 Revision of gastrojejunal anastomosis with vagotomy | 43848 Revision, open, of gastric restrictive procedure | 0 | CPT Separate procedure definition | 31.93 | $1791.96 | 293.86 |
| 118 | missing_modifier_1_edit | 44207 Laparoscopic colectomy, partial, with colorectal anastomosis | 44603 Suture small intestine | 1 | Standards of medical/surgical practice | 27.46 | $1484.34 | 292.14 |
| 119 | missing_modifier_0_edit | 43845 Gastroplasty with duodenal switch | 44120 Enterectomy, resection of small intestine; single resection  | 0 | Standards of medical/surgical practice | 20.30 | $1136.30 | 291.41 |
| 120 | missing_modifier_0_edit | 44126 Enterectomy w/o taper cong | 44120 Enterectomy, resection of small intestine; single resection  | 0 | Mutually exclusive procedures | 20.30 | $1136.30 | 291.41 |
| 121 | missing_modifier_0_edit | 44127 Enterectomy w/taper cong | 44120 Enterectomy, resection of small intestine; single resection  | 0 | Mutually exclusive procedures | 20.30 | $1136.30 | 291.41 |
| 122 | missing_modifier_0_edit | 49591 Repair initial incisional/ventral hernia, reducible; <3 cm | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | CPT Manual or CMS manual coding instruction | 22.10 | $1131.62 | 290.78 |
| 123 | missing_modifier_0_edit | 49592 Repair initial incisional/ventral hernia, incarcerated/stran | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | CPT Manual or CMS manual coding instruction | 22.10 | $1131.62 | 290.78 |
| 124 | missing_modifier_0_edit | 49593 Repair initial incisional/ventral hernia, reducible; 3-10 cm | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | Mutually exclusive procedures | 22.10 | $1131.62 | 290.78 |
| 125 | missing_modifier_0_edit | 49594 Repair initial incisional/ventral hernia, incarcerated/stran | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | Mutually exclusive procedures | 22.10 | $1131.62 | 290.78 |
| 126 | missing_modifier_0_edit | 49595 Repair initial incisional/ventral hernia, reducible; >10 cm | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | Mutually exclusive procedures | 22.10 | $1131.62 | 290.78 |
| 127 | missing_modifier_1_edit | 47562 Laparoscopy, surgical; cholecystectomy | 44603 Suture small intestine | 1 | Standards of medical/surgical practice | 27.46 | $1484.34 | 290.14 |
| 128 | missing_modifier_1_edit | 47563 Laparoscopy, surgical; cholecystectomy with cholangiography | 44603 Suture small intestine | 1 | Standards of medical/surgical practice | 27.46 | $1484.34 | 290.14 |
| 129 | missing_modifier_1_edit | 44120 Enterectomy, resection of small intestine; single resection  | 44603 Suture small intestine | 1 | Standards of medical/surgical practice | 27.46 | $1484.34 | 288.14 |
| 130 | missing_modifier_1_edit | 44140 Colectomy, partial; with anastomosis | 44603 Suture small intestine | 1 | Standards of medical/surgical practice | 27.46 | $1484.34 | 288.14 |
| 131 | missing_modifier_0_edit | 44120 Enterectomy, resection of small intestine; single resection  | 44125 Removal of small intestine | 0 | Mutually exclusive procedures | 19.53 | $1097.55 | 287.94 |
| 132 | missing_separate_procedure_suppression | 44140 Colectomy, partial; with anastomosis | 44346 Revision of colostomy; with repair of paracolostomy hernia | 0 | CPT Separate procedure definition | 19.14 | $1100.23 | 287.29 |
| 133 | missing_separate_procedure_suppression | 44055 Correction of malrotation by lysis of duodenal bands and/or  | 44005 Enterolysis (freeing of intestinal adhesion) | 0 | CPT Separate procedure definition | 18.00 | $1020.40 | 287.02 |
| 134 | missing_modifier_0_edit | 49613 Repair recurrent incisional/ventral hernia, reducible; <3 cm | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | Mutually exclusive procedures | 22.10 | $1131.62 | 286.78 |
| 135 | missing_modifier_0_edit | 49614 Repair recurrent incisional/ventral hernia, incarcerated/str | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | Mutually exclusive procedures | 22.10 | $1131.62 | 286.78 |
| 136 | missing_modifier_0_edit | 49615 Repair recurrent incisional/ventral hernia, reducible; 3-10  | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | Mutually exclusive procedures | 22.10 | $1131.62 | 286.78 |
| 137 | missing_modifier_0_edit | 49616 Repair recurrent incisional/ventral hernia, incarcerated/str | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | Mutually exclusive procedures | 22.10 | $1131.62 | 286.78 |
| 138 | missing_modifier_0_edit | 49617 Repair recurrent incisional/ventral hernia, reducible; >10 c | 49618 Repair recurrent incisional/ventral hernia, incarcerated/str | 0 | Mutually exclusive procedures | 22.10 | $1131.62 | 286.78 |
| 139 | missing_modifier_1_edit | 44140 Colectomy, partial; with anastomosis | 44626 Closure of enterostomy, large or small intestine; with resec | 1 | Standards of medical/surgical practice | 27.20 | $1456.28 | 286.21 |
| 140 | missing_modifier_0_edit | 58952 Bilateral salpingo-oophorectomy with omentectomy, total abdo | 58200 Total abdominal hysterectomy with radical dissection | 0 | Misuse of Column Two code with Column One code | 22.52 | $1256.54 | 285.87 |
| 141 | missing_modifier_1_edit | 44120 Enterectomy, resection of small intestine; single resection  | 49020 Drainage abdom abscess open | 1 | Standards of medical/surgical practice | 26.00 | $1488.01 | 285.40 |
| 142 | missing_modifier_1_edit | 44140 Colectomy, partial; with anastomosis | 49020 Drainage abdom abscess open | 1 | Misuse of Column Two code with Column One code | 26.00 | $1488.01 | 285.40 |
| 143 | missing_separate_procedure_suppression | 34820 Open iliac artery exposure for EVAR | 44005 Enterolysis (freeing of intestinal adhesion) | 0 | CPT Separate procedure definition | 18.00 | $1020.40 | 285.02 |
| 144 | missing_modifier_0_edit | 35081 Direct repair of aneurysm, abdominal aorta | 44005 Enterolysis (freeing of intestinal adhesion) | 0 | Standards of medical/surgical practice | 18.00 | $1020.40 | 285.02 |
| 145 | missing_separate_procedure_suppression | 35082 Direct repair, ruptured abdominal aortic aneurysm | 44005 Enterolysis (freeing of intestinal adhesion) | 0 | CPT Separate procedure definition | 18.00 | $1020.40 | 285.02 |
| 146 | missing_separate_procedure_suppression | 35102 Direct repair, aneurysm, abdominal aorta, iliac | 44005 Enterolysis (freeing of intestinal adhesion) | 0 | CPT Separate procedure definition | 18.00 | $1020.40 | 285.02 |
| 147 | missing_separate_procedure_suppression | 38100 Splenectomy; total (separate procedure) | 44005 Enterolysis (freeing of intestinal adhesion) | 0 | CPT Separate procedure definition | 18.00 | $1020.40 | 285.02 |
| 148 | missing_separate_procedure_suppression | 38101 Splenectomy; partial (separate procedure) | 44005 Enterolysis (freeing of intestinal adhesion) | 0 | CPT Separate procedure definition | 18.00 | $1020.40 | 285.02 |
| 149 | missing_separate_procedure_suppression | 38115 Splenectomy, with repair of ruptured spleen | 44005 Enterolysis (freeing of intestinal adhesion) | 0 | CPT Separate procedure definition | 18.00 | $1020.40 | 285.02 |
| 150 | missing_separate_procedure_suppression | 39501 Repair, laceration of diaphragm, any approach | 44005 Enterolysis (freeing of intestinal adhesion) | 0 | CPT Separate procedure definition | 18.00 | $1020.40 | 285.02 |

## Interpretation

- The focused 44055 -> 49000 patch is appropriate and low-risk because it matches CMS modifier indicator 0 and the same class as existing 44005 -> 49000 and 44207 -> 44180 hard stops.
- The broader missing list should be reviewed in batches. Modifier-1 edits require documentation-dependent warning behavior, not automatic suppression.
- This audit is intentionally evidence for review, not an automatic bulk import plan.