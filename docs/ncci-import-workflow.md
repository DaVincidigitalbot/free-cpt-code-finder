# CMS NCCI Import Workflow

This workflow keeps FreeCPTCodeFinder NCCI behavior sourced from CMS Practitioner PTP files instead of hand-maintained JSON.

## Source

- CMS NCCI Practitioner PTP quarterly zip files.
- Phase 1 source version: 2026-Q3.
- Phase 1 mode: surgical modifier-0 activation only.
- Modifier-1 infrastructure exists in schema/runtime, but modifier-1 edits are not activated in Phase 1.

## Directory Layout

- scripts/import_cms_ncci_ptp.js: deterministic importer.
- scripts/validate_ncci_phase1_pack.js: regression validator for Phase 1.
- data/ncci/versions/<VERSION>/: immutable generated quarterly dataset and audit files.
- data/ncci/active/: runtime pointer used by index.html.

Runtime file: data/ncci/active/cms_ncci_ptp_active.json

Versioned files:

- data/ncci/versions/2026-Q3/surgical-modifier0-activation-pack.json
- data/ncci/versions/2026-Q3/surgical-modifier0-behavior-change-list.json
- data/ncci/versions/2026-Q3/import-audit.json

## Quarterly Import Command

Run: node scripts/import_cms_ncci_ptp.js --source-dir /path/to/cms-practitioner-ptp-zips --version 2026-Q3 --limit 500

The importer reads CMS zip/txt files, filters active rows, limits to FreeCPT CPT codes in the requested surgical domains, excludes pairs already covered by ncci_bundles.json, activates modifier-0 only, ranks by use likelihood and wRVU/payment impact, then writes versioned data, active runtime data, manifest, behavior-change list, and audit log.

## Validation

Run: node scripts/validate_ncci_phase1_pack.js

Required checks:

- Active dataset schema is freecpt.ncci.ptp.v1.
- Active CMS version matches manifest.
- Exactly 500 Phase 1 pairs are active.
- Every active pair has modifier indicator 0.
- Modifier-1 activation flag is false.
- Required surgical regression pairs are present.
- Every behavior-changing pair has previous behavior, new behavior, selected wRVU impact, and payable wRVU impact.

Browser validation is captured under qa_artifacts/ncci_phase1_surgical_pack_2026_06_23/.

## Production Deployment Plan

1. Review activation-candidate-list.md and screenshots.
2. Confirm regression-validation.json has no failures.
3. Confirm browser validation screenshots show expected selected/payable behavior.
4. Merge only after Graydon approves.
5. Deploy through the normal GitHub Pages main branch path.
6. After deployment, validate live known pairs and an MPPR control case.

## Rollback Plan

Fast rollback: revert the Phase 1 deployment commit from main, push, and re-run live validation.

Data-only rollback: replace data/ncci/active/cms_ncci_ptp_active.json with an empty ptp_pairs dataset, set manifest pair count to 0, deploy, and validate that existing curated ncci_bundles.json behavior remains active.

## Risk Assessment

Benefits: stops known overstatement of payable wRVUs, preserves selected/payable transparency, replaces ad hoc manual rules with a repeatable CMS-source import, and creates version/rollback artifacts before production activation.

Risks: 500 surgeon-facing behavior changes, some low-probability mutually exclusive pairs in edge-case testing, and changed expectations for users accustomed to incorrect payable totals.

Mitigation: modifier-1 disabled, modifier-0 only, behavior-change row for every pair, browser screenshots for common workflows, and fast rollback path.
