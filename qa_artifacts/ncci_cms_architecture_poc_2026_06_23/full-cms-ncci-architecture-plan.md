# Full CMS NCCI Architecture Plan

Generated: 2026-06-23

## Executive Summary

FreeCPTCodeFinder should move away from a hand-maintained NCCI JSON file. The current curated set is useful for high-value known cases, but the CMS Practitioner PTP file contains hundreds of thousands of active relationships across loaded surgical CPT codes. The durable architecture is a versioned CMS import pipeline with a runtime edit index, explicit modifier-indicator semantics, and reviewable release gates.

## Goals

- Import CMS Practitioner PTP files quarterly.
- Preserve selected versus payable wRVU separation.
- Apply modifier-0 edits as hard stops.
- Display modifier-1 edits as documentation-dependent warnings with coder override workflow.
- Keep separate-procedure context rules for cases where CMS PTP alone is insufficient.
- Record the active CMS version used for any case calculation.
- Make updates reproducible from repo artifacts and validation scripts.

## Data Model

Create a generated file such as `data/ncci/2026Q3/practitioner-ptp-index.json`.

Recommended schema:

```json
{
  "source": "CMS NCCI Practitioner PTP",
  "version": "2026Q3-v322r0",
  "effectiveDate": "2026-07-01",
  "generatedAt": "ISO timestamp",
  "records": [
    {
      "column1": "44055",
      "column2": "49000",
      "modifierIndicator": "0",
      "effective": "19970101",
      "deletion": "*",
      "rationale": "CPT Separate procedure definition",
      "sourceFile": "ccipra-v322r0-f3.txt"
    }
  ],
  "index": {
    "44055|49000": 0
  }
}
```

Runtime can load either `records` with an index or a compact map. The key point is that modifier indicator is pair-specific, not column1-group-specific. The existing `ncci_bundles.json` schema cannot safely represent mixed modifier indicators under the same Column 1 code.

## Import Pipeline

1. Download CMS Practitioner PTP quarterly zip files from the official CMS NCCI PTP page.
2. Verify zip integrity and record file names, row counts, SHA256 hashes, posted date, and effective quarter.
3. Parse text files, preserving:
   - Column 1
   - Column 2
   - Effective date
   - Deletion date
   - Modifier indicator
   - PTP rationale
   - Source file
4. Filter active rows where deletion is `*`.
5. Build:
   - Full raw normalized artifact
   - Runtime compact index
   - Human-readable diff versus previous quarter
   - Surgical subset report by specialty/range/loaded CPT inventory
6. Commit generated artifacts and import summary.

## Runtime Logic

### Modifier-0

If a same-case pair matches active NCCI modifier indicator 0:

- Mark Column 2 line as `payableExcluded=true`.
- Set payable wRVU to `0.00`.
- Preserve selected wRVU for transparency.
- Show NCCI Hard Stop warning.
- Block modifier 59, XE, XS, XP, and XU.
- Include CMS version and PTP rationale in audit output.

### Modifier-1

If a pair matches active NCCI modifier indicator 1:

- Do not automatically suppress payable wRVU.
- Show a documentation-required warning card.
- Explain that the edit may be bypassed only if documentation supports distinct procedural service.
- Let coder choose 59/XE/XS/XP/XU in the modifier workflow.
- If no modifier is selected, keep the line payable for review but flag the case state as WARNING.
- Audit should record that a documentation-dependent edit exists.

### Separate-Procedure Rules

Keep separate-procedure context rules as a separate layer for clinical-context suppression that CMS PTP does not fully encode.

Use this order:

1. Load CMS PTP edit index.
2. Apply modifier-0 hard stops.
3. Apply explicit context-dependent separate-procedure suppression rules.
4. Apply modifier-1 warnings.
5. Rank remaining payable lines and calculate MPPR/payment.

## Version Tracking

Every case export and audit JSON should include:

- NCCI source: CMS Practitioner PTP
- Version: e.g. `2026Q3-v322r0`
- Effective date
- Import commit hash
- Runtime loaded row count
- Whether the edit came from CMS PTP, separate-procedure context rule, or local curated rule

## Quarterly Update Process

1. Create branch `data/ncci-YYYYQX-import`.
2. Run import script.
3. Generate diff report:
   - Added modifier-0 edits
   - Removed edits
   - Modifier indicator changes
   - High-impact surgical pairs changed
4. Run browser regression suite.
5. Run spot checks on high-value surgical pairs.
6. Review and approve.
7. Deploy only after validation artifacts are attached.

## Regression Testing

Minimum gates:

- Known modifier-0 hard stops:
  - 44055 + 49000
  - 44207 + 44180
  - 44005 + 49000
  - 44140 + 49000
  - 44970 + 49320
- Known modifier-1 warning pairs:
  - Colectomy + repair/drainage pairs from CMS subset
  - Hernia + bowel repair warning examples
- Selected versus payable totals:
  - bundled line visible but excluded
  - selected wRVU retained
  - payable wRVU excludes Column 2
- MPPR:
  - unaffected when no edit applies
  - applies only to payable lines
- Modifier picker:
  - modifier-0 prevents bypass
  - modifier-1 gives documentation-dependent warning

## Audit Logging

Each line item should carry:

- `ncciEditKey`
- `ncciColumn1`
- `ncciColumn2`
- `modifierIndicator`
- `ncciRationale`
- `ncciVersion`
- `payableExcluded`
- `payableExclusionClass`
- `overrideModifier`
- `overrideReason`
- `coderReviewRequired`

## Deployment Risk Controls

- Do not bulk enable full CMS PTP without staged browser coverage.
- Start with a surgical subset and explicit top-risk validation.
- Keep full import artifact in repo or durable storage, but gate runtime adoption by feature flag/config.
- Roll out in stages:
  1. Top 500 modifier-0 hard stops
  2. Top 500 modifier-1 warnings
  3. Full loaded-code surgical PTP
  4. Full CMS PTP if performance remains acceptable

## Recommendation

Move toward comprehensive CMS NCCI coverage, but do not flip the full file into production in one deploy.

Recommended path: build the full import pipeline now, then deploy a reviewed high-value surgical subset first. This gives immediate user safety for dangerous overpayment cases while avoiding a large silent behavior change across hundreds of thousands of pairs.

