from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_has_tree_breadcrumb_and_context_targets():
    for text in [
        'id="decisionTreeBreadcrumb"',
        'id="decisionTreeContext"',
        'Selected path',
    ]:
        assert text in INDEX_HTML


def test_home_tracks_tree_path_state():
    for text in [
        'appState.currentTreePath',
        'function updateTreePath',
        'function resetDecisionTreePanel',
    ]:
        assert text in INDEX_HTML


def test_tree_flow_updates_breadcrumbs_and_supports_reset():
    for text in [
        'updateTreePath(',
        'resetDecisionTreePanel()',
        'Back to specialty choices',
        'renderDecisionTreePanel(',
    ]:
        assert text in INDEX_HTML
