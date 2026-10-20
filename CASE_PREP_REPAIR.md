# Case-prep search repair

Base: f41ebc0a659518ffa71e8ab88692091fd2d6d16a (main).

The landing page now searches the imported index and live original guide catalog together. Search expands common abbreviations, normalizes punctuation and spacing, matches query words in any order, and prefers title and alias matches. Equivalent imported sheets are grouped under an operative guide with separate rapid-prep links; every imported record remains reachable. Planned guides are excluded. Guide categories are mapped into the imported 20-category taxonomy so specialty filters remain consistent. No generated JSON or clinical material was changed, so future imports preserve this repair.

The results section follows the search hero, ahead of featured guides. The hero is smaller, category controls are simpler on mobile, and example searches are clickable. Load failure exposes a reload action. Search honors text entered before data finishes loading. Index and detail payloads remain separate; only the landing page fetches the existing original-guide catalog in addition to the lightweight index. Internal destination URLs are parsed against the production origin and reject external, protocol-relative, and backslash-normalized destinations. The mobile report control remains compact on both landing and detail pages.

## Validation performed

- `node --test tests/case-prep-search.test.cjs`: 5 passed. Tests cover real catalogs, common queries, filtering, ranking, deduplication, escaping, preservation of all imported destinations, and landing event handlers.
- `python3 -m unittest -v test_case_prep_library.py`: 9 passed.
- `uv run --with selenium python -m unittest discover -p 'test_*.py'`: 13 passed.
- JavaScript syntax checks, importer Python compilation, and `git diff --check`: passed.
- Desktop and 390px mobile browser QA passed for reordered search terms, abbreviations, all 20 categories, clear/show-more controls, original and imported destinations, question-level filters, overflow, report-widget clearance, main CPT search, and the Make No Mistakes advertisement.
- Local runtime-error capture found no JavaScript errors; all expected case-prep requests returned HTTP 200.
- Lighthouse: landing 95 performance / 100 accessibility / 77 best practices / 100 SEO; detail 95 / 100 / 100 / 100. The landing best-practices penalty is from the existing third-party AdSense integration.
- Deployment remains pending final commit, rollback checkpoint, GitHub Pages push, and production verification.

## Applied on the laptop

The supplied patch was applied cleanly to a working tree based on the stated production commit. A browser-discovered mobile report-widget issue and an independent-review category-taxonomy blocker were fixed with regression tests before deployment.

The checks above have been completed. Production must still be verified after the GitHub Pages deployment using the same search, destination, question-level, CPT-search, advertisement, mobile-layout, and request-health checks.

The repository's DEPLOY_PROTOCOL.md also requires its artifact build/canary commands, but those referenced scripts are absent from this revision. Resolve that stale protocol against the current repository's actual GitHub Pages configuration before release; do not claim those checks passed.

Record current production SHA and create a rollback branch before pushing. Commit only the six repair files, then push to main using the normal authenticated deployment process after checks pass. Verify GitHub Pages and the production page, including cache-busted CSS/JS. Revert the repair commit if production checks fail. Preserve CNAME and .nojekyll.
