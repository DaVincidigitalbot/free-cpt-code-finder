import json
from pathlib import Path

INDEX = Path('index.html').read_text()


def extract_cpt_data():
    start = INDEX.index('const CPT_DATA = ') + len('const CPT_DATA = ')
    end = INDEX.index('\n\n        const ICD10_DATA = {')
    return json.loads(INDEX[start:end])


def category(data, name):
    return next(cat for cat in data['categories'] if cat['name'] == name)


def branch_codes(cat, branch_key):
    return {opt['cpt_code'] for opt in cat['branches'][branch_key]['options'] if 'cpt_code' in opt}


def test_urology_expanded_to_oncology_reconstruction_and_mens_health():
    data = extract_cpt_data()
    uro = category(data, 'Urology')
    branch_keys = set(uro['branches'])
    expected = {
        'urology_oncology',
        'urology_reconstruction',
        'urology_mens_health',
    }
    assert expected.issubset(branch_keys)
    assert {'55840', '55845', '51595'}.issubset(branch_codes(uro, 'urology_oncology'))
    assert {'53410', '53520', '53620'}.issubset(branch_codes(uro, 'urology_reconstruction'))
    assert {'54405', '54410', '55899'}.issubset(branch_codes(uro, 'urology_mens_health'))


def test_inpatient_phase2_adds_core_physician_families():
    data = extract_cpt_data()
    inpatient = category(data, 'Inpatient Physician Coding')
    branch_keys = set(inpatient['branches'])
    expected = {
        'inpatient_split_shared',
        'inpatient_prolonged',
        'inpatient_teaching',
        'inpatient_cross_specialty'
    }
    assert expected.issubset(branch_keys)
    cross_labels = {opt['label'] for opt in inpatient['branches']['inpatient_cross_specialty']['options']}
    for label in ['Hospital Medicine / Internal Medicine', 'Cardiology', 'Nephrology', 'Pulmonary / Critical Care', 'Gastroenterology']:
        assert label in cross_labels


def test_interventional_cardiology_has_deeper_ep_and_structural_coverage():
    data = extract_cpt_data()
    ic = category(data, 'Interventional Cardiology')
    ep_codes = branch_codes(ic, 'ep_questions')
    structural_codes = branch_codes(ic, 'structural_questions')
    assert {'93653', '93655', '93657', '33249', '33208', '33285'}.issubset(ep_codes)
    assert {'33361', '33362', '33340', '93580', '93583', '33418', '33419', '0544T'}.issubset(structural_codes)


def test_interventional_radiology_has_broader_gi_gu_and_oncology_coverage():
    data = extract_cpt_data()
    ir = category(data, 'Interventional Radiology')
    gi_gu_codes = branch_codes(ir, 'ir_gi_gu_questions')
    embolization_codes = branch_codes(ir, 'ir_embolization_questions')
    assert {'49406', '49440', '47531', '50387', '50432'}.issubset(gi_gu_codes)
    assert {'37243', '37244', '37241', '37242'}.issubset(embolization_codes)


def test_homepage_phase2_copy_calls_out_expanded_phase2_domains():
    assert 'Electrophysiology' in INDEX
    assert 'Structural Heart' in INDEX
    assert 'Nephrology' in INDEX
    assert 'Gastroenterology' in INDEX
