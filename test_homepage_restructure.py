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
    assert '#/specialty/' in INDEX_HTML
    assert 'specialty.html?s=' not in INDEX_HTML
    for text in [
        'General Surgery',
        'Trauma / Acute Care',
        'Colorectal Surgery',
        'HPB Surgery',
        'Endocrine Surgery',
        'Breast Surgery',
        'Surgical Oncology',
        'Cardiothoracic Surgery',
        'Vascular Surgery',
        'Orthopedic Trauma',
        'Neurosurgery',
        'Pediatric Surgery',
        'Interventional Radiology',
        'Interventional Cardiology',
    ]:
        assert text in INDEX_HTML


def test_restructure_has_inpatient_and_outpatient_cards():
    assert 'Inpatient Coding' in INDEX_HTML
    assert 'Outpatient Coding' in INDEX_HTML
    assert "go('#/inpatient')" in INDEX_HTML
    assert "go('#/outpatient')" in INDEX_HTML
    assert 'inpatient.html#' not in INDEX_HTML
    assert 'outpatient.html#' not in INDEX_HTML
    for text in [
        'Admit / subsequent / discharge',
        'Critical care',
        'Clinic / postop / wound',
        'ASC / office procedures',
    ]:
        assert text in INDEX_HTML
