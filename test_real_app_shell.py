from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_home_uses_approved_v3_mockup_headline_and_command_palette():
    assert 'Code the case.' in INDEX_HTML
    assert 'Not the paperwork.' in INDEX_HTML
    assert 'lap chole · 44970 · rib fixation · ex lap splenectomy' in INDEX_HTML
    assert '⌘K' in INDEX_HTML


def test_home_uses_lane_based_13_specialty_board():
    specialties = [
        'General surgery',
        'Trauma &amp; acute care',
        'Colorectal',
        'HPB',
        'Endocrine',
        'Breast',
        'Surgical oncology',
        'Cardiothoracic',
        'Vascular',
        'Orthopedic trauma',
        'Neurosurgery',
        'Pediatric surgery',
        'Bariatric',
    ]
    for specialty in specialties:
        assert specialty in INDEX_HTML
    assert INDEX_HTML.count('class="ln"') == 13


def test_home_has_quick_start_active_case_rail_and_no_fake_counts():
    for text in [
        'Quick start',
        'Ex lap',
        'Lap chole',
        'Lap appy',
        'Damage control',
        'Total thyroid',
        'Active case',
        '47.82',
        'MPPR applied',
        '49002',
        '38100',
        '44120',
    ]:
        assert text in INDEX_HTML
    assert '412 procedures' not in INDEX_HTML
    assert '209 procedures' not in INDEX_HTML


def test_home_keeps_inpatient_outpatient_split():
    assert 'Encounter coding' in INDEX_HTML
    assert 'Clinic &amp; ASC' in INDEX_HTML
