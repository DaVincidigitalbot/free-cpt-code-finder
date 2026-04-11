from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_search_uses_real_cpt_dataset_loader_not_only_fake_lane_filter():
    assert "fetch('cpt_database.json')" in INDEX_HTML
    assert 'function filterSearchExperience' in INDEX_HTML
    assert 'renderAutocompleteResults()' in INDEX_HTML


def test_home_search_has_real_autocomplete_results_container_and_selection_hook():
    assert 'id="autocompleteResults"' in INDEX_HTML
    assert 'onclick="selectAutocompleteResult(' in INDEX_HTML
    assert 'addAutocompleteResultToCase' in INDEX_HTML


def test_home_search_keeps_specialty_filter_but_adds_real_result_state():
    assert 'specialtyFilter:' in INDEX_HTML
    assert 'searchResults:' in INDEX_HTML
    assert 'searchQuery:' in INDEX_HTML
    assert 'cptSearchIndex:' in INDEX_HTML
