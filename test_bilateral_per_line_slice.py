from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_tracks_bilateral_state_per_line():
    for text in [
        'appState.bilateralAudit',
        'byCode',
        'activeCode',
        'getBilateralStateForCode(',
    ]:
        assert text in INDEX_HTML


def test_home_can_open_bilateral_modal_for_specific_line():
    for text in [
        'function openBilateralModal',
        'function closeBilateralModal',
        'appState.bilateralAudit.activeCode = code',
        'Laterality and bilateral review',
    ]:
        assert text in INDEX_HTML


def test_home_supports_per_line_laterality_and_bilateral_override_actions():
    for text in [
        'Apply bilateral override',
        'Apply LT',
        'Apply RT',
        'function applyBilateralOverride',
        'function applyLateralityOverride',
    ]:
        assert text in INDEX_HTML


def test_render_and_export_can_show_per_line_bilateral_decisions():
    for text in [
        'Laterality',
        'Bilateral recommendation',
        'user-applied bilateral override',
        'bilateralAudit',
    ]:
        assert text in INDEX_HTML
