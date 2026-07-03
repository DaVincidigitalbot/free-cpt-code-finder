# CPT 32320 Post-Fix Data Integrity Check

Generated: 2026-07-03
Branch: review/s27-lung-laceration-completeness
Base production commit: 39e73a9579d611a6331fab87a6a5c0c7d918ee2d

## Source

- CMS PFS RVU26C July 2026 non-QPP
- Source file: PPRRVU2026_Jul_nonQPP.csv
- Source URL: https://www.cms.gov/files/zip/rvu26c-updated-06-30-2026.zip

## Result

- CPT 32320 present in cpt_database.json: yes
- CPT 32320 present in rvu_database.json: yes
- CPT 32320 present in modifier_rules.json: yes
- CPT 32320 present in cpt_decision_tree.json: yes
- CPT 32320 present in regenerated homepage SPECS / Case Builder seed: yes
- CPT 32320 standalone page generated: codes/32320.html
- Work RVU: 26.57
- Facility PE RVU: 12.72
- MP RVU: 6.60
- Total RVU: 45.89
- Global period: 090

The legacy data-integrity scanner is not used for this check because it expects the older homepage SPECS object shape. The current validation gate is scripts/build_homepage_specs.py plus tools/validate_homepage_specs.py.
