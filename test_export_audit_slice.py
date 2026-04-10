from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_has_export_control():
    for text in [
        'Export audit',
        'onclick="exportAuditOutput()"',
        'function exportAuditOutput',
    ]:
        assert text in INDEX_HTML


def test_export_uses_real_case_and_analysis_state():
    for text in [
        'appState.activeCase',
        'appState.caseContext',
        'appState.lastAnalysis',
        'case-audit.txt',
    ]:
        assert text in INDEX_HTML


def test_export_serializes_warnings_and_audit_trail():
    for text in [
        'warnings',
        'auditTrail',
        'Blob',
        'URL.createObjectURL',
    ]:
        assert text in INDEX_HTML
