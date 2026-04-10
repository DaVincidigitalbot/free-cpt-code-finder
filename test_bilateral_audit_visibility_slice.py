from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_bilateral_mode_is_visible_in_audit_panel():
    for text in [
        'Bilateral mode',
        'force-bilateral',
        'auto',
        'off',
    ]:
        assert text in INDEX_HTML


def test_export_includes_bilateral_state_and_guidance():
    for text in [
        'Bilateral mode:',
        'Laterality and bilateral handling may require payer-specific review.',
        'case-audit.txt',
    ]:
        assert text in INDEX_HTML


def test_engine_notes_area_can_surface_bilateral_guidance():
    for text in [
        'Engine notes',
        'Typical modifiers',
        'Recommended role',
    ]:
        assert text in INDEX_HTML
