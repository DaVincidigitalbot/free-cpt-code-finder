from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_has_modifier59_modal_targets():
    for text in [
        'id="modifier59Modal"',
        'id="modifier59ModalBody"',
        'id="modifier59ModalRecommendation"',
        'Before using modifier -59',
    ]:
        assert text in INDEX_HTML


def test_home_can_open_and_close_modifier59_modal():
    for text in [
        'function openModifier59Modal',
        'function closeModifier59Modal',
        'openModifier59Modal(',
        'closeModifier59Modal()',
    ]:
        assert text in INDEX_HTML


def test_modifier59_modal_can_produce_recommendation_states():
    for text in [
        'supports -59',
        'review carefully',
        'would not recommend -59',
        'function computeModifier59Recommendation',
    ]:
        assert text in INDEX_HTML
