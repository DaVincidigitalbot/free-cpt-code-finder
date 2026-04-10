from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_has_recommendation_targets():
    for text in [
        'Recommended role',
        'Typical modifiers',
        'Engine notes',
    ]:
        assert text in INDEX_HTML


def test_render_surfaces_engine_recommendations_from_analysis():
    for text in [
        'procedure.rank',
        'procedure.modifiers',
        'procedure.explanations',
        'Typical modifiers',
    ]:
        assert text in INDEX_HTML


def test_audit_ui_can_show_engine_notes_per_line():
    for text in [
        'explanations.join',
        'Recommended role',
        'Engine notes',
    ]:
        assert text in INDEX_HTML
