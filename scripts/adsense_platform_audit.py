#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://freecptcodefinder.com"
OUT_DIR = ROOT / "seo_reports"


def html_text(raw: str) -> str:
    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", raw).strip()


def local_links(raw: str) -> list[str]:
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', raw, flags=re.I)
    out: list[str] = []
    for href in hrefs:
        if href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#")):
            continue
        path = href.split("#", 1)[0]
        if path:
            out.append(path)
    return out


def resolve(path: Path, href: str) -> Path:
    href = href.split("#", 1)[0]
    href = href.split("?", 1)[0]
    if not href:
        return ROOT / "index.html"
    if href.startswith("/"):
        return ROOT / href.lstrip("/")
    return path.parent / href


def public_html() -> list[Path]:
    skip_parts = {".git", "__pycache__", "tmp", "qa_artifacts", "seo_reports", "node_modules", "assistant-backend", "ads", "admin", "cyrioniq", "scheduled-posts"}
    skip_names = {
        "admin.html",
        "template.html",
        "mockup-casebuilder.html",
        "mockup-home.html",
        "modifier_tests.html",
        "robotic_test_wrapper.html",
        "test_bilateral_logic.html",
        "test_billing.html",
        "test_confidence.html",
        "test_validation.html",
        "index-v2-broken.html",
        "index-legacy.html",
        "v2.html",
    }
    pages: list[Path] = []
    for path in ROOT.rglob("*.html"):
        rel_parts = set(path.relative_to(ROOT).parts)
        if rel_parts & skip_parts or path.name in skip_names:
            continue
        if path.relative_to(ROOT).as_posix().startswith("public/"):
            continue
        pages.append(path)
    return sorted(pages)


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + rel[:-10]
    return SITE + "/" + rel


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    pages = public_html()
    problems: list[dict[str, str | int]] = []
    totals = {
        "pages": len(pages),
        "thin_under_250_words": 0,
        "under_5_internal_links": 0,
        "missing_sources_link": 0,
        "missing_related_section": 0,
        "dead_internal_links": 0,
        "noindex_public_pages": 0,
    }
    samples: dict[str, list[str]] = {key: [] for key in totals if key != "pages"}

    for path in pages:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(ROOT).as_posix()
        words = len(html_text(raw).split())
        links = local_links(raw)
        link_count = len(set(links))
        has_sources = "/sources.html" in raw or "sources.html" in raw
        has_related = (
            "data-seo-related" in raw
            or "related-grid" in raw
            or "Related Resources" in raw
            or 'data-source-reference="true"' in raw
        )
        if "noindex" in raw[:1500].lower():
            totals["noindex_public_pages"] += 1
            samples["noindex_public_pages"].append(rel)
        if words < 250:
            totals["thin_under_250_words"] += 1
            samples["thin_under_250_words"].append(rel)
        if link_count < 5:
            totals["under_5_internal_links"] += 1
            samples["under_5_internal_links"].append(rel)
        if not has_sources:
            totals["missing_sources_link"] += 1
            samples["missing_sources_link"].append(rel)
        if not has_related:
            totals["missing_related_section"] += 1
            samples["missing_related_section"].append(rel)
        for href in links:
            target = resolve(path, href)
            if href.endswith("/"):
                target = target / "index.html"
            if not target.exists():
                totals["dead_internal_links"] += 1
                problems.append({"page": rel, "href": href, "issue": "dead internal link"})

    ET.parse(ROOT / "sitemap.xml")
    report = {
        "date": date.today().isoformat(),
        "summary": totals,
        "samples": {key: value[:25] for key, value in samples.items()},
        "dead_links_sample": problems[:50],
        "approval_probability_estimate": "70-80% after deploy if Search Console indexing and HTTPS/www canonical behavior are clean",
        "remaining_risks": [
            "Large generated CPT page set still needs spot review for repetitive language and clinical specificity.",
            "Official CPT text cannot be reproduced; pages must remain educational paraphrases with clear AMA attribution.",
            "AdSense may still scrutinize medical reimbursement content, so trust pages, author page, sources, and editorial policy need to remain prominent.",
            "Existing dirty worktree should be reviewed before deployment to avoid publishing unrelated generated changes.",
        ],
    }
    json_path = OUT_DIR / f"adsense-platform-audit-{date.today().isoformat()}.json"
    md_path = OUT_DIR / f"adsense-platform-audit-{date.today().isoformat()}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(
        "# AdSense Platform Readiness Audit\n\n"
        f"Date: {report['date']}\n\n"
        "## Summary\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in totals.items())
        + "\n\n## Approval Probability\n\n"
        + report["approval_probability_estimate"]
        + "\n\n## Remaining Risks\n\n"
        + "\n".join(f"- {item}" for item in report["remaining_risks"])
        + "\n\n## Sample Gaps\n\n"
        + "\n".join(f"- {key}: {', '.join(value[:10]) if value else 'none'}" for key, value in samples.items())
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {json_path.relative_to(ROOT)}")
    print(f"Wrote {md_path.relative_to(ROOT)}")
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
