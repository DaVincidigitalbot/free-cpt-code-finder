# AdSense Readiness Audit - 2026-05-17

## Verdict

FreeCPTCodeFinder.com is close, but I would not submit it to AdSense yet.

The site has the important trust pieces in place: live custom domain, indexable pages, privacy policy, terms, legal disclaimer, editorial policy, author/about page, contact page, GA4, robots.txt, sitemap.xml, and ads.txt with the Google publisher ID.

The current approval risk is not lack of content. The risk is technical polish and crawl quality: incomplete sitemap coverage, broken HTTPS on the www host, thin/repetitive generated CPT pages, and missing AdSense site-review code.

## Must Fix Before Submission

1. Fix https://www.freecptcodefinder.com/
   - Current result: HTTPS fails with certificate mismatch.
   - http://www.freecptcodefinder.com/ redirects/serves, but HTTPS www does not validate.
   - AdSense and Google quality review should see one clean canonical host.
   - Action: fix GitHub Pages custom domain / DNS / certificate handling so www redirects cleanly to https://freecptcodefinder.com/, or remove the broken www DNS path.

2. Expand sitemap.xml
   - Current sitemap has 31 URLs.
   - Repo has 678 tracked CPT code pages and 53 blog pages, plus core pages.
   - Action: regenerate sitemap from tracked public HTML pages, excluding internal/admin/template/archive files.
   - Priority pages: homepage, /codes/, all tracked /codes/*.html, /blog/, all tracked blog articles, author/about/contact/legal/privacy/terms/editorial policy.

3. Add the AdSense review script to the live site
   - ads.txt exists and is live:
     google.com, pub-3385830962144023, DIRECT, f08c47fec0942fa0
   - No live adsbygoogle / AdSense account script is currently present in index.html.
   - Action: when ready to submit, add the AdSense script in head using publisher ID ca-pub-3385830962144023.

4. Clean generated thin-page risk
   - Many CPT pages are only around 220-230 words.
   - They are useful, but they are templated enough that AdSense may see them as low-value if the crawl hits mostly those pages.
   - Action: before submission, enrich the highest-traffic 50-100 CPT pages with more distinctive clinical/coding content:
     - when the code is used
     - common documentation trap
     - paired ICD-10 examples
     - modifier caveats
     - neighboring codes to compare
     - source/review note

5. Add visible last reviewed dates to core blog and trust pages
   - Many blog pages do not show a review/update date.
   - Action: add Last reviewed: May 2026 or specific dates to blog articles and key trust pages.

## Should Fix Soon

1. Improve generic legal-page titles
   - privacy.html and terms.html both use generic title: Free CPT Code Finder.com.
   - Action: change to specific titles:
     - Privacy Policy | Free CPT Code Finder
     - Terms of Use | Free CPT Code Finder

2. Verify internal links from index pages
   - Local scan found broken internal hrefs in tracked/untracked index files, mostly category index references and CPT links in codes/index.html.
   - Action: run a live/internal link audit after sitemap regeneration and either create missing pages or remove links.

3. Remove or ignore untracked duplicate public/ tree
   - Local repo contains an untracked public/ copy of many pages.
   - It is not currently served live and not tracked by git, but it makes audits noisy.
   - Action: archive or delete only after confirming it is not used by any build/deploy workflow.

4. Consider a small cookie/consent banner only if required by the account/legal setup
   - Privacy policy already discloses GA4 and AdSense cookies.
   - This is not the top approval blocker, but it may matter depending on traffic geography and consent requirements.

## Good Signs

- https://freecptcodefinder.com/ returns 200.
- ads.txt returns 200 and is correctly formatted for Google.
- robots.txt allows crawling and points to sitemap.
- Privacy, terms, legal, contact, about, author, and editorial policy pages are live.
- All checked core pages return 200.
- Site has real niche utility and clear medical/coding purpose.
- Homepage has trust language and author credentials.

## Submission Order

1. Fix www HTTPS/canonical behavior.
2. Regenerate and deploy full sitemap.
3. Fix titles/review dates on legal/blog pages.
4. Enrich the top 50-100 CPT pages most likely to be crawled.
5. Add AdSense review script.
6. Submit site in AdSense.
7. Watch AdSense Site > Policy center and ads.txt status for several days.

## Current Status

Not ready today. Realistically ready after one focused cleanup pass.
