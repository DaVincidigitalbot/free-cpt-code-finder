#!/usr/bin/env python3
"""Phase 2D-C remediation for deleted/inactive legacy placeholder codes."""

from __future__ import annotations

import copy
import html
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEGACY_CODES = {"27193", "32405", "37228", "37230", "47500", "47511", "92921"}
BANNER = "This code is inactive/deleted and should not be used for current billing."
HISTORICAL_DESCRIPTORS = {
    "27193": "Closed treatment of pelvic ring fracture",
    "32405": "Biopsy, lung or mediastinum, percutaneous needle",
    "37228": "Revascularization, endovascular, open or percutaneous, tibial/peroneal artery",
    "37230": "Revascularization, endovascular, open or percutaneous, tibial/peroneal artery",
    "47500": "Injection procedure for percutaneous transhepatic cholangiography",
    "47511": "Introduction of percutaneous transhepatic stent for internal/external biliary drainage",
    "92921": "Percutaneous transluminal coronary angioplasty; each additional branch",
}
REVIEW_PENDING = {"37228", "37230", "92921"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def remove_code_cards_from_index(path: Path) -> int:
    text = path.read_text()
    removed = 0
    for code in LEGACY_CODES:
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


def remove_from_nested_lists(obj: Any) -> tuple[Any, int]:
    removed = 0
    if isinstance(obj, dict):
        new = {}
        for key, value in obj.items():
            if str(key) in LEGACY_CODES:
                removed += 1
                continue
            if isinstance(value, (dict, list)):
                filtered, count = remove_from_nested_lists(value)
                new[key] = filtered
                removed += count
            else:
                new[key] = value
        return new, removed
    if isinstance(obj, list):
        new_list = []
        for item in obj:
            if isinstance(item, str) and item in LEGACY_CODES:
                removed += 1
                continue
            if isinstance(item, dict):
                if str(item.get("column1", "")) in LEGACY_CODES or str(item.get("column2", "")) in LEGACY_CODES:
                    removed += 1
                    continue
                filtered, count = remove_from_nested_lists(item)
                new_list.append(filtered)
                removed += count
            elif isinstance(item, list):
                if any(str(part) in LEGACY_CODES for part in item):
                    removed += 1
                    continue
                filtered, count = remove_from_nested_lists(item)
                new_list.append(filtered)
                removed += count
            else:
                new_list.append(item)
        return new_list, removed
    return obj, 0


def legacy_page(code: str) -> str:
    descriptor = HISTORICAL_DESCRIPTORS[code]
    review_note = ""
    if code in REVIEW_PENDING:
        review_note = (
            "<p><strong>Replacement-family review pending:</strong> this informational page is retained "
            "without a redirect until the current code family is reviewed and approved.</p>"
        )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CPT {html.escape(code)}: inactive/deleted code | FreeCPTCodeFinder.com</title>
<meta name="description" content="CPT {html.escape(code)} is inactive/deleted and excluded from current active CPT search and Case Builder estimates.">
<link rel="canonical" href="https://freecptcodefinder.com/codes/{html.escape(code)}.html"><link rel="stylesheet" href="/styles/app-mode.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"MedicalWebPage","name":"CPT {html.escape(code)}: inactive/deleted code","url":"https://freecptcodefinder.com/codes/{html.escape(code)}.html","dateModified":"{date.today().isoformat()}"}}</script></head>
<body><main class="container code-page"><nav><a href="/">FreeCPTCodeFinder</a> / <a href="/codes/">CPT Codes</a> / CPT {html.escape(code)}</nav>
<h1>CPT {html.escape(code)} <span class="desc">Inactive/deleted CPT code</span></h1>
<section class="site-card" style="border-left:4px solid #b45309"><h2>Inactive/Deleted Code Notice</h2>
<p><strong>{html.escape(BANNER)}</strong></p>
<p>Historical descriptor retained for reference: {html.escape(descriptor)}.</p>
<p>This URL remains available for audit/history, but CPT {html.escape(code)} is excluded from active search, Case Builder selection, payable RVU estimates, and current CPT datasets.</p>
{review_note}
</section>
<p><strong>Source:</strong> CMS RVU26C July 2026 active CPT/RVU baseline did not include this code. Educational coding support only; confirm final billing against AMA CPT, CMS MPFS, NCCI, and payer policy.</p></main></body></html>
'''


def main() -> None:
    artifact_dir = ROOT / "qa_artifacts" / "phase2d_c_legacy_code_remediation_2026_06_11"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {"legacy_codes": sorted(LEGACY_CODES), "banner": BANNER}

    cpt_path = ROOT / "cpt_database.json"
    cpt = read_json(cpt_path)
    summary["archived_cpt_records"] = {code: copy.deepcopy(cpt.get(code)) for code in sorted(LEGACY_CODES)}
    for code in LEGACY_CODES:
        cpt.pop(code, None)
    write_json(cpt_path, cpt)

    modifier_path = ROOT / "modifier_rules.json"
    modifier_rules = read_json(modifier_path)
    summary["archived_modifier_rules"] = {code: copy.deepcopy(modifier_rules.get(code)) for code in sorted(LEGACY_CODES)}
    for code in LEGACY_CODES:
        modifier_rules.pop(code, None)
    write_json(modifier_path, modifier_rules)

    hierarchy_path = ROOT / "specialty_hierarchy.json"
    hierarchy = read_json(hierarchy_path)
    hierarchy, hierarchy_removed = remove_from_nested_lists(hierarchy)
    write_json(hierarchy_path, hierarchy)
    summary["specialty_hierarchy_entries_removed"] = hierarchy_removed

    ncci_path = ROOT / "ncci_bundles.json"
    ncci = read_json(ncci_path)
    ncci, ncci_removed = remove_from_nested_lists(ncci)
    write_json(ncci_path, ncci)
    summary["ncci_records_removed"] = ncci_removed

    for code in sorted(LEGACY_CODES):
        (ROOT / "codes" / f"{code}.html").write_text(legacy_page(code))

    summary["codes_index_cards_removed"] = remove_code_cards_from_index(ROOT / "codes" / "index.html")
    (artifact_dir / "legacy_code_archive.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
