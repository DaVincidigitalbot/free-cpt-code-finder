from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_tracks_modifier59_recommendation_and_user_override_state():
    for text in [
        'appState.modifier59Audit.recommendation',
        'appState.modifier59Audit.applied',
        'applyModifier59Override()',
    ]:
        assert text in INDEX_HTML


def test_modal_can_apply_user_confirmed_modifier59_override():
    for text in [
        'Apply -59 override',
        'function applyModifier59Override',
        'user override',
    ]:
        assert text in INDEX_HTML


def test_export_and_ui_distinguish_engine_vs_user_modifier59_choice():
    for text in [
        'engine recommendation',
        'user-applied override',
        'modifier59Audit',
        'Typical modifiers',
    ]:
        assert text in INDEX_HTML
