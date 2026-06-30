#!/usr/bin/env python3
import json
import pathlib
import subprocess
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


ROOT = pathlib.Path(__file__).resolve().parent
ART = ROOT / "qa_artifacts" / "icd10_procedure_family_architecture"
ART.mkdir(parents=True, exist_ok=True)
URL = ROOT.joinpath("index.html").as_uri()


def driver(width=1500, height=1250):
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
    out = ART / "procedure_family_architecture_workflow.mp4"
    try:
        subprocess.run([
            "ffmpeg", "-y", "-framerate", "1", "-i", str(frames / "frame_%03d.png"),
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-pix_fmt", "yuv420p", str(out)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(out)
    except Exception:
        return None


def main():
    shots = []
    results = {}
    d = driver()
    try:
        load(d)
        architecture = js(d, """
        return {
          families:Object.fromEntries(Object.entries(PROCEDURE_FAMILIES).map(([key,f])=>[key,{label:f.label,indications:f.indications}])),
          cptFamilies:{
            '31600':CPT_PROCEDURE_FAMILY['31600'],
            '31601':CPT_PROCEDURE_FAMILY['31601'],
            '49440':CPT_PROCEDURE_FAMILY['49440'],
            '43246':CPT_PROCEDURE_FAMILY['43246'],
            '44140':CPT_PROCEDURE_FAMILY['44140'],
            '49507':CPT_PROCEDURE_FAMILY['49507']
          }
        };
        """)
        require(architecture["cptFamilies"]["31600"] == "tracheostomy", "31600 did not inherit tracheostomy family")
        require(architecture["cptFamilies"]["49440"] == "gastrostomy", "49440 did not inherit gastrostomy family")
        require(architecture["cptFamilies"]["44140"] == "colectomy", "44140 did not inherit colectomy family")
        require(architecture["cptFamilies"]["49507"] == "hernia", "49507 did not inherit hernia family")
        results["architecture"] = architecture

        inherited = js(d, """
        clearCase();
        addCptDirectly('31600');
        const trach=caseLines[0];
        const trachIndications=clinicalIndicationsForLine(trach).map(g=>g.label);
        const trachCard=document.querySelector('#lns .rl').textContent;
        clearCase();
        addCptDirectly('49440');
        const peg=caseLines[0];
        const pegIndications=clinicalIndicationsForLine(peg).map(g=>g.label);
        const pegCard=document.querySelector('#lns .rl').textContent;
        clearCase();
        addCptDirectly('44140');
        const colectomy=caseLines[0];
        const colectomyIndications=clinicalIndicationsForLine(colectomy).map(g=>g.label);
        clearCase();
        addCptDirectly('49507');
        const hernia=caseLines[0];
        const herniaIndications=clinicalIndicationsForLine(hernia).map(g=>g.label);
        return {trachIndications,trachCard,pegIndications,pegCard,colectomyIndications,herniaIndications};
        """)
        for expected in ["Respiratory failure", "Ventilator dependence", "Airway obstruction", "Tracheal obstruction"]:
            require(expected in inherited["trachIndications"], f"tracheostomy missing {expected}")
            require(expected in inherited["trachCard"], f"tracheostomy UI missing {expected}")
        for expected in ["Dysphagia", "Malnutrition", "Feeding difficulty", "Aspiration risk"]:
            require(expected in inherited["pegIndications"], f"gastrostomy missing {expected}")
            require(expected in inherited["pegCard"], f"gastrostomy UI missing {expected}")
        for expected in ["Diverticulitis", "Colon cancer", "Volvulus", "Ischemic bowel", "Perforation", "Obstruction"]:
            require(expected in inherited["colectomyIndications"], f"colectomy missing {expected}")
        for expected in ["Inguinal hernia", "Femoral hernia", "Ventral hernia", "Incarcerated hernia", "Strangulated hernia"]:
            require(expected in inherited["herniaIndications"], f"hernia missing {expected}")
        results["inheritance"] = inherited
        shots.append(snap(d, "01_inherited_indication_ui"))

        ranking = js(d, """
        clearCase();
        addCptDirectly('31600');
        const trach=caseLines[0];
        const respiratory=searchIcd10('respiratory failure',8,trach).map(x=>displayIcd(x.code));
        const ventilator=searchIcd10('ventilator',8,trach).map(x=>displayIcd(x.code));
        clearCase();
        addCptDirectly('49440');
        const peg=caseLines[0];
        const dysphagia=searchIcd10('dysphagia',8,peg).map(x=>displayIcd(x.code));
        const feeding=searchIcd10('feeding difficulty',8,peg).map(x=>displayIcd(x.code));
        clearCase();
        addCptDirectly('44140');
        const colectomy=caseLines[0];
        const obstruction=searchIcd10('obstruction',8,colectomy).map(x=>displayIcd(x.code));
        clearCase();
        addCptDirectly('49507');
        const hernia=caseLines[0];
        const incarcerated=searchIcd10('incarcerated hernia',8,hernia).map(x=>displayIcd(x.code));
        return {respiratory,ventilator,dysphagia,feeding,obstruction,incarcerated};
        """)
        require(any(code.startswith("J96.") for code in ranking["respiratory"][:4]), "respiratory failure ranking failed")
        require("Z99.11" in ranking["ventilator"][:3], "ventilator ranking failed")
        require(any(code.startswith("R13.") for code in ranking["dysphagia"][:4]), "dysphagia ranking failed")
        require(any(code.startswith("R63.") for code in ranking["feeding"][:4]), "feeding difficulty ranking failed")
        require(any(code.startswith("K56.") for code in ranking["obstruction"][:5]), "colectomy obstruction ranking failed")
        require(any(code.startswith("K40.") for code in ranking["incarcerated"][:5]), "hernia incarcerated ranking failed")
        results["ranking"] = ranking

        pointers = js(d, """
        clearCase();
        addCptDirectly('31600');
        addCptDirectly('49440');
        addDiagnosis('J9601',{lineId:caseLines[0].id});
        addDiagnosis('Z9911',{lineId:caseLines[0].id});
        addDiagnosis('R1312',{lineId:caseLines[1].id});
        addDiagnosis('E43',{lineId:caseLines[1].id});
        return {
          map:diagnosisPointerMap(),
          diagnoses:caseDiagnoses.map((dx,i)=>({letter:diagnosisLetter(i),code:displayIcd(dx.code),description:dx.description})),
          exportShape:diagnosisPointerMap().map(row=>({cpt:row.cpt,diagnosisPointerField:row.pointerString})),
          globalFloatingCards:document.querySelectorAll('#dxs .dx-line-card,#dxs .line-dx').length,
          integratedDxSections:document.querySelectorAll('#lns .rl .line-dx').length
        };
        """)
        require(pointers["map"][0]["pointerString"] == "A,B", "trach pointer string failed")
        require(pointers["map"][1]["pointerString"] == "C,D", "gastrostomy pointer string failed")
        require(pointers["globalFloatingCards"] == 0 and pointers["integratedDxSections"] == 2, "pointer UI ownership regressed")
        results["pointersAndExport"] = pointers
        shots.append(snap(d, "02_pointer_export_validation"))

        regression = js(d, """
        return {
          ncciAvailable:typeof ncciCheck==='function',
          globalModifierAvailable:typeof applyGlobalModifier==='function' && typeof setCaseBuilderUserModifier==='function',
          inpatientOnlyWarningsAvailable:INPATIENT_ONLY_BY_CPT.size>0,
          medicaidPolicyAvailable:typeof getMedicaidModifierRule==='function',
          appModeTextPresent:document.body.textContent.includes('APP'),
          datasetSize:ICD10_ROWS.length,
          billable:ICD10_ROWS.filter(x=>x.billable).length
        };
        """)
        require(regression["datasetSize"] == 98186 and regression["billable"] == 74719, "ICD dataset changed")
        require(regression["ncciAvailable"] and regression["globalModifierAvailable"], "modifier/NCCI surfaces unavailable")
        require(regression["inpatientOnlyWarningsAvailable"] and regression["medicaidPolicyAvailable"], "compliance warning surfaces unavailable")
        results["regression"] = regression
    finally:
        d.quit()

    video = make_video(shots)
    diagram = """# ICD-10 Procedure Family Architecture

## Data Flow

    CPT line
      -> CPT_PROCEDURE_FAMILY[cpt]
      -> PROCEDURE_FAMILIES[family].indications
      -> CLINICAL_INDICATION_GROUPS[indication].codes
      -> ICD10_ROWS / ICD10_BY_CODE metadata
      -> Common indications UI + CPT-card search ranking
      -> Diagnosis pointer map + export surfaces

## Current Family Map

    Tracheostomy Family
      -> Respiratory failure
      -> Ventilator dependence
      -> Airway obstruction
      -> Tracheal obstruction

    Gastrostomy Family
      -> Dysphagia
      -> Malnutrition
      -> Feeding difficulty
      -> Aspiration risk

    Colectomy Family
      -> Diverticulitis
      -> Colon cancer
      -> Volvulus
      -> Ischemic bowel
      -> Perforation
      -> Obstruction

    Hernia Family
      -> Inguinal hernia
      -> Femoral hernia
      -> Ventral hernia
      -> Incarcerated hernia
      -> Strangulated hernia

## Maintenance Pattern

    Add a new CPT:
      1. Add CPT_PROCEDURE_FAMILY['code']='family'
      2. Only add CPT_ICD10_ADDITIONS when the CPT needs diagnoses beyond family inheritance
      3. Add/adjust CLINICAL_INDICATION_GROUPS once when a concept should apply across multiple CPTs
"""
    (ART / "architecture-diagrams.md").write_text(diagram, encoding="utf-8")
    report = {
        "status": "pass",
        "branch": "review/icd10-procedure-family-architecture",
        "architectureDiagrams": str(ART / "architecture-diagrams.md"),
        "screenshots": shots,
        "browserVideo": video,
        "results": results,
        "productionReadinessRecommendation": "Ready for review, not production deploy. Architecture is cleaner and regression gates passed; final approval should focus on clinical completeness of each indication group's ICD-10 list before deployment."
    }
    (ART / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ART / "regression-report.md").write_text(
        "# ICD-10 Procedure Family Architecture Regression Report\n\n"
        "- Family inheritance: PASS\n"
        "- Common indication UI: PASS\n"
        "- Indication-to-ICD expansion: PASS\n"
        "- CPT-card search ranking: PASS\n"
        "- Diagnosis pointer generation: PASS\n"
        "- Export pointer shape: PASS\n"
        "- NCCI/global modifier/inpatient-only/Medicaid surfaces: PASS\n\n"
        "Production readiness recommendation: Ready for review, not production deploy. Validate clinical completeness of indication groups before approval.\n",
        encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
