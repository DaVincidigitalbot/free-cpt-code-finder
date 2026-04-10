from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_loads_modifier_engine_script_and_state():
    assert 'modifier_engine.js' in INDEX_HTML
    assert 'appState.modifierEngine' in INDEX_HTML
    assert 'appState.lastAnalysis' in INDEX_HTML


def test_home_initializes_modifier_engine():
    for text in [
        'function ensureModifierEngine',
        'new ModifierEngine()',
        'await appState.modifierEngine.initialize()',
    ]:
        assert text in INDEX_HTML


def test_case_builder_runs_real_analysis_before_render():
    for text in [
        'function analyzeActiveCase',
        'await appState.modifierEngine.analyze(',
        'appState.lastAnalysis = analysis',
        'procedure.adjustedWRVU',
        'procedure.modifiers',
    ]:
        assert text in INDEX_HTML


def test_render_uses_analyzed_case_when_available():
    for text in [
        'const analyzedProcedures = appState.lastAnalysis?.procedures || appState.activeCase;',
        'adjustedWRVU',
        'modifiers.join',
    ]:
        assert text in INDEX_HTML
