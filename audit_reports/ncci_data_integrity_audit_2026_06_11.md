# NCCI Data Integrity Audit

Date: 2026-06-11
Branch: audit/ncci-data-integrity-2026-06-11
Mode: audit/report only. No production modification. No automatic repair.

## Source Baseline

CMS source used: CMS Medicare NCCI 2026 Q3 Practitioner PTP Edits v322r0, effective July 1, 2026; posted June 1, 2026.
Downloaded files: ccipra-v322r0-f1 through f4 from CMS.

## Summary

- Site NCCI bundle records: 89
- Site NCCI bundle pairs: 153
- Site common_pairs entries: 51
- CMS active Practitioner PTP rows loaded: 1728585
- CMS deleted Practitioner PTP rows loaded: 836114
- Total issues found: 291
- High risk: 123
- Medium risk: 51
- Low risk: 117

## Issue Categories

| Category | Count |
|---|---:|
| bundle pair missing from common_pairs metadata | 117 |
| reversed direction vs CMS | 53 |
| modifier indicator mismatch vs CMS | 23 |
| unknown/missing Column 2 CPT in site CPT database | 19 |
| not found in active CMS source | 18 |
| unknown/missing Column 1 CPT in site CPT database | 17 |
| common_pairs entry missing from bundles lookup | 15 |
| incomplete bundle record | 11 |
| deleted CMS edit retained in site data | 11 |
| reciprocal/reversed-direction pair | 6 |
| conflicting modifier indicators | 1 |

## Highest Risk Findings

- incomplete bundle record: 49320/44005 (49320 -> 44005; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/44120 (49320 -> 44120; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/44121 (49320 -> 44121; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/44140 (49320 -> 44140; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/44143 (49320 -> 44143; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/44144 (49320 -> 44144; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/44970 (49320 -> 44970; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/44950 (49320 -> 44950; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/47562 (49320 -> 47562; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/47563 (49320 -> 47563; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- incomplete bundle record: 49320/47564 (49320 -> 47564; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — Bundle record missing modifier indicator, reason/rationale.
- reciprocal/reversed-direction pair: 44604/49000 (44604 -> 49000; site indicator 0; CMS 44604 -> 49000, indicator 0) — Site stores both directions for unordered pair 44604|49000; opposing entry 49000 -> 44604 also exists.
- reciprocal/reversed-direction pair: 49000/44604 (49000 -> 44604; site indicator 1; CMS 44604 -> 49000, indicator 0) — Site stores both directions for unordered pair 44604|49000; opposing entry 44604 -> 49000 also exists.
- conflicting modifier indicators: 44604/49000 (44604 -> 49000; site indicator 0; CMS 44604 -> 49000, indicator 0) — Reciprocal entries for 44604|49000 have conflicting site indicators: 44604->49000=0; 49000->44604=1.
- reciprocal/reversed-direction pair: 47562/49320 (47562 -> 49320; site indicator 0; CMS 47562 -> 49320, indicator 0) — Site stores both directions for unordered pair 47562|49320; opposing entry 49320 -> 47562 also exists.
- reciprocal/reversed-direction pair: 49320/47562 (49320 -> 47562; site indicator 0; CMS 47562 -> 49320, indicator 0) — Site stores both directions for unordered pair 47562|49320; opposing entry 47562 -> 49320 also exists.
- reciprocal/reversed-direction pair: 47563/49320 (47563 -> 49320; site indicator 0; CMS 47563 -> 49320, indicator 0) — Site stores both directions for unordered pair 47563|49320; opposing entry 49320 -> 47563 also exists.
- reciprocal/reversed-direction pair: 49320/47563 (49320 -> 47563; site indicator 0; CMS 47563 -> 49320, indicator 0) — Site stores both directions for unordered pair 47563|49320; opposing entry 47563 -> 49320 also exists.
- reversed direction vs CMS: 10060/10061 (10060 -> 10061; site indicator 1; CMS 10061 -> 10060, indicator 1) — Site stores 10060->10061, but CMS active row is 10061->10060.
- reversed direction vs CMS: 11042/11043 (11042 -> 11043; site indicator 1; CMS 11043 -> 11042, indicator 1) — Site stores 11042->11043, but CMS active row is 11043->11042.
- reversed direction vs CMS: 11042/11044 (11042 -> 11044; site indicator 1; CMS 11044 -> 11042, indicator 1) — Site stores 11042->11044, but CMS active row is 11044->11042.
- reversed direction vs CMS: 11043/11044 (11043 -> 11044; site indicator 1; CMS 11044 -> 11043, indicator 1) — Site stores 11043->11044, but CMS active row is 11044->11043.
- modifier indicator mismatch vs CMS: 12001/11042 (12001 -> 11042; site indicator 0; CMS 12001 -> 11042, indicator 1) — Site indicator 0; CMS active indicator 1.
- reversed direction vs CMS: 12001/11043 (12001 -> 11043; site indicator 0; CMS 11043 -> 12001, indicator 1) — Site stores 12001->11043, but CMS active row is 11043->12001.
- reversed direction vs CMS: 12001/11044 (12001 -> 11044; site indicator 0; CMS 11044 -> 12001, indicator 1) — Site stores 12001->11044, but CMS active row is 11044->12001.
- reversed direction vs CMS: 12001/44120 (12001 -> 44120; site indicator 0; CMS 44120 -> 12001, indicator 1) — Site stores 12001->44120, but CMS active row is 44120->12001.
- reversed direction vs CMS: 12001/44140 (12001 -> 44140; site indicator 0; CMS 44140 -> 12001, indicator 1) — Site stores 12001->44140, but CMS active row is 44140->12001.
- reversed direction vs CMS: 12001/38100 (12001 -> 38100; site indicator 0; CMS 38100 -> 12001, indicator 1) — Site stores 12001->38100, but CMS active row is 38100->12001.
- modifier indicator mismatch vs CMS: 12002/11042 (12002 -> 11042; site indicator 0; CMS 12002 -> 11042, indicator 1) — Site indicator 0; CMS active indicator 1.
- reversed direction vs CMS: 12002/11043 (12002 -> 11043; site indicator 0; CMS 11043 -> 12002, indicator 1) — Site stores 12002->11043, but CMS active row is 11043->12002.
- reversed direction vs CMS: 12002/11044 (12002 -> 11044; site indicator 0; CMS 11044 -> 12002, indicator 1) — Site stores 12002->11044, but CMS active row is 11044->12002.
- reversed direction vs CMS: 12002/44120 (12002 -> 44120; site indicator 0; CMS 44120 -> 12002, indicator 1) — Site stores 12002->44120, but CMS active row is 44120->12002.
- reversed direction vs CMS: 12002/44140 (12002 -> 44140; site indicator 0; CMS 44140 -> 12002, indicator 1) — Site stores 12002->44140, but CMS active row is 44140->12002.
- reversed direction vs CMS: 12002/38100 (12002 -> 38100; site indicator 0; CMS 38100 -> 12002, indicator 1) — Site stores 12002->38100, but CMS active row is 38100->12002.
- modifier indicator mismatch vs CMS: 12031/11042 (12031 -> 11042; site indicator 0; CMS 12031 -> 11042, indicator 1) — Site indicator 0; CMS active indicator 1.
- reversed direction vs CMS: 12031/11043 (12031 -> 11043; site indicator 0; CMS 11043 -> 12031, indicator 1) — Site stores 12031->11043, but CMS active row is 11043->12031.
- reversed direction vs CMS: 12031/11044 (12031 -> 11044; site indicator 0; CMS 11044 -> 12031, indicator 1) — Site stores 12031->11044, but CMS active row is 11044->12031.
- reversed direction vs CMS: 12031/44120 (12031 -> 44120; site indicator 0; CMS 44120 -> 12031, indicator 1) — Site stores 12031->44120, but CMS active row is 44120->12031.
- reversed direction vs CMS: 12031/44140 (12031 -> 44140; site indicator 0; CMS 44140 -> 12031, indicator 1) — Site stores 12031->44140, but CMS active row is 44140->12031.
- reversed direction vs CMS: 12031/38100 (12031 -> 38100; site indicator 0; CMS 38100 -> 12031, indicator 1) — Site stores 12031->38100, but CMS active row is 38100->12031.
- modifier indicator mismatch vs CMS: 13100/11042 (13100 -> 11042; site indicator 0; CMS 13100 -> 11042, indicator 1) — Site indicator 0; CMS active indicator 1.
- modifier indicator mismatch vs CMS: 13100/11043 (13100 -> 11043; site indicator 0; CMS 13100 -> 11043, indicator 1) — Site indicator 0; CMS active indicator 1.
- modifier indicator mismatch vs CMS: 13100/11044 (13100 -> 11044; site indicator 0; CMS 13100 -> 11044, indicator 1) — Site indicator 0; CMS active indicator 1.
- reversed direction vs CMS: 13100/44120 (13100 -> 44120; site indicator 0; CMS 44120 -> 13100, indicator 1) — Site stores 13100->44120, but CMS active row is 44120->13100.
- reversed direction vs CMS: 13100/44140 (13100 -> 44140; site indicator 0; CMS 44140 -> 13100, indicator 1) — Site stores 13100->44140, but CMS active row is 44140->13100.
- reversed direction vs CMS: 13100/38100 (13100 -> 38100; site indicator 0; CMS 38100 -> 13100, indicator 1) — Site stores 13100->38100, but CMS active row is 38100->13100.
- not found in active CMS source: 19318/15734 (19318 -> 15734; site indicator 1; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — No exact or reverse active row found in CMS Q3 2026 Practitioner PTP source files.
- deleted CMS edit retained in site data: 19340/19342 (19340 -> 19342; site indicator 1; CMS 19340 -> 19342, indicator 9) — Pair exists only as deleted in CMS Q3 Practitioner source, not active.
- not found in active CMS source: 19340/19350 (19340 -> 19350; site indicator 1; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — No exact or reverse active row found in CMS Q3 2026 Practitioner PTP source files.
- not found in active CMS source: 30520/30140 (30520 -> 30140; site indicator 1; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — No exact or reverse active row found in CMS Q3 2026 Practitioner PTP source files.
- modifier indicator mismatch vs CMS: 31253/31254 (31253 -> 31254; site indicator 0; CMS 31253 -> 31254, indicator 1) — Site indicator 0; CMS active indicator 1.
- modifier indicator mismatch vs CMS: 31256/31231 (31256 -> 31231; site indicator 1; CMS 31256 -> 31231, indicator 0) — Site indicator 1; CMS active indicator 0.
- not found in active CMS source: 31256/31257 (31256 -> 31257; site indicator 1; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — No exact or reverse active row found in CMS Q3 2026 Practitioner PTP source files.
- reversed direction vs CMS: 31256/31267 (31256 -> 31267; site indicator 1; CMS 31267 -> 31256, indicator 1) — Site stores 31256->31267, but CMS active row is 31267->31256.
- reversed direction vs CMS: 31525/31535 (31525 -> 31535; site indicator 0; CMS 31535 -> 31525, indicator 1) — Site stores 31525->31535, but CMS active row is 31535->31525.
- reversed direction vs CMS: 31525/31536 (31525 -> 31536; site indicator 0; CMS 31536 -> 31525, indicator 1) — Site stores 31525->31536, but CMS active row is 31536->31525.
- reversed direction vs CMS: 31525/31541 (31525 -> 31541; site indicator 0; CMS 31541 -> 31525, indicator 1) — Site stores 31525->31541, but CMS active row is 31541->31525.
- reversed direction vs CMS: 31525/31545 (31525 -> 31545; site indicator 0; CMS 31545 -> 31525, indicator 1) — Site stores 31525->31545, but CMS active row is 31545->31525.
- modifier indicator mismatch vs CMS: 32100/32551 (32100 -> 32551; site indicator 0; CMS 32100 -> 32551, indicator 1) — Site indicator 0; CMS active indicator 1.
- not found in active CMS source: 32100/32552 (32100 -> 32552; site indicator 0; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — No exact or reverse active row found in CMS Q3 2026 Practitioner PTP source files.
- modifier indicator mismatch vs CMS: 33533/33508 (33533 -> 33508; site indicator 0; CMS 33533 -> 33508, indicator 1) — Site indicator 0; CMS active indicator 1.
- modifier indicator mismatch vs CMS: 33534/33508 (33534 -> 33508; site indicator 0; CMS 33534 -> 33508, indicator 1) — Site indicator 0; CMS active indicator 1.
- modifier indicator mismatch vs CMS: 33535/33508 (33535 -> 33508; site indicator 0; CMS 33535 -> 33508, indicator 1) — Site indicator 0; CMS active indicator 1.
- modifier indicator mismatch vs CMS: 33536/33508 (33536 -> 33508; site indicator 0; CMS 33536 -> 33508, indicator 1) — Site indicator 0; CMS active indicator 1.
- modifier indicator mismatch vs CMS: 35081/49000 (35081 -> 49000; site indicator 0; CMS 35081 -> 49000, indicator 1) — Site indicator 0; CMS active indicator 1.
- reversed direction vs CMS: 36200/36221 (36200 -> 36221; site indicator 0; CMS 36221 -> 36200, indicator 1) — Site stores 36200->36221, but CMS active row is 36221->36200.
- reversed direction vs CMS: 36200/36222 (36200 -> 36222; site indicator 0; CMS 36222 -> 36200, indicator 1) — Site stores 36200->36222, but CMS active row is 36222->36200.
- reversed direction vs CMS: 36200/36223 (36200 -> 36223; site indicator 0; CMS 36223 -> 36200, indicator 1) — Site stores 36200->36223, but CMS active row is 36223->36200.
- reversed direction vs CMS: 36200/36224 (36200 -> 36224; site indicator 0; CMS 36224 -> 36200, indicator 1) — Site stores 36200->36224, but CMS active row is 36224->36200.
- reversed direction vs CMS: 36200/36225 (36200 -> 36225; site indicator 0; CMS 36225 -> 36200, indicator 1) — Site stores 36200->36225, but CMS active row is 36225->36200.
- reversed direction vs CMS: 36200/36226 (36200 -> 36226; site indicator 0; CMS 36226 -> 36200, indicator 1) — Site stores 36200->36226, but CMS active row is 36226->36200.
- modifier indicator mismatch vs CMS: 38100/44604 (38100 -> 44604; site indicator 0; CMS 38100 -> 44604, indicator 1) — Site indicator 0; CMS active indicator 1.
- modifier indicator mismatch vs CMS: 39560/49000 (39560 -> 49000; site indicator 0; CMS 39560 -> 49000, indicator 1) — Site indicator 0; CMS active indicator 1.
- reversed direction vs CMS: 44005/44120 (44005 -> 44120; site indicator 1; CMS 44120 -> 44005, indicator 0) — Site stores 44005->44120, but CMS active row is 44120->44005.
- reversed direction vs CMS: 44005/44140 (44005 -> 44140; site indicator 1; CMS 44140 -> 44005, indicator 0) — Site stores 44005->44140, but CMS active row is 44140->44005.
- reversed direction vs CMS: 44005/38100 (44005 -> 38100; site indicator 1; CMS 38100 -> 44005, indicator 0) — Site stores 44005->38100, but CMS active row is 38100->44005.
- not found in active CMS source: 44005/47550 (44005 -> 47550; site indicator 1; CMS not found in active CMS Q3 2026 Practitioner PTP, indicator n/a) — No exact or reverse active row found in CMS Q3 2026 Practitioner PTP source files.
- deleted CMS edit retained in site data: 44120/44320 (44120 -> 44320; site indicator 1; CMS 44120 -> 44320, indicator 0) — Pair exists only as deleted in CMS Q3 Practitioner source, not active.
- modifier indicator mismatch vs CMS: 44120/49000 (44120 -> 49000; site indicator 1; CMS 44120 -> 49000, indicator 0) — Site indicator 1; CMS active indicator 0.
- deleted CMS edit retained in site data: 44140/44320 (44140 -> 44320; site indicator 1; CMS 44140 -> 44320, indicator 1) — Pair exists only as deleted in CMS Q3 Practitioner source, not active.

## Complete Issue Inventory

| Category | Pair | Current stored direction | Site indicator | CMS source direction | CMS indicator | Risk | Recommended correction |
|---|---|---|---:|---|---:|---|---|
| unknown/missing Column 1 CPT in site CPT database | 35221/49000 | 35221 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 36200/36221 | 36200 -> 36221 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 36200/36222 | 36200 -> 36222 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 36200/36223 | 36200 -> 36223 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 36200/36224 | 36200 -> 36224 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 36200/36225 | 36200 -> 36225 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 36200/36226 | 36200 -> 36226 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 44180/49320 | 44180 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 44202/49320 | 44202 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 44204/49320 | 44204 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 44205/49320 | 44205 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 44212/49320 | 44212 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 47562/49320 | 47562 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 47563/49320 | 47563 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 1 CPT in site CPT database | 49320/44005 | 49320 -> 44005 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/44005 | 49320 -> 44005 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/44120 | 49320 -> 44120 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/44120 | 49320 -> 44120 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/44121 | 49320 -> 44121 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/44121 | 49320 -> 44121 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/44140 | 49320 -> 44140 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/44140 | 49320 -> 44140 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/44143 | 49320 -> 44143 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/44143 | 49320 -> 44143 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/44144 | 49320 -> 44144 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/44144 | 49320 -> 44144 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/44970 | 49320 -> 44970 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/44970 | 49320 -> 44970 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/44950 | 49320 -> 44950 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/44950 | 49320 -> 44950 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/47562 | 49320 -> 47562 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/47562 | 49320 -> 47562 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/47563 | 49320 -> 47563 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/47563 | 49320 -> 47563 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 1 CPT in site CPT database | 49320/47564 | 49320 -> 47564 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| incomplete bundle record | 49320/47564 | 49320 -> 47564 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Add explicit CMS-derived modifier indicator, description, and rationale; do not rely on default false. |
| unknown/missing Column 2 CPT in site CPT database | 49650/49320 | 49650 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 49651/49320 | 49651 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 49652/49320 | 49652 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 49653/49320 | 49653 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 49654/49320 | 49654 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 2 CPT in site CPT database | 49655/49320 | 49655 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 1 CPT in site CPT database | 50220/49000 | 50220 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 1 CPT in site CPT database | 50230/49000 | 50230 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 1 CPT in site CPT database | 50240/49000 | 50240 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 1 CPT in site CPT database | 50520/49000 | 50520 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| unknown/missing Column 1 CPT in site CPT database | 51900/49000 | 51900 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | Verify code validity/source before retaining this bundle. |
| reciprocal/reversed-direction pair | 44604/49000 | 44604 -> 49000 | 0 | 44604 -> 49000 | 0 | high | Retain only CMS-supported direction and remove reciprocal duplicate. |
| reciprocal/reversed-direction pair | 49000/44604 | 49000 -> 44604 | 1 | 44604 -> 49000 | 0 | high | Reverse to CMS direction and remove reciprocal duplicate. |
| conflicting modifier indicators | 44604/49000 | 44604 -> 49000 | 0 | 44604 -> 49000 | 0 | high | Use the active CMS modifier indicator for the single valid CMS direction. |
| reciprocal/reversed-direction pair | 47562/49320 | 47562 -> 49320 | 0 | 47562 -> 49320 | 0 | high | Retain only CMS-supported direction and remove reciprocal duplicate. |
| reciprocal/reversed-direction pair | 49320/47562 | 49320 -> 47562 | 0 | 47562 -> 49320 | 0 | high | Reverse to CMS direction and remove reciprocal duplicate. |
| reciprocal/reversed-direction pair | 47563/49320 | 47563 -> 49320 | 0 | 47563 -> 49320 | 0 | high | Retain only CMS-supported direction and remove reciprocal duplicate. |
| reciprocal/reversed-direction pair | 49320/47563 | 49320 -> 47563 | 0 | 47563 -> 49320 | 0 | high | Reverse to CMS direction and remove reciprocal duplicate. |
| common_pairs entry missing from bundles lookup | 31535/31525 | 31535 -> 31525 | n/a | 31535 -> 31525 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 31536/31525 | 31536 -> 31525 | n/a | 31536 -> 31525 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 31541/31525 | 31541 -> 31525 | n/a | 31541 -> 31525 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 31545/31525 | 31545 -> 31525 | n/a | 31545 -> 31525 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 36221/36200 | 36221 -> 36200 | n/a | 36221 -> 36200 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 11043/11042 | 11043 -> 11042 | n/a | 11043 -> 11042 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 11044/11042 | 11044 -> 11042 | n/a | 11044 -> 11042 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 11044/11043 | 11044 -> 11043 | n/a | 11044 -> 11043 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 44120/44005 | 44120 -> 44005 | n/a | 44120 -> 44005 | 0 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 44140/44005 | 44140 -> 44005 | n/a | 44140 -> 44005 | 0 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 38100/44005 | 38100 -> 44005 | n/a | 38100 -> 44005 | 0 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 47550/44005 | 47550 -> 44005 | n/a | not found in active CMS Q3 2026 Practitioner PTP | n/a | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 60260/60240 | 60260 -> 60240 | n/a | 60260 -> 60240 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 60270/60240 | 60270 -> 60240 | n/a | 60240 -> 60270 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| common_pairs entry missing from bundles lookup | 10061/10060 | 10061 -> 10060 | n/a | 10061 -> 10060 | 1 | medium | If CMS-current, add to bundles; otherwise remove from common_pairs. |
| bundle pair missing from common_pairs metadata | 10060/10061 | 10060 -> 10061 | 1 | 10061 -> 10060 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 11042/11043 | 11042 -> 11043 | 1 | 11043 -> 11042 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 11042/11044 | 11042 -> 11044 | 1 | 11044 -> 11042 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 11043/11044 | 11043 -> 11044 | 1 | 11044 -> 11043 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12001/11042 | 12001 -> 11042 | 0 | 12001 -> 11042 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12001/11043 | 12001 -> 11043 | 0 | 11043 -> 12001 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12001/11044 | 12001 -> 11044 | 0 | 11044 -> 12001 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12001/44120 | 12001 -> 44120 | 0 | 44120 -> 12001 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12001/44140 | 12001 -> 44140 | 0 | 44140 -> 12001 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12001/38100 | 12001 -> 38100 | 0 | 38100 -> 12001 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12002/11042 | 12002 -> 11042 | 0 | 12002 -> 11042 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12002/11043 | 12002 -> 11043 | 0 | 11043 -> 12002 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12002/11044 | 12002 -> 11044 | 0 | 11044 -> 12002 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12002/44120 | 12002 -> 44120 | 0 | 44120 -> 12002 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12002/44140 | 12002 -> 44140 | 0 | 44140 -> 12002 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12002/38100 | 12002 -> 38100 | 0 | 38100 -> 12002 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12031/11042 | 12031 -> 11042 | 0 | 12031 -> 11042 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12031/11043 | 12031 -> 11043 | 0 | 11043 -> 12031 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12031/11044 | 12031 -> 11044 | 0 | 11044 -> 12031 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12031/44120 | 12031 -> 44120 | 0 | 44120 -> 12031 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12031/44140 | 12031 -> 44140 | 0 | 44140 -> 12031 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 12031/38100 | 12031 -> 38100 | 0 | 38100 -> 12031 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 13100/11042 | 13100 -> 11042 | 0 | 13100 -> 11042 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 13100/11043 | 13100 -> 11043 | 0 | 13100 -> 11043 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 13100/11044 | 13100 -> 11044 | 0 | 13100 -> 11044 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 13100/44120 | 13100 -> 44120 | 0 | 44120 -> 13100 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 13100/44140 | 13100 -> 44140 | 0 | 44140 -> 13100 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 13100/38100 | 13100 -> 38100 | 0 | 38100 -> 13100 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 31256/31257 | 31256 -> 31257 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 31256/31267 | 31256 -> 31267 | 1 | 31267 -> 31256 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 31525/31535 | 31525 -> 31535 | 0 | 31535 -> 31525 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 31525/31536 | 31525 -> 31536 | 0 | 31536 -> 31525 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 31525/31541 | 31525 -> 31541 | 0 | 31541 -> 31525 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 31525/31545 | 31525 -> 31545 | 0 | 31545 -> 31525 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 32100/32552 | 32100 -> 32552 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 35081/49000 | 35081 -> 49000 | 0 | 35081 -> 49000 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 35221/49000 | 35221 -> 49000 | 0 | 35221 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 36200/36221 | 36200 -> 36221 | 0 | 36221 -> 36200 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 36200/36222 | 36200 -> 36222 | 0 | 36222 -> 36200 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 36200/36223 | 36200 -> 36223 | 0 | 36223 -> 36200 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 36200/36224 | 36200 -> 36224 | 0 | 36224 -> 36200 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 36200/36225 | 36200 -> 36225 | 0 | 36225 -> 36200 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 36200/36226 | 36200 -> 36226 | 0 | 36226 -> 36200 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 38100/49000 | 38100 -> 49000 | 0 | 38100 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 38102/49000 | 38102 -> 49000 | 0 | 38102 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 39501/49000 | 39501 -> 49000 | 0 | 39501 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 39560/49000 | 39560 -> 49000 | 0 | 39560 -> 49000 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 42826/42830 | 42826 -> 42830 | 0 | 42826 -> 42830 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44005/44120 | 44005 -> 44120 | 1 | 44120 -> 44005 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44005/44140 | 44005 -> 44140 | 1 | 44140 -> 44005 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44005/38100 | 44005 -> 38100 | 1 | 38100 -> 44005 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44005/47550 | 44005 -> 47550 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44120/44604 | 44120 -> 44604 | 1 | 44120 -> 44604 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44120/44320 | 44120 -> 44320 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44120/49000 | 44120 -> 49000 | 1 | 44120 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44140/44320 | 44140 -> 44320 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44140/49000 | 44140 -> 49000 | 1 | 44140 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44141/49000 | 44141 -> 49000 | 0 | 44141 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44143/49000 | 44143 -> 49000 | 0 | 44143 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44144/49000 | 44144 -> 49000 | 0 | 44144 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44145/49000 | 44145 -> 49000 | 0 | 44145 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44146/49000 | 44146 -> 49000 | 0 | 44146 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44147/49000 | 44147 -> 49000 | 0 | 44147 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44150/49000 | 44150 -> 49000 | 0 | 44150 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44155/49000 | 44155 -> 49000 | 0 | 44155 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44160/49000 | 44160 -> 49000 | 0 | 44160 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44202/49320 | 44202 -> 49320 | 0 | 44202 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44204/49320 | 44204 -> 49320 | 0 | 44204 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44205/49320 | 44205 -> 49320 | 0 | 44205 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44207/44180 | 44207 -> 44180 | 0 | 44207 -> 44180 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44212/49320 | 44212 -> 49320 | 0 | 44212 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44604/49000 | 44604 -> 49000 | 0 | 44604 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44605/49000 | 44605 -> 49000 | 0 | 44605 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44970/44180 | 44970 -> 44180 | 1 | 44970 -> 44180 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 44970/44005 | 44970 -> 44005 | 1 | 44970 -> 44005 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 47350/49000 | 47350 -> 49000 | 0 | 47350 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 47360/49000 | 47360 -> 49000 | 0 | 47360 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 47550/49000 | 47550 -> 49000 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 47562/49000 | 47562 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 47563/49320 | 47563 -> 49320 | 0 | 47563 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 47563/49000 | 47563 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 47564/49000 | 47564 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 48140/49000 | 48140 -> 49000 | 0 | 48140 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 48145/49000 | 48145 -> 49000 | 0 | 48145 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 48150/49000 | 48150 -> 49000 | 0 | 48150 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 48153/49000 | 48153 -> 49000 | 0 | 48153 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49000/97606 | 49000 -> 97606 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/44005 | 49320 -> 44005 | 0 | 49320 -> 44005 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/44120 | 49320 -> 44120 | 0 | 44120 -> 49320 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/44121 | 49320 -> 44121 | 0 | 44121 -> 49320 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/44140 | 49320 -> 44140 | 0 | 44140 -> 49320 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/44143 | 49320 -> 44143 | 0 | 44143 -> 49320 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/44144 | 49320 -> 44144 | 0 | 44144 -> 49320 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/44970 | 49320 -> 44970 | 0 | 44970 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/44950 | 49320 -> 44950 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/47562 | 49320 -> 47562 | 0 | 47562 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/47563 | 49320 -> 47563 | 0 | 47563 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49320/47564 | 49320 -> 47564 | 0 | 47564 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49507/49568 | 49507 -> 49568 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49520/49568 | 49520 -> 49568 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49525/49568 | 49525 -> 49568 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49651/49320 | 49651 -> 49320 | 0 | 49651 -> 49320 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49652/49320 | 49652 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49653/49320 | 49653 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49654/49320 | 49654 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 49655/49320 | 49655 -> 49320 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 50220/49000 | 50220 -> 49000 | 0 | 50220 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 50230/49000 | 50230 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 50240/49000 | 50240 -> 49000 | 0 | 50240 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 50520/49000 | 50520 -> 49000 | 0 | 50520 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 51860/49000 | 51860 -> 49000 | 0 | 51860 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 51900/49000 | 51900 -> 49000 | 0 | 51900 -> 49000 | 0 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 60240/60260 | 60240 -> 60260 | 0 | 60260 -> 60240 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 60240/60270 | 60240 -> 60270 | 0 | 60240 -> 60270 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 92928/93458 | 92928 -> 93458 | 0 | 92928 -> 93458 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 92928/93452 | 92928 -> 93452 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| bundle pair missing from common_pairs metadata | 92928/93454 | 92928 -> 93454 | 0 | 92928 -> 93454 | 1 | low | Either add common_pairs metadata or retire common_pairs as a redundant/non-authoritative structure. |
| reversed direction vs CMS | 10060/10061 | 10060 -> 10061 | 1 | 10061 -> 10060 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 11042/11043 | 11042 -> 11043 | 1 | 11043 -> 11042 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 11042/11044 | 11042 -> 11044 | 1 | 11044 -> 11042 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 11043/11044 | 11043 -> 11044 | 1 | 11044 -> 11043 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| modifier indicator mismatch vs CMS | 12001/11042 | 12001 -> 11042 | 0 | 12001 -> 11042 | 1 | high | Update site modifier indicator to CMS value. |
| reversed direction vs CMS | 12001/11043 | 12001 -> 11043 | 0 | 11043 -> 12001 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12001/11044 | 12001 -> 11044 | 0 | 11044 -> 12001 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12001/44120 | 12001 -> 44120 | 0 | 44120 -> 12001 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12001/44140 | 12001 -> 44140 | 0 | 44140 -> 12001 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12001/38100 | 12001 -> 38100 | 0 | 38100 -> 12001 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| modifier indicator mismatch vs CMS | 12002/11042 | 12002 -> 11042 | 0 | 12002 -> 11042 | 1 | high | Update site modifier indicator to CMS value. |
| reversed direction vs CMS | 12002/11043 | 12002 -> 11043 | 0 | 11043 -> 12002 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12002/11044 | 12002 -> 11044 | 0 | 11044 -> 12002 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12002/44120 | 12002 -> 44120 | 0 | 44120 -> 12002 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12002/44140 | 12002 -> 44140 | 0 | 44140 -> 12002 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12002/38100 | 12002 -> 38100 | 0 | 38100 -> 12002 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| modifier indicator mismatch vs CMS | 12031/11042 | 12031 -> 11042 | 0 | 12031 -> 11042 | 1 | high | Update site modifier indicator to CMS value. |
| reversed direction vs CMS | 12031/11043 | 12031 -> 11043 | 0 | 11043 -> 12031 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12031/11044 | 12031 -> 11044 | 0 | 11044 -> 12031 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12031/44120 | 12031 -> 44120 | 0 | 44120 -> 12031 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12031/44140 | 12031 -> 44140 | 0 | 44140 -> 12031 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 12031/38100 | 12031 -> 38100 | 0 | 38100 -> 12031 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| modifier indicator mismatch vs CMS | 13100/11042 | 13100 -> 11042 | 0 | 13100 -> 11042 | 1 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 13100/11043 | 13100 -> 11043 | 0 | 13100 -> 11043 | 1 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 13100/11044 | 13100 -> 11044 | 0 | 13100 -> 11044 | 1 | high | Update site modifier indicator to CMS value. |
| reversed direction vs CMS | 13100/44120 | 13100 -> 44120 | 0 | 44120 -> 13100 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 13100/44140 | 13100 -> 44140 | 0 | 44140 -> 13100 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 13100/38100 | 13100 -> 38100 | 0 | 38100 -> 13100 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| not found in active CMS source | 19318/15734 | 19318 -> 15734 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| deleted CMS edit retained in site data | 19340/19342 | 19340 -> 19342 | 1 | 19340 -> 19342 | 9 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| not found in active CMS source | 19340/19350 | 19340 -> 19350 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| not found in active CMS source | 30520/30140 | 30520 -> 30140 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| modifier indicator mismatch vs CMS | 31253/31254 | 31253 -> 31254 | 0 | 31253 -> 31254 | 1 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 31256/31231 | 31256 -> 31231 | 1 | 31256 -> 31231 | 0 | high | Update site modifier indicator to CMS value. |
| not found in active CMS source | 31256/31257 | 31256 -> 31257 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| reversed direction vs CMS | 31256/31267 | 31256 -> 31267 | 1 | 31267 -> 31256 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 31525/31535 | 31525 -> 31535 | 0 | 31535 -> 31525 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 31525/31536 | 31525 -> 31536 | 0 | 31536 -> 31525 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 31525/31541 | 31525 -> 31541 | 0 | 31541 -> 31525 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 31525/31545 | 31525 -> 31545 | 0 | 31545 -> 31525 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| modifier indicator mismatch vs CMS | 32100/32551 | 32100 -> 32551 | 0 | 32100 -> 32551 | 1 | high | Update site modifier indicator to CMS value. |
| not found in active CMS source | 32100/32552 | 32100 -> 32552 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| modifier indicator mismatch vs CMS | 33533/33508 | 33533 -> 33508 | 0 | 33533 -> 33508 | 1 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 33534/33508 | 33534 -> 33508 | 0 | 33534 -> 33508 | 1 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 33535/33508 | 33535 -> 33508 | 0 | 33535 -> 33508 | 1 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 33536/33508 | 33536 -> 33508 | 0 | 33536 -> 33508 | 1 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 35081/49000 | 35081 -> 49000 | 0 | 35081 -> 49000 | 1 | high | Update site modifier indicator to CMS value. |
| reversed direction vs CMS | 36200/36221 | 36200 -> 36221 | 0 | 36221 -> 36200 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 36200/36222 | 36200 -> 36222 | 0 | 36222 -> 36200 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 36200/36223 | 36200 -> 36223 | 0 | 36223 -> 36200 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 36200/36224 | 36200 -> 36224 | 0 | 36224 -> 36200 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 36200/36225 | 36200 -> 36225 | 0 | 36225 -> 36200 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 36200/36226 | 36200 -> 36226 | 0 | 36226 -> 36200 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| modifier indicator mismatch vs CMS | 38100/44604 | 38100 -> 44604 | 0 | 38100 -> 44604 | 1 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 39560/49000 | 39560 -> 49000 | 0 | 39560 -> 49000 | 1 | high | Update site modifier indicator to CMS value. |
| reversed direction vs CMS | 44005/44120 | 44005 -> 44120 | 1 | 44120 -> 44005 | 0 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 44005/44140 | 44005 -> 44140 | 1 | 44140 -> 44005 | 0 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 44005/38100 | 44005 -> 38100 | 1 | 38100 -> 44005 | 0 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| not found in active CMS source | 44005/47550 | 44005 -> 47550 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| deleted CMS edit retained in site data | 44120/44320 | 44120 -> 44320 | 1 | 44120 -> 44320 | 0 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| modifier indicator mismatch vs CMS | 44120/49000 | 44120 -> 49000 | 1 | 44120 -> 49000 | 0 | high | Update site modifier indicator to CMS value. |
| deleted CMS edit retained in site data | 44140/44320 | 44140 -> 44320 | 1 | 44140 -> 44320 | 1 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| modifier indicator mismatch vs CMS | 44140/49000 | 44140 -> 49000 | 1 | 44140 -> 49000 | 0 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 44970/44180 | 44970 -> 44180 | 1 | 44970 -> 44180 | 0 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 44970/44005 | 44970 -> 44005 | 1 | 44970 -> 44005 | 0 | high | Update site modifier indicator to CMS value. |
| not found in active CMS source | 47550/44604 | 47550 -> 44604 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| not found in active CMS source | 47550/49000 | 47550 -> 49000 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| not found in active CMS source | 47562/49000 | 47562 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| not found in active CMS source | 47563/49000 | 47563 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| not found in active CMS source | 47564/49000 | 47564 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| reversed direction vs CMS | 49000/44604 | 49000 -> 44604 | 1 | 44604 -> 49000 | 0 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| not found in active CMS source | 49000/97606 | 49000 -> 97606 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| reversed direction vs CMS | 49320/44120 | 49320 -> 44120 | 0 | 44120 -> 49320 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 49320/44121 | 49320 -> 44121 | 0 | 44121 -> 49320 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 49320/44140 | 49320 -> 44140 | 0 | 44140 -> 49320 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 49320/44143 | 49320 -> 44143 | 0 | 44143 -> 49320 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 49320/44144 | 49320 -> 44144 | 0 | 44144 -> 49320 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 49320/44970 | 49320 -> 44970 | 0 | 44970 -> 49320 | 0 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| not found in active CMS source | 49320/44950 | 49320 -> 44950 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| reversed direction vs CMS | 49320/47562 | 49320 -> 47562 | 0 | 47562 -> 49320 | 0 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 49320/47563 | 49320 -> 47563 | 0 | 47563 -> 49320 | 0 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 49320/47564 | 49320 -> 47564 | 0 | 47564 -> 49320 | 0 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| deleted CMS edit retained in site data | 49505/49568 | 49505 -> 49568 | 0 | 49505 -> 49568 | 1 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| deleted CMS edit retained in site data | 49507/49568 | 49507 -> 49568 | 0 | 49507 -> 49568 | 1 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| deleted CMS edit retained in site data | 49520/49568 | 49520 -> 49568 | 0 | 49520 -> 49568 | 1 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| deleted CMS edit retained in site data | 49525/49568 | 49525 -> 49568 | 0 | 49525 -> 49568 | 1 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| not found in active CMS source | 49560/15734 | 49560 -> 15734 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| not found in active CMS source | 49561/15734 | 49561 -> 15734 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| deleted CMS edit retained in site data | 49652/49320 | 49652 -> 49320 | 0 | 49652 -> 49320 | 0 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| deleted CMS edit retained in site data | 49653/49320 | 49653 -> 49320 | 0 | 49653 -> 49320 | 0 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| deleted CMS edit retained in site data | 49654/49320 | 49654 -> 49320 | 0 | 49654 -> 49320 | 0 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| deleted CMS edit retained in site data | 49655/49320 | 49655 -> 49320 | 0 | 49655 -> 49320 | 0 | high | Remove or archive deleted edit unless another authoritative source supports it. |
| not found in active CMS source | 50230/49000 | 50230 -> 49000 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| not found in active CMS source | 58662/58670 | 58662 -> 58670 | 1 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| reversed direction vs CMS | 58662/58700 | 58662 -> 58700 | 1 | 58700 -> 58662 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 60240/60260 | 60240 -> 60260 | 0 | 60260 -> 60240 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| modifier indicator mismatch vs CMS | 60240/60270 | 60240 -> 60270 | 0 | 60240 -> 60270 | 1 | high | Update site modifier indicator to CMS value. |
| modifier indicator mismatch vs CMS | 92928/93458 | 92928 -> 93458 | 0 | 92928 -> 93458 | 1 | high | Update site modifier indicator to CMS value. |
| not found in active CMS source | 92928/93452 | 92928 -> 93452 | 0 | not found in active CMS Q3 2026 Practitioner PTP | n/a | high | Remove unless a different authoritative source is documented; do not use as CMS NCCI edit. |
| modifier indicator mismatch vs CMS | 92928/93454 | 92928 -> 93454 | 0 | 92928 -> 93454 | 1 | high | Update site modifier indicator to CMS value. |
| reversed direction vs CMS | 99291/36556 | 99291 -> 36556 | 0 | 36556 -> 99291 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 99291/36620 | 99291 -> 36620 | 0 | 36620 -> 99291 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 99291/31500 | 99291 -> 31500 | 0 | 31500 -> 99291 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 99291/32551 | 99291 -> 32551 | 0 | 32551 -> 99291 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |
| reversed direction vs CMS | 99291/62270 | 99291 -> 62270 | 0 | 62270 -> 99291 | 1 | high | Reverse stored direction to CMS Column 1/Column 2 and preserve CMS indicator. |

## Recommended Remediation Plan

1. Freeze new manual NCCI additions until a canonical import workflow exists.
2. Replace curated bundle data with a generated CMS Practitioner PTP import keyed by exact Column 1 / Column 2 / modifier indicator / deletion status / effective date.
3. Remove or quarantine all pairs not found in active CMS Q3 2026 Practitioner PTP unless a separate authoritative source is documented.
4. Resolve reciprocal pairs by retaining only the CMS-current direction and modifier indicator.
5. Add schema validation that fails on missing modifier indicators, missing rationale/source, self-references, duplicate exact pairs, reciprocal pairs, and common_pairs/bundles drift.
6. Treat common_pairs as deprecated unless it is regenerated from the same canonical source as bundles.
7. Re-run Case Builder no-injection tests for the corrected high-risk pairs before staging deployment.

## Production Safety

No production changes were made for this audit. This branch adds only the audit report/artifacts.
