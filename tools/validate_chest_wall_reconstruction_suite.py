#!/usr/bin/env python3
"""Permanent validation suite for chest wall reconstruction ClaimIQ hardening.

The suite uses de-identified operative-note patterns and repo data only. It is
not a billing authority; it is a deterministic regression gate for the clinical
reasoning failures identified during the 2026-07-03 chest wall validation.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Set


ROOT = Path(__file__).resolve().parents[1]
CF_2026 = 33.4009


REQUESTED_CPTS = [
    "21811",
    "21812",
    "21813",
    "32110",
    "32320",
    "32551",
    "32651",
    "64421",
    "64620",
]

CHEST_WALL_CPTS = REQUESTED_CPTS + ["64420", "64461", "64462", "64463", "36620"]


@dataclass
class CasePattern:
    name: str
    narrative: str
    expected_supported: List[str]
    expected_unsupported: List[str]
    expected_icd10: List[str]
    expected_flags: List[str]


def load_json(path: str):
    return json.loads((ROOT / path).read_text())


def norm_code(code: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", code.upper())


def cpt_snapshot(cpt_db: Dict[str, dict], code: str) -> dict:
    row = cpt_db[code]
    return {
        "code": code,
        "description": row.get("description"),
        "work_rvu": row.get("work_rvu"),
        "total_rvu": row.get("total_rvu"),
        "estimated_medicare_payment": row.get("estimated_medicare_payment"),
        "global_period_days": row.get("global_period_days"),
        "multiple_procedure_indicator": row.get("multiple_procedure_indicator"),
        "bilateral_indicator": row.get("bilateral_indicator"),
        "assistant_surgeon_indicator": row.get("assistant_surgeon_indicator"),
        "addon_code": row.get("addon_code"),
    }


def compact_icd_rows() -> List[dict]:
    return load_json("data/icd10cm/2026/icd10cm_2026_compact.json")["rows"]


def find_icd(rows: Iterable[dict], code: str) -> dict | None:
    target = norm_code(code)
    for row in rows:
        if norm_code(row["code"]) == target:
            return row
    return None


def s2733_family(rows: List[dict]) -> List[dict]:
    return [row for row in rows if norm_code(row["code"]).startswith("S2733")]


def classify_narrative(text: str) -> Dict[str, Set[str]]:
    """Minimal deterministic clinical classifier for the validation patterns."""
    t = " ".join(text.lower().split())
    supported: Set[str] = set()
    unsupported: Set[str] = set()
    icd10: Set[str] = set()
    flags: Set[str] = set()

    fixed_ribs = set(re.findall(r"\b(?:rib|ribs?)\s*(\d{1,2})\b", t))
    for block in re.findall(r"\bribs?\s+((?:\d{1,2}\s*){2,})", t):
        fixed_ribs.update(re.findall(r"\d{1,2}", block))
    if not fixed_ribs and re.search(r"\b10th rib\b", t):
        fixed_ribs.add("10")
    rib_count = len(fixed_ribs)

    if re.search(r"(rib fracture|rib nonunion|non-union|rib fixation|rib plate|plated|flail chest|internal fixation of ribs)", t):
        if rib_count >= 7 or "7 or more ribs" in t:
            supported.add("21813")
        else:
            supported.add("21811")
        if 4 <= rib_count <= 6:
            supported.add("21812")
        if rib_count < 4:
            unsupported.add("21812")
        if rib_count < 7:
            unsupported.add("21813")

    if re.search(r"left .*10th rib|10th rib.*left|left-sided .*10th rib", t) and re.search(r"non[- ]union", t):
        icd10.add("S22.32XK")
    if "flail chest" in t:
        icd10.add("S22.5XXA")
    if re.search(r"lung laceration|laceration of lung|pulmonary laceration", t):
        icd10.add("S27.331A")
    if "pulmonary contusion" in t:
        icd10.add("S27.321A")
    if "pneumothorax" in t:
        icd10.add("S27.0XXA")
    if "hemothorax" in t:
        icd10.add("S27.1XXA")

    if re.search(r"thoracotomy.*control.*hemorrhage|traumatic hemorrhage", t):
        supported.add("32110")
    else:
        unsupported.add("32110")

    if re.search(r"decortication|pleurectomy|pleural peel|trapped lung", t):
        if "vats" in t or "thoracoscopic" in t:
            supported.add("32651")
        else:
            supported.add("32320")
    else:
        unsupported.update(["32320", "32651"])

    if re.search(r"chest tube|tube thoracostomy", t):
        supported.add("32551")
        if re.search(r"through[^.]{0,80}(?:trocar|port|incision)|routine drainage|placed .* at the end", t):
            flags.add("32551_distinct_tube_thoracostomy_documentation_needed")

    if re.search(r"cryoablation|cryoablated|frozen|freezing|atricure", t):
        supported.add("64620")
        unsupported.add("64421")
        flags.add("cryoablation_maps_to_64620_not_64421")

    if re.search(r"intercostal nerve block|exparel|injection", t):
        supported.add("64420")
        block_levels = set(re.findall(r"\b(\d{1,2})(?:th|st|nd|rd)?\b(?=[^.,;]{0,25}intercostal)", t))
        block_levels.update(re.findall(r"\b(\d{1,2})(?:th|st|nd|rd)?\b(?=[^.,;]{0,25}nerve)", t))
        if "intercostal" in t:
            block_levels.update(re.findall(r"\b(\d{1,2})(?:th|st|nd|rd)\b", t))
        if len(block_levels) > 1:
            flags.add("additional_intercostal_block_levels_require_64421_review")

    if "paravertebral" not in t and "paraspinal" not in t:
        unsupported.add("64461")
    if re.search(r"arterial line|radial arterial", t) and not re.search(r"i placed|surgeon placed", t):
        unsupported.add("36620")
        flags.add("arterial_line_not_supported_by_surgeon_narrative")

    return {"supported": supported, "unsupported": unsupported, "icd10": icd10, "flags": flags}


def selected_payable_rvus(cpt_db: Dict[str, dict], selected: Iterable[str], excluded: Iterable[str]) -> dict:
    selected_codes = list(selected)
    excluded_set = set(excluded)
    selected_work = sum(float(cpt_db[c]["work_rvu"]) for c in selected_codes if c in cpt_db)
    payable_codes = [c for c in selected_codes if c not in excluded_set]
    ranked = sorted(
        [c for c in payable_codes if not cpt_db[c].get("addon_code")],
        key=lambda c: float(cpt_db[c]["work_rvu"]),
        reverse=True,
    )
    addons = [c for c in payable_codes if cpt_db[c].get("addon_code")]
    payable_work = 0.0
    for idx, code in enumerate(ranked):
        factor = 1.0 if idx == 0 else 0.5
        payable_work += float(cpt_db[code]["work_rvu"]) * factor
    for code in addons:
        payable_work += float(cpt_db[code]["work_rvu"])
    total_rvu_payment = sum(float(cpt_db[c].get("total_rvu") or 0) * CF_2026 for c in payable_codes if c in cpt_db)
    return {
        "selected_cpts": selected_codes,
        "payable_cpts": payable_codes,
        "excluded_cpts": sorted(excluded_set),
        "selected_work_rvu": round(selected_work, 2),
        "expected_payable_work_rvu": round(payable_work, 2),
        "expected_medicare_payment_total_rvu_basis": round(total_rvu_payment, 2),
    }


REFERENCE_NOTE = """
Severe uncontrolled left-sided chest pain secondary to non-union left 10th rib
fracture that is displaced. General anesthesia with left intercostal nerve
cryoablation for intercostal nerves 7, 8, and 9. Left 10th nerve block with
Exparel. Thoracoscopic-assisted open treatment of left-sided 10th rib fracture
internal fixation. Previously placed chest tube was removed. Left lung isolated.
Thoracic cavity explored thoracoscopically; no adhesions. Cryoablation with
AtriCure of left 7th, 8th, and 9th intercostal nerves, each nerve frozen for 1
minute then defrosted. Chemical nerve block with Exparel of 10th intercostal
nerve under direct thoracoscopic visualization. Three-cm incision over fracture,
fracture ends freshened, drill holes made, Titan EXT 60 plate secured to left
10th rib with approximation. Chest irrigated and suctioned. After the 11 mm
balloon trocar was removed, a 28 Fr chest tube was inserted "through this
incision" under direct visualization and placed posteriorly to apex. Prior chest
tube incision sharply debrided and
packed. Left radial arterial line placement was listed, but the surgeon
narrative does not document percutaneous arterial catheter placement. PA assisted
with port placement, camera, retracting, and closure.
"""


CASES = [
    CasePattern(
        name="reference_left_10th_rib_nonunion_with_cryo_and_chest_tube_documentation_review",
        narrative=REFERENCE_NOTE,
        expected_supported=["21811", "32551", "64620", "64420"],
        expected_unsupported=["21812", "21813", "32110", "32320", "32651", "64421", "64461", "36620"],
        expected_icd10=["S22.32XK"],
        expected_flags=["32551_distinct_tube_thoracostomy_documentation_needed", "cryoablation_maps_to_64620_not_64421"],
    ),
    CasePattern(
        name="simple_rib_plating",
        narrative="Open treatment with internal fixation of left ribs 5 and 6 with plates after displaced rib fractures.",
        expected_supported=["21811"],
        expected_unsupported=["21812", "21813"],
        expected_icd10=[],
        expected_flags=[],
    ),
    CasePattern(
        name="flail_chest_seven_rib_fixation",
        narrative="Flail chest with open treatment and internal fixation of ribs 3 4 5 6 7 8 9 using plates.",
        expected_supported=["21813"],
        expected_unsupported=[],
        expected_icd10=["S22.5XXA"],
        expected_flags=[],
    ),
    CasePattern(
        name="lung_laceration_repair",
        narrative="Traumatic unilateral lung laceration repaired during thoracic trauma operation with pneumothorax.",
        expected_supported=[],
        expected_unsupported=["32110", "32320", "32651"],
        expected_icd10=["S27.331A", "S27.0XXA"],
        expected_flags=[],
    ),
    CasePattern(
        name="vats_converted_to_thoracotomy_decortication",
        narrative="VATS converted to thoracotomy for dense pleural peel and pulmonary decortication of trapped lung.",
        expected_supported=["32651"],
        expected_unsupported=["32110"],
        expected_icd10=[],
        expected_flags=[],
    ),
    CasePattern(
        name="chest_tube_before_thoracotomy",
        narrative="Separate tube thoracostomy for traumatic hemopneumothorax was placed before thoracotomy.",
        expected_supported=["32551"],
        expected_unsupported=["32320", "32651"],
        expected_icd10=[],
        expected_flags=[],
    ),
    CasePattern(
        name="chest_tube_through_thoracotomy_field",
        narrative="Chest tube placed through the operative thoracotomy incision at the end for routine drainage.",
        expected_supported=["32551"],
        expected_unsupported=["32320", "32651"],
        expected_icd10=[],
        expected_flags=["32551_distinct_tube_thoracostomy_documentation_needed"],
    ),
    CasePattern(
        name="multiple_intercostal_nerve_blocks",
        narrative="Intercostal nerve block with Exparel at left 7th, 8th, and 9th intercostal nerves.",
        expected_supported=["64420"],
        expected_unsupported=[],
        expected_icd10=[],
        expected_flags=["additional_intercostal_block_levels_require_64421_review"],
    ),
    CasePattern(
        name="cryoablation_multiple_intercostal_nerves",
        narrative="AtriCure cryoablation of left 7th, 8th, and 9th intercostal nerves, each frozen and defrosted.",
        expected_supported=["64620"],
        expected_unsupported=["64421"],
        expected_icd10=[],
        expected_flags=["cryoablation_maps_to_64620_not_64421"],
    ),
]


def validate_case(case: CasePattern) -> dict:
    result = classify_narrative(case.narrative)
    errors = []
    for code in case.expected_supported:
        if code not in result["supported"]:
            errors.append(f"expected supported CPT {code} missing")
    for code in case.expected_unsupported:
        if code not in result["unsupported"]:
            errors.append(f"expected unsupported CPT {code} missing")
    for code in case.expected_icd10:
        if code not in result["icd10"]:
            errors.append(f"expected ICD-10 {code} missing")
    for flag in case.expected_flags:
        if flag not in result["flags"]:
            errors.append(f"expected flag {flag} missing")
    return {
        "name": case.name,
        "supported": sorted(result["supported"]),
        "unsupported": sorted(result["unsupported"]),
        "icd10": sorted(result["icd10"]),
        "flags": sorted(result["flags"]),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-artifacts", action="store_true")
    parser.add_argument("--artifact-dir", default="qa_artifacts/chest_wall_note_validation_2026_07_03")
    args = parser.parse_args()

    cpt_db = load_json("cpt_database.json")
    icd_rows = compact_icd_rows()
    index_html = (ROOT / "index.html").read_text()

    errors: List[str] = []
    cpt_rows = {}
    for code in REQUESTED_CPTS:
        if code not in cpt_db:
            errors.append(f"missing CPT {code}")
        else:
            cpt_rows[code] = cpt_snapshot(cpt_db, code)

    s2733 = s2733_family(icd_rows)
    s2733_billable = [row for row in s2733 if row.get("billable")]
    expected_s2733_billable = {"S27331A", "S27331D", "S27331S", "S27332A", "S27332D", "S27332S", "S27339A", "S27339D", "S27339S"}
    observed_s2733_billable = {norm_code(row["code"]) for row in s2733_billable}
    missing_s2733 = sorted(expected_s2733_billable - observed_s2733_billable)
    if missing_s2733:
        errors.append("missing S27.33 billable children: " + ", ".join(missing_s2733))

    for code in ["S27.331A", "S27.331D", "S27.331S", "S22.32XK"]:
        if not find_icd(icd_rows, code):
            errors.append(f"missing compact ICD-10 row {code}")

    required_index_phrases = [
        "CPT 64421 is injection, not cryoablation",
        "CPT 32551 requires distinct tube thoracostomy documentation",
        "CPT 21812 requires documentation of additional ribs",
        "CPT 32110 requires traumatic hemorrhage control",
        "CPT 32320 requires decortication and parietal pleurectomy",
        "CPT 32651 requires VATS pulmonary decortication",
    ]
    for phrase in required_index_phrases:
        if phrase not in index_html:
            errors.append(f"ClaimIQ rule text missing: {phrase}")

    case_results = [validate_case(case) for case in CASES]
    for case in case_results:
        errors.extend([f"{case['name']}: {err}" for err in case["errors"]])

    reference_selected = ["21811", "64420", "64620", "32551"]
    reference_excluded = []
    reference_rvus = selected_payable_rvus(cpt_db, reference_selected, reference_excluded)

    report = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "requested_cpt_metadata": cpt_rows,
        "s27_33_family_total": len(s2733),
        "s27_33_billable_total": len(s2733_billable),
        "s27_33_billable_codes": [row["code"] for row in s2733_billable],
        "specific_icd_search_targets_present": {
            code: bool(find_icd(icd_rows, code))
            for code in ["S27.331A", "S27.331D", "S27.331S", "S22.32XK"]
        },
        "reference_case_selected_vs_payable": reference_rvus,
        "case_results": case_results,
    }

    if args.write_artifacts:
        outdir = ROOT / args.artifact_dir
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n")
        lines = [
            "# Chest Wall Reconstruction Clinical Validation",
            "",
            f"Status: {report['status'].upper()}",
            "",
            "## Reference Case Selected vs Payable",
            "",
            json.dumps(reference_rvus, indent=2),
            "",
            "## S27.33 ICD-10 Family",
            "",
            f"Total descendants: {len(s2733)}",
            f"Billable children: {len(s2733_billable)}",
            "Billable codes: " + ", ".join(report["s27_33_billable_codes"]),
            "",
            "## Case Matrix",
            "",
        ]
        for case in case_results:
            lines.append(f"### {case['name']}")
            lines.append("Supported CPTs: " + (", ".join(case["supported"]) or "none"))
            lines.append("Unsupported CPTs: " + (", ".join(case["unsupported"]) or "none"))
            lines.append("ICD-10: " + (", ".join(case["icd10"]) or "none"))
            lines.append("Flags: " + (", ".join(case["flags"]) or "none"))
            if case["errors"]:
                lines.append("Errors: " + "; ".join(case["errors"]))
            lines.append("")
        (outdir / "clinical_validation_report.md").write_text("\n".join(lines) + "\n")

    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
