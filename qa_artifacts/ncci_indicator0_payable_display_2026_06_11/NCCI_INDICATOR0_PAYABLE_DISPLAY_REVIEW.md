# NCCI Indicator 0 Payable Display Review

Generated: 2026-06-11

Branch: `feature/modifier-denial-guidance`

## Question Reviewed

For CPT 44207 + CPT 44180 with current CMS NCCI modifier indicator 0, should the Case Builder show the combined 46.01 wRVU / $2,081.55 as payable?

Answer: no.

CPT 44180 is Column 2 to CPT 44207 under current CMS NCCI PTP edits with modifier indicator 0. The Column 2 line is bundled and cannot be bypassed with modifier 59/XS/XE/XP/XU. The payable estimate should exclude 44180 and show only the payable primary procedure estimate unless another supported coding pathway exists.

## Current Behavior Before Fix

The Case Builder did not distinguish between:

- Selected code total
- Submitted code total
- Allowed/payable estimated total
- Blocked/bundled code total

The main display summed every selected line's effective wRVU even when a secondary line was BLOCKED by a non-bypassable NCCI edit.

Before screenshot from prior validation:

`qa_artifacts/modifier_caution_guidance_2026_06_11/screenshots/03_blocked_indicator_0.png`

Before result:

| Metric | Value |
| --- | ---: |
| Selected codes | 44207 + 44180 |
| Displayed total wRVU | 46.01 |
| Displayed payment | $2,081.55 |
| Status | BLOCKED |
| Problem | Bundled 44180 was still included in the displayed total |

## Fix Classification

This required a calculation-display fix, not only a messaging fix.

The underlying NCCI decision logic did not change. The fix marks non-bypassable bundled Column 2 lines as selected-but-not-payable and excludes them from the payable estimate shown in the Case Builder totals.

## Display Behavior After Fix

Runtime validation used the same NCCI indicator 0 test pair:

- 44207 = payable/primary
- 44180 = bundled into 44207
- Modifier 59/XS/XE/XP/XU cannot bypass the edit
- 44180 remains visible as selected for review
- 44180 payable wRVU/payment contribution = 0
- Main total now reflects payable estimate only

After screenshot:

`qa_artifacts/ncci_indicator0_payable_display_2026_06_11/screenshots/after_44207_44180_indicator0_payable_display.png`

After result:

| Metric | Value |
| --- | ---: |
| Selected code total | 46.01 wRVU |
| Payable displayed total | 31.12 wRVU |
| Payable displayed estimate | $1,649.34 |
| 44207 payable | Yes |
| 44180 included in payable estimate | No |
| 44180 line display | Selected wRVU 14.89 / Payable wRVU 0.00 / Not included |
| Modifier 59 on 44180 | Removed |
| Case status | BLOCKED |

## User-Facing Message Added

The bundled line now shows:

"Bundled / not payable estimate: Bundled into CPT 44207 under a non-bypassable NCCI edit. This line is selected for review but excluded from the payable estimate. Consider whether modifier 22 on 44207 is supportable when documentation shows substantially increased work."

The denial panel continues to show that 44180 is bundled into 44207, modifier indicator 0 cannot be bypassed, and modifier 59/XS/XE/XP/XU are not permitted.

## Regression Validation

`qa_artifacts/ncci_indicator0_payable_display_2026_06_11/regression_validation.json`

| State | Result |
| --- | --- |
| Routine valid modifier 43280-RT | CLEAN, RT applied, no exclusion, 17.65 wRVU, $1,012.05 |
| NCCI indicator 1 documentation-dependent modifier | WARNING, -59 applied, caution panel shown, no exclusion, 40.08 wRVU, $1,892.84 |
| NCCI indicator 0 non-bypassable edit | BLOCKED, -59 removed, denial panel shown, 44180 excluded, payable total 31.12 wRVU / $1,649.34 |

HTTP browser validation captured no console errors or warnings.

## Guardrails

No changes were made to:

- CPT/RVU data files
- NCCI pair data
- NCCI pair lookup logic
- modifier allowance rules
- MPPR formula
- base RVU values
- code selection/search behavior
- production deployment

Changed behavior is limited to Case Builder payable-total display and line-level display when a non-bypassable NCCI edit blocks a bundled Column 2 code.

## Conclusion

The concern was valid. Prior display could cause a surgeon to believe 46.01 wRVU / $2,081.55 was payable. After the fix, the Case Builder shows 31.12 wRVU / $1,649.34 as the payable estimate, keeps selected 46.01 wRVU visible for transparency, and clearly marks 44180 as bundled/not included.

