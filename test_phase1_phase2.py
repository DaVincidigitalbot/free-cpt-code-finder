import json
import re
from pathlib import Path

INDEX = Path('index.html').read_text()


def extract_cpt_data():
    start = INDEX.index('const CPT_DATA = ') + len('const CPT_DATA = ')
    end = INDEX.index('\n\n        const ICD10_DATA = {')
    return json.loads(INDEX[start:end])


def test_header_blog_link_present():
    assert 'href="/blog/"' in INDEX


def test_homepage_has_two_entry_sections():
    assert 'Surgical Specialty Coding' in INDEX
    assert 'In-patient Physician Coding' in INDEX
    assert 'id="specialtyBrowser"' in INDEX
    assert 'id="inpatientBrowser"' in INDEX


def test_blog_quick_links_present():
    for href in ['/blog/', '/blog/guides/', '/blog/modifiers/', '/blog/rvu/', '/blog/icd10/']:
        assert href in INDEX


def test_cpt_tree_contains_urology_and_inpatient():
    data = extract_cpt_data()
    names = {category['name'] for category in data['categories']}
    assert 'Urology' in names
    assert 'Inpatient Physician Coding' in names


def test_interventional_cardiology_keeps_structural_and_ep():
    data = extract_cpt_data()
    ic = next(category for category in data['categories'] if category['name'] == 'Interventional Cardiology')
    labels = [opt['label'] for opt in ic['questions'][0]['options']]
    assert any('Structural Heart' in label for label in labels)
    assert any('Electrophysiology' in label or 'EP' in label for label in labels)


def test_urology_tree_has_core_branches():
    data = extract_cpt_data()
    uro = next(category for category in data['categories'] if category['name'] == 'Urology')
    branch_keys = set(uro['branches'].keys())
    expected = {
        'urology_cysto',
        'urology_ureteroscopy',
        'urology_stents',
        'urology_prostate',
        'urology_scrotal',
        'urology_renal',
        'urology_female',
    }
    assert expected.issubset(branch_keys)


def test_inpatient_tree_has_core_em_codes():
    data = extract_cpt_data()
    inpatient = next(category for category in data['categories'] if category['name'] == 'Inpatient Physician Coding')
    codes = set()
    for branch in inpatient['branches'].values():
        for option in branch['options']:
            codes.add(option['cpt_code'])
    for code in ['99221', '99223', '99231', '99233', '99238', '99239', '99252', '99255', '99291', '99292', '99234', '99236']:
        assert code in codes


def test_featured_buttons_include_urology_and_inpatient():
    assert 'Urology' in INDEX
    assert 'Inpatient Physician Coding' in INDEX
    assert 'featuredNames' in INDEX
