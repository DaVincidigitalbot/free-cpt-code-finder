from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_has_decision_tree_panel_targets():
    for text in [
        'id="decisionTreePanel"',
        'id="decisionTreeTitle"',
        'id="decisionTreeQuestion"',
        'id="decisionTreeOptions"',
    ]:
        assert text in INDEX_HTML


def test_home_defines_tree_flow_functions():
    for text in [
        'function renderDecisionTreePanel',
        'function startCategoryFlow',
        'function chooseTreeOption',
        'function addTreeResultToCase',
        'appState.currentTreeCategory',
        'appState.currentTreeNodeKey',
    ]:
        assert text in INDEX_HTML


def test_home_can_render_category_choices_from_real_lane_selection():
    for text in [
        'function renderCategoryChoices',
        'id="decisionTreeCategoryChoices"',
        'startCategoryFlow(categoryName)',
        'openSpecialtyLane(routeKey)',
    ]:
        assert text in INDEX_HTML


def test_tree_answers_can_add_real_cpt_lines_into_active_case():
    for text in [
        "cpt_code",
        'addTreeResultToCase(option)',
        'renderCaseBuilder()',
        'document.getElementById(\'activeCaseLines\')',
    ]:
        assert text in INDEX_HTML
