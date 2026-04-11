from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_tar_rule_mentions_side_documentation_and_multicode_review():
    for text in [
        'left-sided posterior release',
        'right-sided posterior release',
        'separate side documentation',
        'multi-15734 review',
    ]:
        assert text in INDEX_HTML


def test_tar_rule_mentions_user_decision_not_auto_assignment():
    for text in [
        'user should decide',
        'do not auto-assign bilateral 15734',
        'do not auto-assign -59',
    ]:
        assert text in INDEX_HTML
