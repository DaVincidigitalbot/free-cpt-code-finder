from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_supports_case_line_removal_controls():
    for text in [
        'function removeCaseLine',
        'onclick="removeCaseLine(',
        'Remove',
    ]:
        assert text in INDEX_HTML


def test_case_removal_reanalyzes_and_rerenders():
    for text in [
        'appState.activeCase.splice(index, 1)',
        'syncCaseAnalysisAndRender()',
        'renderCaseBuilder()',
    ]:
        assert text in INDEX_HTML


def test_empty_case_state_is_handled():
    for text in [
        'No procedures selected yet.',
        'No active case',
    ]:
        assert text in INDEX_HTML
