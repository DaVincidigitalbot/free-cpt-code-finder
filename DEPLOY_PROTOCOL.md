# FreeCPTCodeFinder Deploy / Rollback Protocol

## Default rule
Every production deploy must have an immediate rollback path.

## Deploy checklist
1. Verify working tree and commit intended changes only.
2. Run local artifact build:
   - `python3 scripts/build-pages-artifact.py`
   - `python3 scripts/pages-artifact-canary.py public`
3. Create rollback checkpoint before push:
   - record current production/base commit
   - create timestamped backup branch from that commit
4. Push deploy branch.
5. Confirm GitHub Pages workflow succeeds.
6. Verify live site critical paths:
   - homepage loads
   - CPT search works
   - representative CPT/wRVU pages load
7. If broken, revert immediately by resetting deploy branch to rollback checkpoint and pushing again.

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
