from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_export_includes_tar_answer_state_and_recommendation():
    for text in [
        'tarAnswers',
        'TAR recommendation',
        'supports bilateral review',
        'documentation unclear, review carefully',
        'would not recommend bilateral assignment',
    ]:
        assert text in INDEX_HTML


def test_audit_ui_can_surface_tar_reasoning_language():
    for text in [
        'TAR review',
        'separate side documentation',
        'multi-15734 review',
    ]:
        assert text in INDEX_HTML
