import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent
INDEX_HTML = (ROOT / "index.html").read_text(encoding="utf-8")
GUIDE_HTML = (ROOT / "blog/guides/cpt-code-inguinal-hernia-repair.html").read_text(encoding="utf-8")


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def spec_wrvu(code):
    match = re.search(rf'\["{code}","[^"]+",([0-9.]+),1\]', INDEX_HTML)
    assert match, f"{code} missing from on-page specialty/search data"
    return float(match.group(1))


def guide_wrvu(code):
    match = re.search(
        rf"<td><strong>{code}</strong></td>\s*<td>.*?</td>\s*<td>.*?</td>\s*<td>([0-9.]+)</td>",
        GUIDE_HTML,
        re.S,
    )
    assert match, f"{code} missing from inguinal guide table"
    return float(match.group(1))


def test_inguinal_wrvu_source_data_is_current_work_rvu():
    for path in ["cpt_database.json", "rvu_database.json", "public/rvu_database.json"]:
        data = load_json(path)
        if "codes" in data:
            data = data["codes"]
        assert data["49650"]["work_rvu"] == 6.20
        assert data["49651"]["work_rvu"] == 8.17


def test_inguinal_guideline_table_uses_wrvu_labels_and_values():
    assert "<th>WRVU</th>" in GUIDE_HTML
    assert "12.00" not in GUIDE_HTML
    assert "14.22" not in GUIDE_HTML
    assert guide_wrvu("49650") == 6.20
    assert guide_wrvu("49651") == 8.17


def test_search_and_case_builder_wrvus_match_guideline_table():
    assert spec_wrvu("49650") == guide_wrvu("49650")
    assert spec_wrvu("49651") == guide_wrvu("49651")
    assert "wRVU ${Number(item.wrvu||0).toFixed(2)}" in INDEX_HTML
    assert "addAutocompleteResultToCase(item)" in INDEX_HTML
    assert "addProc(cpt,desc,w" in INDEX_HTML


def test_bilateral_modifier_calculates_expected_wrvu():
    assert 6.20 * 1.5 == pytest.approx(9.30)
    assert 8.17 * 1.5 == pytest.approx(12.255)
    assert Decimal("12.255").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal("12.26")
    assert "l.effWrvu=Number((l.baseWrvu*1.5).toFixed(6))" in INDEX_HTML


def test_case_builder_has_inguinal_bilateral_sources():
    assert re.search(r'\["49650","[^"]+",6\.2,1\]', INDEX_HTML)
    assert re.search(r'\["49651","[^"]+",8\.17,1\]', INDEX_HTML)
    assert "'49651':['K40.91','K40.31']" in INDEX_HTML


def test_decision_tree_recurrent_49651_and_initial_49650_paths():
    tree = load_json("cpt_decision_tree.json")
    branches = tree["categories"][0]["branches"]
    initial_lap_codes = {o["label"]: o["cpt_code"] for o in branches["inguinal_lap"]["options"]}
    recurrent_lap_codes = {o["label"]: o["cpt_code"] for o in branches["inguinal_recurrent_lap"]["options"]}
    assert initial_lap_codes == {"Unilateral": "49650", "Bilateral": "49650"}
    assert recurrent_lap_codes == {"Unilateral": "49651", "Bilateral": "49651"}
