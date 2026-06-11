# Phase 1 Browser Findings

No fixes applied. Browser checks were run against the local build on the audit branch.

## Findings
- 44950: search=True, case_builder_accepted=True, displayed_wrvu=10.34, canonical_wrvu=10.34, displayed_payment=$345.37, canonical_payment=$605.56
  - Case Builder displayed payment differs from canonical total-RVU Medicare estimate.
- 44960: search=True, case_builder_accepted=True, displayed_wrvu=14.14, canonical_wrvu=14.14, displayed_payment=$472.29, canonical_payment=$825.0
  - Case Builder displayed payment differs from canonical total-RVU Medicare estimate.
- 44970: search=True, case_builder_accepted=True, displayed_wrvu=9.21, canonical_wrvu=9.21, displayed_payment=$307.62, canonical_payment=$578.17
  - Case Builder displayed payment differs from canonical total-RVU Medicare estimate.
- 47562: search=True, case_builder_accepted=True, displayed_wrvu=11.47, canonical_wrvu=10.21, displayed_payment=$383.11, canonical_payment=$631.95
  - Case Builder displayed wRVU differs from canonical work RVU.
  - Case Builder displayed payment differs from canonical total-RVU Medicare estimate.
- 49505: search=False, case_builder_accepted=False, displayed_wrvu=0.0, canonical_wrvu=7.09, displayed_payment=$0.0, canonical_payment=$508.03
  - Case Builder did not accept/add code from homepage search flow.
  - Homepage search did not return code.
  - Case Builder displayed wRVU differs from canonical work RVU.
  - Case Builder displayed payment differs from canonical total-RVU Medicare estimate.
