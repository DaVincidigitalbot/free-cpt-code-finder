from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_has_audit_and_warning_targets():
    for text in [
        'id="caseWarnings"',
        'id="caseAuditTrail"',
        'Audit trail',
        'Warnings',
    ]:
        assert text in INDEX_HTML


def test_home_renders_modifier_engine_output_into_ui():
    for text in [
        'function renderAuditPanel',
        'appState.lastAnalysis?.warnings',
        'appState.lastAnalysis?.auditTrail',
        'document.getElementById("caseWarnings")',
        'document.getElementById("caseAuditTrail")',
    ]:
        assert text in INDEX_HTML


def test_case_sync_updates_audit_panel_after_analysis():
    for text in [
        'renderAuditPanel()',
        'await analyzeActiveCase()',
        'syncCaseAnalysisAndRender()',
    ]:
        assert text in INDEX_HTML
