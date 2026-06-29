#!/usr/bin/env python3
import json
import pathlib
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ROOT = pathlib.Path(__file__).resolve().parent
ART = ROOT / "qa_artifacts" / "medicaid_payer_mode_modifier_warnings"
ART.mkdir(parents=True, exist_ok=True)
URL = ROOT.joinpath("index.html").as_uri()

def driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--allow-file-access-from-files")
    opts.add_argument("--window-size=1440,1200")
    return webdriver.Chrome(options=opts)

def setup(d, payer="medicaid"):
    d.get(URL)
    time.sleep(.25)
    d.execute_script("payer=arguments[0]; document.querySelectorAll('#payer-seg button').forEach(b=>b.classList.toggle('on',b.dataset.v===arguments[0])); recalc('test payer');", payer)

def snapshot(d, name):
    d.save_screenshot(str(ART / f"{name}.png"))
    return d.execute_script("""
      return {
        payer,
        panelVisible: document.getElementById('medicaidCasePanel').classList.contains('show'),
        panelText: document.getElementById('medicaidCasePanel').textContent.trim(),
        state: getModifierConflictState(),
        totalWrvu: document.getElementById('tn').textContent,
        totalText: document.getElementById('ts').textContent,
        warningsRendered: document.body.textContent.includes('Medicaid modifier rules vary by state and Medicaid managed-care plan'),
        lineWarnings: caseLines.map(l=>({cpt:l.cpt,mods:l.mods,medicaidWarnings:l.medicaidWarnings||[],payable:l.payableWrvu,engineState:l.engineState}))
      }
    """)

def add(d, code, laterality=""):
    d.execute_script("""
      const item=getCptSearchEntry(arguments[0]);
      if(!item) throw new Error('missing '+arguments[0]);
      addProc(item.code,item.description,item.wrvu||0,arguments[1]||'',item.bi||0,undefined,undefined,{technicalComponent:item.technicalComponent,estimatedPayment:item.estimatedPayment,totalRvu:item.totalRvu,addonCode:item.addonCode});
    """, code, laterality)

def require(cond, msg):
    if not cond:
        raise AssertionError(msg)

def warning_mods(result):
    return [w["modifier"] for l in result["lineWarnings"] for w in l["medicaidWarnings"]]

def main():
    d = driver()
    results = {}
    try:
        setup(d, "medicaid")
        add(d, "44625")
        d.execute_script("caseLines[0].modifier22Selected=true; recalc('mod22 selected');")
        results["medicaid_modifier_22"] = snapshot(d, "medicaid_modifier_22")
        require("22" in warning_mods(results["medicaid_modifier_22"]), "Modifier 22 Medicaid caution missing")

        setup(d, "medicaid")
        add(d, "49505", "LT")
        add(d, "49505", "RT")
        results["medicaid_lt_rt"] = snapshot(d, "medicaid_lt_rt")
        mods = warning_mods(results["medicaid_lt_rt"])
        require("LT" in mods and "RT" in mods, "LT/RT Medicaid cautions missing")

        setup(d, "medicaid")
        add(d, "44625")
        add(d, "49402")
        d.execute_script("caseLines[1].userMod='52'; recalc('modifier 52 selected');")
        results["medicaid_modifier_52"] = snapshot(d, "medicaid_modifier_52")
        require("52" in warning_mods(results["medicaid_modifier_52"]), "Modifier 52 Medicaid caution missing")

        setup(d, "medicaid")
        add(d, "44625")
        add(d, "49402")
        d.execute_script("caseLines[1].userMod='53'; recalc('modifier 53 selected');")
        results["medicaid_modifier_53"] = snapshot(d, "medicaid_modifier_53")
        require("53" in warning_mods(results["medicaid_modifier_53"]), "Modifier 53 Medicaid caution missing")

        setup(d, "medicaid")
        add(d, "44625")
        add(d, "49402")
        d.execute_script("applyGlobalModifier('58');")
        results["medicaid_modifier_58"] = snapshot(d, "medicaid_modifier_58")
        require(results["medicaid_modifier_58"]["panelVisible"], "Medicaid panel hidden with modifier 58")
        require("58" in results["medicaid_modifier_58"]["lineWarnings"][0]["mods"], "Modifier 58 display missing")
        require("58" not in warning_mods(results["medicaid_modifier_58"]), "Modifier 58 incorrectly received Medicaid-specific warning")

        setup(d, "medicare")
        add(d, "44625")
        d.execute_script("caseLines[0].modifier22Selected=true; recalc('medicare mod22');")
        results["medicare_unchanged"] = snapshot(d, "medicare_unchanged")
        require(not results["medicare_unchanged"]["panelVisible"], "Medicare unexpectedly shows Medicaid panel")
        require(not warning_mods(results["medicare_unchanged"]), "Medicare unexpectedly has Medicaid warnings")

        setup(d, "commercial")
        add(d, "49505", "LT")
        results["commercial_unchanged"] = snapshot(d, "commercial_unchanged")
        require(not results["commercial_unchanged"]["panelVisible"], "Commercial unexpectedly shows Medicaid panel")
        require(not warning_mods(results["commercial_unchanged"]), "Commercial unexpectedly has Medicaid warnings")

        setup(d, "medicaid")
        add(d, "44625")
        d.execute_script("caseLines[0].modifier22Selected=true; recalc('export test');")
        export_data = d.execute_script("""
          return {
            medicaidReview: payer==='medicaid'?{
              warning:medicaidCaseWarningText(),
              behavior:'Default Medicaid behavior is caution, not hard denial, unless a verified state or payer-specific rules table says a modifier is not accepted.',
              rulesDataStructure:MEDICAID_MODIFIER_RULES
            }:null,
            lineWarnings: caseLines.map(l=>l.medicaidWarnings||[])
          };
        """)
        results["export_validation"] = export_data
        require(export_data["medicaidReview"] and export_data["lineWarnings"][0][0]["modifier"] == "22", "Export Medicaid warning payload missing")

        (ART / "medicaid_modifier_validation.json").write_text(json.dumps({"status":"pass","results":results}, indent=2), encoding="utf-8")
        print(json.dumps({"status":"pass","artifactDir":str(ART),"validated":list(results)}, indent=2))
    finally:
        d.quit()

if __name__ == "__main__":
    main()

