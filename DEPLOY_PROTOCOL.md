# FreeCPTCodeFinder Deploy / Rollback Protocol

## Default rule
Every production deploy must have an immediate rollback path.

## Safe EP/source rebuild blockers
The `safe-ep-sources-rebuild` branch is not complete and must not be staged or deployed unless the root source page is restored and verified.

Required source-page checks:
- `/sources.html` exists at the root of the production artifact.
- `/sources.html` returns 200 in staging before any production deploy.
- `/sources.html` returns 200 on `https://freecptcodefinder.com/sources.html` immediately after production deploy.
- Source links use `/sources.html`, not `/sources/sources.html`, `/source.html`, `/references.html`, or a dev-only path.
- Header/nav links may include Sources if space allows; footer links must include Sources; homepage source/reference links must use `/sources.html`.
- The source page must include CMS Physician Fee Schedule, CMS National Physician Fee Schedule Relative Value File, Medicare Claims Processing Manual, CMS NCCI Policy Manual, CMS MPFS lookup/database, AMA CPT resources, and any other source references used by the authority package.
- Source restoration must not change the stable homepage layout from `a93de45` except for verified links/copy.

Required blocker test:
- Run `node tools/audit_sources_page.js .` against the built/staged artifact.
- Result must show `missingInternalLinks: 0`, `missingSourceLinks: 0`, and `rootSourcesStatus: 200`.
- Then open `/sources.html` directly in the browser on staging and confirm no desktop or mobile layout break.

## Deploy checklist
1. Verify working tree and commit intended changes only.
2. Run local artifact build:
   - `python3 scripts/build-pages-artifact.py`
   - `python3 scripts/pages-artifact-canary.py public`
3. For `safe-ep-sources-rebuild`, verify `/sources.html` before staging:
   - `node tools/audit_sources_page.js .`
   - open `/sources.html` directly in the staging browser
   - confirm footer and homepage links reach `/sources.html`
   - confirm no homepage clipping, overflow, or header/logo regression
4. Create rollback checkpoint before push:
   - record current production/base commit
   - create timestamped backup branch from that commit
5. Push deploy branch.
6. Confirm GitHub Pages workflow succeeds.
7. Verify live site critical paths:
   - homepage loads
   - CPT search works
   - representative CPT/wRVU pages load
   - `https://freecptcodefinder.com/sources.html` returns 200
   - header/footer source links work live
   - internal link audit remains 0 missing links
   - source link audit remains 0 missing source links
8. If broken, revert immediately by resetting deploy branch to rollback checkpoint and pushing again.

## Rollback commands
```bash
# Example
BACKUP_BRANCH="backup/predeploy-$(date +%Y%m%d-%H%M%S)"
BASE_COMMIT=$(git rev-parse origin/main)
git branch "$BACKUP_BRANCH" "$BASE_COMMIT"

# If rollback needed
git checkout audit/wrvu-cms-pass
git reset --hard "$BASE_COMMIT"
git push --force-with-lease origin audit/wrvu-cms-pass
```

## Notes
- No production push without a fresh rollback checkpoint.
- No unverified deploy gets to stay live.
- Keep rollback limited to the deploy branch unless a broader incident requires a different recovery path.
