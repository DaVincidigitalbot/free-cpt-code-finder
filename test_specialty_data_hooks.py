from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_embeds_real_specialty_map_for_lane_actions():
    assert 'const specialtyRouteMap =' in INDEX_HTML
    for text in [
        'General surgery',
        'Trauma &amp; acute care',
        'Colorectal',
        'HPB',
        'Endocrine',
        'Breast',
        'Surgical oncology',
        'Cardiothoracic',
        'Vascular',
        'Neurosurgery',
        'Pediatric surgery',
    ]:
        assert text in INDEX_HTML


def test_lane_rows_are_clickable_into_real_specialty_routes():
    assert 'onclick="openSpecialtyLane(' in INDEX_HTML
    assert 'function openSpecialtyLane' in INDEX_HTML
    assert 'id="ci"' in INDEX_HTML


def test_home_loads_real_decision_tree_data_file():
    assert "fetch('cpt_decision_tree.json')" in INDEX_HTML
    assert 'function loadDecisionTreeData' in INDEX_HTML
    assert 'appState.decisionTree' in INDEX_HTML
