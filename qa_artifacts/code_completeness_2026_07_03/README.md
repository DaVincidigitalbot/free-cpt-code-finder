# Code Completeness Audit - 2026-07-03

Sources:
- ICD-10-CM: CDC/NCHS April 1 2026 icd10cm-codes-April-1-2026.txt
- CPT/HCPCS benchmark: CMS RVU26C updated 06/30/2026 PPRRVU2026_Jul_nonQPP.csv

## Findings Before Any Further Production Deploy

- ICD-10 official billable codes: 74719
- Site ICD-10 billable codes: 74719
- Missing ICD-10 billable codes: 0
- S27 site rows before fix: 235 total, 162 billable
- S27.33 official billable children: 9
- S27.33 missing billable children: 0

- CMS PFS CPT/HCPCS rows: 17096
- Site CPT/HCPCS unique codes: 3890
- Missing CMS PFS CPT/HCPCS rows: 13341
- Missing numeric CPT rows: 7249
- Missing alphanumeric HCPCS rows: 6092
- CPT 32320 present in production branch: False

Detailed CSVs are in this directory.
