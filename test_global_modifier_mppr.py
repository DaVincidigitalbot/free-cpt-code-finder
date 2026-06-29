#!/usr/bin/env python3
import json
import pathlib
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ROOT = pathlib.Path(__import__("os").environ.get("FREECPT_ROOT") or pathlib.Path(__file__).resolve().parent).resolve()
URL = ROOT.joinpath("index.html").as_uri()
ARTIFACT_ROOT = pathlib.Path(__import__("os").environ.get("FREECPT_ARTIFACT_ROOT") or ROOT).resolve()

CASES = [
    {
        "name": "Case A - all lines marked Modifier 58",
        "codes": ["44625", "49402", "13160"],
        "global_modifier": "58",
        "mod22_first": False,
        "expect_same_as": "B",
        "expect_addons_full": [],
    },
    {
        "name": "Case B - same lines without Modifier 58",
        "codes": ["44625", "49402", "13160"],
        "global_modifier": None,
        "mod22_first": False,
        "expect_addons_full": [],
    },
    {
        "name": "Case C - Modifier 58 with Modifier 22 candidate and add-on debridement",
        "codes": ["44625", "49402", "11043", "11046"],
        "global_modifier": "58",
        "mod22_first": True,
        "expect_addons_full": ["11046"],
    },
    {
        "name": "Case D - NCCI bundled line with Modifier 58",
        "codes": ["44005", "49000"],
        "global_modifier": "58",
        "mod22_first": False,
        "expect_bundled_zero": ["49000"],
        "expect_addons_full": [],
    },
]

def open_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--allow-file-access-from-files")
    opts.add_argument("--window-size=1440,1200")
    return webdriver.Chrome(options=opts)

def run_case(driver, case):
    driver.get(URL)
    time.sleep(0.2)
    missing = []
    for code in case["codes"]:
        ok = driver.execute_script("return !!getCptSearchEntry(arguments[0]);", code)
        if not ok:
            missing.append(code)
        driver.execute_script("addCptDirectly(arguments[0]);", code)
    if missing:
        raise AssertionError(f"Missing searchable CPT entries: {missing}")
    if case.get("global_modifier"):
        driver.execute_script("applyGlobalModifier(arguments[0]);", case["global_modifier"])
    if case.get("mod22_first"):
        driver.execute_script("caseLines[0].modifier22Selected=true; recalc('test mod22');")
    time.sleep(0.1)
    return driver.execute_script("""
        return {
          totalPayableWrvu: Number(document.getElementById('tn').textContent),
          totalText: document.getElementById('ts').textContent,
          lines: caseLines.map(l => ({
            cpt: l.cpt,
            rank: l.rank,
            mods: l.mods.slice(),
            baseWrvu: Number(l.baseWrvu || 0),
            effectiveWrvu: Number(l.effWrvu || 0),
            payableWrvu: Number(l.payableWrvu || 0),
            mpprFactor: Number(l.sameSessionMpprFactor || 0),
            pay: Number(l.pay || 0),
            payableExcluded: !!l.payableExcluded,
            addon: !!lineIsAddon(l),
            denials: l.modifierDenials || [],
            warnings: l.warnings || []
          }))
        };
    """)

def assert_case(name, result, case_b_result=None, case=None):
    lines = result["lines"]
    payable = [l for l in lines if not l["payableExcluded"] and not l["addon"]]
    if payable:
        if payable[0]["mpprFactor"] != 1:
            raise AssertionError(f"{name}: primary MPPR factor was {payable[0]['mpprFactor']}, expected 1")
        for l in payable[1:]:
            if "58" in l["mods"] and l["mpprFactor"] == 1:
                raise AssertionError(f"{name}: {l['cpt']}-58 bypassed MPPR")
            expected = round(l["effectiveWrvu"] * l["mpprFactor"], 6)
            if abs(l["payableWrvu"] - expected) > 0.0001:
                raise AssertionError(f"{name}: {l['cpt']} payable wRVU {l['payableWrvu']} != {expected}")
    if case and case.get("global_modifier"):
        for l in lines:
            if not l["payableExcluded"] and not l["addon"] and case["global_modifier"] not in l["mods"]:
                raise AssertionError(f"{name}: {l['cpt']} missing global modifier display")
    if case and case.get("mod22_first"):
        first = lines[0]
        if "22" not in first["mods"]:
            raise AssertionError(f"{name}: first line missing Modifier 22 marker")
        if first["mpprFactor"] != 1:
            raise AssertionError(f"{name}: Modifier 22 changed primary MPPR factor")
    if case:
        for code in case.get("expect_addons_full", []):
            found = next((l for l in lines if l["cpt"] == code), None)
            if not found:
                raise AssertionError(f"{name}: add-on {code} not found")
            if not found["addon"] or found["mpprFactor"] != 1:
                raise AssertionError(f"{name}: add-on {code} did not keep normal add-on full-payment logic")
        for code in case.get("expect_bundled_zero", []):
            found = next((l for l in lines if l["cpt"] == code), None)
            if not found:
                raise AssertionError(f"{name}: bundled code {code} not found")
            if not found["payableExcluded"] or found["payableWrvu"] != 0:
                raise AssertionError(f"{name}: Modifier 58 overrode NCCI/bundling exclusion for {code}")
    if case_b_result:
        a = [round(l["payableWrvu"], 4) for l in lines]
        b = [round(l["payableWrvu"], 4) for l in case_b_result["lines"]]
        if a != b:
            raise AssertionError(f"{name}: Modifier 58 changed MPPR payable wRVU math: {a} != {b}")

def main():
    artifacts = ARTIFACT_ROOT / "qa_artifacts" / "global_modifier_mppr_fix"
    artifacts.mkdir(parents=True, exist_ok=True)
    driver = open_driver()
    try:
        results = {}
        for case in CASES:
            result = run_case(driver, case)
            results[case["name"]] = result
            safe = case["name"].lower().replace(" ", "_").replace("-", "").replace("/", "_")
            driver.save_screenshot(str(artifacts / f"{safe}.png"))
        assert_case("Case B", results["Case B - same lines without Modifier 58"], case=CASES[1])
        assert_case("Case A", results["Case A - all lines marked Modifier 58"], results["Case B - same lines without Modifier 58"], CASES[0])
        assert_case("Case C", results["Case C - Modifier 58 with Modifier 22 candidate and add-on debridement"], case=CASES[2])
        assert_case("Case D", results["Case D - NCCI bundled line with Modifier 58"], case=CASES[3])
        out = {"status": "pass", "url": URL, "cases": results}
        (artifacts / "mppr_math_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(json.dumps(out, indent=2))
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
