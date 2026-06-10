#!/usr/bin/env python3
"""Validate Phase A colorectal/HPB/pancreas CPT integrity.

Fails non-zero if any active CMS CPT in the audited Phase A specialties is
missing database/RVU/modifier/page/sitemap/search-index coverage or has an
unresolved CMS RVU discrepancy.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CMS = Path("/home/setup/Desktop/FreeCPTCodeFinder/tmp/abos_sports_import/rvu26c/PPRRVU2026_Jul_nonQPP.csv")
CF = 33.4009


def num(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def in_range(code: str, lo: int, hi: int) -> bool:
    return lo <= int(code) <= hi


def parse_cms() -> dict[str, dict]:
    rows = {}
    with CMS.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.reader(handle):
            if not row or len(row) < 32:
                continue
            if not re.fullmatch(r"\d{5}", row[0] or "") or row[1] != "" or row[3] != "A":
                continue
            rows[row[0]] = {
                "code": row[0],
                "description": row[2].strip(),
                "work_rvu": num(row[5]),
                "pe_rvu": num(row[6]),
                "mp_rvu": num(row[10]),
                "total_rvu": num(row[11]),
                "global": row[14].strip(),
                "multiple": row[18].strip(),
                "bilateral": row[19].strip(),
                "assistant": row[20].strip(),
                "cosurgeon": row[21].strip(),
                "team": row[22].strip(),
            }
    return rows


def phase_categories(code: str, row: dict) -> set[str]:
    d = row["description"].lower()
    cats = set()
    if (in_range(code, 44100, 44799) or in_range(code, 45300, 45399)) and any(k in d for k in ["colon", "colonic", "colect", "colonoscopy", "large bowel", "cecum", "ileocolic"]):
        cats.add("Colon")
    if in_range(code, 45000, 45999) and any(k in d for k in ["rect", "anus", "anal", "proct", "hemorrhoid", "fistula", "fissure"]):
        cats.add("Rectum")
    if in_range(code, 44000, 44799) and any(k in d for k in ["ostomy", "enterostomy", "colostomy", "ileostomy", "cecostomy", "stoma"]):
        cats.add("Ostomy")
    if in_range(code, 47000, 47999) and any(k in d for k in ["liver", "hep", "bile", "biliary", "gallbladder", "chole", "choledo", "donor liver"]):
        cats.add("Hepatobiliary")
    if in_range(code, 48000, 48999) and any(k in d for k in ["pancre", "whipple"]):
        cats.add("Pancreas")
    return cats


def main() -> int:
    cms = parse_cms()
    phase_codes = sorted(code for code, row in cms.items() if phase_categories(code, row))

    cpt_db = json.loads((ROOT / "cpt_database.json").read_text())
    rvu_db = json.loads((ROOT / "rvu_database.json").read_text())["codes"]
    modifier_rules = json.loads((ROOT / "modifier_rules.json").read_text())
    sitemap = (ROOT / "sitemap.xml").read_text()
    codes_index = (ROOT / "codes" / "index.html").read_text()

    hard_errors = []
    warnings = []

    for code in phase_codes:
        row = cms[code]
        entry = cpt_db.get(code)
        if not entry:
            hard_errors.append({"type": "missing_cpt_database", "code": code})
            continue

        if code not in rvu_db:
            hard_errors.append({"type": "missing_rvu_database", "code": code})
        if code not in modifier_rules:
            hard_errors.append({"type": "missing_modifier_rules", "code": code})

        page = ROOT / "codes" / f"{code}.html"
        if not page.exists():
            hard_errors.append({"type": "missing_cpt_page", "code": code})
        else:
            page_text = page.read_text(errors="replace")
            if code not in page_text:
                hard_errors.append({"type": "cpt_page_missing_code_text", "code": code})
            expected_work_strings = {str(entry.get("work_rvu")), f"{float(entry.get('work_rvu', 0) or 0):.2f}"}
            expected_payment = round(float(entry.get("total_rvu", 0) or 0) * CF, 2)
            expected_payment_strings = {str(entry.get("estimated_medicare_payment")), f"{expected_payment:.2f}", "$" + f"{expected_payment:.2f}"}
            if not any(s in page_text for s in expected_work_strings):
                hard_errors.append({"type": "cpt_page_work_rvu_mismatch", "code": code, "expected": entry.get("work_rvu")})
            if not any(s in page_text for s in expected_payment_strings):
                hard_errors.append({"type": "cpt_page_payment_mismatch", "code": code, "expected": expected_payment})

        if f"https://freecptcodefinder.com/codes/{code}.html" not in sitemap:
            hard_errors.append({"type": "missing_sitemap_entry", "code": code})
        if f"/codes/{code}.html" not in codes_index:
            hard_errors.append({"type": "missing_search_index_entry", "code": code})

        for field in ["work_rvu", "pe_rvu", "mp_rvu", "total_rvu", "estimated_medicare_payment", "global_period_days"]:
            if entry.get(field) in [None, ""]:
                hard_errors.append({"type": "missing_cpt_field", "code": code, "field": field})

        rvu_entry = rvu_db.get(code, {})
        for field in ["work_rvu", "pe_rvu", "mp_rvu", "total_rvu"]:
            if rvu_entry.get(field) in [None, ""]:
                hard_errors.append({"type": "missing_rvu_field", "code": code, "field": field})

        expected_payment = round(float(entry.get("total_rvu", 0) or 0) * CF, 2)
        if round(float(entry.get("estimated_medicare_payment", 0) or 0), 2) != expected_payment:
            hard_errors.append({"type": "payment_formula_mismatch", "code": code, "site": entry.get("estimated_medicare_payment"), "expected": expected_payment})

        for field, cms_value, site_value in [
            ("work_rvu", row["work_rvu"], entry.get("work_rvu")),
            ("pe_rvu", row["pe_rvu"], entry.get("pe_rvu")),
            ("mp_rvu", row["mp_rvu"], entry.get("mp_rvu")),
            ("total_rvu", row["total_rvu"], entry.get("total_rvu")),
        ]:
            if round(float(site_value or 0), 2) != round(float(cms_value or 0), 2):
                hard_errors.append({"type": "cms_rvu_discrepancy", "code": code, "field": field, "site": site_value, "cms": cms_value})

        rule = modifier_rules.get(code, {})
        cms_addon = row["global"] == "ZZZ"
        if bool(entry.get("addon_code")) != cms_addon:
            hard_errors.append({"type": "cpt_addon_flag_mismatch", "code": code, "site": entry.get("addon_code"), "cms_global": row["global"]})
        if bool(rule.get("addon_code")) != cms_addon:
            hard_errors.append({"type": "modifier_addon_flag_mismatch", "code": code, "site": rule.get("addon_code"), "cms_global": row["global"]})
        if cms_addon and rule.get("global_period") != "ZZZ":
            hard_errors.append({"type": "addon_global_period_mismatch", "code": code, "site": rule.get("global_period")})
        if row["multiple"] == "0" and not rule.get("mod51_exempt"):
            hard_errors.append({"type": "modifier_51_exempt_mismatch", "code": code, "cms_multiple": row["multiple"], "site": rule.get("mod51_exempt")})

    summary = {
        "phase_code_count": len(phase_codes),
        "hard_error_count": len(hard_errors),
        "warning_count": len(warnings),
        "hard_error_types": dict(Counter(item["type"] for item in hard_errors)),
        "warning_types": dict(Counter(item["type"] for item in warnings)),
        "hard_errors": hard_errors,
        "warnings": warnings,
    }

    out_dir = ROOT / "qa_artifacts" / "phase_a_colorectal_hpb_pancreas_2026_06_10"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "phase_a_integrity_validation.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 1 if hard_errors else 0


if __name__ == "__main__":
    sys.exit(main())

