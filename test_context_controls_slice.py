from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_tracks_case_context_state():
    for text in [
        'appState.caseContext',
        "payerType: 'medicare'",
        "siteOfService: 'facility'",
    ]:
        assert text in INDEX_HTML


def test_home_context_controls_are_clickable():
    for text in [
        'setPayerType(',
        'setSiteOfService(',
        'onclick="setPayerType(\'medicare\')"',
        'onclick="setPayerType(\'commercial\')"',
        'onclick="setSiteOfService(\'facility\')"',
        'onclick="setSiteOfService(\'nonfacility\')"',
    ]:
        assert text in INDEX_HTML


def test_case_analysis_uses_live_context_instead_of_hardcoded_medicare_only():
    for text in [
        'appState.caseContext.payerType',
        'appState.caseContext.siteOfService',
        'await appState.modifierEngine.analyze(analysisInput, appState.caseContext)',
    ]:
        assert text in INDEX_HTML
