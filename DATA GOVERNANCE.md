# DATA GOVERNANCE

## CMS Source Of Truth

The authoritative RVU and indicator baseline is CMS RVU26C July 2026 non-QPP:

- Archive: https://www.cms.gov/files/zip/rvu26c.zip
- File: PPRRVU2026_Jul_nonQPP.csv
- Conversion factor used by the current platform: 33.4009

FreeCPTCodeFinder generated CPT data, search data, Case Builder data, CPT pages, and modifier metadata must be derived from that canonical source unless a documented and approved exception exists.

## Import Process

1. Download the CMS RVU26C archive.
2. Parse PPRRVU2026_Jul_nonQPP.csv from the archive.
3. Build canonical CPT/RVU records.
4. Derive assistant surgeon, co-surgeon, bilateral, multiple procedure, team surgeon, and global period indicators from CMS fields.
5. Regenerate homepage search and Case Builder metadata from cpt_database.json.
6. Regenerate CPT pages from canonical CPT descriptors and RVU records.
7. Run python3 tools/platform_hardening_audit.py before review, merge, staging deployment, or production deployment.

Generated artifacts must not be hand-edited when a canonical source update or generator change is the correct fix.

## Override Policy

Manual RVU or indicator overrides are forbidden by default.

An override may exist only when an audit report documents:

- CPT code and field
- CMS value
- site value
- source rationale
- date introduced
- commit hash
- approving review context

Unsupported overrides must be reverted to CMS. User-requested overrides are not valid unless they include a durable source note and review approval.

## Deleted-Code Policy

Deleted, inactive, or legacy CPT codes must not appear in:

- active CPT datasets
- homepage search
- Case Builder
- payable CPT workflows
- active modifier-rule datasets
- active CPT index cards

The URL may remain live with an inactive/deleted warning banner when the page has informational or search-preservation value. The banner must state that the code is inactive/deleted and should not be used for current billing. Redirects require replacement-family review before implementation.

## Validation Process

The single platform integrity gate is:

    python3 tools/platform_hardening_audit.py

The command fails the build when it finds:

- active CPT pages with placeholder descriptors
- active CPT pages with missing descriptors
- active CPT records with 0.00 RVU and no inactive/deleted classification
- homepage search rows that differ from the canonical CPT dataset
- Case Builder rows that differ from the canonical CPT dataset
- indicator fields that differ from CMS RVU26C
- deleted/inactive CPT codes in active search
- deleted/inactive CPT codes in Case Builder
- malformed CPT page title, H1, or meta description fields

The command writes a scorecard to qa_artifacts/phase3a_platform_hardening_2026_06_11/platform_integrity_scorecard.json.
