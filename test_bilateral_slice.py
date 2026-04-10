from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_tracks_bilateral_context_controls():
    for text in [
        'appState.caseContext.bilateralMode',
        "bilateralMode: 'auto'",
        'setBilateralMode(',
    ]:
        assert text in INDEX_HTML


def test_home_has_bilateral_ui_controls():
    for text in [
        'onclick="setBilateralMode(\'auto\')"',
        'onclick="setBilateralMode(\'force-bilateral\')"',
        'onclick="setBilateralMode(\'off\')"',
        'bilateral',
    ]:
        assert text in INDEX_HTML


def test_analysis_uses_bilateral_context_and_surfaces_it():
    for text in [
        'appState.caseContext.bilateralMode',
        'Bilateral mode',
        'Typical modifiers',
        'Engine notes',
    ]:
        assert text in INDEX_HTML
