#!/usr/bin/env python3
"""Repair placeholder CPT descriptors from the CMS RVU26C descriptor column."""
from __future__ import annotations

import csv
import html
import json
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CMS = ROOT / "tmp" / "abos_sports_import" / "rvu26c" / "PPRRVU2026_Jul_nonQPP.csv"
FALLBACK_CMS = Path("/home/setup/Desktop/FreeCPTCodeFinder/tmp/abos_sports_import/rvu26c/PPRRVU2026_Jul_nonQPP.csv")
OUT = ROOT / "qa_artifacts" / "phase2a_b_placeholder_descriptor_remediation_2026_06_11"
TODAY = date.today().isoformat()


def cms_path() -> Path:
    return CMS if CMS.exists() else FALLBACK_CMS


def num(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def money(value) -> str:
    return "$" + f"{num(value):,.2f}"


def read_json(path: Path):
    return json.loads(path.read_text())


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def parse_cms_descriptors() -> dict[str, str]:
    descriptors: dict[str, str] = {}
    with cms_path().open(newline="", encoding="utf-8-sig", errors="replace") as f:
        for row in csv.reader(f):
            if len(row) < 3:
                continue
            code = row[0].strip()
            modifier = row[1].strip()
            if re.fullmatch(r"\d{5}", code) and not modifier:
                descriptors[code] = row[2].strip()
    return descriptors


def is_placeholder_descriptor(value: str) -> bool:
    return bool(re.fullmatch(r"CPT\s+\d{5}", str(value or "").strip(), re.I))


def is_suspicious_descriptor(value: str) -> bool:
    value = str(value or "").strip()
    return (not value) or is_placeholder_descriptor(value) or len(value) < 12 or value.endswith(("...", "…"))


def page_html(code: str, entry: dict) -> str:
    desc = html.escape(str(entry.get("description", "")))
    payment = money(entry.get("estimated_medicare_payment", 0))
    global_indicator = entry.get("global_period_indicator", entry.get("global_period_days", ""))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CPT {code}: {desc} | FreeCPTCodeFinder.com</title>
<meta name="description" content="CPT code {code} - {desc}. Work RVU: {num(entry.get('work_rvu')):.2f}, total RVU: {num(entry.get('total_rvu')):.2f}, estimated Medicare payment: {payment}.">
<link rel="canonical" href="https://freecptcodefinder.com/codes/{code}.html"><link rel="stylesheet" href="/styles/app-mode.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"MedicalWebPage","name":"CPT {code}: {desc}","url":"https://freecptcodefinder.com/codes/{code}.html","dateModified":"{TODAY}"}}</script></head>
<body><main class="container code-page"><nav><a href="/">FreeCPTCodeFinder</a> / <a href="/codes/">CPT Codes</a> / CPT {code}</nav>
<h1>CPT {code} <span class="desc">{desc}</span></h1>
<section class="site-card"><h2>RVU Snapshot</h2><ul><li><strong>Work RVU:</strong> {num(entry.get('work_rvu')):.2f}</li><li><strong>PE RVU:</strong> {num(entry.get('pe_rvu')):.2f}</li><li><strong>MP RVU:</strong> {num(entry.get('mp_rvu')):.2f}</li><li><strong>Total RVU:</strong> {num(entry.get('total_rvu')):.2f}</li><li><strong>Estimated Medicare payment:</strong> {payment}</li><li><strong>Global period:</strong> {html.escape(str(global_indicator))}</li><li><strong>Assistant surgeon indicator:</strong> {html.escape(str(entry.get('assistant_surgeon_indicator','')))}</li><li><strong>Co-surgeon indicator:</strong> {html.escape(str(entry.get('cosurgeon_indicator','')))}</li><li><strong>Team surgeon indicator:</strong> {html.escape(str(entry.get('team_surgeon_indicator','')))}</li><li><strong>Bilateral indicator:</strong> {html.escape(str(entry.get('bilateral_indicator','')))}</li><li><strong>Multiple procedure indicator:</strong> {html.escape(str(entry.get('multiple_procedure_indicator','')))}</li></ul></section>
<section class="site-card"><h2>Coding Note</h2><p>Case Builder uses this same total-RVU Medicare payment estimate and applies modifier or MPPR adjustments only at the case level.</p></section>
<p><strong>Sources:</strong> RVU values from {html.escape(str(entry.get('wrvu_source','cpt_database.json')))}. Indicator metadata from {html.escape(str(entry.get('indicator_source','CMS PFS RVU26C July 2026 non-QPP')))}. Descriptor from CMS PFS RVU26C July 2026 non-QPP. Educational coding support only; confirm final billing against AMA CPT, CMS MPFS, NCCI, and payer policy.</p></main></body></html>
"""


def scan(db: dict) -> dict:
    placeholder = []
    suspicious = []
    for code, entry in sorted(db.items()):
        desc = str(entry.get("description", "")).strip()
        if is_placeholder_descriptor(desc):
            placeholder.append({"code": code, "description": desc})
        if is_suspicious_descriptor(desc):
            suspicious.append({"code": code, "description": desc})
    return {"placeholder_descriptors": placeholder, "truncated_or_suspicious_descriptors": suspicious}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cpt_path = ROOT / "cpt_database.json"
    db = read_json(cpt_path)
    cms = parse_cms_descriptors()
    before = scan(db)
    candidate_codes = {row["code"] for rows in before.values() for row in rows}
    repaired = []
    retained = []

    for code in sorted(candidate_codes):
        entry = db.get(code)
        if not entry:
            continue
        current = str(entry.get("description", "")).strip()
        canonical = cms.get(code, "").strip()
        if canonical and canonical != current and not is_placeholder_descriptor(canonical):
            entry["description"] = canonical
            entry["descriptor_source"] = "CMS PFS RVU26C July 2026 non-QPP"
            entry["descriptor_source_file"] = "PPRRVU2026_Jul_nonQPP.csv"
            repaired.append({"code": code, "before": current, "after": canonical})
        else:
            retained.append({
                "code": code,
                "description": current,
                "reason": "No active CMS RVU26C replacement descriptor found" if not canonical else "Current descriptor already matches CMS RVU26C",
            })

    write_json(cpt_path, db)
    for row in repaired:
        page = ROOT / "codes" / f"{row['code']}.html"
        if page.exists():
            page.write_text(page_html(row["code"], db[row["code"]]))

    subprocess.check_call(["python3", "scripts/build_homepage_specs.py"], cwd=ROOT)

    after_db = read_json(cpt_path)
    after = scan(after_db)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cms_source": str(cms_path()),
        "before_counts": {key: len(value) for key, value in before.items()},
        "after_counts": {key: len(value) for key, value in after.items()},
        "repaired_count": len(repaired),
        "retained_review_count": len(retained),
        "repaired": repaired,
        "retained_review": retained,
        "example_codes": {code: next((row for row in repaired if row["code"] == code), None) for code in ["19318", "19325", "19340", "19342", "19350", "19355"]},
    }
    (OUT / "descriptor_remediation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
