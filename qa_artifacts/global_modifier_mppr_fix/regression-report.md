# Global Modifier MPPR Fix Regression Report

Branch: `review/global-modifier-mppr-fix`  
Production deployed: No

## Issue

Modifier 58 is a postoperative/global-period modifier. It should remain visible on the applicable CPT lines, but it must not exempt same-session procedures from MPPR, modifier 51 logic, NCCI exclusion logic, add-on logic, APP mode, or Modifier 22 review behavior.

## Fix

- Added a dedicated same-session MPPR factor after modifiers are applied: `sameSessionMpprFactorForLine(line, payableProcIndex)`.
- Case Builder now stores `payableWrvu` separately from selected/effective wRVU.
- Modifier 58/78/79 display remains attached to each applicable line, but MPPR payable wRVU and payment are calculated independently.
- Secondary procedure display now shows selected wRVU plus MPPR-adjusted payable wRVU.

## Exact wRVU Math Table

### Case A: 44625-58, 49402-58, 13160-58

| CPT | Displayed modifiers | Rank | Selected wRVU | MPPR factor | Payable wRVU | Estimated payment |
|---|---:|---|---:|---:|---:|---:|
| 44625 | -58 | Primary | 16.85 | 100% | 16.85 | $933.56 |
| 49402 | -58 | Secondary #1 | 13.74 | 50% | 6.87 | $399.81 |
| 13160 | -58 | Secondary #2 | 11.74 | 50% | 5.87 | $370.42 |
| **Total** |  |  | **42.33 selected** |  | **29.59 payable** | **$1,703.78** |

### Case B: same CPTs without Modifier 58

| CPT | Displayed modifiers | Rank | Selected wRVU | MPPR factor | Payable wRVU | Estimated payment |
|---|---:|---|---:|---:|---:|---:|
| 44625 | none | Primary | 16.85 | 100% | 16.85 | $933.56 |
| 49402 | none | Secondary #1 | 13.74 | 50% | 6.87 | $399.81 |
| 13160 | none | Secondary #2 | 11.74 | 50% | 5.87 | $370.42 |
| **Total** |  |  | **42.33 selected** |  | **29.59 payable** | **$1,703.78** |

Result: Case A and Case B match exactly. Modifier 58 does not change same-session MPPR math.

### Case C: 44625-58-22, 49402-58, 11043-58, 11046-58

| CPT | Displayed modifiers | Rank | Selected wRVU | MPPR factor | Payable wRVU | Estimated payment |
|---|---:|---|---:|---:|---:|---:|
| 44625 | -58-22 | Primary | 16.85 | 100% | 16.85 | $933.56 |
| 49402 | -58 | Secondary #1 | 13.74 | 50% | 6.87 | $399.81 |
| 11043 | -58 | Secondary #2 | 2.63 | 50% | 1.315 | $119.74 |
| 11046 | -58 | Add-on | 1.00 | 100% | 1.00 | $76.49 |
| **Total** |  |  | **34.22 selected** |  | **26.04 payable** | **$1,529.60** |

Result: Modifier 22 remains a review marker only. It does not automatically increase payment. Add-on code 11046 keeps normal add-on full-payment logic.

### Case D: NCCI/separate-procedure bundled line with Modifier 58

| CPT | Displayed modifiers | Rank | Selected wRVU | MPPR factor | Payable wRVU | Estimated payment |
|---|---:|---|---:|---:|---:|---:|
| 44005 | -58 | Primary | 18.00 | 100% | 18.00 | $1,020.40 |
| 49000 | none, bundled | Bundled | 12.23 | 0% | 0.00 | $0.00 |
| **Total** |  |  | **30.23 selected** |  | **18.00 payable** | **$1,020.40** |

Result: Modifier 58 does not override NCCI/separate-procedure exclusion logic.

## Browser Evidence

Artifacts: `qa_artifacts/global_modifier_mppr_fix/`

- Before screenshots: `*_before.png`
- After screenshots: `*_after.png`
- Browser validation video: `browser_validation_video.mp4`
- Targeted MPPR browser test JSON: `mppr_math_results.json`

## Validation

| Check | Result |
|---|---|
| Inline executable JavaScript syntax | Pass |
| `python3 test_global_modifier_mppr.py` | Pass |
| `node test_global_modifier_engine.js` | Pass |
| `node validate_global_modifier_cases.js` | Pass |
| `node validation_evidence.js` | Pass |
| `node final_hardening_validation.js` | Pass |
| `node kill_test_suite.js` | 50/54 pass; same 4 failures reproduced on origin/main before this fix |
| `node tools/audit_sources_page.js .` | Same pre-existing non-root source-link warning reproduced on origin/main |

## Regression Notes

- Modifier 58, 78, and 79 remain display/review modifiers for global-period context.
- Modifier 58 no longer has any path that bypasses same-session MPPR.
- Modifier 22 remains non-automatic and does not change modeled payment.
- Add-on codes preserve normal add-on behavior.
- NCCI/separate-procedure exclusions still set payable wRVU and payment to 0.
- APP productivity display continues to use its existing productivity estimate pathway.

## Final Recommendation

Ready after review.

