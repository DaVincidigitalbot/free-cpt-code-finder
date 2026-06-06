#!/usr/bin/env python3
"""Import ABOS sports medicine CPT codes into FreeCPTCodeFinder orthopedic data."""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PDF_TEXT = ROOT / "tmp" / "abos_sports_import" / "sports-cpt-updated.txt"
CMS_JULY_NON_QPP = ROOT / "tmp" / "abos_sports_import" / "rvu26c" / "PPRRVU2026_Jul_nonQPP.csv"
AUDIT_JSON = ROOT / "audit_reports" / "abos_sports_orthopedic_import_2026-06-06.json"
AUDIT_CSV = ROOT / "audit_reports" / "abos_sports_orthopedic_import_2026-06-06.csv"
SOURCE_URL = "https://www.abos.org/wp-content/uploads/2019/12/sports-cpt-updated.pdf"
CMS_SOURCE_URL = "https://www.cms.gov/files/zip/rvu26c.zip"
CMS_SOURCE = "CMS PFS RVU26C July 2026 non-QPP"
CMS_SOURCE_FILE = "PPRRVU2026_Jul_nonQPP.csv"

ORTHO_SPEC_KEY = "General Orthopedic Surgery"

CATEGORY_MAP = {
    "GENERAL": "General",
    "SHOULDER": "Shoulder",
    "HUMERUS (UPPER ARM) AND ELBOW": "Humerus/Upper Arm/Elbow",
    "FOREARM AND WRIST": "Forearm/Wrist",
    "HAND OR FINGERS": "Hand/Fingers",
    "PELVIS AND HIP JOINT": "Pelvis/Hip",
    "FEMUR (THIGH REGION) AND KNEE JOINT": "Femur/Knee",
    "LEG (TIBIA AND FIBULA) AND ANKLE JOINT": "Leg/Ankle/Foot",
    "FOOT AND TOES": "Leg/Ankle/Foot",
    "ENDOSCOPY/ARTHROSCOPY": "Arthroscopy codes",
    "NEUROPLASTY (EXPLORATION, NEUROLYSIS, OR NREVE DECOMPRESSION": "Neuroplasty",
}

ORTHO_SYSTEM_ORDER = [
    "General",
    "Shoulder",
    "Humerus/Upper Arm/Elbow",
    "Forearm/Wrist",
    "Hand/Fingers",
    "Pelvis/Hip",
    "Femur/Knee",
    "Leg/Ankle/Foot",
    "Arthroscopy codes",
    "Neuroplasty",
]


def normalize_description(value: str) -> str:
    value = re.sub(r"\s+", " ", value.replace("\f", " ")).strip()
    value = value.replace(" ;", ";").replace(" ,", ",")
    return value


def extract_abos_codes() -> list[dict]:
    raw = PDF_TEXT.read_text(encoding="utf-8")
    current = None
    rows: list[dict] = []
    for line in raw.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        cleaned = cleaned.replace("\f", "").strip()
        upper = cleaned.upper()
        if upper in CATEGORY_MAP:
            current = CATEGORY_MAP[upper]
            continue
        if upper.startswith("NEUROPLASTY"):
            current = CATEGORY_MAP["NEUROPLASTY (EXPLORATION, NEUROLYSIS, OR NREVE DECOMPRESSION"]
            continue
        match = re.match(r"^(\d{5})\s+(.+)$", cleaned)
        if match:
            rows.append({
                "code": match.group(1),
                "abos_description": normalize_description(match.group(2)),
                "orthopedic_subsection": current or "Other",
            })
        elif rows and current:
            rows[-1]["abos_description"] = normalize_description(
                rows[-1]["abos_description"] + " " + cleaned
            )

    deduped: dict[str, dict] = {}
    duplicate_rows = []
    for row in rows:
        code = row["code"]
        if code in deduped:
            duplicate_rows.append(row)
            if row["orthopedic_subsection"] not in deduped[code]["all_abos_subsections"]:
                deduped[code]["all_abos_subsections"].append(row["orthopedic_subsection"])
            continue
        row["all_abos_subsections"] = [row["orthopedic_subsection"]]
        deduped[code] = row

    ordered = [deduped[code] for code in sorted(deduped)]
    return ordered, duplicate_rows


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def money(value: str | int | float | None) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def load_cms_july_rvus() -> dict[str, dict]:
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
                "work_rvu": money(row[5]),
                "pe_rvu": money(row[8]),
                "mp_rvu": money(row[10]),
                "total_rvu": money(row[12]),
                "global_period": row[14].strip(),
                "wrvu_source": CMS_SOURCE,
                "wrvu_source_file": CMS_SOURCE_FILE,
                "wrvu_source_url": CMS_SOURCE_URL,
            }
    return out


def hydrate_site_rvu_database(rvu_db: dict, cms_rows: dict[str, dict], abos_rows: list[dict]) -> dict:
    rvu_db.setdefault("codes", {})
    for row in abos_rows:
        code = row["code"]
        if code not in rvu_db["codes"] and code in cms_rows:
            rvu_db["codes"][code] = {
                "description": cms_rows[code]["description"] or row["abos_description"],
                "global_period": cms_rows[code]["global_period"],
                "mp_rvu": cms_rows[code]["mp_rvu"],
                "pe_rvu": cms_rows[code]["pe_rvu"],
                "total_rvu": cms_rows[code]["total_rvu"],
                "work_rvu": cms_rows[code]["work_rvu"],
                "wrvu_source": CMS_SOURCE,
                "wrvu_source_file": CMS_SOURCE_FILE,
                "wrvu_source_url": CMS_SOURCE_URL,
            }
    return rvu_db


def as_specialty_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def family_for_subsection(subsection: str) -> str:
    slug = subsection.lower()
    slug = slug.replace("/", "_").replace("&", "and")
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    return f"abos_sports_{slug or 'other'}"


def typical_modifiers_for(row: dict, entry: dict | None) -> list[str]:
    existing = list((entry or {}).get("typical_modifiers") or [])
    desc = row["abos_description"].lower()
    subsection = row["orthopedic_subsection"]
    if subsection in {"Shoulder", "Humerus/Upper Arm/Elbow", "Forearm/Wrist", "Pelvis/Hip", "Femur/Knee", "Leg/Ankle/Foot", "Arthroscopy codes", "Neuroplasty"}:
        for mod in ["-LT", "-RT"]:
            if mod not in existing:
                existing.append(mod)
    if subsection == "Hand/Fingers":
        for mod in ["-F1 to -F0"]:
            if mod not in existing:
                existing.append(mod)
    if "toe" in desc and "-T1 to -T9" not in existing:
        existing.append("-T1 to -T9")
    return existing


def make_entry(row: dict, rvu_entry: dict | None, conversion_factor: float) -> dict:
    work_rvu = (rvu_entry or {}).get("work_rvu", 0)
    total_rvu = (rvu_entry or {}).get("total_rvu", 0)
    global_period = (rvu_entry or {}).get("global_period", 0)
    if global_period == "YYY":
        global_days = 90
    elif global_period in {"ZZZ", "XXX"}:
        global_days = 0
    else:
        try:
            global_days = int(global_period)
        except (TypeError, ValueError):
            global_days = 0
    desc = row["abos_description"] or (rvu_entry or {}).get("description") or f"CPT {row['code']}"
    return {
        "addon_code": global_period == "ZZZ",
        "assistant_allowed": True,
        "bilateral_eligible": row["orthopedic_subsection"] not in {"General"},
        "category": "Surgery",
        "code": row["code"],
        "code_family": family_for_subsection(row["orthopedic_subsection"]),
        "cosurgeon_eligible": False,
        "description": desc,
        "estimated": False if rvu_entry else True,
        "global_period_days": global_days,
        "hierarchy_tier": 2,
        "inclusive_of": [],
        "mp_rvu": (rvu_entry or {}).get("mp_rvu", 0),
        "never_primary_with": [],
        "orthopedic_subsection": row["orthopedic_subsection"],
        "abos_sports_medicine": True,
        "abos_source_url": SOURCE_URL,
        "pe_rvu": (rvu_entry or {}).get("pe_rvu", 0),
        "search_terms": [
            "orthopedic surgery",
            "orthopaedic sports medicine",
            "ABOS sports medicine case list",
            row["orthopedic_subsection"],
        ],
        "specialty": "orthopedic_surgery",
        "subcategory": "orthopedic_sports_medicine",
        "total_rvu": total_rvu,
        "typical_modifiers": typical_modifiers_for(row, None),
        "work_rvu": work_rvu,
        "wrvu_source": (rvu_entry or {}).get("wrvu_source", "Not found in current CMS MPFS source used by site"),
        "wrvu_source_file": (rvu_entry or {}).get("wrvu_source_file"),
        "wrvu_source_url": (rvu_entry or {}).get("wrvu_source_url"),
        "estimated_medicare_payment": round(float(total_rvu or 0) * conversion_factor, 2) if total_rvu else 0,
    }


def update_cpt_database(cpt_db: dict, rvu_db: dict, rows: list[dict], prior_status: dict[str, str]) -> tuple[dict, list[dict]]:
    conversion_factor = float(rvu_db.get("conversion_factor") or 0)
    audit_rows = []
    for row in rows:
        code = row["code"]
        before = cpt_db.get(code)
        rvu_entry = rvu_db.get("codes", {}).get(code)
        status = prior_status.get(code) or ("already_present" if before else "newly_added")
        if before:
            entry = before
            if entry.get("description", "").startswith("CPT ") or len(entry.get("description", "")) < 12:
                entry["description"] = row["abos_description"]
            entry["abos_sports_medicine"] = True
            entry["abos_source_url"] = SOURCE_URL
            entry["orthopedic_subsection"] = row["orthopedic_subsection"]
            entry["additional_specialties"] = sorted(set(entry.get("additional_specialties", []) + ["orthopedic_surgery"]))
            entry["subcategory"] = entry.get("subcategory") or "orthopedic_sports_medicine"
            entry["code_family"] = entry.get("code_family") if entry.get("code_family") not in {"unclassified", "", None} else family_for_subsection(row["orthopedic_subsection"])
            entry["typical_modifiers"] = typical_modifiers_for(row, entry)
            search_terms = set(entry.get("search_terms", []))
            search_terms.update([
                "orthopedic surgery",
                "orthopaedic sports medicine",
                "ABOS sports medicine case list",
                row["orthopedic_subsection"],
            ])
            entry["search_terms"] = sorted(search_terms)
            if rvu_entry:
                entry["estimated"] = False
                entry["work_rvu"] = rvu_entry.get("work_rvu", entry.get("work_rvu", 0))
                entry["pe_rvu"] = rvu_entry.get("pe_rvu", entry.get("pe_rvu", 0))
                entry["mp_rvu"] = rvu_entry.get("mp_rvu", entry.get("mp_rvu", 0))
                entry["total_rvu"] = rvu_entry.get("total_rvu", entry.get("total_rvu", 0))
                gp = rvu_entry.get("global_period", entry.get("global_period_days", 0))
                if isinstance(gp, int):
                    entry["global_period_days"] = gp
                elif str(gp).isdigit():
                    entry["global_period_days"] = int(gp)
                entry["wrvu_source"] = rvu_entry.get("wrvu_source", entry.get("wrvu_source"))
                entry["wrvu_source_file"] = rvu_entry.get("wrvu_source_file", entry.get("wrvu_source_file"))
                entry["wrvu_source_url"] = rvu_entry.get("wrvu_source_url", entry.get("wrvu_source_url"))
            total_rvu = entry.get("total_rvu") or 0
            entry["estimated_medicare_payment"] = round(float(total_rvu) * conversion_factor, 2) if total_rvu else 0
        else:
            entry = make_entry(row, rvu_entry, conversion_factor)
            cpt_db[code] = entry

        work = cpt_db[code].get("work_rvu") or 0
        total = cpt_db[code].get("total_rvu") or 0
        if not rvu_entry:
            wrvu_status = "not_found_in_site_mpfs_source"
            reason = "Code absent from current RVU26C non-QPP file used by site"
        elif not work:
            wrvu_status = "no_work_rvu"
            reason = "CMS source lists zero work RVU; likely unlisted, contractor-priced, add-on/global indicator, deleted, or non-valued"
        else:
            wrvu_status = "verified"
            reason = ""

        audit_rows.append({
            "code": code,
            "abos_description": row["abos_description"],
            "orthopedic_subsection": row["orthopedic_subsection"],
            "status": status,
            "wrvu_status": wrvu_status,
            "wrvu_missing_reason": reason,
            "work_rvu": work,
            "total_rvu": total,
            "global_period_days": cpt_db[code].get("global_period_days"),
            "estimated_medicare_payment": cpt_db[code].get("estimated_medicare_payment", 0),
            "cms_source_file": cpt_db[code].get("wrvu_source_file"),
        })
    return cpt_db, audit_rows


def update_public_copy(cpt_db: dict) -> None:
    public_path = ROOT / "public" / "cpt_database.json"
    if public_path.exists():
        write_json(public_path, cpt_db)


def update_public_rvu_copy(rvu_db: dict) -> None:
    public_path = ROOT / "public" / "rvu_database.json"
    if public_path.exists():
        write_json(public_path, rvu_db)


def update_specialty_hierarchy(rows: list[dict]) -> None:
    path = ROOT / "specialty_hierarchy.json"
    data = load_json(path)
    by_section = {section: [] for section in ORTHO_SYSTEM_ORDER}
    for row in rows:
        by_section.setdefault(row["orthopedic_subsection"], []).append(row["code"])

    systems = []
    for section in ORTHO_SYSTEM_ORDER:
        codes = sorted(set(by_section.get(section, [])))
        if not codes:
            continue
        systems.append({
            "label": section,
            "groups": [{
                "label": f"ABOS Sports Medicine - {section}",
                "codes": codes,
            }],
        })

    for specialty in data.get("specialties", []):
        if specialty.get("id") == "orthopedic":
            existing_codes = []
            for system in specialty.get("systems", []):
                for group in system.get("groups", []):
                    existing_codes.extend(group.get("codes", []))
            existing = set(existing_codes)
            for system in systems:
                for group in system["groups"]:
                    group["codes"] = sorted(set(group["codes"]) | (existing & set(group["codes"])))
            specialty["systems"] = systems
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
    existing = {item[0] for item in specs.get(ORTHO_SPEC_KEY, [])}
    additions = []
    for row in rows:
        code = row["code"]
        entry = cpt_db[code]
        if code in existing:
            continue
        bi = 1 if entry.get("bilateral_eligible") else 0
        additions.append([
            code,
            f"{row['orthopedic_subsection']}: {entry.get('description') or row['abos_description']}",
            round(float(entry.get("work_rvu") or 0), 2),
            bi,
        ])
    specs.setdefault(ORTHO_SPEC_KEY, [])
    specs[ORTHO_SPEC_KEY].extend(sorted(additions, key=lambda x: x[0]))
    specs[ORTHO_SPEC_KEY] = sorted({item[0]: item for item in specs[ORTHO_SPEC_KEY]}.values(), key=lambda x: x[0])
    encoded = json.dumps(specs, separators=(",", ":"), ensure_ascii=False)
    path.write_text(raw[:start] + encoded + raw[end:], encoding="utf-8")


def write_audit(audit_rows: list[dict], duplicate_rows: list[dict]) -> dict:
    AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated_at": date.today().isoformat(),
        "source_pdf": SOURCE_URL,
        "total_codes_extracted": len(audit_rows),
        "codes_already_present": sum(1 for row in audit_rows if row["status"] == "already_present"),
        "codes_newly_added": sum(1 for row in audit_rows if row["status"] == "newly_added"),
        "codes_with_verified_wrvu": sum(1 for row in audit_rows if row["wrvu_status"] == "verified"),
        "codes_missing_wrvu_data": sum(1 for row in audit_rows if row["wrvu_status"] != "verified"),
        "codes_not_found_deleted_inactive": sum(1 for row in audit_rows if row["wrvu_status"] == "not_found_in_site_mpfs_source"),
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


def prior_import_status() -> dict[str, str]:
    if not AUDIT_JSON.exists():
        return {}
    try:
        data = load_json(AUDIT_JSON)
    except json.JSONDecodeError:
        return {}
    return {str(row["code"]): row.get("status", "already_present") for row in data.get("rows", [])}


def main() -> None:
    rows, duplicate_rows = extract_abos_codes()
    prior_status = prior_import_status()
    cpt_db = load_json(ROOT / "cpt_database.json")
    rvu_db = load_json(ROOT / "rvu_database.json")
    cms_rows = load_cms_july_rvus()
    rvu_db = hydrate_site_rvu_database(rvu_db, cms_rows, rows)
    write_json(ROOT / "rvu_database.json", rvu_db)
    update_public_rvu_copy(rvu_db)
    cpt_db, audit_rows = update_cpt_database(cpt_db, rvu_db, rows, prior_status)
    write_json(ROOT / "cpt_database.json", dict(sorted(cpt_db.items())))
    update_public_copy(dict(sorted(cpt_db.items())))
    update_specialty_hierarchy(rows)
    update_index_specs(cpt_db, rows)
    summary = write_audit(audit_rows, duplicate_rows)
    print(json.dumps({key: summary[key] for key in summary if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
