from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_includes_app_state_and_case_builder_hooks():
    assert 'const appState =' in INDEX_HTML
    assert 'function addQuickProcedure' in INDEX_HTML
    assert 'function renderCaseBuilder' in INDEX_HTML
    assert 'function filterSpecialties' in INDEX_HTML


def test_home_quick_start_buttons_are_wired_to_real_actions():
    expected = [
        "onclick=\"addQuickProcedure('49000')\"",
        "onclick=\"addQuickProcedure('47562')\"",
        "onclick=\"addQuickProcedure('44970')\"",
        "onclick=\"addQuickProcedure('49002')\"",
        "onclick=\"addQuickProcedure('60240')\"",
    ]
    for needle in expected:
        assert needle in INDEX_HTML


def test_home_has_real_targets_for_specialty_and_search_interaction():
    assert 'id="specialtyLanes"' in INDEX_HTML
    assert 'id="activeCaseLines"' in INDEX_HTML
    assert 'id="totalWrvu"' in INDEX_HTML
    assert 'id="estimatedPayment"' in INDEX_HTML
    assert 'id="ci"' in INDEX_HTML
    assert 'oninput="filterSpecialties(this.value)"' in INDEX_HTML
