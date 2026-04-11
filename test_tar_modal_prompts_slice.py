from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_tar_modal_can_render_specific_prompt_set():
    for text in [
        'function renderTarSpecificPrompts',
        'left-sided posterior release documented?',
        'right-sided posterior release documented?',
        'separate side documentation present?',
        'multi-15734 review completed?',
    ]:
        assert text in INDEX_HTML


def test_bilateral_modal_uses_tar_prompt_set_when_tar_pattern_detected():
    for text in [
        'isTarPattern(',
        'renderTarSpecificPrompts()',
        'posterior component separation',
    ]:
        assert text in INDEX_HTML
