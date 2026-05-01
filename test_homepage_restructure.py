from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_restructure_uses_requested_navigation_sections():
    assert '<a href="#specialties">Specialties</a>' in INDEX_HTML
    assert '<a href="#inpatient">Inpatient</a>' in INDEX_HTML
    assert '<a href="#outpatient">Outpatient</a>' in INDEX_HTML


def test_restructure_has_requested_hero_copy():
    assert 'Surgical CPT coding, built by surgeons' in INDEX_HTML
    assert 'Inpatient and outpatient coding kept separate' in INDEX_HTML


def test_restructure_has_surgical_subspecialty_grid():
    assert 'Surgical Subspecialties' in INDEX_HTML
    for href in [
        'specialty.html?s=general',
        'specialty.html?s=trauma',
        'specialty.html?s=colorectal',
        'specialty.html?s=hpb',
        'specialty.html?s=endocrine',
        'specialty.html?s=breast',
        'specialty.html?s=surgonc',
        'specialty.html?s=ct',
        'specialty.html?s=vascular',
        'specialty.html?s=ortho',
        'specialty.html?s=neuro',
        'specialty.html?s=ent',
        'specialty.html?s=omfs',
        'specialty.html?s=plastics',
        'specialty.html?s=peds',
        'specialty.html?s=urology',
        'specialty.html?s=obgyn',
        'specialty.html?s=gynonc',
        'specialty.html?s=transplant',
        'specialty.html?s=bariatric',
        'specialty.html?s=ir',
        'specialty.html?s=intcards',
    ]:
        assert href in INDEX_HTML


def test_restructure_has_inpatient_and_outpatient_cards():
    assert 'Inpatient Coding' in INDEX_HTML
    assert 'Outpatient Coding' in INDEX_HTML
    for href in [
        'inpatient.html#admit',
        'inpatient.html#subseq',
        'inpatient.html#discharge',
        'inpatient.html#consult',
        'inpatient.html#cc',
        'inpatient.html#obs',
        'inpatient.html#proc',
        'inpatient.html#prolonged',
        'inpatient.html#modifiers',
        'outpatient.html#new',
        'outpatient.html#est',
        'outpatient.html#consult',
        'outpatient.html#postop',
        'outpatient.html#minor',
        'outpatient.html#asc',
        'outpatient.html#wound',
        'outpatient.html#modifiers',
    ]:
        assert href in INDEX_HTML
