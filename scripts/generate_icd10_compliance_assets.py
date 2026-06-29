#!/usr/bin/env python3
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ICD_DIR = ROOT / "data" / "icd10cm" / "2026"
IPO_DIR = ROOT / "data" / "inpatient_only" / "2026"
ICD_DIR.mkdir(parents=True, exist_ok=True)
IPO_DIR.mkdir(parents=True, exist_ok=True)

def parse_icd_order():
    path = ICD_DIR / "icd10cm_order_2026.txt"
    rows = []
    code_set = set()
    for raw in path.read_text(encoding="latin1").splitlines():
        if not raw.strip():
            continue
        # CMS order file: sequence, code, header/billable flag, short desc, long desc
        seq = raw[0:5].strip()
        code = raw[6:13].strip()
        flag = raw[14:15].strip()
        short_desc = raw[16:76].strip()
        long_desc = raw[77:].strip() or short_desc
        if not code:
            continue
        rows.append({
            "code": code,
            "description": long_desc,
            "shortDescription": short_desc,
            "billable": flag == "1",
            "effectiveDate": "2025-10-01",
            "retired": False,
            "replacedBy": None,
            "seq": int(seq) if seq.isdigit() else None,
        })
        code_set.add(code)
    for row in rows:
        code = row["code"]
        parent = None
        for i in range(len(code)-1, 2, -1):
            cand = code[:i]
            if cand in code_set:
                parent = cand
                break
        row["parent"] = parent
    return rows

def parse_ipo_pdf():
    pdf = pathlib.Path("/tmp/ipo2026.pdf")
    if not pdf.exists():
        return []
    txt = subprocess.check_output(["pdftotext", str(pdf), "-"], text=True, errors="ignore")
    rows = []
    seen = set()
    for line in txt.splitlines():
        code = line.strip()
        # pdftotext emits table cells on separate lines. Capture only HCPCS/CPT-like code cells.
        if not re.fullmatch(r"(?:\d{5}|\d{4}T|[A-Z]\d{4})", code):
            continue
        if code in seen:
            continue
        # Keep descriptors out of app payload; descriptions remain in source artifact only.
        seen.add(code)
        rows.append({
            "cpt": code,
            "inpatientOnly": True,
            "effectiveDate": "2026-01-01",
            "source": "CY2026 OPPS Addendum E - HCPCS Codes That Would Be Paid Only as Inpatient Procedures",
            "sourceNote": "Code-only compliance payload. CPT descriptors are intentionally not redistributed in the app."
        })
    return sorted(rows, key=lambda r: r["cpt"])

def js_string(data):
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)

icd_rows = parse_icd_order()
ipo_rows = parse_ipo_pdf()

(ICD_DIR / "icd10cm_2026_compact.json").write_text(json.dumps({
    "version": "FY2026",
    "source": "CMS 2026 Code Descriptions in Tabular Order",
    "effectiveDate": "2025-10-01",
    "codeCount": len(icd_rows),
    "billableCount": sum(1 for r in icd_rows if r["billable"]),
    "rows": icd_rows,
}, indent=2), encoding="utf-8")

(IPO_DIR / "cms_ipo_2026.json").write_text(json.dumps({
    "version": "CY2026",
    "source": "CY2026 OPPS Addendum E",
    "effectiveDate": "2026-01-01",
    "codeCount": len(ipo_rows),
    "rows": ipo_rows,
}, indent=2), encoding="utf-8")

# Compact JS payloads loaded by index.html.
icd_compact = [[r["code"], r["description"], 1 if r["billable"] else 0, r["parent"] or "", r["effectiveDate"], 1 if r["retired"] else 0, r["replacedBy"] or ""] for r in icd_rows]
ipo_compact = [[r["cpt"], r["effectiveDate"], r["source"], r["sourceNote"]] for r in ipo_rows]

(ROOT / "icd10cm_2026_data.js").write_text(
    "window.ICD10_DATA_VERSION={version:'FY2026',effectiveDate:'2025-10-01',source:'CMS 2026 Code Descriptions in Tabular Order'};\n"
    "window.ICD10_CM_2026="+js_string(icd_compact)+";\n",
    encoding="utf-8"
)
(ROOT / "inpatient_only_2026_data.js").write_text(
    "window.INPATIENT_ONLY_VERSION={version:'CY2026',effectiveDate:'2026-01-01',source:'CY2026 OPPS Addendum E'};\n"
    "window.INPATIENT_ONLY_2026="+js_string(ipo_compact)+";\n",
    encoding="utf-8"
)

stats = {
    "icd10Version": "FY2026",
    "icd10Codes": len(icd_rows),
    "icd10Billable": sum(1 for r in icd_rows if r["billable"]),
    "icd10NonBillable": sum(1 for r in icd_rows if not r["billable"]),
    "inpatientOnlyVersion": "CY2026",
    "inpatientOnlyCodes": len(ipo_rows),
}
(ROOT / "qa_artifacts" / "icd10_inpatient_compliance").mkdir(parents=True, exist_ok=True)
(ROOT / "qa_artifacts" / "icd10_inpatient_compliance" / "database-statistics.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
print(json.dumps(stats, indent=2))
