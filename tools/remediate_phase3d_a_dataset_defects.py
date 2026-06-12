#!/usr/bin/env python3
"""Phase 3D-A remediation for dataset-defect records marked inactive/deleted.

Removes unsafe records from active billing workflows while preserving public
code URLs with a clear inactive/deleted/not-supported warning.
"""

from __future__ import annotations

import copy
import csv
import html
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "phase3d_a_dataset_defect_batch1_2026_06_11"
SOURCE_CSV = ROOT / "qa_artifacts" / "phase3c_dataset_defect_investigation_2026_06_11" / "dataset_defect_117_investigation.csv"
BANNER = "This code is inactive, deleted, or not supported by the current CMS RVU26C dataset and should not be used for current billing."


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def load_codes() -> dict[str, dict[str, str]]:
    rows = {}
    with SOURCE_CSV.open(newline="") as fh:
        for row in csv.DictReader(fh):
            if row["classification"] == "should be inactive/deleted":
                rows[row["cpt_code"]] = row
    if len(rows) != 28:
        raise SystemExit(f"Expected 28 Phase 3D-A codes, found {len(rows)}")
    return dict(sorted(rows.items()))


def remove_codes_from_obj(obj: Any, codes: set[str]) -> tuple[Any, int]:
    removed = 0
    if isinstance(obj, dict):
        new = {}
        for key, value in obj.items():
            if str(key) in codes:
                removed += 1
                continue
            if isinstance(value, dict):
                direct_codes = {
                    str(value.get("column1", "")),
                    str(value.get("column2", "")),
                    str(value.get("code", "")),
                    str(value.get("primary_code", "")),
                    str(value.get("bundled_code", "")),
                }
                if direct_codes & codes:
                    removed += 1
                    continue
            filtered, count = remove_codes_from_obj(value, codes) if isinstance(value, (dict, list)) else (value, 0)
            new[key] = filtered
            removed += count
        return new, removed

    if isinstance(obj, list):
        new_list = []
        for item in obj:
            if isinstance(item, str) and item in codes:
                removed += 1
                continue
            if isinstance(item, dict):
                direct_codes = {
                    str(item.get("column1", "")),
                    str(item.get("column2", "")),
                    str(item.get("code", "")),
                    str(item.get("primary_code", "")),
                    str(item.get("bundled_code", "")),
                }
                if direct_codes & codes:
                    removed += 1
                    continue
            if isinstance(item, list) and any(str(part) in codes for part in item):
                removed += 1
                continue
            filtered, count = remove_codes_from_obj(item, codes) if isinstance(item, (dict, list)) else (item, 0)
            new_list.append(filtered)
            removed += count
        return new_list, removed

    return obj, 0


def prune_code_references(obj: Any, codes: set[str]) -> tuple[Any, int]:
    """Remove nested legacy references even when they appear inside strings."""
    removed = 0

    def contains_code(value: Any) -> bool:
        text = str(value)
        return any(code in text for code in codes)

    if isinstance(obj, dict):
        new = {}
        for key, value in obj.items():
            if contains_code(key):
                removed += 1
                continue
            if isinstance(value, str) and contains_code(value):
                removed += 1
                continue
            if isinstance(value, (dict, list)):
                filtered, count = prune_code_references(value, codes)
                new[key] = filtered
                removed += count
            else:
                new[key] = value
        return new, removed

    if isinstance(obj, list):
        new_list = []
        for item in obj:
            if isinstance(item, str) and contains_code(item):
                removed += 1
                continue
            if isinstance(item, list) and any(isinstance(part, str) and part in codes for part in item):
                removed += 1
                continue
            if isinstance(item, (dict, list)):
                filtered, count = prune_code_references(item, codes)
                new_list.append(filtered)
                removed += count
            else:
                new_list.append(item)
        return new_list, removed

    return obj, 0


def remove_code_cards_from_index(path: Path, codes: set[str]) -> int:
    text = path.read_text()
    removed = 0
    for code in sorted(codes):
        patterns = [
            f'<a class="code-card" href="{code}.html">',
            f'<a href="/codes/{code}.html" class="code-card">',
            f'<a href="{code}.html" class="code-card">',
        ]
        start = min((pos for marker in patterns if (pos := text.find(marker)) != -1), default=-1)
        while start != -1:
            end = text.find("</a>", start)
            if end == -1:
                break
            text = text[:start] + text[end + len("</a>") :]
            removed += 1
            start = min((pos for marker in patterns if (pos := text.find(marker)) != -1), default=-1)
    path.write_text(text)
    return removed


def remove_dx_entries_from_index(path: Path, codes: set[str]) -> int:
    text = path.read_text()
    removed = 0
    for code in sorted(codes):
        before = text
        text = "\n".join(line for line in text.splitlines() if f"'{code}':" not in line)
        if text != before:
            removed += 1
    path.write_text(text + "\n")
    return removed


def disable_umbilical_guided_flow(path: Path) -> bool:
    text = path.read_text()
    start = text.find(" if(guidedState.kind==='umbilical-hernia'){")
    if start == -1:
        return False
    end = text.find("\n}\n\nfunction buildSearchIndexFromSpecs", start)
    if end == -1:
        raise SystemExit("Could not locate end of umbilical hernia guided-flow block")
    replacement = """ if(guidedState.kind==='umbilical-hernia'){
  el.innerHTML='<div class="sec-h surg" style="border:0;padding:0;margin:0 0 8px">Umbilical Hernia</div><div>This legacy guided pathway is inactive because its prior CPT codes are no longer supported by the current CMS RVU26C dataset.</div><div style="margin-top:12px"><button class="lat-cancel" onclick="cancelGuidedFlow()">cancel</button></div>';
  return;
 }"""
    path.write_text(text[:start] + replacement + text[end:])
    return True


def remove_reason_text_references(obj: Any, codes: set[str]) -> tuple[Any, int]:
    removed = 0
    if isinstance(obj, dict):
        new = {}
        for key, value in obj.items():
            if isinstance(value, str) and any(code in value for code in codes):
                new[key] = "Legacy inactive/deleted add-on code is not separately billable and cannot be bypassed with modifier -59."
                removed += 1
            elif isinstance(value, (dict, list)):
                new[key], count = remove_reason_text_references(value, codes)
                removed += count
            else:
                new[key] = value
        return new, removed
    if isinstance(obj, list):
        new_list = []
        for item in obj:
            if isinstance(item, str) and any(code in item for code in codes):
                removed += 1
                continue
            if isinstance(item, (dict, list)):
                item, count = remove_reason_text_references(item, codes)
                removed += count
            new_list.append(item)
        return new_list, removed
    return obj, 0


def inactive_page(code: str, row: dict[str, str]) -> str:
    descriptor = row["descriptor"]
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CPT {html.escape(code)}: inactive/deleted code | FreeCPTCodeFinder.com</title>
<meta name="description" content="CPT {html.escape(code)} is inactive, deleted, or not supported by the current CMS RVU26C dataset and excluded from active CPT search and Case Builder estimates.">
<link rel="canonical" href="https://freecptcodefinder.com/codes/{html.escape(code)}.html"><link rel="stylesheet" href="/styles/app-mode.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"MedicalWebPage","name":"CPT {html.escape(code)}: inactive/deleted code","url":"https://freecptcodefinder.com/codes/{html.escape(code)}.html","dateModified":"{date.today().isoformat()}"}}</script></head>
<body><main class="container code-page"><nav><a href="/">FreeCPTCodeFinder</a> / <a href="/codes/">CPT Codes</a> / CPT {html.escape(code)}</nav>
<h1>CPT {html.escape(code)} <span class="desc">Inactive/deleted CPT code</span></h1>
<section class="site-card" style="border-left:4px solid #b45309"><h2>Inactive/Deleted Code Notice</h2>
<p><strong>{html.escape(BANNER)}</strong></p>
<p>Historical descriptor retained for reference: {html.escape(descriptor)}.</p>
<p>This URL remains available for audit/history, but CPT {html.escape(code)} is excluded from active search, Case Builder selection, payable RVU estimates, modifier-rule workflows, and current CPT datasets.</p>
</section>
<p><strong>Source:</strong> Phase 3D-A dataset-defect remediation. CMS RVU26C July 2026 active CPT/RVU baseline did not include this code. Educational coding support only; confirm final billing against AMA CPT, CMS MPFS, NCCI, and payer policy.</p></main></body></html>
'''


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    code_rows = load_codes()
    codes = set(code_rows)
    archive_path = ARTIFACT_DIR / "dataset_defect_batch1_archive.json"
    summary: dict[str, Any] = json.loads(archive_path.read_text()) if archive_path.exists() else {"codes": sorted(codes), "banner": BANNER}
    summary["codes"] = sorted(codes)
    summary["banner"] = BANNER

    cpt_path = ROOT / "cpt_database.json"
    cpt = read_json(cpt_path)
    summary["before_cpt_count"] = sum(1 for code in cpt if str(code).isdigit() and len(str(code)) == 5)
    summary.setdefault("archived_cpt_records", {})
    for code in sorted(codes):
        summary["archived_cpt_records"].setdefault(code, copy.deepcopy(cpt.get(code)))
    for code in codes:
        cpt.pop(code, None)
    write_json(cpt_path, cpt)
    summary["after_cpt_count"] = sum(1 for code in cpt if str(code).isdigit() and len(str(code)) == 5)

    rvu_path = ROOT / "rvu_database.json"
    rvu = read_json(rvu_path)
    summary.setdefault("archived_rvu_records", {})
    for code in sorted(codes):
        summary["archived_rvu_records"].setdefault(code, copy.deepcopy(rvu.get("codes", {}).get(code)))
    for code in codes:
        rvu.get("codes", {}).pop(code, None)
    write_json(rvu_path, rvu)

    modifier_path = ROOT / "modifier_rules.json"
    modifier_rules = read_json(modifier_path)
    summary.setdefault("archived_modifier_rules", {})
    for code in sorted(codes):
        summary["archived_modifier_rules"].setdefault(code, copy.deepcopy(modifier_rules.get(code)))
    for code in codes:
        modifier_rules.pop(code, None)
    write_json(modifier_path, modifier_rules)

    decision_path = ROOT / "cpt_decision_tree.json"
    decision_tree = read_json(decision_path)
    decision_tree, decision_removed = remove_codes_from_obj(decision_tree, codes)
    decision_tree, decision_pruned = prune_code_references(decision_tree, codes)
    write_json(decision_path, decision_tree)
    summary["cpt_decision_tree_entries_removed"] = decision_removed + decision_pruned

    hierarchy_path = ROOT / "specialty_hierarchy.json"
    hierarchy = read_json(hierarchy_path)
    hierarchy, hierarchy_removed = remove_codes_from_obj(hierarchy, codes)
    write_json(hierarchy_path, hierarchy)
    summary["specialty_hierarchy_entries_removed"] = hierarchy_removed

    ncci_path = ROOT / "ncci_bundles.json"
    ncci = read_json(ncci_path)
    ncci, ncci_removed = remove_codes_from_obj(ncci, codes)
    ncci, ncci_reason_refs_removed = remove_reason_text_references(ncci, codes)
    write_json(ncci_path, ncci)
    summary["ncci_records_removed"] = ncci_removed
    summary["ncci_reason_references_removed"] = ncci_reason_refs_removed

    for code, row in code_rows.items():
        (ROOT / "codes" / f"{code}.html").write_text(inactive_page(code, row))

    summary["codes_index_cards_removed"] = remove_code_cards_from_index(ROOT / "codes" / "index.html", codes)
    summary["homepage_dx_entries_removed"] = remove_dx_entries_from_index(ROOT / "index.html", codes)
    summary["umbilical_guided_flow_disabled"] = disable_umbilical_guided_flow(ROOT / "index.html")

    subprocess.check_call(["python3", "scripts/build_homepage_specs.py"], cwd=ROOT)

    archive_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
