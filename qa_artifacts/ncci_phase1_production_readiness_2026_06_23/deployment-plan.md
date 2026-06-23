# Production Deployment Plan - 159-Pair Phase 1 NCCI Activation

Status: not deployed. Deploy only after Graydon approval.

## Rollout Plan

1. Confirm the review branch is clean and current:
   - Branch: review/ncci-phase1-surgical-pack-20260623
   - Candidate active dataset: data/ncci/active/cms_ncci_ptp_active.json
   - Pair count: 159
   - Modifier-1 activated: false
2. Run local gates:
   - node scripts/validate_ncci_phase1_pack.js
   - Review qa_artifacts/ncci_phase1_production_readiness_2026_06_23/top-25-workflow-browser-validation.json
3. Merge the review branch to main only after explicit approval.
4. Push main to GitHub Pages production.
5. Wait for GitHub Pages propagation.
6. Run live production validation checklist below.

## Rollback Plan

Fast rollback:

1. Revert the deployment commit on main.
2. Push the revert to GitHub.
3. Wait for GitHub Pages propagation.
4. Validate that known Phase 1 pairs no longer load from data/ncci/active/cms_ncci_ptp_active.json.

Data-only rollback:

1. Replace data/ncci/active/cms_ncci_ptp_active.json with an empty ptp_pairs dataset.
2. Update data/ncci/active/manifest.json pairCount to 0 and activationMode to disabled.
3. Push the rollback commit.
4. Validate existing curated ncci_bundles.json behavior remains active.

## Production Validation Checklist

After deployment, validate live:

- 44140 + 44005: selected 40.03, payable 22.03, hard-stop card visible.
- 44620 + 44005: selected 32.07, payable 14.07, hard-stop card visible.
- 44120 + 44005: selected 38.30, payable 20.30, hard-stop card visible.
- 44055 + 49000: selected 37.22, payable 24.99, hard-stop card visible.
- 38100 + 44005: selected 37.06, payable 19.06, hard-stop card visible.
- 49593 + 15734: clean control, selected/payable 32.43.
- 60240 + 60500: clean control, selected/payable 29.87.
- 21811 + 32551: clean control, selected/payable 13.48.
- 49002 + 97606: clean control, selected/payable 17.78.

Also confirm:

- data/ncci/active/manifest.json returns 200.
- data/ncci/active/cms_ncci_ptp_active.json returns 200.
- Active dataset pairCount is 159.
- Modifier-1 activated is false.
- Case Builder still shows selected vs payable totals separately.
- Existing MPPR control still works.

## Post-Deployment Monitoring Plan

Monitor for 7 days:

- Issue-report submissions mentioning NCCI, bundled, 44005, 49000, selected wRVU, payable wRVU, or missing RVUs.
- High-frequency searches/case-builder entries involving 44005.
- Any surgeon feedback that a code disappeared or totals are unclear.
- Console/network failures for data/ncci/active/cms_ncci_ptp_active.json.
- Regression reports for TAR/component separation, thyroid/parathyroid, rib fixation, and open abdomen controls.

Escalation:

- If a true data/load failure occurs, use data-only rollback immediately.
- If the complaint is policy disagreement but UI is correct, keep deployed and improve explanation text if needed.
- If a specific pair creates repeated clinically credible confusion, remove that pair from active dataset and schedule specialty review.
