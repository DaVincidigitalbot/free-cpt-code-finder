#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://freecptcodefinder.com"
OG_IMAGE = f"{SITE}/og-image.png"
TODAY = date.today().isoformat()

PUBLIC_NO_INDEX = {
    "admin.html",
    "blog/template.html",
    "cyrioniq/index.html",
    "index-legacy.html",
    "index-v2-broken.html",
    "mockup-casebuilder.html",
    "mockup-home.html",
    "modifier_tests.html",
    "robotic_test_wrapper.html",
    "test_bilateral_logic.html",
    "test_billing.html",
    "test_confidence.html",
    "test_validation.html",
    "v2.html",
    "public/admin.html",
    "public/blog/template.html",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_if_changed(path: Path, value: str) -> bool:
    old = read(path)
    if old == value:
        return False
    path.write_text(value, encoding="utf-8")
    return True


def clean_text(value: str) -> str:
    value = re.sub(r"<script[\s\S]*?</script>", " ", value, flags=re.I)
    value = re.sub(r"<style[\s\S]*?</style>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return html.unescape(re.sub(r"\s+", " ", value)).strip()


def title_for(raw: str, fallback: str) -> str:
    match = re.search(r"<title>([\s\S]*?)</title>", raw, flags=re.I)
    return clean_text(match.group(1)) if match else fallback


def desc_for(raw: str) -> str:
    match = re.search(r'<meta\s+name=["\']description["\']\s+content=(["\'])(.*?)\1', raw, flags=re.I)
    if match:
        return html.unescape(match.group(2)).strip()
    text = clean_text(raw)
    return text[:155].strip()


def h1_for(raw: str, fallback: str) -> str:
    match = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", raw, flags=re.I)
    return clean_text(match.group(1)) if match else fallback


def canonical_from_rel(rel: str) -> str:
    if rel == "index.html":
        return f"{SITE}/"
    if rel.endswith("/index.html"):
        return f"{SITE}/{rel[:-10]}"
    return f"{SITE}/{rel}"


def canonical_for(path: Path, raw: str) -> str:
    match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', raw, flags=re.I)
    if match:
        return match.group(1)
    return canonical_from_rel(path.relative_to(ROOT).as_posix())


def insert_before_head(raw: str, block: str) -> str:
    return re.sub(r"\s*</head>", lambda _: "\n" + block.rstrip() + "\n</head>", raw, count=1, flags=re.I)


def ensure_meta_tag(raw: str, key_attr: str, key_value: str, tag: str) -> str:
    pattern = rf'<meta\s+{key_attr}=["\']{re.escape(key_value)}["\'][^>]*>'
    if re.search(pattern, raw, flags=re.I):
        return re.sub(pattern, tag, raw, count=1, flags=re.I)
    return insert_before_head(raw, tag)


def ensure_og_twitter(path: Path, raw: str) -> str:
    title = title_for(raw, h1_for(raw, "Free CPT Code Finder"))
    desc = desc_for(raw)
    url = canonical_for(path, raw)
    page_type = "article" if "/blog/" in path.as_posix() else "website"
    tags = [
        ("property", "og:title", f'<meta property="og:title" content="{html.escape(title, quote=True)}">'),
        ("property", "og:description", f'<meta property="og:description" content="{html.escape(desc, quote=True)}">'),
        ("property", "og:url", f'<meta property="og:url" content="{url}">'),
        ("property", "og:type", f'<meta property="og:type" content="{page_type}">'),
        ("property", "og:site_name", '<meta property="og:site_name" content="Free CPT Code Finder">'),
        ("property", "og:image", f'<meta property="og:image" content="{OG_IMAGE}">'),
        ("name", "twitter:card", '<meta name="twitter:card" content="summary_large_image">'),
        ("name", "twitter:title", f'<meta name="twitter:title" content="{html.escape(title, quote=True)}">'),
        ("name", "twitter:description", f'<meta name="twitter:description" content="{html.escape(desc, quote=True)}">'),
        ("name", "twitter:image", f'<meta name="twitter:image" content="{OG_IMAGE}">'),
    ]
    for attr, value, tag in tags:
        raw = ensure_meta_tag(raw, attr, value, tag)
    return raw


def remove_render_blocking_font_link(raw: str) -> str:
    return re.sub(r'\s*<link\s+href=["\']https://fonts\.googleapis\.com/[^"\']+["\']\s+rel=["\']stylesheet["\']>\s*', "\n", raw, flags=re.I)


def breadcrumb_from_path(path: Path, title: str) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"}]
    if rel.startswith("blog/"):
        items.append({"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"})
    elif rel.startswith("codes/"):
        items.append({"@type": "ListItem", "position": 2, "name": "CPT Codes", "item": f"{SITE}/codes/"})
    if rel != "index.html":
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": title[:110], "item": canonical_from_rel(rel)})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def extract_existing_jsonld(raw: str) -> list[dict]:
    out = []
    for match in re.finditer(r'<script\s+type=["\']application/ld\+json["\']>([\s\S]*?)</script>', raw, flags=re.I):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@graph"):
            out.extend(x for x in data["@graph"] if isinstance(x, dict))
        elif isinstance(data, dict):
            out.append(data)
    return out


def replace_jsonld(raw: str, graph: list[dict]) -> str:
    raw = re.sub(r'\s*<script\s+type=["\']application/ld\+json["\']>[\s\S]*?</script>', "", raw, flags=re.I)
    block = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":")) + "</script>"
    return insert_before_head(raw, block)


def ensure_code_schema(path: Path, raw: str) -> str:
    code = path.stem
    title = title_for(raw, f"CPT {code} Guide")
    desc = desc_for(raw)
    url = canonical_for(path, raw)
    graph = []
    for node in extract_existing_jsonld(raw):
        if node.get("@type") == "FAQPage":
            graph.append(node)
    graph.insert(0, {
        "@type": "MedicalWebPage",
        "name": title,
        "url": url,
        "description": desc,
        "dateModified": TODAY,
        "isPartOf": {"@type": "WebSite", "name": "Free CPT Code Finder", "url": f"{SITE}/"},
        "reviewedBy": {"@type": "Person", "name": "Graydon Stallard, DO, FACOS, FACS", "jobTitle": "Board-certified general, trauma, acute care, and critical care surgeon"},
        "about": [{"@type": "MedicalProcedure", "name": f"CPT {code} coding"}, {"@type": "Thing", "name": "work RVU"}],
    })
    graph.append(breadcrumb_from_path(path, f"CPT {code}"))
    return replace_jsonld(raw, graph)


def ensure_article_schema(path: Path, raw: str) -> str:
    title = title_for(raw, h1_for(raw, "Free CPT Code Finder Guide"))
    desc = desc_for(raw)
    url = canonical_for(path, raw)
    existing = [n for n in extract_existing_jsonld(raw) if n.get("@type") == "FAQPage"]
    graph = [{
        "@type": "Article",
        "headline": title,
        "description": desc,
        "url": url,
        "mainEntityOfPage": url,
        "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Graydon Stallard, DO, FACOS, FACS", "jobTitle": "Board-certified general, trauma, acute care, and critical care surgeon"},
        "publisher": {"@type": "Organization", "name": "Free CPT Code Finder", "url": f"{SITE}/", "logo": {"@type": "ImageObject", "url": OG_IMAGE}},
    }]
    graph.extend(existing)
    graph.append(breadcrumb_from_path(path, title))
    return replace_jsonld(raw, graph)


def ensure_webpage_schema(path: Path, raw: str) -> str:
    title = title_for(raw, h1_for(raw, "Free CPT Code Finder"))
    desc = desc_for(raw)
    url = canonical_for(path, raw)
    graph = [{
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": url,
        "isPartOf": {"@type": "WebSite", "name": "Free CPT Code Finder", "url": f"{SITE}/"},
    }]
    graph.append(breadcrumb_from_path(path, title))
    return replace_jsonld(raw, graph)


def fix_robots_meta(path: Path, raw: str) -> str:
    rel = path.relative_to(ROOT).as_posix()
    indexable = rel not in PUBLIC_NO_INDEX and not rel.startswith("_internal_archive/") and not rel.startswith("public/")
    desired = "index, follow" if indexable else "noindex, follow"
    tag = f'<meta name="robots" content="{desired}">'
    if re.search(r'<meta\s+name=["\']robots["\'][^>]*>', raw, flags=re.I):
        return re.sub(r'<meta\s+name=["\']robots["\'][^>]*>', tag, raw, count=1, flags=re.I)
    return insert_before_head(raw, tag)


LINK_BANK = [
    ("modifier", "/blog/modifiers/modifier-59-explained.html", "Modifier 59 vs XS/XE/XP/XU"),
    ("modifier", "/blog/modifiers/modifier-51-vs-59-compared.html", "Modifier 51 vs 59"),
    ("modifier", "/blog/modifiers/modifier-25-vs-57-compared.html", "Modifier 25 vs 57"),
    ("rvu", "/blog/rvu/cpt-code-wrvu-values.html", "CPT wRVU lookup guide"),
    ("rvu", "/blog/rvu/understanding-work-rvus.html", "Understanding work RVUs"),
    ("hernia", "/blog/guides/cpt-code-ventral-hernia-repair.html", "Ventral hernia CPT coding"),
    ("hernia", "/codes/49593.html", "CPT 49593 ventral hernia repair"),
    ("hernia", "/codes/49650.html", "CPT 49650 laparoscopic inguinal hernia repair"),
    ("robot", "/blog/guides/cpt-code-laparoscopic-cholecystectomy.html", "Robotic/laparoscopic coding principles"),
    ("multiple", "/blog/guides/how-to-bill-multiple-procedures-surgery.html", "Multiple procedure billing"),
    ("global", "/blog/guides/global-period-rules-money.html", "Global period rules"),
    ("laparotomy", "/blog/guides/trauma-laparotomy-cpt-guide.html", "Trauma laparotomy CPT guide"),
    ("append", "/codes/44970.html", "CPT 44970 laparoscopic appendectomy"),
    ("chole", "/codes/47563.html", "CPT 47563 lap chole with cholangiography"),
]


def related_links_for(path: Path, raw: str, limit: int = 5) -> list[tuple[str, str]]:
    text = (path.as_posix() + " " + clean_text(raw)).lower()
    scored: list[tuple[int, str, str]] = []
    for key, href, label in LINK_BANK:
        if href.endswith(path.relative_to(ROOT).as_posix()):
            continue
        score = 0
        for token in key.split():
            if token in text:
                score += 3
        if any(word in text for word in ["modifier", "59", "xs", "multiple"]):
            score += 1 if "modifier" in key or "multiple" in key else 0
        if any(word in text for word in ["wrvu", "rvu", "payment"]):
            score += 1 if key == "rvu" else 0
        if score:
            scored.append((score, href, label))
    if len(scored) < 3:
        scored.extend([(1, "/blog/rvu/cpt-code-wrvu-values.html", "CPT wRVU lookup guide"), (1, "/blog/modifiers/modifier-59-explained.html", "Modifier 59 vs XS/XE/XP/XU"), (1, "/codes/", "Browse all CPT code pages")])
    seen = set()
    out = []
    for _, href, label in sorted(scored, reverse=True):
        if href not in seen:
            seen.add(href)
            out.append((href, label))
        if len(out) >= limit:
            break
    return out


def ensure_related_section(path: Path, raw: str) -> str:
    if 'data-seo-related="true"' in raw:
        return raw
    links = related_links_for(path, raw)
    if not links:
        return raw
    items = "\n".join(f'<li><a href="{href}">{html.escape(label)}</a></li>' for href, label in links)
    section = f'''
<section class="site-card seo-related-links" data-seo-related="true">
<h2>Related Surgical Coding Questions</h2>
<ul>
{items}
</ul>
</section>
'''
    if "</main>" in raw:
        return raw.replace("</main>", section + "\n</main>", 1)
    return raw.replace("</body>", section + "\n</body>", 1)


def update_sitemap() -> None:
    skip_dirs = {
        ".git",
        "__pycache__",
        "tmp",
        "qa_artifacts",
        "seo_reports",
        "node_modules",
        "assistant-backend",
        "ads",
        "admin",
        "cyrioniq",
        "public",
        "scheduled-posts",
    }
    priority_by_prefix = {
        "index.html": 1.0,
        "codes/index.html": 0.95,
        "blog/index.html": 0.9,
        "cpt-code-for/index.html": 0.9,
        "coding-centers/": 0.88,
        "specialties/": 0.86,
        "categories/": 0.84,
        "documentation/": 0.82,
        "academy/": 0.82,
        "blog/": 0.82,
        "codes/": 0.78,
        "modifiers/": 0.78,
    }
    urls: list[tuple[str, float]] = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        if set(path.relative_to(ROOT).parts) & skip_dirs:
            continue
        if rel.startswith("_internal_archive/") or rel in PUBLIC_NO_INDEX:
            continue
        raw = read(path)
        if "noindex" in raw[:1500].lower():
            continue
        priority = 0.72
        for prefix, candidate in priority_by_prefix.items():
            if rel == prefix or rel.startswith(prefix):
                priority = candidate
                break
        urls.append((canonical_from_rel(rel), priority))
    seen = set()
    entries = []
    for url, priority in urls:
        if url in seen:
            continue
        seen.add(url)
        changefreq = "weekly" if "/blog/" in url or "/codes/" in url else "daily"
        entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority:.2f}</priority>
  </url>""")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n", encoding="utf-8")


def update_robots() -> None:
    (ROOT / "robots.txt").write_text("""User-agent: *
Allow: /
Disallow: /admin.html
Disallow: /public/
Disallow: /_internal_archive/
Sitemap: https://freecptcodefinder.com/sitemap.xml
Sitemap: https://freecptcodefinder.com/feed.xml
""", encoding="utf-8")


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("_internal_archive/"):
            continue
        raw = read(path)
        raw = fix_robots_meta(path, raw)
        if not rel.startswith("public/") and rel not in PUBLIC_NO_INDEX:
            if rel != "index.html":
                raw = remove_render_blocking_font_link(raw)
            raw = ensure_og_twitter(path, raw)
            if rel.startswith("codes/"):
                raw = ensure_webpage_schema(path, raw) if path.name == "index.html" else ensure_code_schema(path, raw)
                if path.name != "index.html":
                    raw = ensure_related_section(path, raw)
            elif rel.startswith("blog/") and path.name != "template.html":
                raw = ensure_article_schema(path, raw)
                if path.name != "index.html":
                    raw = ensure_related_section(path, raw)
        if write_if_changed(path, raw):
            changed += 1
    update_sitemap()
    update_robots()
    print(f"SEO enhanced {changed} HTML files; sitemap.xml and robots.txt regenerated.")


if __name__ == "__main__":
    main()
