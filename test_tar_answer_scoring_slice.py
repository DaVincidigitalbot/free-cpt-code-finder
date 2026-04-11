from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_tar_modal_tracks_answer_state():
    for text in [
        'tarAnswers',
        'answerTarPrompt(',
        'computeTarRecommendation(',
    ]:
        assert text in INDEX_HTML


def test_tar_answers_can_change_bilateral_recommendation():
    for text in [
        'supports bilateral review',
        'documentation unclear, review carefully',
        'would not recommend bilateral assignment',
    ]:
        assert text in INDEX_HTML


def test_tar_prompt_answers_feed_rendered_output():
    for text in [
        'renderTarSpecificPrompts()',
        'computeTarRecommendation(',
        'Bilateral recommendation',
    ]:
        assert text in INDEX_HTML
