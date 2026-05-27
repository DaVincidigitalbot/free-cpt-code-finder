#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://freecptcodefinder.com"
REPORT_DIR = ROOT / "seo_reports"
REPORT_DIR.mkdir(exist_ok=True)
TODAY = dt.date.today().isoformat()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def text_only(raw: str) -> str:
    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return html.unescape(re.sub(r"\s+", " ", raw)).strip()


def public_html_files() -> list[Path]:
    out = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT).as_posix()
        if any(part in path.parts for part in [".git", "__pycache__"]):
            continue
        if rel.startswith(("public/", "_internal_archive/", "assistant-backend/node_modules/")):
            continue
        if rel in {
            "admin.html",
            "blog/template.html",
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
            "cyrioniq/index.html",
        }:
            continue
        out.append(path)
    return sorted(out)


def canonical_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return f"{SITE}/"
    if rel.endswith("/index.html"):
        return f"{SITE}/{rel[:-10]}"
    return f"{SITE}/{rel}"


def sitemap_urls() -> list[str]:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in root.findall(".//sm:loc", ns) if loc.text]


def audit_local_metadata() -> dict:
    sitemap = set(sitemap_urls())
    problems: list[dict] = []
    title_seen: dict[str, list[str]] = {}
    desc_seen: dict[str, list[str]] = {}
    for path in public_html_files():
        rel = path.relative_to(ROOT).as_posix()
        raw = read(path)
        title = re.search(r"<title>([\s\S]*?)</title>", raw, flags=re.I)
        desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)', raw, flags=re.I)
        canonical = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', raw, flags=re.I)
        robots = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)', raw, flags=re.I)
        h1 = re.search(r"<h1\b", raw, flags=re.I)
        url = canonical_for(path)
        if robots and "noindex" in robots.group(1).lower() and url in sitemap:
            problems.append({"severity": "error", "page": rel, "issue": "noindex page included in sitemap"})
        if not title:
            problems.append({"severity": "error", "page": rel, "issue": "missing title"})
        else:
            title_seen.setdefault(text_only(title.group(1)), []).append(rel)
        if not desc:
            problems.append({"severity": "warning", "page": rel, "issue": "missing meta description"})
        else:
            desc_seen.setdefault(desc.group(1).strip(), []).append(rel)
        if not canonical:
            problems.append({"severity": "error", "page": rel, "issue": "missing canonical"})
        elif canonical.group(1) != url:
            problems.append({"severity": "warning", "page": rel, "issue": f"canonical mismatch: {canonical.group(1)} expected {url}"})
        if not h1:
            problems.append({"severity": "warning", "page": rel, "issue": "missing H1"})
        if 'property="og:title"' not in raw:
            problems.append({"severity": "warning", "page": rel, "issue": "missing OpenGraph title"})
        if 'name="twitter:card"' not in raw:
            problems.append({"severity": "warning", "page": rel, "issue": "missing Twitter card"})
        if rel.startswith(("codes/", "blog/")) and "BreadcrumbList" not in raw:
            problems.append({"severity": "warning", "page": rel, "issue": "missing breadcrumb schema"})
    for title, pages in title_seen.items():
        if title and len(pages) > 1:
            problems.append({"severity": "warning", "page": ", ".join(pages[:5]), "issue": f"duplicate title across {len(pages)} pages: {title[:90]}"})
    for desc, pages in desc_seen.items():
        if desc and len(pages) > 1:
            problems.append({"severity": "warning", "page": ", ".join(pages[:5]), "issue": f"duplicate description across {len(pages)} pages"})
    return {
        "public_html_count": len(public_html_files()),
        "sitemap_url_count": len(sitemap),
        "problems": problems,
    }


def audit_internal_links(limit_pages: int | None = None) -> list[dict]:
    files = public_html_files()
    if limit_pages:
        files = files[:limit_pages]
    dead = []
    for path in files:
        raw = read(path)
        for href in re.findall(r'href=["\']([^"\']+)["\']', raw, flags=re.I):
            if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:")):
                continue
            target_path = href.split("#")[0]
            if not target_path:
                continue
            if target_path.startswith("/"):
                local = ROOT / target_path.lstrip("/")
            else:
                local = path.parent / target_path
            if local.is_dir():
                local = local / "index.html"
            elif not local.suffix:
                local = local / "index.html"
            if not local.exists():
                dead.append({"page": path.relative_to(ROOT).as_posix(), "href": href})
    return dead


def fetch_status(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "FreeCPTCodeFinderSEOAudit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"url": url, "status": resp.status, "final_url": resp.geturl(), "bytes": len(resp.read(250000))}
    except urllib.error.HTTPError as exc:
        return {"url": url, "status": exc.code, "final_url": exc.geturl(), "error": str(exc)}
    except Exception as exc:
        return {"url": url, "status": None, "error": str(exc)}


def live_smoke_urls() -> list[str]:
    return [
        f"{SITE}/",
        f"{SITE}/blog/",
        f"{SITE}/codes/",
        f"{SITE}/codes/49593.html",
        f"{SITE}/codes/49650.html",
        f"{SITE}/codes/44970.html",
        f"{SITE}/blog/modifiers/modifier-59-explained.html",
        f"{SITE}/blog/rvu/cpt-code-wrvu-values.html",
        f"{SITE}/sitemap.xml",
        f"{SITE}/robots.txt",
    ]


def gsc_note() -> dict:
    creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    site_url = os.getenv("FREECPT_GSC_SITE_URL", "sc-domain:freecptcodefinder.com")
    if not creds or not Path(creds).exists():
        return {
            "available": False,
            "site_url": site_url,
            "note": "Search Console API not run: set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON with Search Console access. This workflow intentionally does not scrape Google rankings.",
        }
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except Exception as exc:
        return {"available": False, "site_url": site_url, "note": f"Google API libraries unavailable: {exc}"}
    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
    credentials = service_account.Credentials.from_service_account_file(creds, scopes=scopes)
    service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)
    end = dt.date.today() - dt.timedelta(days=2)
    start = end - dt.timedelta(days=28)
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": ["page", "query"],
        "rowLimit": 25000,
    }
    response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    rows = response.get("rows", [])
    low_ctr = []
    pages: dict[str, dict] = {}
    queries: dict[str, dict] = {}
    for row in rows:
        page, query = row.get("keys", ["", ""])
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        ctr = row.get("ctr", 0)
        position = row.get("position", 0)
        pages.setdefault(page, {"clicks": 0, "impressions": 0, "queries": set()})
        pages[page]["clicks"] += clicks
        pages[page]["impressions"] += impressions
        pages[page]["queries"].add(query)
        queries.setdefault(query, {"clicks": 0, "impressions": 0, "position_sum": 0, "n": 0})
        queries[query]["clicks"] += clicks
        queries[query]["impressions"] += impressions
        queries[query]["position_sum"] += position
        queries[query]["n"] += 1
        if impressions >= 20 and ctr < 0.02:
            low_ctr.append({"page": page, "query": query, "impressions": impressions, "clicks": clicks, "ctr": ctr, "position": position})
    topics = suggest_topics(queries)
    return {
        "available": True,
        "site_url": site_url,
        "date_range": {"start": start.isoformat(), "end": end.isoformat()},
        "rows": len(rows),
        "top_pages": sorted(
            [{"page": k, "clicks": v["clicks"], "impressions": v["impressions"], "query_count": len(v["queries"])} for k, v in pages.items()],
            key=lambda x: (x["clicks"], x["impressions"]),
            reverse=True,
        )[:25],
        "low_ctr": sorted(low_ctr, key=lambda x: x["impressions"], reverse=True)[:50],
        "topic_suggestions": topics,
    }


def suggest_topics(queries: dict[str, dict]) -> list[str]:
    seeds = [
        "Can CPT {code_a} and {code_b} be billed together?",
        "WRVU for {procedure}",
        "Modifier 59 vs XS for surgical procedures",
        "Robotic surgery CPT coding guide",
        "Multiple procedure modifier calculator examples",
        "Hernia CPT coding: open, laparoscopic, robotic, mesh, recurrent",
    ]
    observed = " ".join(queries.keys()).lower()
    topics = []
    if "modifier 59" in observed or "xs" in observed:
        topics.append("Modifier 59 vs XS: when surgeons should use an X modifier instead of 59")
    if "wrvu" in observed or "rvu" in observed:
        topics.append("High-yield surgical wRVU table for common general surgery CPT codes")
    if "hernia" in observed:
        topics.append("2026 ventral hernia CPT coding: defect size, recurrence, incarceration, mesh, and 15734")
    if "robot" in observed or "robotic" in observed:
        topics.append("Robotic surgery CPT coding: why robotic assistance usually does not create a separate CPT code")
    return topics + [x for x in seeds if x not in topics]


def write_report(data: dict) -> Path:
    json_path = REPORT_DIR / f"daily-seo-report-{TODAY}.json"
    md_path = REPORT_DIR / f"daily-seo-report-{TODAY}.md"
    json_path.write_text(json.dumps(data, indent=2, default=list), encoding="utf-8")
    problems = data["local"]["problems"]
    live = data["live_status"]
    gsc = data["search_console"]
    lines = [
        f"# FreeCPTCodeFinder Daily SEO Report - {TODAY}",
        "",
        "## Summary",
        f"- Public HTML pages audited: {data['local']['public_html_count']}",
        f"- Sitemap URLs: {data['local']['sitemap_url_count']}",
        f"- Metadata/schema issues: {len(problems)}",
        f"- Broken internal links: {len(data['dead_internal_links'])}",
        f"- Search Console connected: {'yes' if gsc.get('available') else 'no'}",
        "",
        "## Live Fetch Checks",
    ]
    lines += [f"- {row['url']} -> {row.get('status')} ({row.get('final_url', '')})" for row in live]
    lines += ["", "## Priority Issues"]
    if problems:
        lines += [f"- [{p['severity']}] {p['page']}: {p['issue']}" for p in problems[:75]]
    else:
        lines.append("- No local metadata/schema blockers found.")
    lines += ["", "## Search Console"]
    if gsc.get("available"):
        lines.append(f"- Date range: {gsc['date_range']['start']} to {gsc['date_range']['end']}")
        lines.append(f"- Rows analyzed: {gsc['rows']}")
        lines.append("- Low CTR pages/queries:")
        lines += [f"  - {x['query']} | {x['page']} | impressions {x['impressions']} | CTR {x['ctr']:.2%} | pos {x['position']:.1f}" for x in gsc.get("low_ctr", [])[:20]]
        lines.append("- Suggested topics:")
        lines += [f"  - {x}" for x in gsc.get("topic_suggestions", [])[:10]]
    else:
        lines.append(f"- {gsc.get('note')}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path


def main() -> None:
    data = {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "local": audit_local_metadata(),
        "dead_internal_links": audit_internal_links(),
        "live_status": [fetch_status(url) for url in live_smoke_urls()],
        "search_console": gsc_note(),
    }
    report = write_report(data)
    print(report)


if __name__ == "__main__":
    main()
