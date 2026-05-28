# SEO Indexing Handoff

## Branch
main

## Commit Hash
4158630

Latest handoff update: 62ff6c1

## Live / Preview URL
https://freecptcodefinder.com/

## Summary of Changes
- Standardized primary public-facing brand signals to **FreeCPTCodeFinder.com**.
- Kept **Free CPT Code Finder** only as a readable alternate phrase where useful for search intent and natural language.
- Removed legacy CYRIONYX/Cyrionyx/Cyrioniq text from indexable public HTML surfaces.
- Converted the legacy /cyrioniq/ page into a noindex/canonical transition page pointing to the homepage.
- Updated homepage title, meta description, Open Graph/Twitter tags, and JSON-LD.
- Normalized Open Graph site_name and structured-data publisher/site names to FreeCPTCodeFinder.com.
- Added/confirmed Person schema for Graydon Stallard, DO, FACOS, FACS on the about/founder surfaces.
- Added datePublished to blog Article schema where missing.
- Improved homepage internal links to codes index, CPT Code For, case builder, modifier guides, RVU guide, global period guide, about, and editorial policy.
- Regenerated sitemap.xml from canonical, indexable public HTML pages.
- Cleaned robots.txt and confirmed it references sitemap.xml.

## CYRIONYX Cleanup
PASS: Local audit found **0** remaining CYRIONYX/Cyrionyx/Cyrioniq hits in HTML after cleanup.

## Sitemap
PASS: sitemap.xml regenerated with 758 canonical URLs.
PASS: Includes homepage, blog index, codes index, CPT Code For, about/contact/legal/editorial pages, all indexed blog posts, and all indexed CPT code detail pages.
PASS: robots.txt references https://freecptcodefinder.com/sitemap.xml.

## Indexability
PASS: Local HTML audit found:
- 758 indexable HTML pages
- 14 intentional noindex pages (admin/test/mockup/legacy/demo surfaces)
- 0 missing title/meta/canonical on indexable pages
- 0 bad canonical URLs
- 0 duplicate titles
- 0 duplicate meta descriptions
- 0 missing/multiple H1 issues on indexable pages
- 0 broken internal links in local public HTML audit

## Key Title / Meta Changes
- Homepage title: FreeCPTCodeFinder.com | CPT Code Lookup, wRVUs, Modifiers & Case Builder
- Homepage meta description: Free CPT code lookup for medical students, residents, APPs, surgeons, and coders. Search CPT codes, wRVUs, modifiers, global periods, billing guides, and build cases with a free wRVU case builder.
- Blog index title normalized to FreeCPTCodeFinder.com branding.
- Codes index title normalized to FreeCPTCodeFinder.com branding.
- CPT Code For title normalized to FreeCPTCodeFinder.com branding.
- Code detail title suffixes normalized to FreeCPTCodeFinder.com.
- Blog page publisher/site_name signals normalized to FreeCPTCodeFinder.com.

## Search Console URL Inspection Findings
BLOCKED: Google Search Console inspection/submission could not be run from this environment because no authenticated Search Console API credential or browser-authenticated GSC session is available locally.

Requested inspection URLs:
- https://freecptcodefinder.com/
- https://freecptcodefinder.com/blog/
- https://freecptcodefinder.com/codes/
- https://freecptcodefinder.com/codes/10060.html
- https://freecptcodefinder.com/about.html
- https://freecptcodefinder.com/editorial-policy.html

Status fields not available without GSC auth:
- URL is on Google
- Page is indexable
- User-declared canonical
- Google-selected canonical
- Last crawl date
- Crawl/indexing errors
- Whether indexing was requested

## Sitemap Submission Status
BLOCKED: Sitemap submission in Google Search Console requires authenticated Search Console access. The site now exposes the canonical sitemap at:
https://freecptcodefinder.com/sitemap.xml

## Live Validation
PASS: Cache-busted live homepage returned the updated title, meta description, canonical URL, and robots meta.

PASS: These live URLs returned 200 and did not send an X-Robots-Tag noindex header:
- https://freecptcodefinder.com/
- https://freecptcodefinder.com/blog/
- https://freecptcodefinder.com/codes/
- https://freecptcodefinder.com/codes/10060.html
- https://freecptcodefinder.com/about.html
- https://freecptcodefinder.com/editorial-policy.html
- https://freecptcodefinder.com/robots.txt
- https://freecptcodefinder.com/sitemap.xml

PASS: Live sitemap.xml contains 758 URLs and includes:
- https://freecptcodefinder.com/
- https://freecptcodefinder.com/blog/
- https://freecptcodefinder.com/codes/
- https://freecptcodefinder.com/codes/10060.html
- https://freecptcodefinder.com/about.html
- https://freecptcodefinder.com/editorial-policy.html

PASS: Live robots.txt references:
Sitemap: https://freecptcodefinder.com/sitemap.xml

PASS: Key live page signals verified:
- Homepage title: FreeCPTCodeFinder.com | CPT Code Lookup, wRVUs, Modifiers & Case Builder
- Homepage canonical: https://freecptcodefinder.com/
- Blog canonical: https://freecptcodefinder.com/blog/
- Codes canonical: https://freecptcodefinder.com/codes/
- CPT 10060 canonical: https://freecptcodefinder.com/codes/10060.html

## Hosting / Redirect Findings
PASS: https://freecptcodefinder.com/ works.

FAIL: https://www.freecptcodefinder.com/ currently fails TLS validation because the certificate does not include www.freecptcodefinder.com.

FAIL: http://freecptcodefinder.com/ currently returns 200 instead of redirecting to https://freecptcodefinder.com/.

FAIL: GitHub Pages API inspection could not be completed because the local gh CLI is not authenticated in this shell.

## Remaining Issues
- Search Console property verification and URL inspection still need authenticated GSC access.
- Fix GitHub Pages/DNS/certificate handling for https://www.freecptcodefinder.com/.
- Enforce HTTP to HTTPS redirect for the apex domain.
