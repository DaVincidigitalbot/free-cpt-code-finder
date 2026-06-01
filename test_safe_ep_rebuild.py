import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INDEX_HTML = (ROOT / "index.html").read_text()
CATEGORY_HTML = (ROOT / "categories" / "cardiac-electrophysiology.html").read_text()
CPT_DB = json.loads((ROOT / "cpt_database.json").read_text())
RVU_DB = json.loads((ROOT / "rvu_database.json").read_text())["codes"]
SPECIALTY_HIERARCHY = json.loads((ROOT / "specialty_hierarchy.json").read_text())


REQUIRED_EP_CODES = {
    "99204", "99214", "99215", "93000", "93010", "92960", "93660",
    "93224", "93227", "93228", "93229", "93241", "93244", "93248",
    "93279", "93280", "93281", "93282", "93283", "93284", "93288",
    "93289", "93291", "93294", "93295", "93296", "93298", "33206",
    "33207", "33208", "33224", "33225", "33227", "33228", "33229",
    "33233", "33244", "33249", "33262", "33263", "33264", "33270",
    "33274", "33285", "93650", "93653", "93654", "93655", "93656",
    "93657",
}

REQUIRED_ALIASES = {
    "Electrophysiology", "Cardiac EP", "EP", "Heart Rhythm", "Arrhythmia",
    "Pacemaker", "ICD", "Defibrillator", "Ablation", "Loop Recorder",
    "Rhythm Monitoring", "Cardiophysiology",
}

DELETED_HERNIA_CODES = {"49568", "49652", "49653", "49654", "49655", "49656", "49657"}


def specs_object_text():
    marker = "const SPECS="
    start = INDEX_HTML.index(marker) + len(marker)
    depth = 0
    in_string = False
    escape = False
    for pos in range(start, len(INDEX_HTML)):
        ch = INDEX_HTML[pos]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return INDEX_HTML[start : pos + 1]
    raise AssertionError("Could not parse SPECS object")


def active_spec_codes():
    return set(re.findall(r'\["(\d{5})"', specs_object_text()))


def ep_rows():
    return {
        code: entry
        for code, entry in CPT_DB.items()
        if entry.get("specialty_id") == "cardiac_electrophysiology"
        or entry.get("specialty") == "Cardiac Electrophysiology"
    }


def work_rvu(code):
    return float(RVU_DB[code]["work_rvu"])


def test_sources_page_is_rooted_and_globally_linked():
    assert (ROOT / "sources.html").exists()
    assert 'href="/sources.html"' in INDEX_HTML or 'href="sources.html"' in INDEX_HTML
    assert '["/sources.html", "Sources"]' in (ROOT / "js" / "site-chrome.js").read_text()


def test_ep_category_loader_supports_object_database_and_empty_state():
    for text in [
        "Array.isArray(data.codes)",
        "Object.entries(data||{})",
        'specialty_id === "cardiac_electrophysiology"',
        'specialty === "Cardiac Electrophysiology"',
        "No Cardiac Electrophysiology CPT rows loaded",
    ]:
        assert text in CATEGORY_HTML


def test_ep_specialty_aliases_and_required_codes_present():
    rows = ep_rows()
    assert REQUIRED_EP_CODES <= set(rows)
    assert len(rows) == 52

    ep_specialty = next(
        specialty
        for specialty in SPECIALTY_HIERARCHY["specialties"]
        if specialty["id"] == "cardiac_electrophysiology"
    )
    assert REQUIRED_ALIASES <= set(ep_specialty["aliases"])


def test_ep_add_on_and_technical_flags_are_explicit():
    for code in ["33225", "93655", "93657"]:
        entry = CPT_DB[code]
        assert entry["add_on_code"] is True
        assert entry["standalone_primary_allowed"] is False

    for code in ["93229", "93296"]:
        entry = CPT_DB[code]
        assert entry["technical_component"] is True
        assert float(entry["work_rvu"]) == 0.0
        assert float(RVU_DB[code]["work_rvu"]) == 0.0


def test_ep_study_codes_are_normalized_and_93620_is_not_zero():
    assert (ROOT / "codes" / "93619.html").exists()
    for code in ["93619", "93620"]:
        entry = CPT_DB[code]
        page = (ROOT / "codes" / f"{code}.html").read_text()
        assert entry["specialty_id"] == "cardiac_electrophysiology"
        assert entry["specialty"] == "Cardiac Electrophysiology"
        assert entry["work_rvu"] > 0
        assert "Cardiac Electrophysiology" in page
        assert "0.00 Work RVU" not in page
        assert not entry.get("inclusive_of")
    assert "93620" not in active_spec_codes()


def test_homepage_hydrates_embedded_specs_from_database_source_of_truth():
    for text in [
        "function normalizeCptDatabaseRows",
        "function hydrateSpecsFromDatabase",
        "fetch('cpt_database.json')",
        "hydrateSpecsFromDatabase(external)",
        "buildSearchIndexFromSpecs()",
    ]:
        assert text in INDEX_HTML


def test_deleted_anterior_hernia_codes_are_not_active_case_builder_prompts():
    active_codes = active_spec_codes()
    assert not (DELETED_HERNIA_CODES & active_codes)

    for file_name in ["js/specialty_navigator.js", "js/icd10_engine.js"]:
        text = (ROOT / file_name).read_text()
        for code in DELETED_HERNIA_CODES:
            assert code not in text


def test_required_case_builder_math_uses_work_rvu_values():
    expected = {
        ("93656",): 16.58,
        ("93656", "93657"): 21.94,
        ("33249",): 14.55,
        ("33249", "33225"): 22.67,
        ("93229",): 0.00,
        ("93295", "93296"): 0.72,
    }
    for codes, total in expected.items():
        assert round(sum(work_rvu(code) for code in codes), 2) == total
