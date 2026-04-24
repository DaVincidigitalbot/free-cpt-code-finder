#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / 'cpt_database.json'
MOD_PATH = ROOT / 'modifier_rules.json'
PATCH_PATH = ROOT / 'tools' / 'obgyn_patch_source.json'

BASE_MAJOR = {
    'mod51_exempt': False,
    'addon_code': False,
    'bilateral_eligible': False,
    'laterality_applicable': False,
    'bilateral_method': None,
    'global_period': 90,
    'assistant_allowed': True,
    'cosurgeon_eligible': True,
    'inherently_bilateral': False,
    'distinct_procedure_class': None,
    'category': 'gynecologic',
    'inclusive_of': ['12001', '12002', '12003', '12004', '12005'],
    'never_primary_with': [],
    'specialty_bundle_rules': {
        'ent': {'always_with': [], 'never_with': []},
        'general': {'always_with': [], 'never_with': []}
    },
    'payer_notes': {
        'medicare': 'Major surgery - 90-day global period applies',
        'commercial': 'Plastic surgery codes - verify coverage'
    },
    'x_modifier_eligible': True,
    'hierarchy_tier': 2,
}

BASE_MINOR = {
    **BASE_MAJOR,
    'global_period': 0,
    'assistant_allowed': False,
    'cosurgeon_eligible': False,
    'hierarchy_tier': 3,
}


def load_json(path: Path):
    return json.loads(path.read_text())


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2))


def make_modifier_entry(code: str, meta: dict) -> dict:
    gp = meta['global_period_days']
    bilateral = bool(meta.get('bilateral_eligible'))
    entry = dict(BASE_MINOR if gp == 0 else BASE_MAJOR)
    entry['global_period'] = gp
    entry['assistant_allowed'] = meta['assistant_allowed']
    entry['cosurgeon_eligible'] = meta['cosurgeon_eligible']
    entry['hierarchy_tier'] = meta['hierarchy_tier']
    entry['bilateral_eligible'] = bilateral
    entry['laterality_applicable'] = bilateral
    entry['bilateral_method'] = 'modifier_50' if bilateral else None

    hint = meta.get('category_hint', 'gynecologic')
    if hint == 'urogynecology':
        entry['category'] = 'urogynecology'
    elif hint == 'cervical':
        entry['category'] = 'cervical'
    elif hint == 'vulvar':
        entry['category'] = 'vulvar'
    elif hint == 'obstetric':
        entry['category'] = 'obstetric'
    else:
        entry['category'] = 'gynecologic'
    return entry


def main():
    db = load_json(DB_PATH)
    mod = load_json(MOD_PATH)
    patch = load_json(PATCH_PATH)
    codes = patch['codes']

    created = 0
    updated = 0
    mod_created = 0
    mod_updated = 0

    for code, meta in codes.items():
        existed = code in db
        record = db.get(code, {
            'code': code,
            'inclusive_of': [],
            'never_primary_with': [],
            'typical_modifiers': [],
            'estimated': False,
            'addon_code': False,
        })
        record.update({
            'code': code,
            'description': meta['description'],
            'category': 'Surgery',
            'subcategory': meta['subcategory'],
            'specialty': 'obgyn',
            'work_rvu': meta['work_rvu'],
            'global_period_days': meta['global_period_days'],
            'bilateral_eligible': meta['bilateral_eligible'],
            'addon_code': False,
            'cosurgeon_eligible': meta['cosurgeon_eligible'],
            'assistant_allowed': meta['assistant_allowed'],
            'hierarchy_tier': meta['hierarchy_tier'],
            'code_family': meta['code_family'],
            'estimated': False,
        })
        record.setdefault('inclusive_of', [])
        record.setdefault('never_primary_with', [])
        record.setdefault('typical_modifiers', [])
        db[code] = record
        if existed:
            updated += 1
        else:
            created += 1

        mod_existed = code in mod
        mod[code] = make_modifier_entry(code, meta)
        if mod_existed:
            mod_updated += 1
        else:
            mod_created += 1

    save_json(DB_PATH, db)
    save_json(MOD_PATH, mod)

    print(f'OB/GYN patch applied: {len(codes)} codes')
    print(f'cpt_database.json -> created {created}, updated {updated}')
    print(f'modifier_rules.json -> created {mod_created}, updated {mod_updated}')


if __name__ == '__main__':
    main()
