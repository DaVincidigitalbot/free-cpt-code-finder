#!/usr/bin/env python3
"""
Phase A General Surgery audit/import:
- Coverage dashboard
- Colorectal/ostomy/hepatobiliary/pancreatic missing-code report
- Adds missing active CMS PFS codes to FreeCPTCodeFinder local data and pages
No deploy/push behavior.
"""
from __future__ import annotations
import csv, json, re
import subprocess
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CMS = Path("/home/setup/Desktop/FreeCPTCodeFinder/tmp/abos_sports_import/rvu26c/PPRRVU2026_Jul_nonQPP.csv")
OUT = ROOT / "qa_artifacts" / "phase_a_colorectal_hpb_pancreas_2026_06_10"
CF = 33.4009
SOURCE = "CMS PFS RVU26C July 2026 non-QPP"
SOURCE_FILE = "PPRRVU2026_Jul_nonQPP.csv"
SOURCE_URL = "https://www.cms.gov/files/zip/rvu26c.zip"
TODAY = "2026-06-10"
DASHBOARD_CATEGORIES = [
    "Esophagus", "Foregut", "Stomach", "Small bowel", "Colon", "Rectum", "Appendix",
    "Hepatobiliary", "Pancreas", "Spleen", "Breast", "Hernia", "Soft tissue",
    "Trauma", "Acute Care Surgery", "Rib fixation",
]
PHASE_CATEGORIES = ["Colon", "Rectum", "Ostomy", "Hepatobiliary", "Pancreas"]

def num(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0

def int_global(value: str) -> int:
    value = str(value or "").strip().upper()
    if value in {"", "XXX", "YYY", "ZZZ"}:
        return 0
    try:
        return int(value)
    except ValueError:
        return 0

def yes_indicator(value: str) -> bool:
    return str(value).strip() in {"1", "2", "3"}

def in_range(code: str, lo: int, hi: int) -> bool:
    return lo <= int(code) <= hi

def parse_cms() -> dict[str, dict]:
    rows = {}
    with CMS.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.reader(handle):
            if not row or len(row) < 32 or not re.fullmatch(r"\d{5}", row[0] or ""):
                continue
            if row[1] != "":
                continue
            status = row[3]
            if status not in {"A", "C", "R", "T"}:
                continue
            code = row[0]
            rows[code] = {
                "code": code,
                "cms_description": row[2].strip(),
                "status": status,
                "work_rvu": num(row[5]),
                "pe_rvu": num(row[6]),
                "mp_rvu": num(row[10]),
                "total_rvu": num(row[11]),
                "facility_total_rvu": num(row[12]),
                "global_period": row[14].strip(),
                "multiple_indicator": row[18].strip(),
                "bilateral_indicator": row[19].strip(),
                "assistant_indicator": row[20].strip(),
                "cosurgeon_indicator": row[21].strip(),
                "team_indicator": row[22].strip(),
                "conversion_factor": num(row[25]) or CF,
            }
    return rows

def load_json(name: str):
    return json.loads((ROOT / name).read_text())

def load_head_json(name: str):
    raw = subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=ROOT)
    return json.loads(raw)

def write_json(name: str, data) -> None:
    (ROOT / name).write_text(json.dumps(data, indent=2) + "\n")

def description_for(code: str, cms: dict[str, dict], db: dict[str, dict]) -> str:
    return str(db.get(code, {}).get("description") or cms.get(code, {}).get("cms_description") or "")

def cms_description_for(code: str, cms: dict[str, dict]) -> str:
    return str(cms.get(code, {}).get("cms_description") or "")

def classify_code(code: str, cms: dict[str, dict], db: dict[str, dict]) -> set[str]:
    row = cms[code]
    if row["status"] != "A":
        return set()
    d = cms_description_for(code, cms).lower()
    cats = set()
    if in_range(code, 43000, 43499) and any(k in d for k in ["esoph", "cricopharyngeal"]):
        cats.add("Esophagus")
    if in_range(code, 43200, 43999) and any(k in d for k in ["stomach", "gastric", "gastro", "bypass", "sleeve", "fundop", "hiatal", "pylor", "duoden", "egd", "esophagogastroduodenoscopy", "gastrostomy"]):
        cats.add("Foregut")
    if in_range(code, 43500, 43999) and any(k in d for k in ["stomach", "gastric", "gastro", "bypass", "sleeve", "gastrect", "gastrostomy", "pylor"]):
        cats.add("Stomach")
    if in_range(code, 44000, 44799) and any(k in d for k in ["small intestine", "small bowel", "ileum", "jejun", "bowel", "enter"]):
        cats.add("Small bowel")
    if (in_range(code, 44100, 44799) or in_range(code, 45300, 45399)) and any(k in d for k in ["colon", "colonic", "colect", "colonoscopy", "large bowel", "cecum", "ileocolic"]):
        cats.add("Colon")
    if in_range(code, 45000, 45999) and any(k in d for k in ["rect", "anus", "anal", "proct", "hemorrhoid", "fistula", "fissure"]):
        cats.add("Rectum")
    if in_range(code, 44000, 44799) and any(k in d for k in ["ostomy", "enterostomy", "colostomy", "ileostomy", "cecostomy", "stoma"]):
        cats.add("Ostomy")
    if in_range(code, 44900, 44999) or "append" in d:
        cats.add("Appendix")
    if in_range(code, 47000, 47999) and any(k in d for k in ["liver", "hep", "bile", "biliary", "gallbladder", "chole", "choledo", "donor liver"]):
        cats.add("Hepatobiliary")
    if in_range(code, 48000, 48999) and any(k in d for k in ["pancre", "whipple"]):
        cats.add("Pancreas")
    if in_range(code, 38100, 38129) or (in_range(code, 48000, 48999) and "spleen" in d):
        cats.add("Spleen")
    if in_range(code, 19000, 19499) and any(k in d for k in ["breast", "mastect", "lumpect", "axillary"]):
        cats.add("Breast")
    if in_range(code, 49491, 49659) or "hernia" in d:
        cats.add("Hernia")
    if (in_range(code, 10000, 19999) or in_range(code, 20000, 29999)) and any(k in d for k in ["excision", "biopsy", "tumor", "abscess", "debrid", "skin", "subcutaneous", "soft tissue", "foreign body", "wound"]):
        cats.add("Soft tissue")
    if (in_range(code, 32000, 32999) or in_range(code, 49000, 49999) or in_range(code, 20000, 29999)) and any(k in d for k in ["trauma", "wound", "lacer", "hemorr", "packing", "exploration", "damage", "foreign body", "debrid"]):
        cats.add("Trauma")
    if (in_range(code, 44000, 44999) or in_range(code, 47000, 47999) or in_range(code, 49000, 49999)) and any(k in d for k in ["append", "chole", "abscess", "obstruction", "periton", "exploration", "peritoneal", "bowel", "intestine", "gallbladder"]):
        cats.add("Acute Care Surgery")
    if in_range(code, 21800, 21899) and "rib" in d:
        cats.add("Rib fixation")
    return cats

def category_codes(category: str, cms: dict[str, dict], db: dict[str, dict]) -> set[str]:
    return {code for code in cms if category in classify_code(code, cms, db)}

def primary_phase_category(code: str, cats: set[str]) -> str:
    for cat in ["Colon", "Rectum", "Ostomy", "Hepatobiliary", "Pancreas"]:
        if cat in cats:
            return cat
    return sorted(cats)[0] if cats else "General Surgery"

def slug_category(cat: str) -> str:
    return cat.lower().replace(" ", "_")

def entry_for(code: str, row: dict, cat: str, cats: set[str]) -> dict:
    global_days = int_global(row["global_period"])
    total = round(row["total_rvu"], 2)
    work = round(row["work_rvu"], 2)
    pe = round(row["pe_rvu"], 2)
    mp = round(row["mp_rvu"], 2)
    payment = round(total * CF, 2) if total else 0
    family = slug_category(cat)
    typical = []
    if row["multiple_indicator"] == "2":
        typical.append("-51")
    if cat in {"Colon", "Rectum", "Ostomy"}:
        typical.append("-59")
    return {
        "addon_code": row["global_period"].upper() == "ZZZ",
        "assistant_allowed": yes_indicator(row["assistant_indicator"]),
        "assistant_surgeon_indicator": row["assistant_indicator"],
        "bilateral_eligible": row["bilateral_indicator"] in {"1", "2"},
        "bilateral_indicator": row["bilateral_indicator"],
        "category": "Surgery",
        "code": code,
        "code_family": family,
        "cosurgeon_eligible": yes_indicator(row["cosurgeon_indicator"]),
        "cosurgeon_indicator": row["cosurgeon_indicator"],
        "description": row["cms_description"],
        "estimated": False,
        "estimated_medicare_payment": payment,
        "global_period_days": global_days,
        "hierarchy_tier": 2,
        "inclusive_of": ["12001", "12002", "12003", "12004", "12005"] + (["49000"] if cat in {"Colon", "Rectum", "Ostomy", "Hepatobiliary", "Pancreas"} else []),
        "mp_rvu": mp,
        "multiple_procedure_indicator": row["multiple_indicator"],
        "never_primary_with": [],
        "pe_rvu": pe,
        "search_terms": sorted({cat.lower(), *(c.lower() for c in cats), row["cms_description"].lower()}),
        "specialty": "general_surgery",
        "subcategory": slug_category(cat),
        "team_surgeon_indicator": row["team_indicator"],
        "total_rvu": total,
        "typical_modifiers": typical,
        "work_rvu": work,
        "wrvu_source": SOURCE,
        "wrvu_source_file": SOURCE_FILE,
        "wrvu_source_url": SOURCE_URL,
    }

def rvu_entry(entry: dict) -> dict:
    return {
        "description": entry["description"],
        "global_period": entry["global_period_days"],
        "mp_rvu": entry["mp_rvu"],
        "pe_rvu": entry["pe_rvu"],
        "total_rvu": entry["total_rvu"],
        "work_rvu": entry["work_rvu"],
        "wrvu_source": SOURCE,
        "wrvu_source_file": SOURCE_FILE,
        "wrvu_source_url": SOURCE_URL,
    }

def modifier_entry(entry: dict) -> dict:
    return {
        "mod51_exempt": entry["multiple_procedure_indicator"] == "0",
        "addon_code": entry["addon_code"],
        "bilateral_eligible": entry["bilateral_eligible"],
        "laterality_applicable": entry["bilateral_eligible"],
        "bilateral_method": "modifier_50" if entry["bilateral_eligible"] else None,
        "global_period": entry["global_period_days"],
        "assistant_allowed": entry["assistant_allowed"],
        "cosurgeon_eligible": entry["cosurgeon_eligible"],
        "team_surgeon_eligible": entry["team_surgeon_indicator"] in {"1", "2"},
        "inherently_bilateral": entry["bilateral_indicator"] == "2",
        "distinct_procedure_class": entry["subcategory"],
        "category": entry["subcategory"],
        "inclusive_of": entry["inclusive_of"],
        "never_primary_with": [],
        "payer_notes": {
            "medicare": "Use CMS PFS indicators; apply MPPR only when multiple-procedure rules apply.",
            "commercial": "Verify payer-specific bundling, endoscopy base-code, and assistant surgeon policy.",
        },
        "x_modifier_eligible": entry["subcategory"] in {"colon", "rectum", "ostomy", "hepatobiliary", "pancreas"},
        "hierarchy_tier": entry["hierarchy_tier"],
        "code_family": entry["code_family"],
    }

def page_html(entry: dict, related: list[dict]) -> str:
    title = f"CPT {entry['code']}: {entry['description']}"
    payment = f"${entry['estimated_medicare_payment']:,.2f}"
    related_links = "\n".join(
        f'<a href="/codes/{r["code"]}.html" class="site-card related-inline"><strong class="inline-code-link">CPT {r["code"]}</strong> - {escape(r["description"])}</a>'
        for r in related if r["code"] != entry["code"]
    )
    note = {
        "colon": "Colon and colonoscopy coding should be selected from the documented approach, anatomic extent, therapeutic maneuver, and whether the service is performed through a stoma.",
        "rectum": "Rectal and anorectal coding should be selected from the documented site, approach, excision/repair/drainage work, and whether the service is diagnostic or therapeutic.",
        "ostomy": "Ostomy coding should distinguish creation, revision, closure, endoscopy through stoma, and separately supported therapeutic maneuvers.",
        "hepatobiliary": "Hepatobiliary coding should be selected from the documented liver, bile duct, gallbladder, percutaneous biliary, or donor-preparation work.",
        "pancreas": "Pancreatic coding should be selected from the documented procedure type, pancreatic anatomy, associated reconstruction, and whether transplant/autotransplant work is separately supported.",
    }.get(entry["subcategory"], "Select the CPT code from the operative facts and verify final billing against current AMA CPT, CMS, NCCI, and payer policy.")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} | FreeCPTCodeFinder.com</title>
<meta name="description" content="CPT code {entry['code']} - {escape(entry['description'])}. Work RVU: {entry['work_rvu']:.2f}, total RVU: {entry['total_rvu']:.2f}, estimated Medicare payment: {payment}.">
<link rel="canonical" href="https://freecptcodefinder.com/codes/{entry['code']}.html"><link rel="stylesheet" href="/styles/app-mode.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"MedicalWebPage","name":"{escape(title)}","url":"https://freecptcodefinder.com/codes/{entry['code']}.html","dateModified":"{TODAY}"}}</script></head>
<body><main class="container code-page"><nav><a href="/">FreeCPTCodeFinder</a> / <a href="/codes/">CPT Codes</a> / CPT {entry['code']}</nav>
<h1>CPT {entry['code']} <span class="desc">{escape(entry['description'])}</span></h1>
<section class="site-card"><h2>RVU Snapshot</h2><ul><li><strong>Work RVU:</strong> {entry['work_rvu']:.2f}</li><li><strong>PE RVU:</strong> {entry['pe_rvu']:.2f}</li><li><strong>MP RVU:</strong> {entry['mp_rvu']:.2f}</li><li><strong>Total RVU:</strong> {entry['total_rvu']:.2f}</li><li><strong>Estimated Medicare payment:</strong> {payment}</li><li><strong>Global period:</strong> {entry['global_period_days']} days</li><li><strong>Assistant surgeon indicator:</strong> {entry['assistant_surgeon_indicator']}</li><li><strong>Co-surgeon indicator:</strong> {entry['cosurgeon_indicator']}</li><li><strong>Team surgeon indicator:</strong> {entry['team_surgeon_indicator']}</li><li><strong>Bilateral indicator:</strong> {entry['bilateral_indicator']}</li><li><strong>Multiple procedure indicator:</strong> {entry['multiple_procedure_indicator']}</li></ul></section>
<section class="site-card"><h2>{escape(entry['subcategory'].replace('_',' ').title())} Coding Note</h2><p>{escape(note)}</p><p>Case Builder uses the same total-RVU Medicare payment estimate and applies modifier or MPPR adjustments only at the case level.</p></section>
<section class="site-card"><h2>Related Phase A Codes</h2>{related_links}</section>
<p><strong>Source:</strong> {SOURCE} ({SOURCE_FILE}). Educational coding support only; confirm final billing against AMA CPT, CMS MPFS, NCCI, and payer policy.</p></main></body></html>'''

def update_codes_index(codes: list[str], db: dict[str, dict]) -> None:
    path = ROOT / "codes" / "index.html"
    text = path.read_text()
    additions = []
    for code in codes:
        marker = f"/codes/{code}.html"
        if marker in text:
            continue
        entry = db[code]
        additions.append(f'<li><a href="/codes/{code}.html">CPT {code}</a> - {escape(entry["description"])}</li>')
    if not additions:
        return
    block = "\n<section class=\"site-card\"><h2>Phase A Colorectal, Hepatobiliary, and Pancreatic CPT Codes</h2><ul>\n" + "\n".join(additions) + "\n</ul></section>\n"
    text = text.replace("</main>", block + "</main>") if "</main>" in text else text + block
    path.write_text(text)

def update_sitemap(codes: list[str]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text()
    additions = []
    for code in codes:
        loc = f"https://freecptcodefinder.com/codes/{code}.html"
        if loc not in text:
            additions.append(f"<url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>")
    if additions:
        text = text.replace("</urlset>", "\n".join(additions) + "\n</urlset>")
        path.write_text(text)

def update_decision_tree(codes: list[str], db: dict[str, dict]) -> None:
    path = ROOT / "cpt_decision_tree.json"
    tree = load_json("cpt_decision_tree.json")
    rows = tree.get("General Surgery", [])
    existing = {str(r[0]) for r in rows if isinstance(r, list) and r}
    for code in codes:
        if code not in existing:
            e = db[code]
            rows.append([code, e["description"], e["work_rvu"], e["global_period_days"]])
    rows.sort(key=lambda r: str(r[0]))
    tree["General Surgery"] = rows
    write_json("cpt_decision_tree.json", tree)

def coverage_dashboard(cms: dict[str, dict], db: dict[str, dict]) -> list[dict]:
    rows = []
    for cat in DASHBOARD_CATEGORIES:
        universe = category_codes(cat, cms, db)
        site = {code for code in universe if code in db}
        missing = sorted(universe - site)
        rows.append({
            "category": cat,
            "cms_count": len(universe),
            "site_count": len(site),
            "missing_count": len(missing),
            "coverage_pct": round((len(site) / len(universe) * 100) if universe else 100.0, 1),
            "missing_codes": missing,
        })
    return rows

def compare_existing(phase_union: set[str], cms: dict[str, dict], db: dict[str, dict]) -> list[dict]:
    mismatches = []
    for code in sorted(phase_union & set(db)):
        e = db[code]
        r = cms[code]
        checks = [
            ("work_rvu", round(r["work_rvu"], 2), round(float(e.get("work_rvu", 0) or 0), 2)),
            ("pe_rvu", round(r["pe_rvu"], 2), round(float(e.get("pe_rvu", 0) or 0), 2)),
            ("mp_rvu", round(r["mp_rvu"], 2), round(float(e.get("mp_rvu", 0) or 0), 2)),
            ("total_rvu", round(r["total_rvu"], 2), round(float(e.get("total_rvu", 0) or 0), 2)),
            ("estimated_medicare_payment", round(r["total_rvu"] * CF, 2), round(float(e.get("estimated_medicare_payment", 0) or 0), 2)),
        ]
        diffs = [{"field": field, "cms": cms_value, "site": site_value} for field, cms_value, site_value in checks if cms_value != site_value]
        if diffs:
            mismatches.append({"code": code, "description": description_for(code, cms, db), "differences": diffs})
    return mismatches

def write_reports(before, after, phase_sets, phase_missing_before, added, mismatches) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": TODAY,
        "cms_source": str(CMS),
        "phase_categories": PHASE_CATEGORIES,
        "coverage_dashboard_before": before,
        "coverage_dashboard_after": after,
        "phase_sets": {k: sorted(v) for k, v in phase_sets.items()},
        "missing_codes_before": phase_missing_before,
        "added_codes": added,
        "existing_value_conflicts": mismatches,
    }
    (OUT / "phase_a_audit_report.json").write_text(json.dumps(report, indent=2))
    lines = ["# Phase A Colorectal + Hepatobiliary + Pancreatic Audit", "", "## Coverage Dashboard Before"]
    for row in before:
        lines.append(f"- {row['category']}: CMS {row['cms_count']} | Site {row['site_count']} | Missing {row['missing_count']} | Coverage {row['coverage_pct']}%")
    lines += ["", "## Coverage Dashboard After"]
    for row in after:
        lines.append(f"- {row['category']}: CMS {row['cms_count']} | Site {row['site_count']} | Missing {row['missing_count']} | Coverage {row['coverage_pct']}%")
    lines += ["", f"## Added Missing Phase A Codes ({len(added)})", ", ".join(added), "", "## Existing Value Conflicts"]
    if mismatches:
        for item in mismatches:
            diff = "; ".join(f"{d['field']} CMS {d['cms']} vs site {d['site']}" for d in item["differences"])
            lines.append(f"- {item['code']} {item['description']}: {diff}")
    else:
        lines.append("- None")
    (OUT / "phase_a_audit_report.md").write_text("\n".join(lines) + "\n")

def main() -> None:
    cms = parse_cms()
    before_db = load_head_json("cpt_database.json")
    db = load_json("cpt_database.json")
    rvu = load_json("rvu_database.json")
    mods = load_json("modifier_rules.json")
    before = coverage_dashboard(cms, before_db)
    phase_sets = {cat: category_codes(cat, cms, before_db) for cat in PHASE_CATEGORIES}
    phase_union = set().union(*phase_sets.values())
    missing = sorted(code for code in phase_union if code not in before_db)
    mismatches = compare_existing(phase_union, cms, before_db)

    added_entries = {}
    for code in missing:
        if code in db:
            continue
        cats = classify_code(code, cms, db)
        cat = primary_phase_category(code, cats)
        entry = entry_for(code, cms[code], cat, cats)
        db[code] = entry
        rvu.setdefault("codes", {})[code] = rvu_entry(entry)
        mods[code] = modifier_entry(entry)
        added_entries[code] = entry

    write_json("cpt_database.json", db)
    write_json("rvu_database.json", rvu)
    write_json("modifier_rules.json", mods)
    update_decision_tree(missing, db)
    update_codes_index(missing, db)
    update_sitemap(missing)

    by_cat = {}
    for code, entry in added_entries.items():
        by_cat.setdefault(entry["subcategory"], []).append(entry)
    for code, entry in added_entries.items():
        related = by_cat.get(entry["subcategory"], [])[:10]
        (ROOT / "codes" / f"{code}.html").write_text(page_html(entry, related))

    after = coverage_dashboard(cms, db)
    write_reports(before, after, phase_sets, missing, missing, mismatches)
    print(json.dumps({
        "added_count": len(missing),
        "added_codes": missing,
        "report": str(OUT / "phase_a_audit_report.md"),
        "dashboard_before": before,
        "dashboard_after": after,
        "existing_value_conflicts": len(mismatches),
    }, indent=2))

if __name__ == "__main__":
    main()
