#!/usr/bin/env python3
"""Import ABOS hand surgery CPT codes into FreeCPTCodeFinder orthopedic data."""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://ebhmc.com/cptabos/"
SOURCE_HTML = ROOT / "tmp" / "abos_hand_import" / "ebhmc-cptabos.html"
SOURCE_TEXT = ROOT / "tmp" / "abos_hand_import" / "ebhmc-cptabos.txt"
CMS_JULY_NON_QPP = ROOT / "tmp" / "abos_hand_import" / "rvu26c" / "PPRRVU2026_Jul_nonQPP.csv"
CMS_SOURCE_URL = "https://www.cms.gov/files/zip/rvu26c.zip"
CMS_SOURCE = "CMS PFS RVU26C July 2026 non-QPP"
CMS_SOURCE_FILE = "PPRRVU2026_Jul_nonQPP.csv"
AUDIT_JSON = ROOT / "audit_reports" / "abos_hand_orthopedic_import_2026-06-06.json"
AUDIT_CSV = ROOT / "audit_reports" / "abos_hand_orthopedic_import_2026-06-06.csv"
ORTHO_SPEC_KEY = "General Orthopedic Surgery"


def clean_description(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace(" ,", ",").replace(" ;", ";")
    return value


def extract_source_text() -> str:
    if SOURCE_TEXT.exists():
        return SOURCE_TEXT.read_text(encoding="utf-8")
    html = SOURCE_HTML.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer"]):
        tag.decompose()
    text = soup.get_text("\n")
    start = text.find("CPT Codes for the ABOS Hand Subspecialty Case List")
    if start < 0:
        raise RuntimeError("Could not find ABOS hand list heading in source page")
    text = text[start:]
    SOURCE_TEXT.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_TEXT.write_text(text, encoding="utf-8")
    return text


def extract_abos_hand_codes() -> tuple[list[dict], list[dict]]:
    text = extract_source_text().split("Skip to content")[0]
    rows = []
    current = None
    for line in [item.strip() for item in text.splitlines()]:
        if not line:
            continue
        if re.fullmatch(r"\d{5}", line):
            if current:
                rows.append(current)
            current = {"code": line, "description_parts": []}
        elif current:
            current["description_parts"].append(line)
    if current:
        rows.append(current)

    deduped: dict[str, dict] = {}
    duplicate_rows = []
    for row in rows:
        parsed = {
            "code": row["code"],
            "source_description": clean_description(" ".join(row["description_parts"])),
            "orthopedic_subsection": "Hand Surgery",
        }
        if parsed["code"] in deduped:
            duplicate_rows.append(parsed)
            continue
        deduped[parsed["code"]] = parsed
    return [deduped[code] for code in sorted(deduped)], duplicate_rows


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def number(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def load_cms_rvus() -> dict[str, dict]:
    if not CMS_JULY_NON_QPP.exists():
        return {}
    out: dict[str, dict] = {}
    with CMS_JULY_NON_QPP.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
        for _ in range(9):
            next(handle, None)
        reader = csv.reader(handle)
        next(reader, None)
        for row in reader:
            if len(row) < 15:
                continue
            code = row[0].strip()
            modifier = row[1].strip()
            if not re.fullmatch(r"\d{5}", code) or modifier:
                continue
            out[code] = {
                "description": row[2].strip(),
                "status_code": row[3].strip(),
                "work_rvu": number(row[5]),
                "pe_rvu": number(row[8]),
                "mp_rvu": number(row[10]),
                "total_rvu": number(row[12]),
                "global_period": row[14].strip(),
                "wrvu_source": CMS_SOURCE,
                "wrvu_source_file": CMS_SOURCE_FILE,
                "wrvu_source_url": CMS_SOURCE_URL,
            }
    return out


def global_days(value) -> int:
    if isinstance(value, int):
        return value
    value = str(value or "").strip()
    if value.isdigit():
        return int(value)
    if value == "YYY":
        return 90
    return 0


def modifiers_for(code: str, description: str, existing: list[str] | None = None) -> list[str]:
    mods = list(existing or [])
    desc = description.lower()
    if any(token in desc for token in ["finger", "thumb", "digit", "interphalangeal", "metacarpal", "phalangeal"]) and "-F1 to -F0" not in mods:
        mods.append("-F1 to -F0")
    if any(token in desc for token in ["hand", "wrist", "forearm", "elbow", "arm", "ulnar", "radial", "carpal"]) and "-LT" not in mods:
        mods.append("-LT")
    if any(token in desc for token in ["hand", "wrist", "forearm", "elbow", "arm", "ulnar", "radial", "carpal"]) and "-RT" not in mods:
        mods.append("-RT")
    return mods


def source_status(row: dict, cms: dict | None) -> tuple[str, str]:
    if cms is None:
        return "not_found_deleted_inactive", "Code is absent from current CMS RVU26C non-QPP source; likely deleted, inactive, or not valued in MPFS"
    if not number(cms.get("work_rvu")):
        return "no_work_rvu", "CMS source lists zero work RVU; likely unlisted, contractor-priced, add-on/global indicator, or non-valued"
    return "verified", ""


def hydrate_rvu_database(rvu_db: dict, cms_rows: dict[str, dict], rows: list[dict]) -> dict:
    rvu_db.setdefault("codes", {})
    for row in rows:
        code = row["code"]
        if code not in rvu_db["codes"] and code in cms_rows:
            cms = cms_rows[code]
            rvu_db["codes"][code] = {
                "description": cms["description"] or row["source_description"],
                "global_period": cms["global_period"],
                "mp_rvu": cms["mp_rvu"],
                "pe_rvu": cms["pe_rvu"],
                "total_rvu": cms["total_rvu"],
                "work_rvu": cms["work_rvu"],
                "wrvu_source": CMS_SOURCE,
                "wrvu_source_file": CMS_SOURCE_FILE,
                "wrvu_source_url": CMS_SOURCE_URL,
            }
    return rvu_db


def make_entry(row: dict, cms: dict | None, conversion_factor: float) -> dict:
    desc = row["source_description"] or (cms or {}).get("description") or f"CPT {row['code']}"
    total = number((cms or {}).get("total_rvu"))
    return {
        "addon_code": (cms or {}).get("global_period") == "ZZZ",
        "assistant_allowed": True,
        "bilateral_eligible": bool(re.search(r"\b(hand|wrist|forearm|elbow|arm|finger|thumb|digit|ulnar|radial|carpal)\b", desc, re.I)),
        "category": "Surgery",
        "code": row["code"],
        "code_family": "abos_hand_surgery",
        "cosurgeon_eligible": False,
        "description": desc,
        "estimated": cms is None,
        "global_period_days": global_days((cms or {}).get("global_period")),
        "hierarchy_tier": 2,
        "inclusive_of": [],
        "mp_rvu": number((cms or {}).get("mp_rvu")),
        "never_primary_with": [],
        "pe_rvu": number((cms or {}).get("pe_rvu")),
        "specialty": "orthopedic_surgery",
        "subcategory": "orthopedic_hand_surgery",
        "total_rvu": total,
        "typical_modifiers": modifiers_for(row["code"], desc),
        "work_rvu": number((cms or {}).get("work_rvu")),
        "wrvu_source": (cms or {}).get("wrvu_source", "Not found in current CMS MPFS source used by site"),
        "wrvu_source_file": (cms or {}).get("wrvu_source_file"),
        "wrvu_source_url": (cms or {}).get("wrvu_source_url"),
        "abos_hand_surgery": True,
        "abos_hand_source_url": SOURCE_URL,
        "hand_surgery_subsection": "Hand Surgery",
        "search_terms": ["ABOS hand surgery case list", "orthopedic hand surgery", "hand surgery", "orthopedic surgery"],
        "estimated_medicare_payment": round(total * conversion_factor, 2) if total else 0,
    }


def update_cpt_database(cpt_db: dict, rvu_db: dict, rows: list[dict]) -> tuple[dict, list[dict]]:
    conversion_factor = number(rvu_db.get("conversion_factor")) or 33.4009
    audit_rows = []
    for row in rows:
        code = row["code"]
        before = cpt_db.get(code)
        rvu_entry = rvu_db.get("codes", {}).get(code)
        status = "already_present" if before else "newly_added"
        if before:
            entry = before
            desc = row["source_description"]
            if entry.get("description", "").startswith("CPT ") or len(entry.get("description", "")) < 12:
                entry["description"] = desc
            entry["abos_hand_surgery"] = True
            entry["abos_hand_source_url"] = SOURCE_URL
            entry["hand_surgery_subsection"] = "Hand Surgery"
            entry["additional_specialties"] = sorted(set(entry.get("additional_specialties", []) + ["orthopedic_surgery"]))
            entry["subcategory"] = entry.get("subcategory") or "orthopedic_hand_surgery"
            if entry.get("code_family") in {"", None, "unclassified"}:
                entry["code_family"] = "abos_hand_surgery"
            terms = set(entry.get("search_terms", []))
            terms.update(["ABOS hand surgery case list", "orthopedic hand surgery", "hand surgery", "orthopedic surgery"])
            entry["search_terms"] = sorted(terms)
            entry["typical_modifiers"] = modifiers_for(code, entry.get("description") or desc, entry.get("typical_modifiers") or [])
            if rvu_entry:
                entry["estimated"] = False
                entry["work_rvu"] = rvu_entry.get("work_rvu", entry.get("work_rvu", 0))
                entry["pe_rvu"] = rvu_entry.get("pe_rvu", entry.get("pe_rvu", 0))
                entry["mp_rvu"] = rvu_entry.get("mp_rvu", entry.get("mp_rvu", 0))
                entry["total_rvu"] = rvu_entry.get("total_rvu", entry.get("total_rvu", 0))
                entry["global_period_days"] = global_days(rvu_entry.get("global_period", entry.get("global_period_days", 0)))
                entry["wrvu_source"] = rvu_entry.get("wrvu_source", entry.get("wrvu_source"))
                entry["wrvu_source_file"] = rvu_entry.get("wrvu_source_file", entry.get("wrvu_source_file"))
                entry["wrvu_source_url"] = rvu_entry.get("wrvu_source_url", entry.get("wrvu_source_url"))
            total = number(entry.get("total_rvu"))
            entry["estimated_medicare_payment"] = round(total * conversion_factor, 2) if total else 0
        else:
            cpt_db[code] = make_entry(row, rvu_entry, conversion_factor)

        wrvu_status, reason = source_status(row, rvu_entry)
        audit_rows.append({
            "code": code,
            "source_description": row["source_description"],
            "orthopedic_subsection": "Hand Surgery",
            "status": status,
            "wrvu_status": wrvu_status,
            "wrvu_missing_reason": reason,
            "work_rvu": cpt_db[code].get("work_rvu", 0),
            "total_rvu": cpt_db[code].get("total_rvu", 0),
            "global_period_days": cpt_db[code].get("global_period_days"),
            "estimated_medicare_payment": cpt_db[code].get("estimated_medicare_payment", 0),
            "cms_source_file": cpt_db[code].get("wrvu_source_file"),
        })
    return cpt_db, audit_rows


def update_specialty_hierarchy(rows: list[dict]) -> None:
    path = ROOT / "specialty_hierarchy.json"
    data = read_json(path)
    hand_codes = sorted({row["code"] for row in rows})
    for specialty in data.get("specialties", []):
        if specialty.get("id") != "orthopedic":
            continue
        systems = specialty.setdefault("systems", [])
        hand_system = next((system for system in systems if system.get("label") == "Hand Surgery"), None)
        if hand_system is None:
            hand_system = {"label": "Hand Surgery", "groups": []}
            systems.append(hand_system)
        group = next((item for item in hand_system.setdefault("groups", []) if item.get("label") == "ABOS Hand Surgery"), None)
        if group is None:
            group = {"label": "ABOS Hand Surgery", "codes": []}
            hand_system["groups"].append(group)
        group["codes"] = sorted(set(group.get("codes", [])) | set(hand_codes))
        break
    write_json(path, data)


def extract_specs(raw: str) -> tuple[int, int, dict]:
    marker = "const SPECS="
    start = raw.index(marker) + len(marker)
    in_str = False
    esc = False
    depth = 0
    end = None
    for i in range(start, len(raw)):
        ch = raw[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
    if end is None:
        raise RuntimeError("Could not locate SPECS object end")
    return start, end, json.loads(raw[start:end])


def update_index_specs(cpt_db: dict, rows: list[dict]) -> None:
    path = ROOT / "index.html"
    raw = path.read_text(encoding="utf-8")
    start, end, specs = extract_specs(raw)
    specs.setdefault(ORTHO_SPEC_KEY, [])
    by_code = {item[0]: item for item in specs[ORTHO_SPEC_KEY]}
    for row in rows:
        code = row["code"]
        if code in by_code:
            continue
        entry = cpt_db[code]
        bi = 1 if entry.get("bilateral_eligible") else 0
        by_code[code] = [
            code,
            f"Hand Surgery: {entry.get('description') or row['source_description']}",
            round(number(entry.get("work_rvu")), 2),
            bi,
        ]
    specs[ORTHO_SPEC_KEY] = sorted(by_code.values(), key=lambda item: item[0])
    encoded = json.dumps(specs, separators=(",", ":"), ensure_ascii=False)
    path.write_text(raw[:start] + encoded + raw[end:], encoding="utf-8")


def write_audit(audit_rows: list[dict], duplicate_rows: list[dict]) -> dict:
    AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated_at": date.today().isoformat(),
        "source_url": SOURCE_URL,
        "total_code_rows_extracted": len(audit_rows) + len(duplicate_rows),
        "total_codes_extracted": len(audit_rows),
        "codes_already_present": sum(1 for row in audit_rows if row["status"] == "already_present"),
        "codes_newly_added": sum(1 for row in audit_rows if row["status"] == "newly_added"),
        "codes_with_verified_wrvu": sum(1 for row in audit_rows if row["wrvu_status"] == "verified"),
        "codes_missing_wrvu_data": sum(1 for row in audit_rows if row["wrvu_status"] != "verified"),
        "codes_not_found_deleted_inactive": sum(1 for row in audit_rows if row["wrvu_status"] == "not_found_deleted_inactive"),
        "duplicates_removed": len(duplicate_rows),
        "duplicate_rows_removed": duplicate_rows,
        "rows": audit_rows,
    }
    write_json(AUDIT_JSON, summary)
    with AUDIT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit_rows[0].keys()))
        writer.writeheader()
        writer.writerows(audit_rows)
    return summary


def main() -> None:
    rows, duplicate_rows = extract_abos_hand_codes()
    cpt_db = read_json(ROOT / "cpt_database.json")
    rvu_db = read_json(ROOT / "rvu_database.json")
    cms_rows = load_cms_rvus()
    rvu_db = hydrate_rvu_database(rvu_db, cms_rows, rows)
    write_json(ROOT / "rvu_database.json", rvu_db)
    cpt_db, audit_rows = update_cpt_database(cpt_db, rvu_db, rows)
    write_json(ROOT / "cpt_database.json", dict(sorted(cpt_db.items())))
    update_specialty_hierarchy(rows)
    update_index_specs(cpt_db, rows)
    summary = write_audit(audit_rows, duplicate_rows)
    print(json.dumps({key: summary[key] for key in summary if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
