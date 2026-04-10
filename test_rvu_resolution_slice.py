from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_loads_real_rvu_data_file():
    assert "fetch('rvu_database.json')" in INDEX_HTML
    assert 'function loadRvuData' in INDEX_HTML
    assert 'appState.rvuData' in INDEX_HTML


def test_tree_results_resolve_wrvu_from_real_data_before_case_insert():
    for text in [
        'function resolveWrvuForCode',
        'await loadRvuData()',
        'addTreeResultToCase(option)',
        'resolveWrvuForCode(option.cpt_code)',
    ]:
        assert text in INDEX_HTML


def test_case_totals_can_use_real_resolved_values():
    for text in [
        'wrvu: resolvedWrvu',
        'total.toFixed(2)',
        'currency(total * 29.37)',
    ]:
        assert text in INDEX_HTML
