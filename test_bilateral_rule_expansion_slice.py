from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_bilateral_rules_include_rectus_pattern():
    for text in [
        '15734',
        'rectus',
        'abdominal wall work',
    ]:
        assert text in INDEX_HTML


def test_bilateral_rules_include_inguinal_hernia_pattern():
    for text in [
        'inguinal',
        'hernia work',
        '49505',
    ]:
        assert text in INDEX_HTML


def test_bilateral_rules_include_paired_extremity_pattern():
    for text in [
        'extremity',
        'hand',
        'foot',
        'LT/RT',
    ]:
        assert text in INDEX_HTML


def test_bilateral_rules_include_breast_and_carpal_patterns():
    for text in [
        'breast',
        'mastectomy',
        'carpal',
        'median nerve',
    ]:
        assert text in INDEX_HTML
