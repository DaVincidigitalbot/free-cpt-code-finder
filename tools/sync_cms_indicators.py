#!/usr/bin/env python3
"""Synchronize CPT indicator fields from CMS RVU26C.

This repairs indicator drift without hand-editing individual CPT records.
It preserves raw CMS indicator values in cpt_database.json, derives
modifier_rules.json from those values, rebuilds affected CPT pages, and
regenerates homepage SPECS from the corrected source data.
"""
from __future__ import annotations

import csv
import html
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CMS = ROOT / "tmp" / "abos_sports_import" / "rvu26c" / "PPRRVU2026_Jul_nonQPP.csv"
FALLBACK_CMS = Path("/home/setup/Desktop/FreeCPTCodeFinder/tmp/abos_sports_import/rvu26c/PPRRVU2026_Jul_nonQPP.csv")
CF = 33.4009
TODAY = date.today().isoformat()
MANUAL_REVIEW_FIELDS = {("38120", "assistant_surgeon"), ("38120", "co_surgeon")}
FIELDS = [
    "assistant_surgeon",
    "co_surgeon",
    "bilateral",
    "multiple_procedure",
    "team_surgeon",
    "global_period",
]


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


def parse_cms() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    source = cms_path()
    with source.open(newline="", encoding="utf-8-sig", errors="replace") as f:
        for row in csv.reader(f):
            if not row or len(row) < 23:
                continue
            code = row[0].strip()
            modifier = row[1].strip()
            if not re.fullmatch(r"\d{5}", code) or modifier:
                continue
            rows[code] = {
                "description": row[2].strip(),
                "work_rvu": num(row[5]),
                "pe_rvu": num(row[6]),
                "mp_rvu": num(row[10]),
                "total_rvu": num(row[11]),
                "global_period": normalize_global_indicator(row[14].strip()),
                "multiple_procedure": row[18].strip(),
                "bilateral": row[19].strip(),
                "assistant_surgeon": row[20].strip(),
                "co_surgeon": row[21].strip(),
                "team_surgeon": row[22].strip(),
            }
    return rows


def normalize_global_indicator(value: str) -> str:
    value = str(value or "").strip().upper()
    if value.isdigit():
        return str(int(value))
    return value


def global_days(indicator: str):
    indicator = str(indicator or "").strip().upper()
    if indicator.isdigit():
        return int(indicator)
    if indicator == "YYY":
        return 90
    return 0


def site_indicator(entry: dict, field: str):
    if field == "assistant_surgeon":
        return str(entry.get("assistant_surgeon_indicator", "0"))
    if field == "co_surgeon":
        return str(entry.get("cosurgeon_indicator", "0"))
    if field == "bilateral":
        return str(entry.get("bilateral_indicator", "0"))
    if field == "multiple_procedure":
        return str(entry.get("multiple_procedure_indicator", "2"))
    if field == "team_surgeon":
        return str(entry.get("team_surgeon_indicator", "0"))
    if field == "global_period":
        return str(entry.get("global_period_indicator", entry.get("global_period_days", entry.get("global_period", 0))))
    raise KeyError(field)


def cms_indicator(row: dict, field: str) -> str:
    return str(row[field])


def mismatch_rows(cpt_db: dict, cms_rows: dict) -> list[dict]:
    rows = []
    for code, entry in sorted(cpt_db.items()):
        cms = cms_rows.get(code)
        if not cms:
            continue
        for field in FIELDS:
            observed = site_indicator(entry, field)
            expected = cms_indicator(cms, field)
            if observed != expected:
                rows.append({
                    "code": code,
                    "field": field,
                    "site_value": observed,
                    "cms_value": expected,
                    "description": entry.get("description") or cms.get("description") or "",
                    "manual_review": (code, field) in MANUAL_REVIEW_FIELDS,
                })
    return rows


def update_entry(code: str, entry: dict, cms: dict) -> bool:
    changed = False
    updates = {
        "bilateral_indicator": cms["bilateral"],
        "multiple_procedure_indicator": cms["multiple_procedure"],
        "team_surgeon_indicator": cms["team_surgeon"],
        "global_period_indicator": cms["global_period"],
        "global_period_days": global_days(cms["global_period"]),
        "bilateral_eligible": cms["bilateral"] == "1",
        "addon_code": cms["global_period"] == "ZZZ",
        "indicator_source": "CMS PFS RVU26C July 2026 non-QPP",
        "indicator_source_file": "PPRRVU2026_Jul_nonQPP.csv",
    }
    if (code, "assistant_surgeon") not in MANUAL_REVIEW_FIELDS:
        updates["assistant_surgeon_indicator"] = cms["assistant_surgeon"]
        updates["assistant_allowed"] = cms["assistant_surgeon"] in {"2", "3"}
    if (code, "co_surgeon") not in MANUAL_REVIEW_FIELDS:
        updates["cosurgeon_indicator"] = cms["co_surgeon"]
        updates["cosurgeon_eligible"] = cms["co_surgeon"] in {"1", "2"}
    for key, value in updates.items():
        if entry.get(key) != value:
            entry[key] = value
            changed = True
    return changed


def modifier_from_cpt(entry: dict) -> dict:
    multiple = str(entry.get("multiple_procedure_indicator", "2"))
    bilateral = str(entry.get("bilateral_indicator", "0"))
    global_indicator = str(entry.get("global_period_indicator", entry.get("global_period_days", 0)))
    addon = bool(entry.get("addon_code")) or global_indicator == "ZZZ"
    bilateral_eligible = bilateral == "1"
    return {
        "addon_code": addon,
        "assistant_allowed": bool(entry.get("assistant_allowed")),
        "bilateral_eligible": bilateral_eligible,
        "bilateral_method": "modifier_50" if bilateral_eligible else None,
        "code_family": entry.get("code_family") or entry.get("subcategory") or "cpt",
        "cosurgeon_eligible": bool(entry.get("cosurgeon_eligible")),
        "category": entry.get("subcategory") or entry.get("category"),
        "distinct_procedure_class": entry.get("subcategory") or entry.get("code_family"),
        "global_period": global_indicator,
        "global_period_days": entry.get("global_period_days", global_days(global_indicator)),
        "hierarchy_tier": entry.get("hierarchy_tier", 3),
        "inherently_bilateral": bilateral == "2",
        "inclusive_of": entry.get("inclusive_of", []),
        "laterality_applicable": bilateral in {"1", "3"},
        "mod51_exempt": addon or multiple == "0",
        "never_primary_with": entry.get("never_primary_with", []),
        "payer_notes": {
            "medicare": "Use CMS PFS RVU26C indicators; apply MPPR only when multiple-procedure rules apply.",
            "commercial": "Verify payer-specific modifier, assistant, and bundling policy.",
        },
        "team_surgeon_eligible": str(entry.get("team_surgeon_indicator", "0")) in {"1", "2"},
        "x_modifier_eligible": not addon,
    }


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
<p><strong>Sources:</strong> RVU values from {html.escape(str(entry.get('wrvu_source','cpt_database.json')))}. Indicator metadata from {html.escape(str(entry.get('indicator_source','CMS PFS RVU26C July 2026 non-QPP')))}. Educational coding support only; confirm final billing against AMA CPT, CMS MPFS, NCCI, and payer policy.</p></main></body></html>
"""


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def count_by_field(rows: list[dict]) -> dict[str, int]:
    return dict(Counter(row["field"] for row in rows))


def pattern_counts(rows: list[dict]) -> list[dict]:
    counter = Counter((row["field"], row["site_value"], row["cms_value"]) for row in rows)
    return [
        {"field": field, "site_value": site, "cms_value": cms, "count": count}
        for (field, site, cms), count in counter.most_common()
    ]


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> int:
    out = ROOT / "qa_artifacts" / "phase1d_c_indicator_sync_2026_06_11"
    out.mkdir(parents=True, exist_ok=True)
    cpt_path = ROOT / "cpt_database.json"
    modifier_path = ROOT / "modifier_rules.json"
    cpt_db = read_json(cpt_path)
    modifier_rules = read_json(modifier_path)
    cms_rows = parse_cms()

    before = mismatch_rows(cpt_db, cms_rows)
    manual_review = []
    updated_codes: list[str] = []
    before_values = []
    after_values = []

    for code, entry in sorted(cpt_db.items()):
        cms = cms_rows.get(code)
        if not cms:
            continue
        for field in FIELDS:
            if (code, field) in MANUAL_REVIEW_FIELDS and site_indicator(entry, field) != cms_indicator(cms, field):
                manual_review.append({
                    "code": code,
                    "field": field,
                    "site_value": site_indicator(entry, field),
                    "cms_value": cms_indicator(cms, field),
                    "description": entry.get("description") or cms.get("description") or "",
                    "reason": "Manual-override provenance; held out for explicit human review.",
                })
        changed_fields = {}
        for field in FIELDS:
            if (code, field) in MANUAL_REVIEW_FIELDS:
                continue
            observed = site_indicator(entry, field)
            expected = cms_indicator(cms, field)
            if observed != expected:
                changed_fields[field] = (observed, expected)
        if update_entry(code, entry, cms):
            updated_codes.append(code)
            for field, (observed, expected) in changed_fields.items():
                before_values.append({
                    "code": code,
                    "field": field,
                    "value": observed,
                    "description": entry.get("description") or cms.get("description") or "",
                })
                after_values.append({
                    "code": code,
                    "field": field,
                    "value": expected,
                    "description": entry.get("description") or cms.get("description") or "",
                })
            modifier_rules[code] = modifier_from_cpt(entry)

    write_json(cpt_path, cpt_db)
    write_json(modifier_path, modifier_rules)

    for code in updated_codes:
        page = ROOT / "codes" / f"{code}.html"
        if page.exists():
            page.write_text(page_html(code, cpt_db[code]))

    subprocess.check_call(["python3", "scripts/build_homepage_specs.py"], cwd=ROOT)

    cpt_db_after = read_json(cpt_path)
    after = mismatch_rows(cpt_db_after, cms_rows)

    write_csv(out / "before_indicator_mismatches.csv", before, ["code", "field", "site_value", "cms_value", "description", "manual_review"])
    write_csv(out / "after_indicator_mismatches.csv", after, ["code", "field", "site_value", "cms_value", "description", "manual_review"])
    write_csv(out / "manual_review_exceptions.csv", manual_review, ["code", "field", "site_value", "cms_value", "description", "reason"])
    write_csv(out / "indicator_before_values_changed.csv", before_values, ["code", "field", "value", "description"])
    write_csv(out / "indicator_after_values_changed.csv", after_values, ["code", "field", "value", "description"])

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "branch_commit_before": git_commit(),
        "cms_source": str(cms_path()),
        "cms_baseline": "CMS RVU26C / PPRRVU2026_Jul_nonQPP.csv",
        "mode": "remediation local branch only; no deployment",
        "updated_code_count": len(updated_codes),
        "regenerated_cpt_page_count": len([c for c in updated_codes if (ROOT / "codes" / f"{c}.html").exists()]),
        "total_mismatches_before": len(before),
        "total_mismatches_after": len(after),
        "mismatch_reduction": len(before) - len(after),
        "remaining_mismatches": len(after),
        "before_counts_by_field": count_by_field(before),
        "after_counts_by_field": count_by_field(after),
        "top_before_patterns": pattern_counts(before)[:20],
        "top_after_patterns": pattern_counts(after)[:20],
        "manual_review_exceptions": manual_review,
        "files_changed_intended": [
            "cpt_database.json",
            "modifier_rules.json",
            "index.html",
            "codes/*.html for affected matched CPT pages",
            "tools/sync_cms_indicators.py",
            "qa_artifacts/phase1d_c_indicator_sync_2026_06_11/*",
        ],
        "root_causes_fixed": [
            "assistant/co-surgeon/bilateral/team CMS indicators defaulting to 0",
            "multiple-procedure CMS indicator defaulting to 2",
            "global period symbolic values being stored only as normalized numeric days",
        ],
    }
    (out / "indicator_sync_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
