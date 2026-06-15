#!/usr/bin/env python3
"""Validate homepage SPECS/search/Case Builder seed against canonical CPT JSON."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAND_SPECIALTY_LABEL = "Orthopedic Hand Surgery"


def load_json(name: str):
    with (ROOT / name).open() as f:
        return json.load(f)


def extract_specs(index_text: str) -> dict:
    marker = "const SPECS="
    start = index_text.find(marker)
    if start == -1:
        raise SystemExit("const SPECS= block not found")
    pos = index_text.find("{", start)
    depth = 0
    in_string: str | None = None
    escape = False
    for i in range(pos, len(index_text)):
        ch = index_text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
            continue
        if ch in {'"', "'"}:
            in_string = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(index_text[pos : i + 1])
    raise SystemExit("Could not parse SPECS object")


def num(value):
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def bi_value(entry: dict) -> int:
    indicator = str(entry.get("bilateral_indicator", "0"))
    if indicator == "2":
        return 2
    if entry.get("bilateral_eligible") or indicator == "1":
        return 1
    return 0


def global_value(entry: dict) -> int:
    try:
        return int(entry.get("global_period_days", entry.get("global_period", 0)))
    except (TypeError, ValueError):
        return 0


def is_orthopedic_hand_code(entry: dict) -> bool:
    return any(
        entry.get(field)
        for field in (
            "abos_hand_surgery",
            "hand_surgery_subsection",
            "orthopedic_hand_surgery_subsection",
        )
    ) or str(entry.get("specialty") or "").strip().lower().replace("_", " ") == "orthopedic hand surgery"


def extract_hub_codes() -> set[str]:
    hub_path = ROOT / "specialties" / "orthopedic-hand-surgery.html"
    if not hub_path.exists():
        return set()
    html = hub_path.read_text()
    return set(re.findall(r"[?&]q=(\d{5})", html))


def validate() -> dict:
    cpt_db = load_json("cpt_database.json")
    specs = extract_specs((ROOT / "index.html").read_text())
    spec_by_code = {}
    rows_by_code = {}
    duplicate_codes = []
    for specialty, rows in specs.items():
        for row in rows:
            code = str(row[0])
            rows_by_code.setdefault(code, []).append({"specialty": specialty, "row": row})
            if code in spec_by_code:
                duplicate_codes.append(code)
            spec_by_code.setdefault(code, {"specialty": specialty, "row": row})

    errors = []
    for code, entry in sorted(cpt_db.items()):
        if not str(code).isdigit() or len(str(code)) != 5:
            continue
        items = rows_by_code.get(str(code), [])
        if not items:
            errors.append({"type": "missing_homepage_specs_record", "code": code})
            continue
        for item in items:
            row = item["row"]
            checks = [
                ("description", row[1], entry.get("description")),
                ("work_rvu", num(row[2]), num(entry.get("work_rvu"))),
                ("bilateral_seed", row[3], bi_value(entry)),
                ("total_rvu", num(row[4]), num(entry.get("total_rvu"))),
                ("estimated_medicare_payment", num(row[5]), num(entry.get("estimated_medicare_payment"))),
                ("global_period_days", row[6], global_value(entry)),
                ("addon_code", bool(row[7]), bool(entry.get("addon_code"))),
            ]
            for field, observed, expected in checks:
                if observed != expected:
                    errors.append({"type": "homepage_specs_value_drift", "code": code, "specialty": item["specialty"], "field": field, "observed": observed, "expected": expected})

    duplicate_non_hand_codes = sorted(set(duplicate_codes) - {str(code) for code, entry in cpt_db.items() if is_orthopedic_hand_code(entry)})
    for code in duplicate_non_hand_codes:
        errors.append({"type": "duplicate_homepage_specs_record", "code": code})

    homepage_hand_codes = {str(row[0]) for row in specs.get(HAND_SPECIALTY_LABEL, [])}
    master_hand_codes = {str(code) for code, entry in cpt_db.items() if str(code).isdigit() and len(str(code)) == 5 and is_orthopedic_hand_code(entry)}
    hub_hand_codes = extract_hub_codes()
    if homepage_hand_codes != master_hand_codes:
        errors.append({
            "type": "orthopedic_hand_homepage_master_count_mismatch",
            "homepage_count": len(homepage_hand_codes),
            "master_count": len(master_hand_codes),
            "missing_from_homepage": sorted(master_hand_codes - homepage_hand_codes)[:50],
            "extra_in_homepage": sorted(homepage_hand_codes - master_hand_codes)[:50],
        })
    if hub_hand_codes != master_hand_codes:
        errors.append({
            "type": "orthopedic_hand_hub_master_count_mismatch",
            "hub_count": len(hub_hand_codes),
            "master_count": len(master_hand_codes),
            "missing_from_hub": sorted(master_hand_codes - hub_hand_codes)[:50],
            "extra_in_hub": sorted(hub_hand_codes - master_hand_codes)[:50],
        })
    return {
        "homepage_specs_count": sum(len(rows) for rows in specs.values()),
        "homepage_unique_cpt_count": len(spec_by_code),
        "canonical_numeric_cpt_count": sum(1 for code in cpt_db if str(code).isdigit() and len(str(code)) == 5),
        "orthopedic_hand_homepage_count": len(homepage_hand_codes),
        "orthopedic_hand_hub_count": len(hub_hand_codes),
        "orthopedic_hand_master_count": len(master_hand_codes),
        "hard_error_count": len(errors),
        "hard_errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    args = parser.parse_args()
    result = validate()
    if args.out:
        out = ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["homepage_specs_count", "homepage_unique_cpt_count", "canonical_numeric_cpt_count", "orthopedic_hand_homepage_count", "orthopedic_hand_hub_count", "orthopedic_hand_master_count", "hard_error_count"]}, indent=2))
    return 1 if result["hard_error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
