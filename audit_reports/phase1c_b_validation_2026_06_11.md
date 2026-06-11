# Phase 1C-B Validation Report

Branch: audit/phase1c-b-cms-reversion-2026-06-11
Mode: local/staging validation only. No production deployment performed.

| CPT | CMS wRVU | Site wRVU | Total RVU | Medicare estimate | Search seed | Case Builder seed | Page | Result |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 43280 | 17.65 | 17.65 | 30.30 | $1012.05 | pass | pass | pass | PASS |
| 49505 | 7.76 | 7.76 | 15.21 | $508.03 | pass | pass | pass | PASS |
| 49520 | 9.74 | 9.74 | 18.21 | $608.23 | pass | pass | pass | PASS |
| 49650 | 6.20 | 6.20 | 12.70 | $424.19 | pass | pass | pass | PASS |
| 49651 | 8.17 | 8.17 | 16.47 | $550.11 | pass | pass | pass | PASS |

Scanner note: the legacy Phase 1 scanner was run separately and produced known false-positive homepage SPECS parser noise against object-style SPECS. Direct parsing of the actual SPECS object used by the app passed for all five codes.

Screenshots: qa_artifacts/phase1c_b_cms_reversion_2026_06_11/code_<CPT>_desktop.png. Captured with wkhtmltoimage because local headless Chrome hung before exposing DevTools/screenshot output.

No indicator, descriptor, or deleted-code remediation was performed.
