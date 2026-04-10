from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_has_modifier59_audit_targets():
    for text in [
        'Modifier 59 audit',
        'id="modifier59AuditPanel"',
        'id="modifier59AuditQuestions"',
    ]:
        assert text in INDEX_HTML


def test_home_can_trigger_modifier59_audit_flow():
    for text in [
        'function triggerModifier59Audit',
        'function renderModifier59AuditPanel',
        'function answerModifier59Audit',
        '-59',
    ]:
        assert text in INDEX_HTML


def test_modifier59_audit_prompts_for_distinct_service_questions():
    for text in [
        'distinct procedural service',
        'separate incision',
        'separate lesion',
        'separate anatomic site',
        'separate encounter',
        'XS',
        'XE',
        'XP',
        'XU',
    ]:
        assert text in INDEX_HTML
