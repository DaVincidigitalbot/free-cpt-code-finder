# NCCI Indicator 0 Forward Fix Validation Report

Date: 2026-06-11
Branch: feature/modifier-denial-guidance
Reviewed base commit: 0b09c4ac0059f6c2b78d391d30ae001217898e27
Scope: Forward fix, no merge, no deployment.

## Summary

The forward fix makes non-bypassable NCCI modifier-indicator-0 exclusion a first-class Case Builder state.

Result: PASS on the validation set.

- Indicator 0 pairs tested: 11
- Indicator 0 excluded without modifier attempt: true
- Indicator 0 excluded after modifier attempt: true
- Indicator 0 Column 2 remains visible: true
- Indicator 0 denial education shown without modifier attempt: true
- Indicator 0 modifier bypass prevented: true
- Indicator 0 no bundled payable leak: true
- Indicator 1 caution behavior preserved: true
- Clean modifier cases remain clean: true

## Implementation

- Preserves NCCI direction by normalizing each edit to Column 1 and Column 2.
- Builds a blocked Column 2 map before modifier selection.
- Reorders selected procedures so payable Column 1 remains primary even when Column 2 has higher wRVU.
- Marks all modifier-indicator-0 Column 2 lines bundled/not separately payable even with no modifier attempt.
- Keeps Column 2 visible as selected/performed while setting payable wRVU and dollars to zero.
- Keeps indicator-1 pairs in the documentation-required caution state.

## Indicator 0 Tests

- 44207 / 44180 (Colorectal): selected 46.01; payable 31.12; display 31.12 / $1,649.34 · selected 46.01 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/prior_44207_44180_44207_44180.png
- 31267 / 31231 (ENT): selected 5.63; payable 4.56; display 4.56 / $224.12 · selected 5.63 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/pass_ent_31267_31231_31267_31231.png
- 32100 / 32551 (Cardiothoracic/Trauma): selected 16.37; payable 13.41; display 13.41 / $777.24 · selected 16.37 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/pass_ct_32100_32551_32100_32551.png
- 44141 / 49000 (Colorectal/General Surgery): selected 41.39; payable 29.16; display 29.16 / $1,691.09 · selected 41.39 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/pass_colorectal_44141_49000_44141_49000.png
- 92928 / 93458 (Cardiology): selected 15.21; payable 9.75; display 9.75 / $463.94 · selected 15.21 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/pass_cardio_92928_93458_92928_93458.png
- 47562 / 49000 (HPB/General Surgery): selected 22.44; payable 10.21; display 10.21 / $631.95 · selected 22.44 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/failfix_hpb_47562_49000_47562_49000.png
- 60240 / 60260 (Endocrine): selected 32.46; payable 14.66; display 14.66 / $829.68 · selected 32.46 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/failfix_endocrine_60240_60260_60240_60260.png
- 33533 / 33508 (Cardiac Surgery): selected 33.21; payable 32.91; display 32.91 / $1,757.89 · selected 33.21 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/failfix_cabg_addon_33533_33508_33533_33508.png
- 12001 / 44140 (Wound/General Surgery): selected 22.85; payable 0.82; display 0.82 / $113.90 · selected 22.85 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/extra_wound_12001_44140_12001_44140.png
- 31287 / 31231 (ENT): selected 4.48; payable 3.41; display 3.41 / $170.34 · selected 4.48 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/extra_sinus_31287_31231_31287_31231.png
- 99291 / 32551 (Critical Care/Trauma): selected 7.46; payable 4.5; display 4.50 / $308.96 · selected 7.46 wRVU; Column 2 excluded without modifier true; Column 2 excluded with -59 true; denial shown true; bypass prevented true; screenshot screenshots/extra_critical_99291_32551_99291_32551.png

## Indicator 1 Tests

- 15734 / 43280: display 40.08 / $1,892.84 · MPPR applied; excluded false; caution shown true; denial shown false; screenshot screenshots/indicator1_15734_43280_15734_43280_retest.png
- 44140 / 49000: display 34.26 / $1,614.61 · MPPR applied; excluded false; caution shown true; denial shown false; screenshot screenshots/indicator1_44140_49000_44140_49000_retest.png

## Clean Modifier Tests

- clean_43280_rt: display 17.65 / $1,012.05; state 1 line · medicare · CLEAN; no denial/caution/exclusion panels; screenshot screenshots/clean_43280_rt.png
- clean_44970_lt: display 9.21 / $578.17; state 1 line · medicare · CLEAN; no denial/caution/exclusion panels; screenshot screenshots/clean_44970_lt.png

## Before / After

Before fix, the prior validation package showed these failures:

- 47562 / 49000: payable stayed 22.44 instead of excluding Column 2.
- 60240 / 60260: payable stayed 32.46 instead of excluding Column 2.
- 33533 / 33508: add-on Column 2 stayed payable.
- Active indicator-0 pairs without a modifier attempt could contribute RVUs/dollars.

After fix:

- 47562 / 49000: selected 22.44, payable 10.21.
- 60240 / 60260: selected 32.46, payable 14.66.
- 33533 / 33508: selected 33.21, payable 32.91.
- All tested indicator-0 pairs excluded Column 2 both before and after a modifier attempt.

## Change-Control Confirmation

No changes were made to:

- NCCI source data
- RVU source data
- MPPR formula
- modifier rule data
- CPT code data
- production deployment state

Product code changed: index.html only.

## Deployment / Merge

No merge performed.
No deployment performed.

Recommended next step: review this commit, then deploy to staging only for live UI verification if approved.