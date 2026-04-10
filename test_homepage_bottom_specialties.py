from pathlib import Path

INDEX_HTML = Path('index.html').read_text(encoding='utf-8')


def test_bottom_specialties_section_exists_after_main_content():
    main_end = INDEX_HTML.index('</main>')
    bottom_section_pos = INDEX_HTML.find('id="bottomSpecialtyLinks"')
    assert bottom_section_pos > main_end, 'Bottom specialty links section must appear after </main>'


def test_bottom_specialties_section_has_heading_and_copy():
    assert 'Browse by Specialty' in INDEX_HTML
    assert 'Use the links below to jump straight into each specialty decision tree and procedure pathway.' in INDEX_HTML


def test_bottom_specialties_section_has_clickable_specialty_groups():
    required_groups = [
        'General Surgery',
        'Urology',
        'Interventional Radiology',
        'Interventional Cardiology',
        'Electrophysiology',
        'Structural Heart',
        'In-patient Physician Coding',
    ]
    for label in required_groups:
        assert label in INDEX_HTML


def test_bottom_specialties_links_point_to_existing_tree_hashes():
    required_hashes = [
        '#hernia',
        '#appendectomy',
        '#urology_oncology',
        '#urology_reconstruction',
        '#urology_mens_health',
        '#inpatient_split_shared',
        '#inpatient_prolonged',
        '#inpatient_teaching',
        '#inpatient_cross_specialty',
    ]
    for href in required_hashes:
        assert f'href="{href}"' in INDEX_HTML, f'Missing bottom link {href}'
