from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_single_file_hash_router_shell_exists():
    assert 'id="app"' in INDEX_HTML
    assert "location.hash" in INDEX_HTML
    assert "window.addEventListener('hashchange',render);" in INDEX_HTML
    assert "go('#/')" in INDEX_HTML
    assert "go('#/inpatient')" in INDEX_HTML
    assert "go('#/outpatient')" in INDEX_HTML


def test_home_contains_specialty_tiles_and_em_entrypoints():
    for text in [
        'Surgical Subspecialties',
        'Inpatient Coding',
        'Outpatient Coding',
        'General Surgery',
        'Trauma / Acute Care',
        'Colorectal Surgery',
        'HPB Surgery',
        'Interventional Radiology',
    ]:
        assert text in INDEX_HTML


def test_specialty_routes_are_hash_based_not_dead_multipage_links():
    assert '#/specialty/' in INDEX_HTML
    assert 'specialty.html?s=' not in INDEX_HTML
    assert 'inpatient.html#' not in INDEX_HTML
    assert 'outpatient.html#' not in INDEX_HTML


def test_case_builder_and_audit_exist_in_same_file():
    for text in [
        'Current case',
        'Audit trail',
        'Total wRVU',
        'Est. payment',
        'MPPR applied',
        'Export .txt',
    ]:
        assert text in INDEX_HTML
