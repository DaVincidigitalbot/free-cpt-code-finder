#!/usr/bin/env python3
"""Phase 3E metadata cleanup for active pages with descriptor mismatch."""

from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa_artifacts" / "phase3e_metadata_cleanup_2026_06_11"
CODES = ["37220", "37221", "37224", "37226", "47510", "92929"]


def num(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def money(value) -> str:
    return "$" + f"{num(value):,.2f}"


def extract_metadata(code: str, text: str, canonical: str) -> dict[str, str]:
    def match(pattern: str, strip_tags: bool = False) -> str:
        found = re.search(pattern, text, re.I | re.S)
        if not found:
            return ""
        value = found.group(1).strip()
        if strip_tags:
            value = re.sub(r"<[^>]+>", "", value)
        return html.unescape(value)

    title = match(r"<title>(.*?)</title>")
    h1 = match(r"<h1[^>]*>(.*?)</h1>", strip_tags=True)
    meta = match(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']')
    return {
        "cpt_code": code,
        "canonical_descriptor": canonical,
        "title": title,
        "h1": h1,
        "meta_description": meta,
        "title_matches": str(canonical in title),
        "h1_matches": str(canonical in h1),
        "meta_matches": str(canonical in meta),
    }


def set_meta(text: str, prop: str, value: str, attr: str = "name") -> str:
    pattern = rf'(<meta\s+{attr}=["\']{re.escape(prop)}["\']\s+content=["\'])(.*?)(["\'])'
    replacement = lambda m: m.group(1) + html.escape(value, quote=True) + m.group(3)
    return re.sub(pattern, replacement, text, flags=re.I | re.S)


def update_json_ld(text: str, code: str, title: str, meta_description: str, canonical: str) -> str:
    pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.I | re.S)

    def replace(match: re.Match[str]) -> str:
        try:
            payload = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)

        graph = payload.get("@graph", [])
        if graph:
            page = graph[0]
            if isinstance(page, dict):
                page["name"] = title
                page["description"] = meta_description

        for node in graph:
            if not isinstance(node, dict) or node.get("@type") != "FAQPage":
                continue
            for question in node.get("mainEntity", []):
                if not isinstance(question, dict):
                    continue
                if question.get("name") != f"What is CPT code {code}?":
                    continue
                answer = question.get("acceptedAnswer")
                if isinstance(answer, dict):
                    answer["text"] = canonical

        return match.group(1) + json.dumps(payload, separators=(",", ":")) + match.group(3)

    return pattern.sub(replace, text, count=1)


def cleanup_page(code: str, entry: dict) -> tuple[dict[str, str], dict[str, str]]:
    page = ROOT / "codes" / f"{code}.html"
    text = page.read_text(errors="ignore")
    canonical = str(entry.get("description") or "").strip()
    before = extract_metadata(code, text, canonical)

    work = num(entry.get("work_rvu"))
    total = num(entry.get("total_rvu"))
    payment = money(entry.get("estimated_medicare_payment", entry.get("medicare_payment", 0)))
    title = f"CPT {code}: {canonical} | FreeCPTCodeFinder.com"
    meta_description = (
        f"CPT code {code} - {canonical}. Work RVU: {work:.2f}, "
        f"total RVU: {total:.2f}, estimated Medicare payment: {payment}."
    )

    text = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", text, flags=re.I | re.S)
    text = set_meta(text, "description", meta_description, "name")
    text = set_meta(text, "og:title", title, "property")
    text = set_meta(text, "og:description", meta_description, "property")
    text = set_meta(text, "twitter:title", title, "name")
    text = set_meta(text, "twitter:description", meta_description, "name")
    text = re.sub(
        rf"(<h1[^>]*>\s*CPT\s+{re.escape(code)}\s*<span class=[\"']desc[\"']>)(.*?)(</span>\s*</h1>)",
        lambda m: m.group(1) + html.escape(canonical) + m.group(3),
        text,
        flags=re.I | re.S,
    )
    text = update_json_ld(text, code, title, meta_description, canonical)

    page.write_text(text)
    after = extract_metadata(code, text, canonical)
    return before, after


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cpt = json.loads((ROOT / "cpt_database.json").read_text())
    before_rows = []
    after_rows = []
    for code in CODES:
        before, after = cleanup_page(code, cpt[code])
        before_rows.append(before)
        after_rows.append(after)
    write_csv(OUT / "metadata_before.csv", before_rows)
    write_csv(OUT / "metadata_after.csv", after_rows)
    summary = {
        "codes": CODES,
        "before_all_match": all(row["title_matches"] == row["h1_matches"] == row["meta_matches"] == "True" for row in before_rows),
        "after_all_match": all(row["title_matches"] == row["h1_matches"] == row["meta_matches"] == "True" for row in after_rows),
        "changed_pages": [f"codes/{code}.html" for code in CODES],
    }
    (OUT / "metadata_cleanup_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
