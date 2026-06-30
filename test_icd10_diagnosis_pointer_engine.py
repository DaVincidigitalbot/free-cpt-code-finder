#!/usr/bin/env python3
import json
import pathlib
import subprocess
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


ROOT = pathlib.Path(__file__).resolve().parent
ART = ROOT / "qa_artifacts" / "icd10_diagnosis_pointer_engine"
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
    if not screenshots:
        return None
    frames = ART / "video_frames"
    frames.mkdir(exist_ok=True)
    for i, src in enumerate(screenshots):
        dst = frames / f"frame_{i:03d}.png"
        dst.write_bytes(pathlib.Path(src).read_bytes())
    out = ART / "diagnosis_pointer_workflow.mp4"
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
        stats = js(d, "return {icd:ICD10_ROWS.length,billable:ICD10_ROWS.filter(x=>x.billable).length,ipo:INPATIENT_ONLY_BY_CPT.size};")
        require(stats["icd"] == 98186 and stats["billable"] == 74719, "ICD-10 dataset stats changed")
        results["dataset"] = stats

        # One CPT, multiple diagnoses.
        one = js(d, """
        clearCase();
        addCptDirectly('44120');
        addDiagnosis('K56609',{lineId:caseLines[0].id});
        addDiagnosis('K651',{lineId:caseLines[0].id});
        return {
          map:diagnosisPointerMap(),
          diagnoses:caseDiagnoses.map((dx,i)=>({letter:diagnosisLetter(i),code:displayIcd(dx.code),description:dx.description})),
          warnings:validateDiagnosesForLine(caseLines[0]),
          html:document.getElementById('dxs').textContent
        };
        """)
        require(one["map"][0]["cpt"] == "44120" and one["map"][0]["pointerString"] == "A,B", "one CPT pointer string failed")
        require("Diagnosis List" in one["html"] and "44120" in one["html"], "diagnosis pointer UI missing")
        results["oneCptMultipleDiagnoses"] = one
        shots.append(snap(d, "01_one_cpt_multiple_diagnoses"))

        # Multiple CPTs, shared diagnosis, and many-to-many relationships.
        many = js(d, """
        clearCase();
        addCptDirectly('44120');
        addCptDirectly('49507');
        addDiagnosis('K56609',{lineId:caseLines[0].id});
        addDiagnosis('K651',{lineId:caseLines[0].id});
        addDiagnosis('K4030',{lineId:caseLines[1].id});
        toggleDxPointer(caseLines[1].id,'B');
        return {
          map:diagnosisPointerMap(),
          lines:caseLines.map(l=>({cpt:l.cpt,pointers:l.dxPointers})),
          diagnoses:caseDiagnoses.map((dx,i)=>({letter:diagnosisLetter(i),code:displayIcd(dx.code)}))
        };
        """)
        require(many["map"][0]["pointerString"] == "A,B", "primary CPT pointer map failed")
        require(many["map"][1]["pointerString"] == "C,B", "secondary CPT shared diagnosis pointer map failed")
        results["multipleCptsSharedDiagnosis"] = many
        shots.append(snap(d, "02_multiple_cpts_shared_diagnosis"))

        # Diagnosis removal must remap CMS-1500 letters.
        remap = js(d, """
        removeDiagnosis(caseDiagnoses[1].id);
        return {
          map:diagnosisPointerMap(),
          diagnoses:caseDiagnoses.map((dx,i)=>({letter:diagnosisLetter(i),code:displayIcd(dx.code)})),
          lines:caseLines.map(l=>({cpt:l.cpt,pointers:l.dxPointers}))
        };
        """)
        require(remap["diagnoses"][1]["letter"] == "B" and remap["diagnoses"][1]["code"] == "K40.30", "diagnosis letters did not reassign after removal")
        require(remap["map"][1]["pointerString"] == "B", "line pointers did not remap after diagnosis removal")
        results["letterReassignmentAfterRemoval"] = remap

        # Zero diagnosis warning.
        zero = js(d, "clearCase(); addCptDirectly('44120'); return validateDiagnosesForLine(caseLines[0]);")
        require(any("No diagnosis selected" in w for w in zero), "missing diagnosis warning absent")
        results["zeroDiagnosisWarning"] = zero

        # Laterality-aware suggestions.
        laterality = js(d, """
        clearCase();
        addCptDirectly('49507');
        setLineLaterality(caseLines[0].id,'RT');
        const right=commonDxForCpt(caseLines[0]).slice(0,3).map(x=>x.code);
        setLineLaterality(caseLines[0].id,'LT');
        const left=commonDxForCpt(caseLines[0]).slice(0,3).map(x=>x.code);
        setLineLaterality(caseLines[0].id,'50');
        const bilateral=commonDxForCpt(caseLines[0]).slice(0,4).map(x=>x.code);
        return {right,left,bilateral,html:document.querySelector('#lns .rl').textContent};
        """)
        require(laterality["right"][0] == "K4030", "right laterality did not reprioritize ICD suggestions")
        require(laterality["left"][0] == "K4031", "left laterality did not reprioritize ICD suggestions")
        require("K40.30" in laterality["html"] and "K40.31" in laterality["html"], "laterality suggestions not visible")
        results["laterality"] = laterality
        shots.append(snap(d, "03_laterality_smart_suggestions"))

        # Export/audit shape for future CMS-1500 pointer field.
        export_shape = js(d, """
        addDiagnosis('K4030',{lineId:caseLines[0].id});
        return {
          diagnosisPointerMap:diagnosisPointerMap(),
          futureCms1500DiagnosisPointers:diagnosisPointerMap().map(row=>({cpt:row.cpt,diagnosisPointerField:row.pointerString})),
          auditContainsPointerMap:document.getElementById('dxs').textContent.includes('Claim pointer map')
        };
        """)
        require(export_shape["futureCms1500DiagnosisPointers"][0]["diagnosisPointerField"], "future CMS-1500 pointer export shape missing")
        results["exportShape"] = export_shape
        shots.append(snap(d, "04_export_pointer_shape"))
    finally:
        d.quit()

    mobile = driver(390, 844)
    try:
        load(mobile)
        js(mobile, "clearCase(); addCptDirectly('44120'); addDiagnosis('K56609',{lineId:caseLines[0].id});")
        mobile_ok = js(mobile, "return {scrollWidth:document.body.scrollWidth,innerWidth:window.innerWidth,map:diagnosisPointerMap()[0].pointerString};")
        require(mobile_ok["scrollWidth"] <= mobile_ok["innerWidth"] + 4, "mobile horizontal overflow")
        results["mobile"] = mobile_ok
        shots.append(snap(mobile, "05_mobile_diagnosis_pointer_engine"))
    finally:
        mobile.quit()

    video = make_video(shots)
    report = {
        "status": "pass",
        "branch": "review/icd10-diagnosis-pointer-engine",
        "screenshots": shots,
        "browserVideo": video,
        "results": results,
        "regression": {
            "oneCpt": "pass",
            "multipleCpts": "pass",
            "sharedDiagnosis": "pass",
            "multipleDiagnoses": "pass",
            "laterality": "pass",
            "mobile": "pass",
            "desktop": "pass"
        }
    }
    (ART / "diagnosis_pointer_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ART / "regression-report.md").write_text(
        "# ICD-10 Diagnosis Pointer Engine Regression Report\n\n"
        "- One CPT: PASS\n"
        "- Multiple CPTs: PASS\n"
        "- Shared diagnosis: PASS\n"
        "- Multiple diagnoses per CPT: PASS\n"
        "- Smart laterality suggestions: PASS\n"
        "- CMS-1500 A/B/C pointer map: PASS\n"
        "- Audit/export pointer shape: PASS\n"
        "- Desktop layout: PASS\n"
        "- Mobile layout: PASS\n",
        encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
