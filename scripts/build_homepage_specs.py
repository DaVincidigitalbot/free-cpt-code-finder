#!/usr/bin/env python3
"""Regenerate homepage SPECS from canonical CPT JSON.

This keeps homepage search and Case Builder seed data from becoming a manually
maintained second source of truth.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


SPECIALTY_LABELS = {
    "general_surgery": "General Surgery",
    "hernia_repair": "Hernia Repair",
    "cardiac_electrophysiology": "Cardiac Electrophysiology",
    "interventional_radiology": "Interventional Radiology",
    "vascular_surgery": "Vascular Surgery",
    "orthopedic_surgery": "General Orthopedic Surgery",
    "hand_surgery": "Hand Surgery",
    "neurosurgery": "Neurosurgery",
    "urology": "Urology",
    "obgyn": "OB/GYN",
    "gynecology": "OB/GYN",
    "ophthalmology": "Ophthalmology",
    "otolaryngology": "Otolaryngology (ENT)",
    "ent": "Otolaryngology (ENT)",
    "oralmaxillofacial": "Oralmaxillofacial (OMFS)",
    "anesthesia": "Anesthesia",
}


def load_json(name: str):
    with (ROOT / name).open() as f:
        return json.load(f)


def specialty_label(entry: dict) -> str:
    raw = str(entry.get("specialty") or entry.get("category") or "Database").strip()
    key = raw.lower().replace(" ", "_").replace("-", "_")
    if key in SPECIALTY_LABELS:
        return SPECIALTY_LABELS[key]
    if raw.lower() == "surgery":
        return "Surgery"
    return raw.replace("_", " ").title() if raw else "Database"


def bi_value(entry: dict) -> int:
    indicator = str(entry.get("bilateral_indicator", "0"))
    if indicator == "2":
        return 2
    if entry.get("bilateral_eligible") or indicator == "1":
        return 1
    return 0


def global_value(entry: dict) -> int:
    value = entry.get("global_period_days", entry.get("global_period", 0))
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def build_specs() -> dict[str, list[list]]:
    cpt_db = load_json("cpt_database.json")
    specs: dict[str, list[list]] = {}
    for code, entry in sorted(cpt_db.items()):
        if not re.fullmatch(r"\d{5}", str(code)):
            continue
        desc = str(entry.get("description") or "").strip()
        if not desc:
            continue
        row = [
            str(code),
            desc,
            round(float(entry.get("work_rvu") or 0), 2),
            bi_value(entry),
            round(float(entry.get("total_rvu") or 0), 2),
            round(float(entry.get("estimated_medicare_payment") or 0), 2),
            global_value(entry),
            bool(entry.get("addon_code")),
        ]
        specs.setdefault(specialty_label(entry), []).append(row)
    return dict(sorted(specs.items(), key=lambda item: item[0]))


def replace_specs(index_text: str, specs: dict[str, list[list]]) -> str:
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
                end = i + 1
                if end < len(index_text) and index_text[end] == ";":
                    end += 1
                payload = "const SPECS=" + json.dumps(specs, separators=(",", ":")) + ";"
                return index_text[:start] + payload + index_text[end:]
    raise SystemExit("Could not parse SPECS object")


def main() -> int:
    specs = build_specs()
    INDEX.write_text(replace_specs(INDEX.read_text(), specs))
    total = sum(len(rows) for rows in specs.values())
    print(json.dumps({"specialties": len(specs), "codes": total}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
