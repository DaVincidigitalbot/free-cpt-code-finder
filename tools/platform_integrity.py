#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, html, json, re, sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CMS = Path("/home/setup/Desktop/FreeCPTCodeFinder/tmp/abos_sports_import/rvu26c/PPRRVU2026_Jul_nonQPP.csv")
TODAY = date.today().isoformat()
CF = 33.4009
CATEGORIES = ["Esophagus","Foregut","Stomach","Small bowel","Colon","Rectum","Appendix","Hepatobiliary","Pancreas","Spleen","Hernia","Breast","Trauma","Acute Care Surgery","Rib Fixation","Soft Tissue"]

def num(v):
    try: return float(v)
    except Exception: return 0.0

def money(v): return "$" + f"{num(v):,.2f}"

def code_int(code):
    return int(code) if re.fullmatch(r"\d{5}", str(code or "")) else None

def in_range(code, lo, hi):
    n = code_int(code)
    return n is not None and lo <= n <= hi

def load_json(p): return json.loads(Path(p).read_text())

def write_json(p, data): Path(p).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

def parse_cms():
    rows = {}
    if not CMS.exists(): return rows
    with CMS.open(newline="", encoding="utf-8-sig", errors="replace") as f:
        for row in csv.reader(f):
            if not row or len(row) < 32: continue
            code = row[0] or ""
            if not re.fullmatch(r"\d{5}", code) or row[1] != "" or row[3] != "A": continue
            rows[code] = {"code": code, "description": row[2].strip(), "work_rvu": num(row[5]), "pe_rvu": num(row[6]), "mp_rvu": num(row[10]), "total_rvu": num(row[11]), "global": row[14].strip(), "multiple": row[18].strip(), "bilateral": row[19].strip(), "assistant": row[20].strip(), "cosurgeon": row[21].strip(), "team": row[22].strip()}
    return rows

def cms_categories(code, row):
    d = str(row.get("description","")).lower(); cats = set()
    if (in_range(code,43000,43499) or "esoph" in d) and any(k in d for k in ["esoph","achalasia","heller"]): cats.add("Esophagus")
    if any(k in d for k in ["fundoplication","hiatal","paraesophageal","gastroesophageal","vagotomy","pyloroplasty"]): cats.add("Foregut")
    if (in_range(code,43500,43999) or any(k in d for k in ["gastr","stomach","bariatric","sleeve","bypass"])) and "gastrocnemius" not in d: cats.add("Stomach")
    if (in_range(code,44000,44799) or in_range(code,44600,44699)) and any(k in d for k in ["small intestine","small bowel","enter","jejuno","jejun","ileum","ileal","ileostomy","duoden","bowel"]): cats.add("Small bowel")
    if (in_range(code,44100,44799) or in_range(code,45300,45399)) and any(k in d for k in ["colon","colonic","colect","colonoscopy","large bowel","cecum","ileocolic","colostomy"]): cats.add("Colon")
    if in_range(code,45000,45999) and any(k in d for k in ["rect","anus","anal","proct","hemorrhoid","fistula","fissure"]): cats.add("Rectum")
    if in_range(code,44900,44979) or "append" in d: cats.add("Appendix")
    if in_range(code,47000,47999) and any(k in d for k in ["liver","hep","bile","biliary","gallbladder","chole","choledo","donor liver"]): cats.add("Hepatobiliary")
    if in_range(code,48000,48999) and any(k in d for k in ["pancre","whipple"]): cats.add("Pancreas")
    if in_range(code,38100,38299) and any(k in d for k in ["spleen","splen"]): cats.add("Spleen")
    if in_range(code,49491,49659) and "hernia" in d: cats.add("Hernia")
    if in_range(code,19000,19499) and any(k in d for k in ["breast","mastect","sentinel lymph"]): cats.add("Breast")
    if any(k in d for k in ["trauma","damage control","exploratory laparotomy","control of bleeding","packing"]): cats.update(["Trauma","Acute Care Surgery"])
    if any(k in d for k in ["abscess","debridement","foreign body","wound","necrotizing","exploratory laparotomy","appendectomy","cholecystectomy"]): cats.add("Acute Care Surgery")
    if any(k in d for k in ["rib fracture","rib fixation","sternal fracture"]): cats.add("Rib Fixation")
    if (in_range(code,10000,21999) or in_range(code,27000,27999)) and any(k in d for k in ["skin","subcutaneous","soft tissue","lesion","abscess","debridement","wound","foreign body","lipoma","tumor"]): cats.add("Soft Tissue")
    return cats

def site_categories(code, entry, cms_row=None):
    if cms_row: return cms_categories(code, cms_row)
    text = " ".join(str(entry.get(k,"")) for k in ["description","specialty","category","subcategory","code_family","notes"]).lower()
    return cms_categories(code, {"description": text})

def global_value(e): return e.get("global_period_days", e.get("global_period", 0))

def rvu_from_cpt(e):
    return {"description": e.get("description",""), "global_period": global_value(e), "mp_rvu": num(e.get("mp_rvu")), "pe_rvu": num(e.get("pe_rvu")), "total_rvu": num(e.get("total_rvu")), "work_rvu": num(e.get("work_rvu")), "wrvu_source": e.get("wrvu_source","cpt_database.json"), "wrvu_source_file": e.get("wrvu_source_file","cpt_database.json"), "wrvu_source_url": e.get("wrvu_source_url","")}

def modifier_from_cpt(e):
    gp = global_value(e); mult = str(e.get("multiple_procedure_indicator","2")); bi = str(e.get("bilateral_indicator","0"))
    addon = bool(e.get("addon_code")) or str(gp).upper() == "ZZZ"; bilateral = bool(e.get("bilateral_eligible")) or bi == "1"
    return {"mod51_exempt": addon or mult == "0", "addon_code": addon, "bilateral_eligible": bilateral, "laterality_applicable": bilateral, "bilateral_method": "modifier_50" if bilateral else None, "global_period": gp, "assistant_allowed": bool(e.get("assistant_allowed", False)), "cosurgeon_eligible": bool(e.get("cosurgeon_eligible", False)), "team_surgeon_eligible": str(e.get("team_surgeon_indicator","0")) in {"1","2"}, "inherently_bilateral": bi == "2", "distinct_procedure_class": e.get("subcategory") or e.get("code_family"), "category": e.get("subcategory") or e.get("category"), "inclusive_of": e.get("inclusive_of", []), "never_primary_with": e.get("never_primary_with", []), "payer_notes": {"medicare": "Use CMS PFS indicators; apply MPPR only when multiple-procedure rules apply.", "commercial": "Verify payer-specific modifier, assistant, and bundling policy."}, "x_modifier_eligible": not addon, "hierarchy_tier": e.get("hierarchy_tier",3), "code_family": e.get("code_family") or e.get("subcategory") or "cpt"}

def cpt_from_cms(code, row, cat):
    gp = int(row["global"]) if str(row["global"]).isdigit() else row["global"]
    return {"addon_code": row["global"] == "ZZZ", "assistant_allowed": row["assistant"] in {"2","3"}, "assistant_surgeon_indicator": row["assistant"], "bilateral_eligible": row["bilateral"] == "1", "bilateral_indicator": row["bilateral"], "category": "General Surgery", "code": code, "code_family": cat.lower().replace(" ","_"), "cosurgeon_eligible": row["cosurgeon"] in {"1","2"}, "cosurgeon_indicator": row["cosurgeon"], "description": row["description"], "estimated": False, "global_period_days": gp, "hierarchy_tier": 2 if row["global"] != "ZZZ" else 4, "inclusive_of": [], "mp_rvu": round(row["mp_rvu"],2), "multiple_procedure_indicator": row["multiple"], "never_primary_with": [], "pe_rvu": round(row["pe_rvu"],2), "search_terms": [cat.lower(),"general surgery"], "specialty": "general_surgery", "specialty_aliases": ["general surgery", cat.lower()], "subcategory": cat.lower().replace(" ","_"), "team_surgeon_indicator": row["team"], "total_rvu": round(row["total_rvu"],2), "typical_modifiers": [], "work_rvu": round(row["work_rvu"],2), "wrvu_source": "CMS PFS RVU26C July 2026 non-QPP", "wrvu_source_file": "PPRRVU2026_Jul_nonQPP.csv", "wrvu_source_url": "https://www.cms.gov/files/zip/rvu26c.zip", "estimated_medicare_payment": round(row["total_rvu"] * CF, 2)}

def page_html(code, e):
    desc = html.escape(str(e.get("description",""))); pay = money(e.get("estimated_medicare_payment",0)); gp = global_value(e)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CPT {code}: {desc} | FreeCPTCodeFinder.com</title>
<meta name="description" content="CPT code {code} - {desc}. Work RVU: {num(e.get('work_rvu')):.2f}, total RVU: {num(e.get('total_rvu')):.2f}, estimated Medicare payment: {pay}.">
<link rel="canonical" href="https://freecptcodefinder.com/codes/{code}.html"><link rel="stylesheet" href="/styles/app-mode.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"MedicalWebPage","name":"CPT {code}: {desc}","url":"https://freecptcodefinder.com/codes/{code}.html","dateModified":"{TODAY}"}}</script></head>
<body><main class="container code-page"><nav><a href="/">FreeCPTCodeFinder</a> / <a href="/codes/">CPT Codes</a> / CPT {code}</nav>
<h1>CPT {code} <span class="desc">{desc}</span></h1>
<section class="site-card"><h2>RVU Snapshot</h2><ul><li><strong>Work RVU:</strong> {num(e.get('work_rvu')):.2f}</li><li><strong>PE RVU:</strong> {num(e.get('pe_rvu')):.2f}</li><li><strong>MP RVU:</strong> {num(e.get('mp_rvu')):.2f}</li><li><strong>Total RVU:</strong> {num(e.get('total_rvu')):.2f}</li><li><strong>Estimated Medicare payment:</strong> {pay}</li><li><strong>Global period:</strong> {gp}</li><li><strong>Assistant surgeon indicator:</strong> {e.get('assistant_surgeon_indicator','')}</li><li><strong>Co-surgeon indicator:</strong> {e.get('cosurgeon_indicator','')}</li><li><strong>Team surgeon indicator:</strong> {e.get('team_surgeon_indicator','')}</li><li><strong>Bilateral indicator:</strong> {e.get('bilateral_indicator','')}</li><li><strong>Multiple procedure indicator:</strong> {e.get('multiple_procedure_indicator','')}</li></ul></section>
<section class="site-card"><h2>Coding Note</h2><p>Case Builder uses this same total-RVU Medicare payment estimate and applies modifier or MPPR adjustments only at the case level.</p></section>
<p><strong>Source:</strong> {html.escape(str(e.get('wrvu_source','cpt_database.json')))}. Educational coding support only; confirm final billing against AMA CPT, CMS MPFS, NCCI, and payer policy.</p></main></body></html>
'''

def normalize_currency_file(path, db):
    text = path.read_text(errors="replace"); orig = text
    m = re.search(r"CPT\s+(\d{5}|\d{4}T)", text)
    if m and m.group(1) in db:
        pay = money(db[m.group(1)].get("estimated_medicare_payment",0))
        text = re.sub(r"(estimated Medicare payment:\s*)(?!\$)([0-9]+(?:\.[0-9]{1,2})?)", lambda mm: mm.group(1)+pay, text, flags=re.I)
        text = re.sub(r"(Estimated Medicare payment:</strong>\s*)(?!\$)([0-9]+(?:\.[0-9]{1,2})?)", lambda mm: mm.group(1)+pay, text, flags=re.I)
    text = re.sub(r"\$(\d{4,})(\.\d{2})", lambda mm: "$"+f"{int(mm.group(1)):,}"+mm.group(2), text)
    if text != orig: path.write_text(text); return True
    return False

def update_codes_index(db):
    path = ROOT/"codes"/"index.html"; text = path.read_text(errors="replace"); adds = []
    for code,e in sorted(db.items()):
        if f"/codes/{code}.html" in text: continue
        adds.append(f'<a href="/codes/{code}.html" class="code-card"><span class="cpt">{code}</span><span class="desc">{html.escape(str(e.get("description","")))}</span><span class="wrvu">{num(e.get("work_rvu")):.2f} wRVU</span></a>')
    if adds:
        text = text.replace("</div>\n</div></section>", "\n".join(adds)+"\n</div>\n</div></section>", 1)
        path.write_text(text)
    return len(adds)

def update_sitemap(db):
    path = ROOT/"sitemap.xml"; text = path.read_text(errors="replace"); adds = []
    for code in sorted(db):
        url = f"https://freecptcodefinder.com/codes/{code}.html"
        if url not in text: adds.append(f'<url><loc>{url}</loc><lastmod>{TODAY}</lastmod></url>')
    if adds:
        path.write_text(text.replace("</urlset>", "\n".join(adds)+"\n</urlset>"))
    return len(adds)

def repair(phase=None):
    db = load_json(ROOT/"cpt_database.json"); rvu = load_json(ROOT/"rvu_database.json"); mods = load_json(ROOT/"modifier_rules.json"); cms = parse_cms()
    added = []
    if phase:
        for code,row in sorted(cms.items()):
            cats = cms_categories(code,row)
            if phase == "phase-b":
                target = "Esophagus" if "Esophagus" in cats else ("Small bowel" if "Small bowel" in cats else None)
            elif phase == "phase-c":
                target = "Acute Care Surgery" if "Acute Care Surgery" in cats else None
            else:
                target = None
            if target and code not in db:
                db[code] = cpt_from_cms(code,row,target); added.append(code)
    rvu_added=mod_added=pages_added=currency_fixed=0
    for code,e in sorted(db.items()):
        if "estimated_medicare_payment" not in e or e.get("estimated_medicare_payment") in [None,""]:
            e["estimated_medicare_payment"] = round(num(e.get("total_rvu")) * CF, 2)
        if code not in rvu["codes"]: rvu["codes"][code]=rvu_from_cpt(e); rvu_added += 1
        if code not in mods: mods[code]=modifier_from_cpt(e); mod_added += 1
        page = ROOT/"codes"/f"{code}.html"
        if not page.exists(): page.write_text(page_html(code,e)); pages_added += 1
        elif normalize_currency_file(page, db): currency_fixed += 1
    write_json(ROOT/"cpt_database.json", db); write_json(ROOT/"rvu_database.json", rvu); write_json(ROOT/"modifier_rules.json", mods)
    index_added = update_codes_index(db); sitemap_added = update_sitemap(db)
    for p in list((ROOT/"specialties").glob("*.html")) + list((ROOT/"cpt-code-for").glob("*.html")) + [ROOT/"codes"/"index.html"]:
        if p.exists(): normalize_currency_file(p, db)
    return {"phase": phase or "repair", "codes_added": added, "rvu_rows_added": rvu_added, "modifier_rows_added": mod_added, "cpt_pages_added": pages_added, "cpt_pages_currency_fixed": currency_fixed, "codes_index_entries_added": index_added, "sitemap_entries_added": sitemap_added}

def validate(scope="all"):
    db = load_json(ROOT/"cpt_database.json"); rvu = load_json(ROOT/"rvu_database.json")["codes"]; mods = load_json(ROOT/"modifier_rules.json")
    sitemap = (ROOT/"sitemap.xml").read_text(errors="replace"); index = (ROOT/"codes"/"index.html").read_text(errors="replace")
    errors=[]; warnings=[]
    for code,e in sorted(db.items()):
        if scope == "general-surgery" and not site_categories(code,e): continue
        page = ROOT/"codes"/f"{code}.html"
        if code not in rvu: errors.append({"type":"missing_rvu_database","code":code})
        if code not in mods: errors.append({"type":"missing_modifier_metadata","code":code})
        if not page.exists(): errors.append({"type":"missing_cpt_page","code":code})
        else:
            text = page.read_text(errors="replace")
            if code not in text: errors.append({"type":"cpt_page_missing_code_text","code":code})
            if num(e.get("estimated_medicare_payment")) and money(e.get("estimated_medicare_payment")) not in text:
                errors.append({"type":"cpt_page_payment_display_mismatch","code":code,"expected":money(e.get("estimated_medicare_payment"))})
        if f"https://freecptcodefinder.com/codes/{code}.html" not in sitemap: errors.append({"type":"missing_sitemap_entry","code":code})
        if f"/codes/{code}.html" not in index: errors.append({"type":"missing_search_index_entry","code":code})
        for field in ["work_rvu","total_rvu","estimated_medicare_payment","global_period_days","assistant_allowed","cosurgeon_eligible"]:
            if field not in e or e.get(field) in [None,""]: errors.append({"type":"missing_cpt_field","code":code,"field":field})
        for field in ["multiple_procedure_indicator","bilateral_indicator"]:
            if field not in e: warnings.append({"type":"missing_cms_indicator","code":code,"field":field})
        if code in rvu:
            for field in ["work_rvu","pe_rvu","mp_rvu","total_rvu"]:
                if field not in rvu[code] or rvu[code].get(field) in [None,""]: errors.append({"type":"missing_rvu_field","code":code,"field":field})
        if num(e.get("total_rvu")) and round(num(e.get("estimated_medicare_payment")),2) != round(num(e.get("total_rvu")) * CF,2):
            errors.append({"type":"payment_formula_mismatch","code":code,"site":e.get("estimated_medicare_payment"),"expected":round(num(e.get("total_rvu"))*CF,2)})
    return {"scope":scope,"total_cpt_count":len(db),"total_page_count":len(list((ROOT/"codes").glob("*.html"))),"total_sitemap_code_count":sitemap.count("/codes/"),"total_rvu_rows":len(rvu),"total_modifier_rule_rows":len(mods),"hard_error_count":len(errors),"warning_count":len(warnings),"hard_error_types":dict(Counter(x["type"] for x in errors)),"warning_types":dict(Counter(x["type"] for x in warnings)),"hard_errors":errors,"warnings":warnings}

def coverage():
    cms = parse_cms(); db = load_json(ROOT/"cpt_database.json")
    cms_cat=defaultdict(set); site_cat=defaultdict(set)
    for code,row in cms.items():
        for c in cms_categories(code,row): cms_cat[c].add(code)
    for code,e in db.items():
        for c in site_categories(code,e,cms.get(code)): site_cat[c].add(code)
    rows=[]
    for c in CATEGORIES:
        cms_codes=cms_cat[c]; site_codes=site_cat[c] & cms_codes; missing=sorted(cms_codes-site_codes)
        rows.append({"category":c,"cms_cpt_count":len(cms_codes),"site_cpt_count":len(site_codes),"missing_cpt_count":len(missing),"coverage_percentage":round(len(site_codes)/len(cms_codes)*100,1) if cms_codes else 100.0,"missing_cpt_codes":missing})
    total_cms=set().union(*(cms_cat[c] for c in CATEGORIES)); total_site=set().union(*(site_cat[c] for c in CATEGORIES)) & total_cms
    return {"generated_at":TODAY,"cms_source":str(CMS),"overall":{"cms_cpt_count":len(total_cms),"site_cpt_count":len(total_site),"missing_cpt_count":len(total_cms-total_site),"coverage_percentage":round(len(total_site)/len(total_cms)*100,1) if total_cms else 100.0,"missing_cpt_codes":sorted(total_cms-total_site)},"categories":rows}

def write_coverage():
    data = coverage(); out = ROOT/"audit_reports"/"general_surgery_coverage_dashboard.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(data, indent=2)+"\n")
    trs = "\n".join(f"<tr><td>{html.escape(r['category'])}</td><td>{r['cms_cpt_count']}</td><td>{r['site_cpt_count']}</td><td>{r['missing_cpt_count']}</td><td>{r['coverage_percentage']:.1f}%</td><td class='missing-codes'>{html.escape(', '.join(r['missing_cpt_codes']) or 'None')}</td></tr>" for r in data["categories"])
    page = ROOT/"admin"/"coverage-dashboard.html"; page.parent.mkdir(exist_ok=True)
    page.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>General Surgery Coverage Dashboard</title><link rel="stylesheet" href="/styles/app-mode.css"><style>.dashboard-table{{width:100%;border-collapse:collapse}}.dashboard-table th,.dashboard-table td{{border:1px solid #d9e1ea;padding:8px;vertical-align:top}}.dashboard-table th{{text-align:left;background:#f4f7fb}}.missing-codes{{font-family:monospace;font-size:12px;line-height:1.5}}</style></head><body><main class="container"><nav><a href="/">FreeCPTCodeFinder</a> / Internal / Coverage</nav><h1>General Surgery Coverage Dashboard</h1><section class="site-card"><h2>Overall</h2><ul><li><strong>CMS CPT count:</strong> {data['overall']['cms_cpt_count']}</li><li><strong>Site CPT count:</strong> {data['overall']['site_cpt_count']}</li><li><strong>Missing CPT count:</strong> {data['overall']['missing_cpt_count']}</li><li><strong>Coverage:</strong> {data['overall']['coverage_percentage']:.1f}%</li><li><strong>Generated:</strong> {TODAY}</li></ul></section><section class="site-card"><h2>Specialty Sections</h2><table class="dashboard-table"><thead><tr><th>Section</th><th>CMS CPT count</th><th>Site CPT count</th><th>Missing</th><th>Coverage</th><th>Missing CPT codes</th></tr></thead><tbody>{trs}</tbody></table></section></main></body></html>''')
    return data

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("command",choices=["repair","phase-b","phase-c","validate","coverage"]); ap.add_argument("--scope",default="all",choices=["all","general-surgery"]); args=ap.parse_args()
    if args.command=="repair": result=repair(None)
    elif args.command=="phase-b": result=repair("phase-b")
    elif args.command=="phase-c": result=repair("phase-c")
    elif args.command=="coverage": result=write_coverage()
    else:
        result=validate(args.scope); out=ROOT/"qa_artifacts"/"platform_validation_2026_06_10"; out.mkdir(parents=True,exist_ok=True); (out/f"platform_validation_{args.scope}.json").write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps(result,indent=2)); return 1 if result["hard_error_count"] else 0
    print(json.dumps(result, indent=2)); return 0

if __name__ == "__main__": sys.exit(main())
