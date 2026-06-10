#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://freecptcodefinder.com"
TODAY = dt.date.today().isoformat()
CF = 33.4009


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def money(value) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "$0.00"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def norm_specialty(row: dict) -> str:
    raw = row.get("specialty_id") or row.get("specialty") or row.get("category") or "uncategorized"
    raw = str(raw).replace("_", " ").replace("-", " ").strip()
    aliases = {
        "general surgery": "General Surgery",
        "bowel resection": "General Surgery",
        "cardiac electrophysiology": "Cardiac Electrophysiology",
        "orthopedic hand surgery": "Orthopedic Hand Surgery",
        "e/m": "E/M",
    }
    return aliases.get(raw.lower(), raw.title())


def page_exists(code: str) -> bool:
    return (ROOT / "codes" / f"{code}.html").exists()


def sitemap_urls() -> set[str]:
    raw = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    return set(re.findall(r"<loc>(.*?)</loc>", raw))


def code_table(codes: list[str], cpt: dict[str, dict]) -> str:
    rows = []
    for code in codes:
        row = cpt.get(code)
        if not row:
            continue
        rows.append(
            "<tr>"
            f"<td><a href=\"/codes/{code}.html\">{code}</a></td>"
            f"<td>{html.escape(str(row.get('description', '')))}</td>"
            f"<td>{row.get('work_rvu', 0)}</td>"
            f"<td>{money(row.get('estimated_medicare_payment', 0))}</td>"
            f"<td>{row.get('global_period_days', '')}</td>"
            "</tr>"
        )
    return (
        "<div class=\"table-wrap\"><table><thead><tr><th>CPT</th><th>Descriptor</th>"
        "<th>wRVU</th><th>Medicare estimate</th><th>Global</th></tr></thead><tbody>"
        + "\n".join(rows)
        + "</tbody></table></div>"
    )


def hub_page(topic: dict, cpt: dict[str, dict]) -> str:
    title = topic["title"]
    desc = topic["description"]
    url = f"{SITE}/cpt-code-for/{topic['slug']}.html"
    faq = "".join(
        f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in topic["faq"]
    )
    links = "".join(
        f"<a class=\"quick-link\" href=\"{href}\">{html.escape(label)}</a>"
        for label, href in topic.get("links", [])
    )
    tips = "".join(f"<li>{html.escape(t)}</li>" for t in topic["tips"])
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "MedicalWebPage",
                "name": title,
                "headline": title,
                "description": desc,
                "url": url,
                "datePublished": TODAY,
                "dateModified": TODAY,
                "isPartOf": {"@type": "WebSite", "name": "FreeCPTCodeFinder.com", "url": SITE + "/"},
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a},
                    }
                    for q, a in topic["faq"]
                ],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "CPT Code For", "item": SITE + "/cpt-code-for/"},
                    {"@type": "ListItem", "position": 3, "name": title, "item": url},
                ],
            },
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} | FreeCPTCodeFinder.com</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/logo-192.png">
<link rel="stylesheet" href="/styles/site-theme.css">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NPFGH437ZS"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-NPFGH437ZS');</script>
<script defer src="/js/site-chrome.js"></script>
<meta property="og:title" content="{html.escape(title)} | FreeCPTCodeFinder.com">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Free CPT Code Finder">
<meta property="og:image" content="https://freecptcodefinder.com/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(schema, separators=(',', ':'))}</script>
<style>.hub-kicker{{font-weight:700;color:var(--accent,#2563eb);text-transform:uppercase;font-size:.78rem;letter-spacing:.08em}}.hub-grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,360px);gap:24px;align-items:start}}.hub-panel{{border:1px solid var(--border,#d8e0ea);border-radius:8px;padding:16px;background:var(--panel,#fff)}}.table-wrap{{overflow:auto;margin:18px 0}}table{{width:100%;border-collapse:collapse;font-size:.92rem}}th,td{{border-bottom:1px solid var(--border,#d8e0ea);padding:8px;text-align:left;vertical-align:top}}th{{font-weight:700}}@media(max-width:860px){{.hub-grid{{grid-template-columns:1fr}}}}</style>
</head>
<body>
<div class="site-shell">
<div class="site-page" data-site-header></div>
<main class="site-content-wrap site-richtext">
<section class="hero site-section"><div class="container"><div class="breadcrumb"><a href="/">Home</a> -> <a href="/cpt-code-for/">CPT Code For</a></div><div class="hub-kicker">Procedure hub</div><h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p><div class="quick-links"><a class="quick-link" href="/">Search CPT codes</a><a class="quick-link" href="/#case-builder">Open Case Builder</a>{links}</div></div></section>
<div class="container hub-grid"><article>
<h2>Key CPT Codes</h2>
{code_table(topic['codes'], cpt)}
<h2>Coding Decision Points</h2>
<ul>{tips}</ul>
<h2>Common Documentation Gaps</h2>
<p>{html.escape(topic['documentation'])}</p>
<h2>FAQ</h2>
{faq}
</article><aside class="hub-panel"><h2>Fast Check</h2><p>Use this page to choose the likely CPT family, then confirm the exact descriptor, global period, modifier metadata, and payment estimate on the CPT page or in the Case Builder.</p><p>Educational reference only. Verify CPT, CMS, NCCI, and payer rules before billing or case logging.</p></aside></div>
</main><div class="site-page" data-site-footer></div></div>
</body>
</html>
"""


def build_dashboard(cpt: dict[str, dict], rvu: dict, mods: dict, sm: set[str], general: dict) -> dict:
    rvu_codes = rvu.get("codes", rvu) if isinstance(rvu, dict) else {}
    grouped: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for code, row in cpt.items():
        grouped[norm_specialty(row)].append((code, row))
    specialty_rows = []
    for name, rows in grouped.items():
        codes = [c for c, _ in rows]
        pages = sum(page_exists(c) for c in codes)
        rvu_rows = sum(c in rvu_codes for c in codes)
        mod_rows = sum(c in mods for c in codes)
        sm_rows = sum(f"{SITE}/codes/{c}.html" in sm for c in codes)
        payment_rows = sum(bool(cpt[c].get("estimated_medicare_payment") or cpt[c].get("total_rvu")) for c in codes)
        completeness = round((pages + rvu_rows + mod_rows + sm_rows + payment_rows) / (len(codes) * 5) * 100, 1) if codes else 100
        specialty_rows.append(
            {
                "specialty": name,
                "site_cpt_count": len(codes),
                "page_count": pages,
                "rvu_rows": rvu_rows,
                "modifier_rows": mod_rows,
                "sitemap_entries": sm_rows,
                "payment_estimates": payment_rows,
                "platform_completeness_percentage": completeness,
            }
        )
    specialty_rows.sort(key=lambda r: (-r["site_cpt_count"], r["specialty"]))
    general_ranked = sorted(general["categories"], key=lambda r: (r["coverage_percentage"], -r["missing_cpt_count"], r["category"]))
    return {
        "generated_at": TODAY,
        "notes": [
            "Site-wide specialty rows are ranked by CPT database count and platform completeness.",
            "CMS coverage counts are currently authoritative for General Surgery categories only.",
        ],
        "sitewide": {
            "total_cpt_count": len(cpt),
            "specialty_count": len(specialty_rows),
            "code_page_count": sum(page_exists(c) for c in cpt),
            "rvu_row_count": sum(c in rvu_codes for c in cpt),
            "modifier_rule_count": sum(c in mods for c in cpt),
            "sitemap_code_count": sum(f"{SITE}/codes/{c}.html" in sm for c in cpt),
        },
        "specialty_rankings": specialty_rows,
        "general_surgery_cms_coverage": general,
        "general_surgery_gap_rankings": general_ranked,
    }


def dashboard_html(data: dict) -> str:
    rows = "\n".join(
        f"<tr><td>{html.escape(r['specialty'])}</td><td>{r['site_cpt_count']}</td><td>{r['page_count']}</td><td>{r['rvu_rows']}</td><td>{r['modifier_rows']}</td><td>{r['sitemap_entries']}</td><td>{r['payment_estimates']}</td><td>{r['platform_completeness_percentage']:.1f}%</td></tr>"
        for r in data["specialty_rankings"]
    )
    gaps = "\n".join(
        f"<tr><td>{html.escape(r['category'])}</td><td>{r['cms_cpt_count']}</td><td>{r['site_cpt_count']}</td><td>{r['missing_cpt_count']}</td><td>{r['coverage_percentage']:.1f}%</td><td>{html.escape(', '.join(r['missing_cpt_codes'][:20]) or 'None')}</td></tr>"
        for r in data["general_surgery_gap_rankings"]
    )
    s = data["sitewide"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Site-Wide CPT Coverage Dashboard</title><meta name="description" content="Internal FreeCPTCodeFinder dashboard for CPT specialty rankings, coverage completeness, and General Surgery CMS gap tracking."><meta name="robots" content="noindex, nofollow"><link rel="canonical" href="{SITE}/admin/sitewide-cpt-coverage-dashboard.html"><meta property="og:title" content="Site-Wide CPT Coverage Dashboard"><meta property="og:description" content="Internal CPT coverage dashboard for FreeCPTCodeFinder."><meta name="twitter:card" content="summary"><link rel="stylesheet" href="/styles/app-mode.css"><style>.dashboard-table{{width:100%;border-collapse:collapse}}.dashboard-table th,.dashboard-table td{{border:1px solid #d9e1ea;padding:8px;vertical-align:top}}.dashboard-table th{{text-align:left;background:#f4f7fb}}.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}.kpi{{border:1px solid #d9e1ea;border-radius:8px;padding:14px;background:#fff}}.kpi strong{{display:block;font-size:1.5rem}}</style></head><body><main class="container"><nav><a href="/">FreeCPTCodeFinder</a> / Internal / Site-Wide Coverage</nav><h1>Site-Wide CPT Coverage Dashboard</h1><section class="kpis"><div class="kpi"><span>Total CPT rows</span><strong>{s['total_cpt_count']}</strong></div><div class="kpi"><span>Code pages</span><strong>{s['code_page_count']}</strong></div><div class="kpi"><span>RVU rows</span><strong>{s['rvu_row_count']}</strong></div><div class="kpi"><span>Modifier rows</span><strong>{s['modifier_rule_count']}</strong></div><div class="kpi"><span>Sitemap code URLs</span><strong>{s['sitemap_code_count']}</strong></div></section><section class="site-card"><h2>Specialty Rankings</h2><table class="dashboard-table"><thead><tr><th>Specialty</th><th>CPT rows</th><th>Pages</th><th>RVU rows</th><th>Modifier rows</th><th>Sitemap URLs</th><th>Payment estimates</th><th>Platform completeness</th></tr></thead><tbody>{rows}</tbody></table></section><section class="site-card"><h2>General Surgery CMS Gap Ranking</h2><table class="dashboard-table"><thead><tr><th>Section</th><th>CMS count</th><th>Site count</th><th>Missing</th><th>Coverage</th><th>Missing CPT codes</th></tr></thead><tbody>{gaps}</tbody></table></section></main></body></html>"""


def build_growth_report(cpt: dict[str, dict], coverage: dict) -> dict:
    observed = {
        "analytics_status": "GA4 tag is present, but no live GA4/Search Console export is checked into the repo for this run.",
        "product_signal_sources": [
            "Static CPT database and generated pages",
            "General Surgery CMS coverage dashboard",
            "Report widget QA artifacts",
            "Existing blog/coding-center inventory",
        ],
    }
    estimated_top_cpt_pages = [
        {"code": "99214", "reason": "Very high national search demand for outpatient E/M and RVU lookup."},
        {"code": "99213", "reason": "Common outpatient E/M lookup; useful for physician productivity content."},
        {"code": "44970", "reason": "High-intent appendectomy search and strong new General Surgery coverage."},
        {"code": "47562", "reason": "Common lap chole search with prior payment/RVU validation."},
        {"code": "44140", "reason": "Colon resection anchor code; strong Case Builder use case."},
        {"code": "44204", "reason": "Laparoscopic colectomy anchor code; recently corrected and validated."},
        {"code": "49020", "reason": "High-value ACS abscess drainage code with new Phase C page."},
        {"code": "49002", "reason": "Open abdomen/reopening laparotomy query intent."},
        {"code": "43775", "reason": "Sleeve gastrectomy has strong bariatric search demand."},
        {"code": "49591", "reason": "Ventral hernia repair search demand and coding complexity."},
    ]
    content_hubs = [
        "Appendectomy",
        "Open abdomen",
        "Intra-abdominal abscess drainage",
        "Foreign body removal",
        "Emergency general surgery",
        "Damage control surgery",
        "Modifier 22",
        "Modifier 57",
        "Trauma surgery coding",
    ]
    roadmap = [
        {"rank": 1, "item": "Appendectomy + lap chole + abscess/open abdomen hub cluster", "traffic_impact": "High", "why": "High-volume procedure-name searches plus strong completed CPT coverage."},
        {"rank": 2, "item": "Modifier 22 and Modifier 57 surgical guides", "traffic_impact": "High", "why": "Broad evergreen search intent; directly improves surgeon documentation behavior."},
        {"rank": 3, "item": "Emergency general surgery and damage-control surgery hubs", "traffic_impact": "Medium-high", "why": "Lower volume than appy/chole but strong topical authority and professional relevance."},
        {"rank": 4, "item": "Internal links from CPT pages to hubs and coding centers", "traffic_impact": "Medium-high", "why": "Moves users from single-code lookup into multi-page sessions."},
        {"rank": 5, "item": "Analytics export pipeline for GA4/Search Console + search/case events", "traffic_impact": "Medium", "why": "Not directly indexable, but stops us from guessing priorities."},
        {"rank": 6, "item": "Future CPT audits: Breast, Soft Tissue, Endocrine", "traffic_impact": "Medium", "why": "Coverage gains matter, but content/hub acquisition is likely the larger near-term traffic lever after 88.4% General Surgery coverage."},
    ]
    future = {
        "Breast Surgery": {"current_site_count": 9, "estimated_cms_count": 34, "estimated_missing": 25, "coverage_gain_points": 3.6, "effort": "Medium"},
        "Soft Tissue Surgery": {"current_site_count": 79, "estimated_cms_count": 116, "estimated_missing": 37, "coverage_gain_points": 5.3, "effort": "Medium-high"},
        "Endocrine Surgery": {"current_site_count": 19, "estimated_cms_count": 24, "estimated_missing": 5, "coverage_gain_points": 0.7, "effort": "Low-medium"},
    }
    return {
        "generated_at": TODAY,
        "observed_data": observed,
        "estimated_highest_traffic_cpt_pages": estimated_top_cpt_pages,
        "estimated_highest_traffic_specialties": [
            "E/M",
            "General Surgery",
            "Orthopedic Hand Surgery",
            "Cardiac Electrophysiology",
            "Critical Care / ACS",
        ],
        "estimated_most_searched_cpt_codes": ["99214", "99213", "44970", "47562", "43775", "49591", "44140", "44204", "49020", "10060"],
        "estimated_most_searched_procedures": [
            "appendectomy",
            "laparoscopic cholecystectomy",
            "ventral hernia repair",
            "colon resection",
            "abscess drainage",
            "open abdomen",
            "sleeve gastrectomy",
            "critical care billing",
        ],
        "estimated_most_used_case_builder_combinations": [
            "44140 + 44139",
            "47562 + 47550",
            "44204 alone",
            "49020 alone",
            "44970 alone",
            "11042 + 11045",
        ],
        "high_volume_searches_not_fully_targeted": [
            "open abdomen CPT code",
            "damage control laparotomy CPT",
            "intra-abdominal abscess drainage CPT",
            "foreign body removal CPT",
            "modifier 22 surgery documentation",
            "modifier 57 decision for surgery",
        ],
        "new_content_hubs": content_hubs,
        "prioritized_roadmap": roadmap,
        "future_audit_preparation": future,
        "strategic_recommendation": "Near-term growth is more likely to come from content hubs, internal linking, and analytics-driven user acquisition than from additional CPT coverage alone. Coverage is now strong enough in core General Surgery to support SEO authority; the bottleneck is targeted content and telemetry.",
    }


def report_md(report: dict) -> str:
    lines = [
        "# Platform Quality + Growth Report",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Data Status",
        f"- {report['observed_data']['analytics_status']}",
        "- Rankings below are estimated from site inventory, search intent, and product signals until GA4/Search Console exports are connected.",
        "",
        "## Estimated Highest-Traffic CPT Pages",
    ]
    lines += [f"- {x['code']}: {x['reason']}" for x in report["estimated_highest_traffic_cpt_pages"]]
    lines += ["", "## Estimated Highest-Traffic Specialties"]
    lines += [f"- {x}" for x in report["estimated_highest_traffic_specialties"]]
    lines += ["", "## Most-Searched Code/Procedure Targets"]
    lines += [f"- CPT codes: {', '.join(report['estimated_most_searched_cpt_codes'])}"]
    lines += [f"- Procedures: {', '.join(report['estimated_most_searched_procedures'])}"]
    lines += ["", "## Most-Used Case Builder Combinations To Track"]
    lines += [f"- {x}" for x in report["estimated_most_used_case_builder_combinations"]]
    lines += ["", "## New Content Hubs"]
    lines += [f"- {x}" for x in report["new_content_hubs"]]
    lines += ["", "## Prioritized Roadmap"]
    lines += [f"{x['rank']}. {x['item']} — {x['traffic_impact']}: {x['why']}" for x in report["prioritized_roadmap"]]
    lines += ["", "## Future CPT Audit Prep"]
    for name, item in report["future_audit_preparation"].items():
        lines.append(f"- {name}: estimated missing {item['estimated_missing']} / CMS {item['estimated_cms_count']}; effort {item['effort']}; expected General Surgery coverage gain ~{item['coverage_gain_points']} pts")
    lines += ["", "## Recommendation", report["strategic_recommendation"], ""]
    return "\n".join(lines)


def update_sitemap(urls: list[str]) -> None:
    path = ROOT / "sitemap.xml"
    raw = path.read_text(encoding="utf-8")
    additions = []
    for url in urls:
        if f"<loc>{url}</loc>" not in raw:
            additions.append(f"<url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>")
    if additions:
        raw = raw.replace("</urlset>", "\n" + "\n".join(additions) + "\n</urlset>")
        path.write_text(raw, encoding="utf-8")


def update_index(hubs: list[dict]) -> None:
    path = ROOT / "cpt-code-for" / "index.html"
    raw = path.read_text(encoding="utf-8")
    links = "\n".join(
        f'                <a href="/cpt-code-for/{h["slug"]}.html" class="site-card related-inline"><strong class="inline-code-link">{html.escape(h["title"])}</strong><span style="display:block;margin-top:6px;color:var(--ink2);font-weight:400">{html.escape(h["description"])}</span></a>'
        for h in hubs
    )
    marker = '<a href="/blog/guides/cpt-code-appendectomy.html" class="site-card related-inline">'
    if "/cpt-code-for/open-abdomen.html" not in raw and marker in raw:
        raw = raw.replace(marker, links + "\n" + "                " + marker, 1)
    path.write_text(raw, encoding="utf-8")


def main() -> None:
    cpt = load_json("cpt_database.json")
    rvu = load_json("rvu_database.json")
    mods = load_json("modifier_rules.json")
    general = load_json("audit_reports/general_surgery_coverage_dashboard.json")
    sm = sitemap_urls()

    hubs = [
        {"slug": "appendectomy", "title": "CPT Code for Appendectomy", "description": "Appendectomy CPT guide for open, ruptured, laparoscopic, interval, and unlisted appendix procedures.", "codes": ["44900", "44950", "44955", "44960", "44970", "44979"], "tips": ["Separate open appendectomy, ruptured appendix with abscess/peritonitis, and laparoscopic appendectomy.", "Do not use the ruptured code just because the appendix is inflamed; the note must support abscess or generalized peritonitis.", "Incidental appendectomy has separate coding logic when performed during another operation."], "documentation": "The op note should state approach, perforation status, abscess or generalized peritonitis when present, contamination, specimen removal, and whether appendectomy was incidental or the primary operation.", "faq": [("What is the CPT code for laparoscopic appendectomy?", "CPT 44970 is the standard laparoscopic appendectomy code."), ("When is 44960 used?", "Use 44960 for open appendectomy for ruptured appendix with abscess or generalized peritonitis when documented.")], "links": [("Appendectomy guide", "/blog/guides/cpt-code-appendectomy.html")]},
        {"slug": "open-abdomen", "title": "CPT Code for Open Abdomen", "description": "Open abdomen and recent laparotomy CPT guide with temporary closure, re-exploration, wound dehiscence, and negative pressure wound therapy context.", "codes": ["49000", "49002", "49014", "49900", "49999", "97605", "97606"], "tips": ["Reopening a recent laparotomy is not the same as the initial exploratory laparotomy.", "Temporary abdominal closure may require unlisted abdomen code or wound therapy codes depending on payer and documentation.", "Document staged return, source control, washout, packing, temporary closure method, and planned re-exploration."], "documentation": "The note should name the indication for re-entry, whether the abdomen was intentionally left open, type of temporary closure, wound dimensions for NPWT, and whether bowel or organ repair was separately performed.", "faq": [("Is there one CPT code for open abdomen?", "No. Coding depends on whether the work is exploratory laparotomy, reopening a recent laparotomy, wound dehiscence repair, temporary closure, or NPWT."), ("Does open abdomen closure bundle everything?", "No. Separately documented organ repair, bowel work, or drainage may change the code set.")], "links": [("Trauma laparotomy guide", "/blog/guides/trauma-laparotomy-cpt-guide.html")]},
        {"slug": "intra-abdominal-abscess-drainage", "title": "CPT Code for Intra-Abdominal Abscess Drainage", "description": "CPT guide for open, pelvic, peritoneal, retroperitoneal, postoperative, and image-guided intra-abdominal abscess drainage.", "codes": ["10060", "10061", "10180", "45000", "49020", "49040", "49405", "49406"], "tips": ["Choose by anatomic site, approach, and image guidance rather than the generic phrase abscess drainage.", "Open abdominal abscess drainage and image-guided peritoneal drainage are different CPT families.", "Postoperative wound infection I&D may route differently than intra-abdominal source control."], "documentation": "Document site, approach, depth, image guidance, abscess cavity, cultures, drain placement, and whether bowel, appendix, or other organ work was performed.", "faq": [("What is CPT 49020?", "CPT 49020 describes open drainage of an abdominal abscess."), ("What is the image-guided peritoneal drainage code?", "CPT 49406 is commonly used for image-guided peritoneal or retroperitoneal fluid collection drainage.")], "links": [("Abscess drainage guide", "/blog/guides/cpt-code-abscess-drainage.html")]},
        {"slug": "foreign-body-removal", "title": "CPT Code for Foreign Body Removal", "description": "Foreign body removal CPT guide across subcutaneous, deep soft tissue, nasal, oral, eye, eyelid, extremity, and intra-thoracic sites.", "codes": ["10120", "10121", "20520", "20525", "24200", "28190", "30300", "30310", "30320", "40804", "40805", "65273", "65286", "65290", "67930", "67935", "67938"], "tips": ["Site and depth drive the code more than the words foreign body removal.", "Simple subcutaneous removal is not the same as deep muscle/tendon sheath removal.", "Eye, eyelid, oral, nasal, and thoracic foreign body work have separate CPT families."], "documentation": "The note should specify location, depth, incision vs non-incision technique, imaging use, complexity, closure, and whether repair of associated wound was performed.", "faq": [("What is CPT 10120?", "CPT 10120 is incision and removal of a subcutaneous foreign body, simple."), ("When does foreign body removal become complicated?", "Depth, dissection, difficult localization, adjacent structure repair, or extensive closure may support a more specific or complex code.")], "links": []},
        {"slug": "emergency-general-surgery", "title": "Emergency General Surgery CPT Coding", "description": "Emergency general surgery coding hub for appendicitis, cholecystitis, bowel obstruction, perforation, abscess, sepsis source control, and reoperation workflows.", "codes": ["44970", "47562", "44120", "44140", "49000", "49002", "49020", "49040", "44602", "44603", "32551"], "tips": ["EGS cases often combine a primary source-control operation with add-on, staged, or modifier-sensitive work.", "Case Builder should be used for multi-procedure RVU and MPPR review.", "The diagnosis does not choose the CPT code; the documented operative work does."], "documentation": "Capture source control, contamination, organ resection or repair, drains, re-exploration intent, wound class, assistant/co-surgeon roles, and unusual difficulty when relevant.", "faq": [("What is the key EGS coding mistake?", "Using a generic exploratory laparotomy code when the note supports a more specific bowel, appendix, gallbladder, drainage, or repair code."), ("When should modifier 57 matter?", "When the E/M decision for urgent or emergent surgery occurs the day before or day of a major procedure.")], "links": [("Browse CPT codes", "/codes/"), ("Case Builder", "/#case-builder")]},
        {"slug": "damage-control-surgery", "title": "Damage Control Surgery CPT Coding", "description": "Damage control surgery CPT hub for trauma laparotomy, bowel control, open abdomen, re-exploration, liver hemorrhage, thoracic source control, and staged returns.", "codes": ["49000", "49002", "49014", "44120", "44140", "44602", "44603", "44604", "44605", "47350", "32151", "32551"], "tips": ["Damage control cases are often staged; modifier 58/78 logic depends on the plan and global period context.", "Temporary closure, packing, bowel discontinuity, and planned return need explicit documentation.", "Unusual time, contamination, adhesions, hemorrhage, or physiologic instability may support modifier 22 only when documented in detail."], "documentation": "State damage-control intent, physiologic instability, abbreviated operation, packing, vascular/bowel control, temporary closure, reoperation plan, and objective difficulty.", "faq": [("Is damage control laparotomy a single CPT code?", "No. Code the actual operative work: exploration, bowel repair/resection, hemorrhage control, drainage, temporary closure, and staged return logic."), ("Which modifier often matters?", "Modifier 58 or 78 may matter for staged or unplanned returns; modifier 22 may apply only with strong documentation.")], "links": [("Trauma laparotomy guide", "/blog/guides/trauma-laparotomy-cpt-guide.html")]},
        {"slug": "modifier-22", "title": "Modifier 22 for Surgery", "description": "Modifier 22 guide for increased procedural services, documentation thresholds, examples, and when not to append it.", "codes": ["44140", "44204", "47562", "44970", "49020", "43775"], "tips": ["Modifier 22 needs objective extra work, not a routine difficult case.", "Document why the work was substantially greater, how much extra time was required, and what anatomic or clinical factors drove it.", "Do not use modifier 22 to compensate for poor code selection."], "documentation": "Use concrete details: additional time, adhesions, inflammation, distorted anatomy, reoperative field, hemorrhage, obesity/body habitus, contamination, or complexity beyond the descriptor.", "faq": [("Does modifier 22 automatically increase payment?", "No. It flags increased services and usually requires payer review and documentation."), ("Should modifier 22 go on add-on codes?", "Usually avoid reflexive modifier 22 on add-on codes; verify payer policy and document why the add-on work itself was increased.")], "links": [("Modifier 22 explained", "/blog/modifiers/modifier-22-explained.html")]},
        {"slug": "modifier-57", "title": "Modifier 57 Decision for Surgery", "description": "Modifier 57 guide for the E/M decision for major surgery, same-day urgent operations, global period context, and common denial traps.", "codes": ["99214", "99223", "99291", "44970", "47562", "49000"], "tips": ["Modifier 57 belongs on the E/M service, not the procedure.", "It applies to the decision for major surgery, typically 90-day global procedures.", "Document the assessment, risk discussion, and decision to proceed urgently or emergently."], "documentation": "The E/M note should make the decision for surgery explicit, separate from routine preoperative H&P work, and tied to the major procedure timing.", "faq": [("What does modifier 57 mean?", "It identifies an E/M service that resulted in the decision for major surgery."), ("Is modifier 57 the same as modifier 25?", "No. Modifier 25 is for a significant separately identifiable E/M service; modifier 57 is the decision for major surgery.")], "links": [("Modifier 57 explained", "/blog/modifiers/modifier-57-explained.html"), ("Modifier 25 vs 57", "/blog/modifiers/modifier-25-vs-57-compared.html")]},
        {"slug": "trauma-surgery-coding", "title": "Trauma Surgery Coding", "description": "Trauma surgery CPT hub for penetrating wound exploration, thoracic trauma, laparotomy, bowel repair, tube thoracostomy, rib fixation, and modifier logic.", "codes": ["20100", "20101", "20103", "32151", "32551", "49000", "49020", "44120", "44140", "21811", "21812"], "tips": ["Use injury site, approach, and actual repair/resection work to choose CPT codes.", "Do not let the trauma diagnosis substitute for operative detail.", "Rib fixation add-on logic and staged reoperation modifiers require careful metadata review."], "documentation": "Document injury mechanism only as context; CPT support comes from exploration, repair, resection, drainage, tube placement, fixation levels, and staged return details.", "faq": [("What is CPT 20100?", "CPT 20100 is exploration of a penetrating wound of the neck."), ("Does trauma surgery have one CPT family?", "No. Trauma coding spans wound exploration, thoracic, abdominal, vascular, soft tissue, rib fixation, and critical care families.")], "links": [("Trauma surgery guide", "/blog/guides/cpt-code-trauma-surgery.html"), ("Trauma coding center", "/coding-centers/trauma-surgery-coding-center.html")]},
    ]

    for hub in hubs:
        (ROOT / "cpt-code-for" / f"{hub['slug']}.html").write_text(hub_page(hub, cpt), encoding="utf-8")

    dashboard = build_dashboard(cpt, rvu, mods, sm, general)
    (ROOT / "audit_reports" / "sitewide_cpt_coverage_dashboard.json").write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    (ROOT / "admin" / "sitewide-cpt-coverage-dashboard.html").write_text(dashboard_html(dashboard), encoding="utf-8")

    report = build_growth_report(cpt, general)
    (ROOT / "audit_reports" / "platform_quality_growth_2026_06_10.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ROOT / "audit_reports" / "platform_quality_growth_2026_06_10.md").write_text(report_md(report), encoding="utf-8")
    (ROOT / "audit_reports" / "future_cpt_audit_prep_2026_06_10.json").write_text(json.dumps(report["future_audit_preparation"], indent=2), encoding="utf-8")

    update_index(hubs)
    update_sitemap([f"{SITE}/cpt-code-for/{hub['slug']}.html" for hub in hubs])

    print(json.dumps({"hubs": [h["slug"] for h in hubs], "dashboard": "admin/sitewide-cpt-coverage-dashboard.html", "report": "audit_reports/platform_quality_growth_2026_06_10.md"}, indent=2))


if __name__ == "__main__":
    main()
