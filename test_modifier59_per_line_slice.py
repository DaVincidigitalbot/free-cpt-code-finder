from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_tracks_modifier59_state_per_line():
    for text in [
        'appState.modifier59Audit.byCode',
        'appState.modifier59Audit.activeCode',
        'getModifier59StateForCode(',
    ]:
        assert text in INDEX_HTML


def test_modifier59_modal_opens_for_specific_code():
    for text in [
        'openModifier59Modal(code)',
        'appState.modifier59Audit.activeCode = code',
        'function triggerModifier59Audit(code = \'\')',
    ]:
        assert text in INDEX_HTML


def test_modifier59_override_and_export_can_be_line_specific():
    for text in [
        'byCode',
        'activeCode',
        'user-applied override',
        'Modifier 59 audit:',
    ]:
        assert text in INDEX_HTML
