#!/usr/bin/env python3
"""Audit and repair musculoskeletal soft tissue tumor CPT production data."""

from __future__ import annotations

import csv
import html
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

from soft_tissue_tumor_source import (
    SOFT_TISSUE_TUMOR_CODES,
    SOURCE_FILE,
    SOURCE_NAME,
    SOURCE_URL,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "soft-tissue-tumor-audit-2026-07-09"
CMS_PATH = ROOT / SOURCE_FILE
SNAPSHOT_PATH = ROOT / "scripts" / "soft_tissue_tumor_cms_snapshot.json"

CMS_FIELDS = {
    "code": 0,
    "short_description": 2,
    "work_rvu": 5,
    "non_facility_pe_rvu": 6,
    "facility_pe_rvu": 8,
    "mp_rvu": 10,
    "non_facility_total_rvu": 11,
    "facility_total_rvu": 12,
    "global_period": 14,
    "multiple_procedure_indicator": 18,
    "bilateral_indicator": 19,
    "assistant_indicator": 20,
    "cosurgery_indicator": 21,
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cms_rows():
    if not CMS_PATH.exists() and SNAPSHOT_PATH.exists():
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        return {
            code: [
                code,
                "",
                data["cms_short_description"],
                "",
                "",
                str(data["work_rvu"]),
                str(data["pe_rvu"]),
                "",
                str(data["facility_pe_rvu"]),
                "",
                str(data["mp_rvu"]),
                str(data["total_rvu"]),
                str(data["facility_total_rvu"]),
                "",
                str(data["global_period"]),
                "",
                "",
                "",
                str(data["multiple_procedure_indicator"]),
                "1" if data["bilateral_eligible"] else "0",
                str(data["assistant_indicator"]),
                str(data["cosurgery_indicator"]),
            ]
            for code, data in snapshot.items()
        }
    rows = {}
    with CMS_PATH.open(newline="", encoding="latin1") as f:
        for row in csv.reader(f):
            if not row or len(row) < 22:
                continue
            code = row[CMS_FIELDS["code"]]
            if code in SOFT_TISSUE_TUMOR_CODES:
                rows[code] = row
    return rows


def as_float(value: str) -> float:
    try:
        return round(float(value), 2)
    except ValueError:
        return 0.0


def as_global(value: str):
    return value if value == "ZZZ" else int(value or 0)


def specialty_for(region: str) -> str:
    if region in {"Neck / thorax", "Neck / anterior thorax"}:
        return "ent"
    if region in {"Shoulder", "Upper arm / elbow", "Forearm / wrist", "Hand / finger", "Pelvis / hip", "Thigh / knee", "Leg / ankle", "Foot / toe"}:
        return "orthopedic_surgery"
    return "general_surgery"


def modifiers_for(region: str, cms: dict) -> list[str]:
    if cms["bilateral_eligible"] is not True:
        return []
    if region == "Hand / finger":
        return ["-F1 to -F0", "-LT", "-RT"]
    if region == "Foot / toe":
        return ["-TA to -T9", "-LT", "-RT"]
    return ["-LT", "-RT"]


def cms_payload(row):
    gp = as_global(row[CMS_FIELDS["global_period"]])
    bilateral = row[CMS_FIELDS["bilateral_indicator"]] == "1"
    assistant = row[CMS_FIELDS["assistant_indicator"]] in {"1", "2"}
    cosurgeon = row[CMS_FIELDS["cosurgery_indicator"]] == "1"
    return {
        "cms_short_description": row[CMS_FIELDS["short_description"]],
        "work_rvu": as_float(row[CMS_FIELDS["work_rvu"]]),
        "pe_rvu": as_float(row[CMS_FIELDS["non_facility_pe_rvu"]]),
        "facility_pe_rvu": as_float(row[CMS_FIELDS["facility_pe_rvu"]]),
        "mp_rvu": as_float(row[CMS_FIELDS["mp_rvu"]]),
        "total_rvu": as_float(row[CMS_FIELDS["non_facility_total_rvu"]]),
        "facility_total_rvu": as_float(row[CMS_FIELDS["facility_total_rvu"]]),
        "global_period_days": gp,
        "global_period": gp,
        "multiple_procedure_indicator": row[CMS_FIELDS["multiple_procedure_indicator"]],
        "bilateral_eligible": bilateral,
        "laterality_applicable": bilateral,
        "assistant_allowed": assistant,
        "assistant_indicator": row[CMS_FIELDS["assistant_indicator"]],
        "cosurgeon_eligible": cosurgeon,
        "cosurgery_indicator": row[CMS_FIELDS["cosurgery_indicator"]],
    }


def expected_code_record(code, source, cms):
    region = source["region"]
    record = {
        "code": code,
        "description": source["descriptor"],
        "category": "Surgery",
        "subcategory": "Musculoskeletal Soft Tissue Tumor",
        "specialty": specialty_for(region),
        "code_family": "musculoskeletal_soft_tissue_tumor",
        "hierarchy_tier": 2 if source["resection"] == "radical resection" else 3,
        "addon_code": False,
        "estimated": False,
        "typical_modifiers": modifiers_for(region, cms),
        "inclusive_of": [],
        "never_primary_with": [],
        "soft_tissue_tumor": {
            "body_region": region,
            "depth_classification": source["depth"],
            "size_category": source["size"],
            "resection_type": source["resection"],
            "source": SOURCE_NAME,
            "source_url": SOURCE_URL,
            "cms_short_description": cms["cms_short_description"],
        },
        "search_terms": search_terms(code, source),
        "wrvu_source": SOURCE_NAME,
        "wrvu_source_file": Path(SOURCE_FILE).name,
        "wrvu_source_url": SOURCE_URL,
    }
    record.update({k: cms[k] for k in ["work_rvu", "pe_rvu", "facility_pe_rvu", "mp_rvu", "total_rvu", "facility_total_rvu", "global_period_days", "bilateral_eligible", "assistant_allowed", "cosurgeon_eligible"]})
    return record


def expected_modifier_rule(code, source, cms):
    return {
        "mod51_exempt": False,
        "addon_code": False,
        "bilateral_eligible": cms["bilateral_eligible"],
        "laterality_applicable": cms["laterality_applicable"],
        "bilateral_method": "LT/RT or modifier 50" if cms["bilateral_eligible"] else None,
        "global_period": cms["global_period"],
        "assistant_allowed": cms["assistant_allowed"],
        "cosurgeon_eligible": cms["cosurgeon_eligible"],
        "inherently_bilateral": False,
        "distinct_procedure_class": "musculoskeletal_soft_tissue_tumor",
        "category": "biopsy" if source["resection"] == "biopsy" else "excision",
        "inclusive_of": [],
        "never_primary_with": [],
        "specialty_bundle_rules": {"musculoskeletal_soft_tissue_tumor": {"always_with": [], "never_with": []}},
        "payer_notes": {
            "medicare": f"CMS global period {cms['global_period']}; multiple-procedure indicator {cms['multiple_procedure_indicator']}",
            "commercial": "Verify payer-specific soft tissue tumor documentation, size, depth, and laterality rules.",
        },
        "x_modifier_eligible": True,
        "hierarchy_tier": 2 if source["resection"] == "radical resection" else 3,
        "soft_tissue_tumor": {
            "body_region": source["region"],
            "depth_classification": source["depth"],
            "size_category": source["size"],
            "resection_type": source["resection"],
        },
    }


def search_terms(code, source):
    region = source["region"].lower().replace(" / ", " ")
    base = [
        "soft tissue tumor", "soft tissue mass", "soft tissue lesion", "lipoma",
        "sarcoma", "subcutaneous mass", "deep soft tissue tumor", "musculoskeletal tumor",
        region, source["depth"], source["size"], source["resection"],
        f"cpt {code}", f"{code} cpt",
    ]
    return sorted({term for term in base if term and term != "not size-based"})


def code_page(code, rec):
    desc = rec["description"]
    meta = rec["soft_tissue_tumor"]
    gp = rec["global_period_days"]
    mods = ", ".join(rec["typical_modifiers"]) if rec["typical_modifiers"] else "None typically required"
    title = f"CPT {code}: {desc} | FreeCPTCodeFinder.com"
    related = "\n".join(
        f'<a href="/codes/{c}.html" class="site-card related-inline"><strong class="inline-code-link">CPT {c}</strong> — {html.escape(SOFT_TISSUE_TUMOR_CODES[c]["descriptor"][:120])}</a>'
        for c in SOFT_TISSUE_TUMOR_CODES
        if c != code and SOFT_TISSUE_TUMOR_CODES[c]["region"] == meta["body_region"]
    )
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="CPT {code} — {html.escape(desc)}. Work RVU: {rec['work_rvu']:.2f}; total RVU: {rec['total_rvu']:.2f}; global period: {gp}.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://freecptcodefinder.com/codes/{code}.html">
<link rel="icon" type="image/png" href="/favicon.png">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NPFGH437ZS"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-NPFGH437ZS');</script>
<link rel="stylesheet" href="../styles/site-theme.css">
<script defer src="../js/site-chrome.js"></script>
</head>
<body>
<div class="site-shell">
<div class="site-page" data-site-header></div>
<main class="site-content-wrap site-richtext">
<section class="hero site-section"><div class="container">
<h1>CPT {code}</h1>
<p class="last-updated">Last reviewed: {date.today().strftime('%B %-d, %Y')}</p>
<p>{html.escape(desc)}</p>
</div></section>
<div class="container">
<div class="rvu-card">
<div><span>Work RVU</span><strong>{rec['work_rvu']:.2f}</strong></div>
<div><span>Total RVU</span><strong>{rec['total_rvu']:.2f}</strong></div>
<div><span>Global</span><strong>{gp}</strong></div>
</div>
<h2>Soft Tissue Tumor Classification</h2>
<ul>
<li><strong>Body region:</strong> {html.escape(meta['body_region'])}</li>
<li><strong>Depth:</strong> {html.escape(meta['depth_classification'])}</li>
<li><strong>Size category:</strong> {html.escape(meta['size_category'])}</li>
<li><strong>Procedure type:</strong> {html.escape(meta['resection_type'])}</li>
<li><strong>Laterality:</strong> {'Applicable' if rec['bilateral_eligible'] else 'Not applicable'}</li>
</ul>
<h2>ClaimIQ Checks</h2>
<ul>
<li>Descriptor, size threshold, depth classification, and body region are locked to the musculoskeletal soft tissue tumor source table.</li>
<li>Assistant-at-surgery allowed: {'yes' if rec['assistant_allowed'] else 'no'}.</li>
<li>Co-surgery eligible: {'yes' if rec['cosurgeon_eligible'] else 'no'}.</li>
<li>Multiple-procedure indicator: 2; Case Builder ranks this family through the MPPR engine.</li>
</ul>
<h2>Common Modifiers</h2>
<p>{html.escape(mods)}</p>
<h2>Documentation and Coding Notes</h2>
<p>Document the exact anatomic site, tumor size, depth relative to fascia or muscle, whether the operation was simple excision versus radical resection, and laterality when applicable.</p>
<p>For multi-procedure cases, use our <a href="/">Case Builder</a> to calculate adjusted wRVUs with MPPR ranking.</p>
<h2>Related Soft Tissue Tumor Codes</h2>
{related}
</div>
</main>
<div class="site-page" data-site-footer></div>
</div>
</body></html>
'''


def update_index_specs(index_path: Path, records: dict):
    text = index_path.read_text(encoding="utf-8")
    match = re.search(r"const SPECS=(\{.*?\});\n\n// ===== STATE =====", text, re.S)
    if not match:
        raise RuntimeError("Could not locate const SPECS in index.html")
    specs = json.loads(match.group(1))
    bucket = specs.setdefault("Musculoskeletal Soft Tissue Tumor", [])
    existing = {str(row[0]): row for row in bucket}
    for code, rec in records.items():
        existing[code] = [code, rec["description"], rec["work_rvu"], rec["global_period_days"]]
    specs["Musculoskeletal Soft Tissue Tumor"] = [existing[c] for c in sorted(existing)]
    replacement = "const SPECS=" + json.dumps(specs, separators=(",", ":")) + ";\n\n// ===== STATE ====="
    index_path.write_text(text[:match.start()] + replacement + text[match.end():], encoding="utf-8")


def update_guided_flow(index_path: Path):
    text = index_path.read_text(encoding="utf-8")
    text = text.replace(
        "back:{small:['21931','Excision soft tissue lesion / lipoma, back or flank, subcutaneous <3 cm',5.40,['D17.1','L72.0']],large:['21932','Excision soft tissue lesion / lipoma, back or flank, subcutaneous 3 cm or greater',7.10,['D17.1','L72.0']]}",
        "back:{small:['21930','Excision, tumor, soft tissue of back or flank, subcutaneous; less than 3 cm',4.82,['D17.1','D21.6']],large:['21931','Excision, tumor, soft tissue of back or flank, subcutaneous; 3 cm or greater',6.71,['D17.1','D21.6']]}",
    )
    text = text.replace(
        "arm:{small:['24071','Excision soft tissue lesion / lipoma, upper arm or elbow, subcutaneous <3 cm',5.20,['D17.21','L72.0']],large:['24073','Excision soft tissue lesion / lipoma, upper arm or elbow, subcutaneous 3 cm or greater',6.90,['D17.21','L72.0']]}",
        "arm:{small:['24075','Excision, tumor, soft tissue of upper arm or elbow area, subcutaneous; less than 3 cm',4.13,['D17.21','D21.1']],large:['24071','Excision, tumor, soft tissue of upper arm or elbow area, subcutaneous; 3 cm or greater',5.56,['D17.21','D21.1']]}",
    )
    text = text.replace(
        "leg:{small:['27327','Excision soft tissue lesion / lipoma, thigh or knee area, subcutaneous <3 cm',5.60,['D17.23','L72.0']],large:['27328','Excision soft tissue lesion / lipoma, thigh or knee area, subcutaneous 3 cm or greater',7.30,['D17.23','L72.0']]}",
        "leg:{small:['27327','Excision, tumor, soft tissue of thigh or knee area, subcutaneous; less than 3 cm',3.86,['D17.23','D21.2']],large:['27337','Excision, tumor, soft tissue of thigh or knee area, subcutaneous; 3 cm or greater',5.76,['D17.23','D21.2']]}",
    )
    text = text.replace(
        "abdomen:{small:['22902','Excision soft tissue lesion / lipoma, anterior abdominal wall, subcutaneous <3 cm',5.10,['D17.1','L72.0']],large:['22903','Excision soft tissue lesion / lipoma, anterior abdominal wall, subcutaneous 3 cm or greater',6.80,['D17.1','L72.0']]}",
        "abdomen:{small:['22902','Excision, tumor, soft tissue of abdominal wall, subcutaneous; less than 3 cm',4.31,['D17.1','D21.4']],large:['22903','Excision, tumor, soft tissue of abdominal wall, subcutaneous; 3 cm or greater',6.23,['D17.1','D21.4']]}",
    )
    index_path.write_text(text, encoding="utf-8")


def update_codes_index(records: dict):
    path = ROOT / "codes" / "index.html"
    text = path.read_text(encoding="utf-8")
    for code in records:
        text = re.sub(rf'<a href="/codes/{code}\.html" class="code-card">.*?</a>\n?', "", text, flags=re.S)
    cards = "".join(
        f'<a href="/codes/{code}.html" class="code-card"><span class="cpt">{code}</span><span class="desc">{html.escape(rec["description"])}</span><span class="wrvu">{rec["work_rvu"]:.2f} wRVU</span></a>\n'
        for code, rec in sorted(records.items())
    )
    marker = '<a href="/codes/22510.html"'
    if marker in text:
        text = text.replace(marker, cards + marker, 1)
    else:
        text = text.replace('</div>\n</div></main>', cards + '</div>\n</div></main>')
    path.write_text(text, encoding="utf-8")


def update_sitemap(records: dict):
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    for code in sorted(records):
        loc = f"https://freecptcodefinder.com/codes/{code}.html"
        if loc not in text:
            text = text.replace("</urlset>", f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.78</priority>\n  </url>\n</urlset>")
    path.write_text(text, encoding="utf-8")


def update_production():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cms = {code: cms_payload(row) for code, row in cms_rows().items()}
    missing_source = sorted(set(SOFT_TISSUE_TUMOR_CODES) - set(cms))
    if missing_source:
        raise RuntimeError(f"CMS source missing expected CPTs: {missing_source}")

    cpt_path = ROOT / "cpt_database.json"
    rules_path = ROOT / "modifier_rules.json"
    cpt_db = load_json(cpt_path)
    rules = load_json(rules_path)
    before = {code: deepcopy(cpt_db.get(code)) for code in SOFT_TISSUE_TUMOR_CODES}
    records = {}
    corrections = []
    for code, source in SOFT_TISSUE_TUMOR_CODES.items():
        rec = expected_code_record(code, source, cms[code])
        records[code] = rec
        if cpt_db.get(code) != rec:
            corrections.append({"code": code, "before": cpt_db.get(code), "after": rec})
        cpt_db[code] = rec
        rules[code] = expected_modifier_rule(code, source, cms[code])
        (ROOT / "codes" / f"{code}.html").write_text(code_page(code, rec), encoding="utf-8")

    write_json(cpt_path, dict(sorted(cpt_db.items())))
    write_json(rules_path, dict(sorted(rules.items())))
    update_index_specs(ROOT / "index.html", records)
    update_guided_flow(ROOT / "index.html")
    update_codes_index(records)
    update_sitemap(records)

    report = {
        "date": str(date.today()),
        "source": SOURCE_NAME,
        "source_file": SOURCE_FILE,
        "source_url": SOURCE_URL,
        "audited_codes": sorted(SOFT_TISSUE_TUMOR_CODES),
        "correction_count": len(corrections),
        "corrections": corrections,
        "before": before,
    }
    (REPORT_DIR / "audit-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, records)
    return report


def write_markdown_report(report, records):
    lines = [
        "# Musculoskeletal Soft Tissue Tumor CPT Audit",
        "",
        f"Date: {report['date']}",
        f"Source: {report['source']} ({report['source_file']})",
        "",
        "## Audited Codes",
        "",
        "| CPT | Region | Depth | Size | Type | wRVU | Total RVU | Global | Laterality |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for code, rec in sorted(records.items()):
        meta = rec["soft_tissue_tumor"]
        lines.append(f"| {code} | {meta['body_region']} | {meta['depth_classification']} | {meta['size_category']} | {meta['resection_type']} | {rec['work_rvu']:.2f} | {rec['total_rvu']:.2f} | {rec['global_period_days']} | {'yes' if rec['bilateral_eligible'] else 'no'} |")
    lines += ["", "## Corrections", ""]
    for item in report["corrections"]:
        before = item["before"] or {}
        after = item["after"]
        lines.append(f"- {item['code']}: {before.get('description', '[missing]')} -> {after['description']}")
    (REPORT_DIR / "audit-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate():
    errors = []
    cms = {code: cms_payload(row) for code, row in cms_rows().items()}
    cpt_db = load_json(ROOT / "cpt_database.json")
    rules = load_json(ROOT / "modifier_rules.json")
    seen = set()
    for code, source in SOFT_TISSUE_TUMOR_CODES.items():
        if code in seen:
            errors.append(f"duplicate source code: {code}")
        seen.add(code)
        if code not in cms:
            errors.append(f"missing CMS row: {code}")
            continue
        expected = expected_code_record(code, source, cms[code])
        actual = cpt_db.get(code)
        if not actual:
            errors.append(f"missing cpt_database row: {code}")
            continue
        for field in ["description", "work_rvu", "total_rvu", "facility_total_rvu", "global_period_days", "bilateral_eligible", "assistant_allowed", "cosurgeon_eligible"]:
            if actual.get(field) != expected.get(field):
                errors.append(f"{code} {field} mismatch: {actual.get(field)!r} != {expected.get(field)!r}")
        actual_meta = actual.get("soft_tissue_tumor", {})
        for field in ["body_region", "depth_classification", "size_category", "resection_type"]:
            if actual_meta.get(field) != expected["soft_tissue_tumor"][field]:
                errors.append(f"{code} {field} mismatch: {actual_meta.get(field)!r} != {expected['soft_tissue_tumor'][field]!r}")
        rule = rules.get(code, {})
        if rule.get("soft_tissue_tumor") != expected_modifier_rule(code, source, cms[code])["soft_tissue_tumor"]:
            errors.append(f"{code} modifier_rules soft tissue metadata mismatch")
        page = ROOT / "codes" / f"{code}.html"
        if not page.exists():
            errors.append(f"{code} page missing")
        else:
            page_text = page.read_text(encoding="utf-8")
            if html.escape(expected["description"]) not in page_text:
                errors.append(f"{code} page descriptor mismatch")
    ordered = sorted(SOFT_TISSUE_TUMOR_CODES)
    if ordered != list(dict.fromkeys(ordered)):
        errors.append("source ordering/duplicate failure")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Validated {len(SOFT_TISSUE_TUMOR_CODES)} soft tissue tumor CPT codes against {SOURCE_NAME}.")
    return 0


def main():
    update = "--update" in sys.argv
    if update:
        report = update_production()
        print(f"Updated production data for {len(report['audited_codes'])} codes; corrections: {report['correction_count']}")
    return validate()


if __name__ == "__main__":
    raise SystemExit(main())
