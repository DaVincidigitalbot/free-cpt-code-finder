#!/usr/bin/env python3
"""Phase 1 data-integrity discrepancy scanner.

Report-only: compares rendered/static surfaces against canonical CPT/RVU JSON
data and writes discrepancy reports without mutating site data, generated pages,
templates, or payment logic.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".html", ".htm", ".js", ".json", ".xml"}
SURFACE_DIRS = ["codes", "blog", "content-hubs", "hubs", "guides", "categories", "specialties"]


@dataclass
class Finding:
    severity: str
    surface: str
    code: str
    field: str
    observed: Any
    expected: Any
    file: str
    note: str


def load_json(name: str) -> Any:
    with (ROOT / name).open() as f:
        return json.load(f)


def normalize_money(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    text = str(value).replace("$", "").replace(",", "").strip()
    try:
        return round(float(text), 2)
    except ValueError:
        return None


def normalize_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def expected_payment(entry: dict[str, Any], conversion_factor: float) -> float:
    return round((normalize_number(entry.get("total_rvu")) or 0) * conversion_factor, 2)


def add_find(findings: list[Finding], severity: str, surface: str, code: str, field: str, observed: Any, expected: Any, file: Path | str, note: str) -> None:
    findings.append(Finding(severity, surface, code, field, observed, expected, str(file), note))


def extract_specs(index_text: str) -> list[dict[str, Any]]:
    marker = "const SPECS="
    start = index_text.find(marker)
    if start == -1:
        return []
    pos = index_text.find("[", start)
    if pos == -1:
        return []
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
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(index_text[pos : i + 1])
                except json.JSONDecodeError:
                    return []
    return []


def scan_database_consistency(codes, cpt_db, rvu_codes, modifier_rules, conversion_factor, findings):
    for code in codes:
        cpt = cpt_db.get(code)
        rvu = rvu_codes.get(code)
        mod = modifier_rules.get(code)
        if not cpt:
            add_find(findings, "error", "cpt_database", code, "record", None, "present", "cpt_database.json", "CPT database record missing.")
            continue
        if not rvu:
            add_find(findings, "error", "rvu_database", code, "record", None, "present", "rvu_database.json", "RVU database row missing.")
        if not mod:
            add_find(findings, "error", "modifier_rules", code, "record", None, "present", "modifier_rules.json", "Modifier metadata missing.")

        if cpt and rvu:
            for field in ["description", "work_rvu", "total_rvu", "pe_rvu", "mp_rvu"]:
                observed = cpt.get(field)
                expected = rvu.get(field)
                if field == "description":
                    if observed != expected:
                        add_find(findings, "error", "cpt_vs_rvu_database", code, field, observed, expected, "cpt_database.json", "CPT descriptor differs from canonical RVU descriptor.")
                elif normalize_number(observed) != normalize_number(expected):
                    add_find(findings, "error", "cpt_vs_rvu_database", code, field, observed, expected, "cpt_database.json", "CPT numeric RVU field differs from canonical RVU database.")
            observed_payment = normalize_money(cpt.get("estimated_medicare_payment"))
            expected = expected_payment(rvu, conversion_factor)
            if observed_payment != expected:
                add_find(findings, "error", "payment_formula", code, "estimated_medicare_payment", observed_payment, expected, "cpt_database.json", "CPT payment should equal total RVU times conversion factor.")
            gp = str(cpt.get("global_period_days") if cpt.get("global_period_days") is not None else "")
            rvu_gp = str(rvu.get("global_period") if rvu.get("global_period") is not None else "")
            if gp != rvu_gp:
                add_find(findings, "warning", "cpt_vs_rvu_database", code, "global_period", gp, rvu_gp, "cpt_database.json", "Global period differs from canonical RVU row.")

        if cpt and mod:
            for field in ["assistant_allowed", "bilateral_eligible", "cosurgeon_eligible", "addon_code", "hierarchy_tier"]:
                if cpt.get(field) != mod.get(field):
                    add_find(findings, "warning", "modifier_rules", code, field, mod.get(field), cpt.get(field), "modifier_rules.json", "Modifier metadata differs from CPT database field.")


def scan_required_static_surfaces(codes, rvu_codes, conversion_factor, findings):
    sitemap = (ROOT / "sitemap.xml").read_text(errors="ignore") if (ROOT / "sitemap.xml").exists() else ""
    for code in codes:
        page = ROOT / "codes" / f"{code}.html"
        if not page.exists():
            add_find(findings, "error", "cpt_page", code, "file", None, f"codes/{code}.html", page, "Generated CPT page missing.")
            continue
        text = page.read_text(errors="ignore")
        canonical = rvu_codes.get(code, {})
        desc = canonical.get("description")
        if desc and desc not in text:
            add_find(findings, "error", "cpt_page", code, "description", "not found", desc, page.relative_to(ROOT), "Canonical descriptor is not rendered on CPT page.")
        for field in ["work_rvu", "total_rvu"]:
            value = canonical.get(field)
            if value is not None and str(value) not in text:
                add_find(findings, "warning", "cpt_page", code, field, "not found", value, page.relative_to(ROOT), "Canonical RVU value is not visible on CPT page.")
        if canonical:
            payment = expected_payment(canonical, conversion_factor)
            formatted_payment = "$" + f"{payment:,.2f}"
            if formatted_payment not in text:
                add_find(findings, "warning", "cpt_page", code, "estimated_medicare_payment", "not found", formatted_payment, page.relative_to(ROOT), "Formatted canonical payment estimate is not visible on CPT page.")
        if f"/codes/{code}.html" not in sitemap:
            add_find(findings, "error", "sitemap", code, "entry", None, f"/codes/{code}.html", "sitemap.xml", "CPT page missing from sitemap.")


def scan_homepage_specs(codes, cpt_db, rvu_codes, findings):
    path = ROOT / "index.html"
    if not path.exists():
        return
    specs = extract_specs(path.read_text(errors="ignore"))
    by_code = {str(row.get("code")): row for row in specs if isinstance(row, dict) and row.get("code") is not None}
    for code in codes:
        spec = by_code.get(code)
        if not spec:
            add_find(findings, "error", "homepage_specs_search_case_builder_seed", code, "record", None, "present", "index.html", "Code missing from homepage SPECS seed used by search and Case Builder.")
            continue
        canonical = rvu_codes.get(code, {})
        cpt = cpt_db.get(code, {})
        checks = [
            ("description", spec.get("desc"), canonical.get("description") or cpt.get("description")),
            ("work_rvu", spec.get("rvu"), canonical.get("work_rvu")),
            ("global_period", spec.get("global"), canonical.get("global_period") or cpt.get("global_period_days")),
        ]
        for field, observed, expected in checks:
            if expected is None:
                continue
            mismatch = normalize_number(observed) != normalize_number(expected) if field == "work_rvu" else str(observed) != str(expected)
            if mismatch:
                add_find(findings, "error", "homepage_specs_search_case_builder_seed", code, field, observed, expected, "index.html", "Homepage SPECS seed differs from canonical source.")


def iter_surface_files() -> list[Path]:
    files = [ROOT / "index.html"] if (ROOT / "index.html").exists() else []
    for dirname in SURFACE_DIRS:
        base = ROOT / dirname
        if base.exists():
            files.extend(path for path in base.rglob("*") if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS)
    return files


def scan_static_text_surfaces(codes, rvu_codes, findings):
    if not codes:
        return
    code_re = re.compile(r"\b(" + "|".join(re.escape(c) for c in codes) + r")\b")
    for path in iter_surface_files():
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        present = sorted(set(code_re.findall(text)))
        if not present:
            continue
        rel = path.relative_to(ROOT)
        for code in present:
            canonical = rvu_codes.get(code, {})
            if not canonical or str(rel) == f"codes/{code}.html":
                continue
            desc = canonical.get("description")
            has_billing_context = bool(re.search(r"\bRVU\b|\bwRVU\b|\$\s?\d|modifier", text, re.I))
            if desc and has_billing_context and desc not in text:
                add_find(findings, "warning", "guide_hub_widget_text", code, "descriptor_context", "code appears without canonical descriptor", desc, rel, "Guide/hub/widget mentions this code in billing context without rendering canonical descriptor nearby.")


def write_reports(payload, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    md = out.with_suffix(".md")
    findings = payload["findings"]
    lines = [
        "# Phase 1 Data-Integrity Discrepancy Report",
        "",
        f"Generated: {payload['generated_at']}",
        f"Branch: {payload['branch']}",
        f"Commit: {payload['commit']}",
        "",
        "## Canonical RVU Source",
        f"- Source: {payload['canonical_source']['source']}",
        f"- Release year: {payload['canonical_source']['year']}",
        f"- Source file: {payload['canonical_source']['source_file']}",
        f"- SHA256: {payload['canonical_source']['source_sha256']}",
        f"- Conversion factor: {payload['canonical_source']['conversion_factor']}",
        f"- Value type: {payload['canonical_source']['value_type']}",
        "",
        "## Summary",
        f"- CPTs scanned: {payload['summary']['codes_scanned']}",
        f"- Errors: {payload['summary']['errors']}",
        f"- Warnings: {payload['summary']['warnings']}",
        "",
        "## Surface Counts",
    ]
    for surface, count in payload["summary"]["by_surface"].items():
        lines.append(f"- {surface}: {count}")
    lines += ["", "## Findings"]
    for item in findings[:500]:
        lines.append(f"- [{item['severity'].upper()}] {item['code']} | {item['surface']} | {item['field']} | {item['file']} | observed={item['observed']!r} | expected={item['expected']!r} | {item['note']}")
    if len(findings) > 500:
        lines.append(f"- ... truncated in markdown; full JSON contains {len(findings)} findings.")
    md.write_text("\n".join(lines) + "\n")


def git_value(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Phase 1 data-integrity discrepancy report without applying fixes.")
    parser.add_argument("--codes", nargs="*", default=["44950", "44960", "44970", "47562", "49505"])
    parser.add_argument("--all-codes", action="store_true")
    parser.add_argument("--out", default="audit_reports/data_integrity_phase1_2026_06_10.json")
    args = parser.parse_args()

    cpt_db = load_json("cpt_database.json")
    rvu_db = load_json("rvu_database.json")
    modifier_rules = load_json("modifier_rules.json")
    rvu_codes = rvu_db["codes"]
    codes = sorted(cpt_db.keys()) if args.all_codes else [str(code) for code in args.codes]
    conversion_factor = float(rvu_db["conversion_factor"])

    findings: list[Finding] = []
    scan_database_consistency(codes, cpt_db, rvu_codes, modifier_rules, conversion_factor, findings)
    scan_required_static_surfaces(codes, rvu_codes, conversion_factor, findings)
    scan_homepage_specs(codes, cpt_db, rvu_codes, findings)
    scan_static_text_surfaces(codes, rvu_codes, findings)

    by_surface: dict[str, int] = {}
    for finding in findings:
        by_surface[finding.surface] = by_surface.get(finding.surface, 0) + 1

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "branch": git_value("branch", "--show-current"),
        "commit": git_value("rev-parse", "HEAD"),
        "canonical_source": {
            "source": rvu_db.get("source"),
            "source_file": rvu_db.get("source_file"),
            "source_sha256": rvu_db.get("source_sha256"),
            "source_url": rvu_db.get("source_url"),
            "year": rvu_db.get("year"),
            "conversion_factor": rvu_db.get("conversion_factor"),
            "value_type": rvu_db.get("value_type"),
        },
        "summary": {
            "codes_scanned": len(codes),
            "errors": sum(1 for f in findings if f.severity == "error"),
            "warnings": sum(1 for f in findings if f.severity == "warning"),
            "by_surface": dict(sorted(by_surface.items())),
        },
        "findings": [asdict(f) for f in findings],
    }
    write_reports(payload, ROOT / args.out)
    print(json.dumps(payload["summary"], indent=2))
    return 1 if payload["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
