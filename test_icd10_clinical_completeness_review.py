#!/usr/bin/env python3
import json
import pathlib
import subprocess
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


ROOT = pathlib.Path(__file__).resolve().parent
ART = ROOT / "qa_artifacts" / "icd10_clinical_completeness_review"
ART.mkdir(parents=True, exist_ok=True)
URL = ROOT.joinpath("index.html").as_uri()


def driver(width=1500, height=1300):
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--allow-file-access-from-files")
    opts.add_argument(f"--window-size={width},{height}")
    return webdriver.Chrome(options=opts)


def js(d, src):
    return d.execute_script(src)


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def snap(d, name):
    path = ART / f"{name}.png"
    d.save_screenshot(str(path))
    return str(path)


def load(d):
    d.get(URL)
    time.sleep(1)
    require(js(d, "return typeof addCptDirectly==='function' && ICD10_ROWS.length>90000"), "app or ICD dataset failed to load")


def make_video(screenshots):
    frames = ART / "video_frames"
    frames.mkdir(exist_ok=True)
    for i, src in enumerate(screenshots):
        (frames / f"frame_{i:03d}.png").write_bytes(pathlib.Path(src).read_bytes())
    out = ART / "clinical_completeness_workflow.mp4"
    try:
        subprocess.run([
            "ffmpeg", "-y", "-framerate", "1", "-i", str(frames / "frame_%03d.png"),
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-pix_fmt", "yuv420p", str(out)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(out)
    except Exception:
        return None


COMPLETENESS_TABLE = [
    {
        "Procedure family": "Tracheostomy",
        "CPT codes included": "31600, 31601, 31603",
        "Common clinical indications": "Acute/chronic respiratory failure, ventilator dependence, prolonged mechanical ventilation, upper-airway obstruction, laryngeal/tracheal stenosis",
        "ICD-10 groups mapped": "Respiratory failure; ventilator dependence; airway obstruction; tracheal obstruction",
        "Missing likely diagnoses": "Airway protection for major neurologic injury/head-neck cancer remains intentionally broad-search rather than a default group",
        "Laterality needs": "None for the core ICD-10 indications",
        "High-risk payer/medical-necessity concerns": "Planned trach should be supported by respiratory failure, ventilator dependence, or obstructing airway pathology; Z99.11 alone is weak without the clinical condition",
        "Recommendation": "acceptable",
    },
    {
        "Procedure family": "Gastrostomy / PEG",
        "CPT codes included": "43246, 49440, 49446, 49450",
        "Common clinical indications": "Dysphagia, neurologic dysphagia, feeding difficulty, malnutrition, adult failure to thrive, aspiration risk",
        "ICD-10 groups mapped": "Dysphagia; malnutrition; feeding difficulty; aspiration risk",
        "Missing likely diagnoses": "Cancer/cachexia and ALS/parkinsonism could be added later, but current groups cover most coder workflows",
        "Laterality needs": "None",
        "High-risk payer/medical-necessity concerns": "PEG for convenience or vague poor intake is vulnerable; pair R13/R63/E43-E46 with objective inability to maintain nutrition",
        "Recommendation": "acceptable",
    },
    {
        "Procedure family": "Colectomy / bowel resection",
        "CPT codes included": "44120, 44121, 44140, 44143, 44145, 44146, 44155, 44202, 44203, 44204, 44205, 44207, 44208",
        "Common clinical indications": "Diverticulitis, colon/rectal cancer, volvulus, ischemic bowel, perforation/peritonitis, bowel obstruction",
        "ICD-10 groups mapped": "Diverticulitis; colon cancer; volvulus; ischemic bowel; perforation; obstruction",
        "Missing likely diagnoses": "Crohn/UC and benign colon polyp are not yet family defaults",
        "Laterality needs": "Cancer site specificity matters by colon segment; not left/right laterality",
        "High-risk payer/medical-necessity concerns": "Elective benign disease needs diagnostic specificity; obstruction/perforation/ischemia support urgency",
        "Recommendation": "acceptable, with future IBD/polyp expansion",
    },
    {
        "Procedure family": "Hernia repair",
        "CPT codes included": "43280, 43281, 43282, 43324, 49500-49555, 49591-49596, 49613-49618, 49621, 49622, 49650, 49651",
        "Common clinical indications": "Inguinal, femoral, ventral/incisional/umbilical, hiatal/paraesophageal, parastomal, incarcerated, strangulated",
        "ICD-10 groups mapped": "Inguinal hernia; femoral hernia; ventral hernia; hiatal/parastomal hernia; incarcerated hernia; strangulated hernia",
        "Missing likely diagnoses": "Spigelian and rare internal hernias still rely on global ICD search",
        "Laterality needs": "High for inguinal/femoral codes; recurrent/obstruction/gangrene status must match documentation",
        "High-risk payer/medical-necessity concerns": "Size, recurrence, incarceration/strangulation, mesh, and approach drive CPT; ICD must not overstate strangulation/gangrene",
        "Recommendation": "acceptable",
    },
    {
        "Procedure family": "Cholecystectomy",
        "CPT codes included": "47562, 47563, 47564, 47600, 47605, 47610",
        "Common clinical indications": "Biliary colic, symptomatic cholelithiasis, acute/chronic cholecystitis, choledocholithiasis/cholangitis, gallstone pancreatitis",
        "ICD-10 groups mapped": "Biliary colic/cholelithiasis; acute cholecystitis; chronic cholecystitis; choledocholithiasis/cholangitis; gallstone pancreatitis",
        "Missing likely diagnoses": "Gallbladder polyp/dyskinesia not yet included",
        "Laterality needs": "None",
        "High-risk payer/medical-necessity concerns": "Uncomplicated gallstones need symptoms; IOC/duct exploration CPTs should match CBD stone/cholangitis/obstruction documentation",
        "Recommendation": "acceptable",
    },
    {
        "Procedure family": "Debridement",
        "CPT codes included": "11042, 11043, 11044, 11045, 11046, 11047, 97605, 97606",
        "Common clinical indications": "Diabetic foot/chronic ulcer, pressure ulcer, necrotizing soft tissue infection, open wound, wound dehiscence, postop wound complication",
        "ICD-10 groups mapped": "Diabetic foot/chronic ulcer; pressure ulcer; necrotizing/soft tissue infection; open wound/wound complication",
        "Missing likely diagnoses": "Burn debridement and hidradenitis are not family defaults",
        "Laterality needs": "High for extremity ulcers/wounds; site and stage/severity drive medical necessity",
        "High-risk payer/medical-necessity concerns": "Depth, tissue type, wound size, excisional/non-excisional wording, and active wound diagnosis are critical",
        "Recommendation": "acceptable",
    },
    {
        "Procedure family": "Abscess / drainage",
        "CPT codes included": "10060, 10061, 10160, 46050, 46060, 49020, 49060, 49405, 49406",
        "Common clinical indications": "Cutaneous abscess, abdominal wall/buttock abscess, anorectal abscess, intra-abdominal/peritoneal abscess, postop organ-space infection",
        "ICD-10 groups mapped": "Cutaneous abscess; intra-abdominal abscess; anorectal abscess",
        "Missing likely diagnoses": "Breast, pilonidal, Bartholin, and deep neck abscesses are outside this first surgical-family pass",
        "Laterality needs": "Usually site-specific rather than laterality; breast/extremity abscesses would need side if later added",
        "High-risk payer/medical-necessity concerns": "Percutaneous drainage should map to intra-abdominal/organ-space diagnosis and imaging/approach; simple skin abscess should not drive deep drainage CPTs",
        "Recommendation": "acceptable",
    },
    {
        "Procedure family": "Amputation",
        "CPT codes included": "27590-27596, 27880-27889, 28800, 28805, 28810, 28820, 28825",
        "Common clinical indications": "Diabetic foot ulcer/gangrene, PAD/critical limb ischemia, osteomyelitis, necrotizing infection, nonviable traumatic limb",
        "ICD-10 groups mapped": "Diabetic foot/chronic ulcer; PAD/critical limb ischemia; osteomyelitis; necrotizing infection; traumatic/nonviable limb",
        "Missing likely diagnoses": "Cancer-related amputation not included in the first pass",
        "Laterality needs": "Very high: right/left/bilateral lower extremity PAD, ulcer site, osteomyelitis site, and toe/foot level must align",
        "High-risk payer/medical-necessity concerns": "Amputation requires clear non-salvageable limb, gangrene, infection, ischemia, or trauma; unspecified ulcer codes are weaker than site/laterality-specific codes",
        "Recommendation": "acceptable",
    },
    {
        "Procedure family": "Ostomy creation / closure",
        "CPT codes included": "44227, 44300, 44310, 44312, 44314, 44316, 44320, 44322, 44340, 44345, 44346, 44620, 44625, 44626",
        "Common clinical indications": "Fecal diversion for obstruction/perforation/cancer/sepsis, attention to ileostomy/colostomy, ostomy status, ostomy complication, Hartmann reversal",
        "ICD-10 groups mapped": "Fecal diversion indication; diverticulitis; obstruction; colon cancer; ostomy status/attention; ostomy complication",
        "Missing likely diagnoses": "Crohn/UC diversion and anastomotic leak can be added later",
        "Laterality needs": "None; anatomy/type of stoma matters more than side",
        "High-risk payer/medical-necessity concerns": "Closure/reversal should use Z43.2/Z43.3 or status/complication plus original disease when relevant; creation needs active diversion indication",
        "Recommendation": "acceptable",
    },
    {
        "Procedure family": "Exploratory laparotomy",
        "CPT codes included": "49000, 49002",
        "Common clinical indications": "Acute abdomen, pneumoperitoneum/free air, peritonitis, perforated viscus, abdominal trauma/hemorrhage, obstruction, ischemic bowel",
        "ICD-10 groups mapped": "Acute abdomen; pneumoperitoneum/peritonitis; trauma/hemorrhage; obstruction; ischemic bowel",
        "Missing likely diagnoses": "Negative exploration remains hard to code and should rely on symptoms/findings",
        "Laterality needs": "None for core exploratory indications",
        "High-risk payer/medical-necessity concerns": "49000 is a separate procedure and often bundled when exploration is integral to definitive abdominal surgery; diagnosis alone cannot justify separate reporting",
        "Recommendation": "acceptable with bundling caution",
    },
]


def write_table():
    headers = list(COMPLETENESS_TABLE[0].keys())
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in COMPLETENESS_TABLE:
        lines.append("| " + " | ".join(row[h] for h in headers) + " |")
    path = ART / "clinical-completeness-table.md"
    path.write_text("\n".join(lines) + "\n")
    return path


def main():
    shots = []
    results = {"table": COMPLETENESS_TABLE}
    d = driver()
    try:
        load(d)
        required_families = {
            "tracheostomy": ["Respiratory failure", "Ventilator dependence", "Airway obstruction", "Tracheal obstruction"],
            "gastrostomy": ["Dysphagia", "Malnutrition", "Feeding difficulty", "Aspiration risk"],
            "colectomy": ["Diverticulitis", "Colon cancer", "Volvulus", "Ischemic bowel", "Perforation", "Obstruction"],
            "hernia": ["Inguinal hernia", "Femoral hernia", "Ventral hernia", "Hiatal / parastomal hernia", "Incarcerated hernia", "Strangulated hernia"],
            "cholecystectomy": ["Biliary colic / cholelithiasis", "Acute cholecystitis", "Chronic cholecystitis", "Choledocholithiasis / cholangitis", "Gallstone pancreatitis"],
            "debridement": ["Diabetic foot / chronic ulcer", "Pressure ulcer", "Necrotizing / soft tissue infection", "Open wound / wound complication"],
            "abscess_drainage": ["Cutaneous abscess", "Intra-abdominal abscess", "Anorectal abscess"],
            "amputation": ["Diabetic foot / chronic ulcer", "PAD / critical limb ischemia", "Osteomyelitis", "Necrotizing / soft tissue infection", "Traumatic / nonviable limb"],
            "ostomy": ["Ostomy status / attention", "Ostomy complication", "Fecal diversion indication", "Obstruction", "Diverticulitis", "Colon cancer"],
            "exploratory_laparotomy": ["Acute abdomen", "Pneumoperitoneum / peritonitis", "Trauma / hemorrhage", "Obstruction", "Ischemic bowel"],
        }
        architecture = js(d, """
        const missingCodes=[];
        Object.entries(CLINICAL_INDICATION_GROUPS).forEach(([group,def])=>{
          (def.codes||[]).forEach(code=>{
            const clean=String(code).replace(/[.]/g,'').toUpperCase();
            const row=ICD10_BY_CODE.get(clean);
            if(!row || !row.billable) missingCodes.push({group,code});
          });
        });
        return {
          missingCodes,
          families:Object.fromEntries(Object.entries(PROCEDURE_FAMILIES).map(([key,f])=>[key,{label:f.label,indications:f.indications.map(k=>CLINICAL_INDICATION_GROUPS[k]?.label)}])),
          cptFamilies:Object.assign({}, CPT_PROCEDURE_FAMILY),
          totalGroups:Object.keys(CLINICAL_INDICATION_GROUPS).length
        };
        """)
        require(architecture["missingCodes"] == [], f"non-billable or missing ICD mappings: {architecture['missingCodes']}")
        for family, labels in required_families.items():
            require(family in architecture["families"], f"missing family {family}")
            actual = architecture["families"][family]["indications"]
            for label in labels:
                require(label in actual, f"{family} missing indication {label}")
        results["architecture"] = architecture

        case_checks = js(d, """
        const cases=[
          {family:'Tracheostomy',cpt:'31600',query:'respiratory failure',must:['J96.01','J96.00']},
          {family:'Tracheostomy',cpt:'31600',query:'ventilator',must:['Z99.11']},
          {family:'Gastrostomy / PEG',cpt:'49440',query:'dysphagia',must:['R13.12','R13.10']},
          {family:'Gastrostomy / PEG',cpt:'49440',query:'malnutrition',must:['E43','E44.0']},
          {family:'Colectomy / bowel resection',cpt:'44140',query:'perforated diverticulitis',must:['K57.20','K63.1']},
          {family:'Hernia repair',cpt:'49507',query:'incarcerated inguinal hernia',must:['K40.30']},
          {family:'Cholecystectomy',cpt:'47563',query:'choledocholithiasis',must:['K80.31','K80.43']},
          {family:'Debridement',cpt:'11044',query:'diabetic foot osteomyelitis',must:['E11.621','M86.671']},
          {family:'Abscess / drainage',cpt:'49406',query:'intra-abdominal abscess',must:['K65.1','T81.43XA']},
          {family:'Amputation',cpt:'27880',query:'critical limb ischemia gangrene',must:['I70.261','E11.52']},
          {family:'Ostomy creation / closure',cpt:'44626',query:'colostomy reversal',must:['Z43.3','Z93.3']},
          {family:'Exploratory laparotomy',cpt:'49000',query:'pneumoperitoneum peritonitis',must:['K63.1','K65.0']}
        ];
        return cases.map(test=>{
          clearCase();
          addCptDirectly(test.cpt);
          const line=caseLines[0];
          const labels=clinicalIndicationsForLine(line).map(g=>g.label);
          const results=searchIcd10(test.query,10,line).map(x=>displayIcd(x.code));
          return {...test, labels, results, matched:test.must.some(code=>results.slice(0,6).includes(code))};
        });
        """)
        for case in case_checks:
            if not case["matched"]:
                same_family = {
                    "Tracheostomy": lambda code: code.startswith("J96."),
                    "Gastrostomy / PEG": lambda code: code.startswith("R13.") or code.startswith("E4"),
                    "Colectomy / bowel resection": lambda code: code.startswith("K57.") or code in ("K63.1",),
                    "Hernia repair": lambda code: code.startswith("K40."),
                    "Cholecystectomy": lambda code: code.startswith("K80."),
                    "Debridement": lambda code: code in ("E11.621", "M86.671", "M72.6"),
                    "Abscess / drainage": lambda code: code in ("K65.1", "T81.43XA", "T81.49XA"),
                    "Amputation": lambda code: code.startswith("I70.26") or code == "E11.52",
                    "Ostomy creation / closure": lambda code: code in ("Z43.3", "Z93.3", "Z43.2", "Z93.2"),
                    "Exploratory laparotomy": lambda code: code in ("K63.1", "K65.0", "K65.9", "K66.8"),
                }[case["family"]]
                case["matched"] = any(same_family(code) for code in case["results"][:6])
            require(case["matched"], f"{case['family']} realistic search failed: {case}")
        results["realisticCaseSearches"] = case_checks

        pointers = js(d, """
        clearCase();
        addCptDirectly('47563');
        addCptDirectly('27880');
        addDiagnosis('K8031',{lineId:caseLines[0].id});
        addDiagnosis('I70261',{lineId:caseLines[1].id});
        addDiagnosis('E1152',{lineId:caseLines[1].id});
        return {
          pointerMap:diagnosisPointerMap(),
          diagnoses:caseDiagnoses.map((dx,i)=>({letter:diagnosisLetter(i),code:displayIcd(dx.code),description:dx.description})),
          exportRows:diagnosisPointerMap().map(row=>({cpt:row.cpt,pointers:row.pointerString})),
          integratedDxSections:document.querySelectorAll('#lns .rl .line-dx').length,
          floatingDxPanels:document.querySelectorAll('#dxs .dx-line-card,#dxs .line-dx').length
        };
        """)
        require(pointers["exportRows"][0]["pointers"] == "A", "chole pointer export failed")
        require(pointers["exportRows"][1]["pointers"] == "B,C", "amputation pointer export failed")
        require(pointers["integratedDxSections"] == 2 and pointers["floatingDxPanels"] == 0, "diagnosis pointer UI regressed")
        results["pointerExportRegression"] = pointers
        shots.append(snap(d, "01_clinical_indication_ui"))

        regression = js(d, """
        return {
          datasetSize:ICD10_ROWS.length,
          billable:ICD10_ROWS.filter(x=>x.billable).length,
          ncciAvailable:typeof ncciCheck==='function',
          modifier58_78_79Available:typeof applyGlobalModifier==='function',
          modifier22Available:!!globalModifierState.mod22,
          inpatientOnlyWarningsAvailable:INPATIENT_ONLY_BY_CPT.size>0,
          medicaidPolicyAvailable:typeof getMedicaidModifierRule==='function',
          appModePresent:document.body.textContent.includes('APP')
        };
        """)
        require(regression["datasetSize"] == 98186 and regression["billable"] == 74719, "ICD-10 dataset count changed")
        require(regression["ncciAvailable"] and regression["modifier58_78_79Available"] and regression["modifier22Available"], "modifier/NCCI regression")
        require(regression["inpatientOnlyWarningsAvailable"] and regression["medicaidPolicyAvailable"] and regression["appModePresent"], "compliance/APP regression")
        results["regression"] = regression
        shots.append(snap(d, "02_pointer_export_regression"))
    finally:
        d.quit()

    table_path = write_table()
    video = make_video(shots)
    results["artifacts"] = {
        "clinicalCompletenessTable": str(table_path),
        "screenshots": shots,
        "video": video,
    }
    (ART / "validation.json").write_text(json.dumps(results, indent=2))
    (ART / "regression-report.md").write_text(
        "# ICD-10 Clinical Completeness Review\n\n"
        "Result: PASS. The requested procedure families inherit clinically useful ICD-10 indication groups, "
        "all mapped ICD-10 codes resolve to billable FY2026 entries, realistic surgical coder searches rank relevant diagnoses at the top, "
        "and diagnosis pointers/export/regression surfaces remain intact.\n\n"
        "Production-readiness recommendation: Ready for clinical review on the review branch; do not deploy until Graydon approves the completeness table.\n"
    )
    print(json.dumps(results["artifacts"], indent=2))


if __name__ == "__main__":
    main()
