from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_embeds_narrow_bilateral_rule_patterns():
    for text in [
        'const bilateralRulePatterns =',
        'rectus',
        'inguinal',
        'extremity',
        'LT/RT',
        '-50',
    ]:
        assert text in INDEX_HTML


def test_home_can_resolve_bilateral_recommendations_from_rule_patterns():
    for text in [
        'function resolveBilateralRecommendation',
        'getBilateralStateForCode(',
        'Bilateral recommendation',
    ]:
        assert text in INDEX_HTML


def test_rule_patterns_are_used_in_modal_and_render_flow():
    for text in [
        'renderBilateralModal()',
        'resolveBilateralRecommendation(',
        'payer-sensitive review',
    ]:
        assert text in INDEX_HTML
