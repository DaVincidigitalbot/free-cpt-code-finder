import json
from pathlib import Path


INDEX_HTML = Path("index.html").read_text(encoding="utf-8")
TARGET_CODES = [
    "99221",
    "99222",
    "99223",
    "99252",
    "99253",
    "99254",
    "99255",
    "99231",
    "99232",
    "99233",
    "99291",
    "99292",
]


def test_case_builder_exposes_modifier57_for_em_lines():
    for text in [
        "const EM_MOD_OPTS=",
        "{v:'57',code:'-57'",
        "{v:'24',code:'-24'",
        "Select E/M modifier",
        "line.kind==='em'",
        "openMpick(${l.id})",
    ]:
        assert text in INDEX_HTML


def test_case_builder_keeps_modifier57_in_em_calculation():
    for text in [
        "l.mods.push('57')",
        "No E/M modifier selected. Use edit to choose -57, -25, -24, or none based on documentation.",
        "l.effWrvu=l.baseWrvu",
        "Coder-affirmed decision for surgery modifier",
        "/^(44|47|48|49|15|31|43|60)/.test(code)",
        "Modifier -57 is usually the decision-for-surgery modifier; confirm documentation before using -25.",
    ]:
        assert text in INDEX_HTML


def test_requested_em_codes_have_modifier57_data():
    for path in [p for p in [Path("cpt_database.json"), Path("public/cpt_database.json")] if p.exists()]:
        data = json.loads(path.read_text(encoding="utf-8"))
        for code in TARGET_CODES:
            assert "57" in data[code]["typical_modifiers"]
