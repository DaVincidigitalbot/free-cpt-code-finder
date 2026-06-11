#!/usr/bin/env python3
"""Phase 2D-A remediation for deleted legacy ventral/incisional hernia codes.

Keeps the public code URLs alive, but removes deleted codes from active data
sources used by search, Case Builder, modifier rules, and NCCI lookups.
"""

from __future__ import annotations

import copy
import html
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DELETED_CODES = {"49560", "49561", "49565", "49570", "49572", "49655"}
BANNER = (
    "⚠️ This CPT code is inactive/deleted and should not be used for current billing. "
    "See current ventral/incisional hernia coding guidance."
)
GUIDE_LINK = "/blog/guides/cpt-code-ventral-hernia-repair.html"
FAMILY_LINK = "/coding-centers/hernia-coding-center.html"
CURRENT_FAMILY_CODES = [
    "49591", "49593", "49595", "49596", "49613", "49615", "49617", "49618", "49621", "49622",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def remove_deleted_from_obj(obj: Any) -> tuple[Any, int]:
    """Recursively remove list/dict records directly tied to deleted codes."""
    removed = 0
    if isinstance(obj, dict):
        new = {}
        for key, value in obj.items():
            if str(key) in DELETED_CODES:
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
                if direct_codes & DELETED_CODES:
                    removed += 1
                    continue
                filtered, count = remove_deleted_from_obj(value)
                new[key] = filtered
                removed += count
            elif isinstance(value, list):
                filtered, count = remove_deleted_from_obj(value)
                new[key] = filtered
                removed += count
            else:
                new[key] = value
        return new, removed

    if isinstance(obj, list):
        new_list = []
        for item in obj:
            if isinstance(item, dict):
                direct_codes = {
                    str(item.get("column1", "")),
                    str(item.get("column2", "")),
                    str(item.get("code", "")),
                    str(item.get("primary_code", "")),
                    str(item.get("bundled_code", "")),
                }
                if direct_codes & DELETED_CODES:
                    removed += 1
                    continue
                filtered, count = remove_deleted_from_obj(item)
                new_list.append(filtered)
                removed += count
            elif isinstance(item, list):
                if any(str(part) in DELETED_CODES for part in item):
                    removed += 1
                    continue
                filtered, count = remove_deleted_from_obj(item)
                new_list.append(filtered)
                removed += count
            elif str(item) in DELETED_CODES:
                removed += 1
            else:
                new_list.append(item)
        return new_list, removed

    return obj, 0


def remove_from_specialty_hierarchy(data: Any) -> tuple[Any, int]:
    removed = 0

    def walk(node: Any) -> Any:
        nonlocal removed
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, list):
            out = []
            for item in node:
                if isinstance(item, str) and item in DELETED_CODES:
                    removed += 1
                    continue
                out.append(walk(item))
            return out
        return node

    return walk(data), removed


def deleted_code_page(code: str) -> str:
    title = f"CPT {code}: inactive/deleted code | FreeCPTCodeFinder.com"
    desc = f"CPT {code} is inactive/deleted and excluded from current active CPT search and Case Builder estimates."
    family_links = "".join(
        f'<li><a href="/codes/{html.escape(c)}.html">CPT {html.escape(c)}</a></li>' for c in CURRENT_FAMILY_CODES
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="https://freecptcodefinder.com/codes/{html.escape(code)}.html"><link rel="stylesheet" href="/styles/app-mode.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"MedicalWebPage","name":"CPT {html.escape(code)}: inactive/deleted code","url":"https://freecptcodefinder.com/codes/{html.escape(code)}.html","dateModified":"{date.today().isoformat()}"}}</script></head>
<body><main class="container code-page"><nav><a href="/">FreeCPTCodeFinder</a> / <a href="/codes/">CPT Codes</a> / CPT {html.escape(code)}</nav>
<h1>CPT {html.escape(code)} <span class="desc">Inactive/deleted CPT code</span></h1>
<section class="site-card" style="border-left:4px solid #b45309"><h2>Deleted Code Notice</h2>
<p><strong>{html.escape(BANNER)}</strong></p>
<p>This URL is retained for reference, but CPT {html.escape(code)} is excluded from active search, Case Builder selection, payable RVU estimates, and current CPT datasets.</p>
</section>
<section class="site-card"><h2>Current Hernia Coding Resources</h2>
<ul>
<li><a href="{GUIDE_LINK}">Current ventral/incisional hernia coding guidance</a></li>
<li><a href="{FAMILY_LINK}">Current hernia CPT family pages</a></li>
{family_links}
</ul></section>
<p><strong>Source:</strong> CMS RVU26C July 2026 active CPT/RVU baseline did not include this code. Educational coding support only; confirm final billing against AMA CPT, CMS MPFS, NCCI, and payer policy.</p></main></body></html>
'''


def remove_code_cards_from_index(path: Path) -> int:
    text = path.read_text()
    removed = 0
    for code in DELETED_CODES:
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


def main() -> None:
    artifact_dir = ROOT / "qa_artifacts" / "phase2d_a_deleted_hernia_2026_06_11"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    archive_path = artifact_dir / "deleted_hernia_archive.json"
    summary: dict[str, Any] = (
        json.loads(archive_path.read_text()) if archive_path.exists() else {"deleted_codes": sorted(DELETED_CODES)}
    )

    cpt_path = ROOT / "cpt_database.json"
    cpt = read_json(cpt_path)
    summary.setdefault("archived_cpt_records", {})
    for code in sorted(DELETED_CODES):
        summary["archived_cpt_records"].setdefault(code, copy.deepcopy(cpt.get(code)))
    for code in DELETED_CODES:
        cpt.pop(code, None)
    write_json(cpt_path, cpt)

    modifier_path = ROOT / "modifier_rules.json"
    modifier_rules = read_json(modifier_path)
    summary.setdefault("archived_modifier_rules", {})
    for code in sorted(DELETED_CODES):
        summary["archived_modifier_rules"].setdefault(code, copy.deepcopy(modifier_rules.get(code)))
    for code in DELETED_CODES:
        modifier_rules.pop(code, None)
    write_json(modifier_path, modifier_rules)

    hierarchy_path = ROOT / "specialty_hierarchy.json"
    hierarchy = read_json(hierarchy_path)
    hierarchy, hierarchy_removed = remove_from_specialty_hierarchy(hierarchy)
    write_json(hierarchy_path, hierarchy)
    summary["specialty_hierarchy_entries_removed"] = hierarchy_removed

    ncci_path = ROOT / "ncci_bundles.json"
    ncci = read_json(ncci_path)
    summary.setdefault("archived_ncci_records", {
        "top_level_keys": {code: copy.deepcopy(ncci.get("bundles", {}).get(code)) for code in sorted(DELETED_CODES)},
        "common_pairs": [
            row for row in ncci.get("common_pairs", [])
            if str(row.get("column1")) in DELETED_CODES or str(row.get("column2")) in DELETED_CODES
        ],
    })
    ncci, ncci_removed = remove_deleted_from_obj(ncci)
    write_json(ncci_path, ncci)
    summary["ncci_records_removed"] = ncci_removed

    for code in sorted(DELETED_CODES):
        (ROOT / "codes" / f"{code}.html").write_text(deleted_code_page(code))

    summary["codes_index_cards_removed"] = remove_code_cards_from_index(ROOT / "codes" / "index.html")
    summary["banner"] = BANNER
    summary["links"] = {"guide": GUIDE_LINK, "family": FAMILY_LINK, "current_family_codes": CURRENT_FAMILY_CODES}
    archive_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
