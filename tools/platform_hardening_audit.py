#!/usr/bin/env python3
"""Platform integrity gate for FreeCPTCodeFinder generated data."""

from __future__ import annotations

import argparse
import csv
import html as html_lib
import json
import os
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONVERSION_FACTOR = 33.4009
CMS_CSV_NAME = "PPRRVU2026_Jul_nonQPP.csv"
CMS_ZIP_CANDIDATES = [
    ROOT / "qa_artifacts" / "phase2d_b_source_review_2026_06_11" / "cms" / "rvu26c.zip",
    ROOT / "tmp" / "rvu26c.zip",
]
INACTIVE_MARKERS = (
    "inactive/deleted and should not be used for current billing",
    "This code is inactive/deleted and should not be used for current billing.",
)


def load_json(path: Path) -> Any:
    with path.open() as fh:
        return json.load(fh)


def number(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_indicator(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text.upper()


def normalize_global(value: Any) -> str:
    text = normalize_indicator(value)
    symbolic = {"000": "0", "010": "10", "090": "90", "MMM": "MMM", "XXX": "XXX", "YYY": "YYY", "ZZZ": "ZZZ"}
    return symbolic.get(text, text)


def descriptor_bad(description: Any, code: str) -> bool:
    text = str(description or "").strip()
    if not text:
        return True
    if text.upper() in {f"CPT {code}", "CPT XXXX", "XXXX"}:
        return True
    if re.fullmatch(r"CPT\s+X{4}(\s+CPT\s+X{4})?", text, flags=re.I):
        return True
    return False


def is_code(value: str) -> bool:
    return bool(re.fullmatch(r"\d{5}", str(value)))


def active_codes(cpt_db: dict[str, Any]) -> set[str]:
    return {code for code in cpt_db if is_code(code)}


def inactive_page_codes() -> set[str]:
    codes: set[str] = set()
    codes_dir = ROOT / "codes"
    if not codes_dir.exists():
        return codes
    for page in codes_dir.glob("*.html"):
        code = page.stem
        if not is_code(code):
            continue
        text = page.read_text(errors="ignore")
        if any(marker in text for marker in INACTIVE_MARKERS):
            codes.add(code)
    return codes


def extract_specs() -> dict[str, list[Any]]:
    index_path = ROOT / "index.html"
    html = index_path.read_text(errors="ignore")
    marker = "const SPECS="
    start = html.find(marker)
    if start == -1:
        raise RuntimeError("index.html does not contain const SPECS=")
    pos = html.find("{", start)
    depth = 0
    in_string: str | None = None
    escape = False
    end = None
    for i in range(pos, len(html)):
        ch = html[i]
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
                break
    if end is None:
        raise RuntimeError("Could not find end of SPECS object")
    raw = html[pos:end]
    specs = json.loads(raw)
    by_code: dict[str, list[Any]] = {}
    for rows in specs.values():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if row:
                by_code[str(row[0])] = row
    return by_code


def cms_zip_path() -> Path | None:
    env_path = os.environ.get("CMS_RVU26C_ZIP")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    for candidate in CMS_ZIP_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def load_cms_rows() -> tuple[dict[str, dict[str, str]], str]:
    path = cms_zip_path()
    if not path:
        return {}, "missing"
    with zipfile.ZipFile(path) as archive:
        with archive.open(CMS_CSV_NAME) as fh:
            lines = fh.read().decode("latin1").splitlines()
    rows: dict[str, dict[str, str]] = {}
    reader = csv.reader(lines[10:])
    for row in reader:
        if len(row) < 23:
            continue
        code = row[0].strip()
        modifier = row[1].strip()
        if not is_code(code) or modifier:
            continue
        rows[code] = {
            "description": row[2].strip(),
            "status_code": row[3].strip(),
            "work_rvu": row[5].strip(),
            "pe_rvu": row[6].strip(),
            "mp_rvu": row[10].strip(),
            "total_rvu": row[11].strip(),
            "global": row[14].strip(),
            "multiple": row[18].strip(),
            "bilateral": row[19].strip(),
            "assistant": row[20].strip(),
            "cosurgeon": row[21].strip(),
            "team": row[22].strip(),
        }
    return rows, str(path)


def add_error(errors: list[dict[str, Any]], category: str, code: str, message: str, **extra: Any) -> None:
    errors.append({"category": category, "code": code, "message": message, **extra})


def validate_descriptors(cpt_db: dict[str, Any], inactive: set[str], errors: list[dict[str, Any]]) -> int:
    count = 0
    for code in sorted(active_codes(cpt_db) - inactive):
        record = cpt_db.get(code, {})
        if descriptor_bad(record.get("description"), code):
            count += 1
            add_error(errors, "descriptor", code, "Active CPT has missing or placeholder descriptor", descriptor=record.get("description"))
    return count


def validate_rvus(cpt_db: dict[str, Any], rvu_db: dict[str, Any], inactive: set[str], errors: list[dict[str, Any]]) -> int:
    count = 0
    for code in sorted(active_codes(cpt_db)):
        record = cpt_db.get(code, {})
        total = number(record.get("total_rvu"))
        if code not in inactive and total == 0:
            count += 1
            add_error(errors, "rvu", code, "Active CPT has 0.00 total RVU without inactive/deleted classification")
        rvu_record = rvu_db.get(code)
        if rvu_record:
            fields = ("work_rvu", "practice_expense_rvu", "malpractice_rvu", "total_rvu")
            diffs = {field: [record.get(field), rvu_record.get(field)] for field in fields if abs(number(record.get(field)) - number(rvu_record.get(field))) > 0.01}
            if diffs:
                count += 1
                add_error(errors, "rvu", code, "cpt_database.json differs from rvu_database.json", diffs=diffs)
        expected_payment = round(total * CONVERSION_FACTOR, 2)
        actual_payment = round(number(record.get("medicare_payment", record.get("estimated_medicare_payment"))), 2)
        if total and abs(expected_payment - actual_payment) > 0.02:
            count += 1
            add_error(errors, "rvu", code, "Medicare estimate does not match total RVU times conversion factor", expected=expected_payment, actual=actual_payment)
    return count


def validate_indicators(cpt_db: dict[str, Any], cms_rows: dict[str, dict[str, str]], cms_source: str, inactive: set[str], errors: list[dict[str, Any]]) -> int:
    if not cms_rows:
        add_error(errors, "indicator", "ALL", "CMS RVU26C baseline was not found", source=cms_source)
        return 1
    count = 0
    mapping = {
        "assistant_surgeon_indicator": ("assistant", normalize_indicator),
        "cosurgeon_indicator": ("cosurgeon", normalize_indicator),
        "bilateral_indicator": ("bilateral", normalize_indicator),
        "multiple_procedure_indicator": ("multiple", normalize_indicator),
        "team_surgeon_indicator": ("team", normalize_indicator),
        "global_period_days": ("global", normalize_global),
    }
    for code in sorted(active_codes(cpt_db) - inactive):
        cms = cms_rows.get(code)
        if not cms:
            continue
        record = cpt_db.get(code, {})
        diffs = {}
        for site_field, (cms_field, normalizer) in mapping.items():
            site = normalizer(record.get(site_field))
            cms_value = normalizer(cms.get(cms_field))
            if site_field == "global_period_days":
                alternate = normalizer(record.get("global_period_indicator"))
                if alternate == cms_value:
                    site = alternate
            if site != cms_value:
                diffs[site_field] = {"site": site, "cms": cms_value}
        if diffs:
            count += len(diffs)
            add_error(errors, "indicator", code, "Indicator fields differ from CMS RVU26C baseline", diffs=diffs)
    return count


def validate_specs(cpt_db: dict[str, Any], specs: dict[str, list[Any]], inactive: set[str], errors: list[dict[str, Any]]) -> int:
    count = 0
    canonical = active_codes(cpt_db) - inactive
    spec_codes = set(specs)
    missing = sorted(canonical - spec_codes)
    extra = sorted((spec_codes - canonical) & active_codes(cpt_db))
    for code in missing:
        count += 1
        add_error(errors, "homepage_case_builder", code, "Canonical active CPT is missing from homepage/Case Builder SPECS")
    for code in extra:
        count += 1
        add_error(errors, "homepage_case_builder", code, "Inactive/deleted CPT appears in homepage/Case Builder SPECS")
    for code in sorted(canonical & spec_codes):
        record = cpt_db[code]
        row = specs[code]
        diffs = {}
        checks = {
            "description": (record.get("description"), row[1] if len(row) > 1 else None),
            "work_rvu": (number(record.get("work_rvu")), number(row[2] if len(row) > 2 else None)),
            "total_rvu": (number(record.get("total_rvu")), number(row[4] if len(row) > 4 else None)),
            "medicare_payment": (round(number(record.get("medicare_payment", record.get("estimated_medicare_payment"))), 2), round(number(row[5] if len(row) > 5 else None), 2)),
        }
        for field, (expected, actual) in checks.items():
            if isinstance(expected, str):
                if str(expected).strip() != str(actual or "").strip():
                    diffs[field] = {"canonical": expected, "specs": actual}
            elif abs(expected - actual) > 0.02:
                diffs[field] = {"canonical": expected, "specs": actual}
        if diffs:
            count += 1
            add_error(errors, "homepage_case_builder", code, "Homepage/Case Builder row differs from canonical CPT dataset", diffs=diffs)
    return count


def validate_deleted_codes(cpt_db: dict[str, Any], specs: dict[str, list[Any]], inactive: set[str], errors: list[dict[str, Any]]) -> int:
    count = 0
    index_html = (ROOT / "codes" / "index.html").read_text(errors="ignore") if (ROOT / "codes" / "index.html").exists() else ""
    for code in sorted(inactive):
        locations = []
        if code in cpt_db:
            locations.append("cpt_database.json")
        if code in specs:
            locations.append("homepage/Case Builder SPECS")
        if re.search(rf"href=[\"']{code}\.html[\"']", index_html):
            locations.append("codes/index.html")
        if locations:
            count += 1
            add_error(errors, "deleted_code", code, "Inactive/deleted CPT appears in active dataset or index", locations=locations)
    return count


def validate_page_metadata(cpt_db: dict[str, Any], inactive: set[str], errors: list[dict[str, Any]]) -> int:
    count = 0
    codes_dir = ROOT / "codes"
    for code in sorted(active_codes(cpt_db) - inactive):
        page = codes_dir / f"{code}.html"
        record = cpt_db.get(code, {})
        descriptor = str(record.get("description") or "").strip()
        if not page.exists():
            count += 1
            add_error(errors, "page_metadata", code, "Active CPT page is missing")
            continue
        html = page.read_text(errors="ignore")
        title = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.I | re.S)
        meta = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, flags=re.I | re.S)
        problems = []
        values = {
            "title": title.group(1).strip() if title else "",
            "h1": re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else "",
            "meta_description": meta.group(1).strip() if meta else "",
        }
        for field, value in values.items():
            if not value:
                problems.append(f"missing {field}")
            if "CPT XXXX" in value or f"CPT {code} CPT {code}" in value:
                problems.append(f"malformed {field}")
        unescaped_html = html_lib.unescape(html)
        if descriptor and descriptor not in unescaped_html:
            problems.append("canonical descriptor not rendered")
        if problems:
            count += 1
            add_error(errors, "page_metadata", code, "CPT page title/H1/meta/descriptor validation failed", problems=problems, values=values)
    return count


def build_scorecard(max_errors: int) -> dict[str, Any]:
    cpt_db = load_json(ROOT / "cpt_database.json")
    rvu_db = load_json(ROOT / "rvu_database.json")
    specs = extract_specs()
    inactive = inactive_page_codes()
    cms_rows, cms_source = load_cms_rows()
    errors: list[dict[str, Any]] = []
    check_counts = {
        "descriptor": validate_descriptors(cpt_db, inactive, errors),
        "rvu": validate_rvus(cpt_db, rvu_db, inactive, errors),
        "indicator": validate_indicators(cpt_db, cms_rows, cms_source, inactive, errors),
        "homepage_case_builder": validate_specs(cpt_db, specs, inactive, errors),
        "deleted_code": validate_deleted_codes(cpt_db, specs, inactive, errors),
        "page_metadata": validate_page_metadata(cpt_db, inactive, errors),
    }
    category_counts = Counter(error["category"] for error in errors)
    active_count = len(active_codes(cpt_db) - inactive)
    hard_error_count = len(errors)
    score = max(0.0, 100.0 - (hard_error_count / max(active_count, 1) * 100.0))
    return {
        "audit": "platform_hardening_audit",
        "cms_indicator_baseline": cms_source,
        "conversion_factor": CONVERSION_FACTOR,
        "active_cpt_count": active_count,
        "homepage_case_builder_count": len(specs),
        "inactive_deleted_page_count": len(inactive),
        "hard_error_count": hard_error_count,
        "integrity_score": round(score, 2),
        "category_counts": dict(sorted(category_counts.items())),
        "check_counts": check_counts,
        "hard_errors": errors[:max_errors],
        "hard_errors_truncated": len(errors) > max_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run FreeCPTCodeFinder platform hardening validation gates.")
    parser.add_argument("--out", default="qa_artifacts/phase3a_platform_hardening_2026_06_11/platform_integrity_scorecard.json")
    parser.add_argument("--max-errors", type=int, default=50)
    args = parser.parse_args()

    scorecard = build_scorecard(args.max_errors)
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scorecard, indent=2) + "\n")

    print(f"Platform hardening audit: {scorecard['hard_error_count']} hard errors")
    print(f"Integrity score: {scorecard['integrity_score']}")
    print(f"Scorecard: {out}")
    for category, count in scorecard["category_counts"].items():
        print(f"- {category}: {count}")
    if scorecard["hard_errors"]:
        print("Sample hard errors:")
        for error in scorecard["hard_errors"][:10]:
            print(f"  - {error['category']} {error['code']}: {error['message']}")
    return 1 if scorecard["hard_error_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
