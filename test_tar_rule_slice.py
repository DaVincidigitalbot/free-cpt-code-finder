from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_bilateral_rules_include_tar_specific_pattern():
    for text in [
        'transversus',
        'TAR',
        'posterior component separation',
        'possible multiple 15734 scenario',
        'possible side-specific documentation question',
        'possible -59 per-side review if separately supported',
    ]:
        assert text in INDEX_HTML


def test_tar_rule_is_distinct_from_generic_rectus_rule():
    assert 'high-risk abdominal wall bilateral review' in INDEX_HTML
    assert '15734' in INDEX_HTML
