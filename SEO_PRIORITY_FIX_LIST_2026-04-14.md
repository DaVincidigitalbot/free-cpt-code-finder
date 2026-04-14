# FreeCPTCodeFinder SEO Priority Fix List

## Tier 1 - Do Now

### 1. Homepage metadata and crawlability
- Status: fixed locally in `index.html`, not deployed yet
- Fixes made:
  - new title
  - meta description
  - canonical
  - robots tag
  - Open Graph tags
  - WebSite + Organization schema
  - H1 added
  - crawlable internal links added
- Why it matters: homepage is the strongest authority page and was basically wasting its equity

### 2. Generic blog titles replaced
- Status: fixed locally across 45+ articles
- Why it matters: duplicate/generic titles kill relevance and CTR

### 3. Remove Cyrionyx-first branding from ranking surfaces
- Homepage fixed locally
- Remaining work:
  - about/contact/legal pages
  - code/category pages where title still leads with CYRIONYX
- Recommendation: brand should be `Free CPT Code Finder` first, everywhere public-facing

### 4. Build/restore specialty hub pages
- Missing high-value URL observed: `/general-surgery-cpt-codes` returned 404
- This is wasted opportunity
- Create at minimum:
  - `/general-surgery-cpt-codes.html`
  - `/trauma-surgery-cpt-codes.html`
  - `/hernia-repair-cpt-codes.html`

## Tier 2 - Next

### 5. Fix outdated ventral hernia targeting
- File: `blog/guides/cpt-code-ventral-hernia-repair.html`
- Problem: meta/content still points at legacy ventral hernia code framing
- Risk: trust, accuracy, SEO quality
- Action: rewrite around current 2023+ ventral/incisional hernia codes and component separation truth

### 6. Improve code-page title format
- Current pattern: `CYRIONYX | CPT 15734 ...`
- Better pattern: `CPT 15734, Muscle Flap Trunk wRVU and Payment | Free CPT Code Finder`
- Why: cleaner keyword targeting, better CTR, less brand clutter

### 7. Add Article schema to all blog posts
- Some pages may already have it, many do not consistently
- Standardize fields:
  - headline
  - description
  - author
  - datePublished
  - dateModified
  - mainEntityOfPage

### 8. Add breadcrumbs
- Use `BreadcrumbList` for:
  - blog posts
  - code pages
  - category pages
- Why: stronger SERP structure and internal hierarchy signals

### 9. Strengthen HTML internal links from homepage and hubs
- Add direct links to:
  - top specialty hubs
  - top CPT pages
  - modifier pillars
  - global period / RVU pillars
- Keep them in raw HTML, not only JS-rendered interactions

## Tier 3 - Important But After Core Cleanup

### 10. Search Console readiness pass
- Submit sitemap
- Inspect homepage, blog hub, codes hub, top 20 guides
- Track coverage exclusions, canonical issues, duplicate title issues, soft 404s

### 11. Consolidate thin or overlapping content
- Review overlap among:
  - global period articles
  - modifier articles
  - RVU articles
- Merge if cannibalization shows up

### 12. Improve snippet CTR
- Rewrite titles/meta for pages that rank but do not get clicks
- Especially modifier and global period content

### 13. Add FAQ blocks carefully
- Best candidates:
  - modifier 25
n  - modifier 57
  - modifier 59
  - global period
  - critical care billing
- Only if content genuinely answers those questions

## Deployment / Certification Checklist
- Commit homepage SEO changes
- Commit blog title replacements
- Preview locally
- Push to GitHub Pages
- Verify live homepage source contains:
  - title
  - meta description
  - canonical
  - H1
  - JSON-LD
- Recheck 5 sample article titles live
- Resubmit sitemap / key URLs in Search Console

## Files Changed Locally Right Now
- `index.html`
- multiple files under `blog/` with title rewrites
- `SEO_CONTENT_MAP_2026-04-14.md`
- `SEO_PRIORITY_FIX_LIST_2026-04-14.md`

## Hard Recommendation
Do not publish more random blog posts until these fixes are deployed. Right now the site has enough content to win more than it is winning.