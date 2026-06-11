# Phase 2A Placeholder Descriptor Repair Planning Package

Generated: 2026-06-11

Mode: planning only. No descriptor remediation performed.

## Scope

Scanned:

- cpt_database.json
- codes/*.html title tags
- codes/*.html H1s
- codes/*.html meta descriptions

## Counts

| Issue category | Count |
| --- | ---: |
| CPT-code placeholder descriptors such as CPT 19318 | 72 |
| Empty descriptors | 0 |
| Truncated descriptors / suspiciously short descriptors | 85 |
| Broken title tags from placeholder descriptors | 72 |
| Broken H1s from placeholder descriptors | 72 |
| Broken meta descriptions from placeholder descriptors | 72 |

## Placeholder Descriptor Examples

| CPT | Current descriptor |
| --- | --- |
| 19318 | CPT 19318 |
| 19325 | CPT 19325 |
| 19340 | CPT 19340 |
| 19342 | CPT 19342 |
| 19350 | CPT 19350 |
| 19355 | CPT 19355 |
| 20206 | CPT 20206 |
| 22510 | CPT 22510 |
| 22513 | CPT 22513 |
| 22612 | CPT 22612 |
| 23472 | CPT 23472 |
| 23500 | CPT 23500 |
| 23605 | CPT 23605 |
| 27125 | CPT 27125 |
| 27130 | CPT 27130 |
| 27193 | CPT 27193 |
| 27217 | CPT 27217 |
| 27226 | CPT 27226 |
| 27447 | CPT 27447 |
| 27487 | CPT 27487 |

Full scan artifact:

- qa_artifacts/phase2a_placeholder_descriptor_planning_2026_06_11/phase2a_descriptor_scan.json

## Recommended Remediation Strategy

1. Source official descriptors from the same canonical CMS RVU26C source already used for RVU and indicator validation.
2. Build a descriptor-only scanner that compares cpt_database.json descriptors against CMS RVU26C descriptors and flags:
   - exact CPT-code placeholders
   - empty descriptors
   - likely truncations
   - title/H1/meta fields generated from placeholder descriptors
3. Apply descriptor replacements in a dedicated Phase 2A remediation branch.
4. Regenerate affected CPT pages only.
5. Rebuild homepage/search metadata if descriptor text is embedded in index.html SPECS.
6. Validate:
   - no RVU values changed
   - no indicator values changed
   - no modifier rules changed
   - affected pages have valid title, H1, meta description
   - homepage search returns repaired descriptors

## Risk Notes

- Placeholder descriptors propagate into title tags, H1s, meta descriptions, homepage search, and Case Builder search labels.
- Descriptor remediation should be treated as content/data repair, not CPT/RVU/payment remediation.
- No Phase 2A value, indicator, NCCI, or modifier changes should be included in the descriptor branch.
