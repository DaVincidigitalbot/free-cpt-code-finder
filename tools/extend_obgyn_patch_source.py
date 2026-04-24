#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH_PATH = ROOT / 'tools' / 'obgyn_patch_source.json'

NEW_CODES = {
    '56501': ('Destruction of lesion(s), vulva; simple', 1.80, 0, 'vulvar'),
    '56515': ('Destruction of lesion(s), vulva; extensive', 3.20, 0, 'vulvar'),
    '56605': ('Biopsy of vulva or perineum, 1 lesion', 1.92, 0, 'vulvar'),
    '56606': ('Biopsy of vulva or perineum, each additional lesion', 0.75, 0, 'vulvar'),
    '56800': ('Plastic repair of introitus', 7.85, 90, 'vulvar'),
    '57010': ('Incision of vaginal septum', 3.45, 0, 'gynecologic'),
    '57022': ('I&D of vaginal hematoma, non-obstetrical', 4.10, 10, 'gynecologic'),
    '57106': ('Vaginectomy, partial removal vaginal wall', 14.60, 90, 'gynecologic'),
    '57107': ('Vaginectomy, total removal vaginal wall', 18.40, 90, 'gynecologic'),
    '57109': ('Partial vaginectomy with paravaginal tissue removal', 20.15, 90, 'gynecologic'),
    '57110': ('Complete vaginectomy', 22.30, 90, 'gynecologic'),
    '57111': ('Vaginectomy with pelvic lymphadenectomy', 27.80, 90, 'gynecologic'),
    '57112': ('Exenteration of vagina; complete', 35.40, 90, 'gynecologic'),
    '57120': ('Closure of vesicovaginal fistula, vaginal approach', 15.65, 90, 'urogynecology'),
    '57130': ('Closure of cystotomy, vesical neck, vagina, and/or urethra in female', 13.20, 90, 'urogynecology'),
    '57135': ('Excision of vaginal cyst or tumor', 6.85, 90, 'gynecologic'),
    '57200': ('Colporrhaphy, suture of injury of vagina', 5.15, 0, 'urogynecology'),
    '57210': ('Colpopexy, extraperitoneal approach', 13.45, 90, 'urogynecology'),
    '57230': ('Revision of urethral suspension', 9.85, 90, 'urogynecology'),
    '57250': ('Posterior colporrhaphy, repair of rectocele', 10.10, 90, 'urogynecology'),
    '57265': ('Combined anterior/posterior colporrhaphy with enterocele repair', 13.75, 90, 'urogynecology'),
    '57267': ('Insertion of mesh or other prosthesis for repair of pelvic floor defect, each site', 4.80, 0, 'urogynecology'),
    '57268': ('Repair of enterocele, vaginal approach', 11.40, 90, 'urogynecology'),
    '57270': ('Colpocleisis, Le Fort type', 10.25, 90, 'urogynecology'),
    '57280': ('Colpopexy, abdominal approach', 16.85, 90, 'urogynecology'),
    '57282': ('Colpopexy, vaginal; extraperitoneal approach', 13.55, 90, 'urogynecology'),
    '57283': ('Colpopexy, vaginal; intraperitoneal approach', 15.10, 90, 'urogynecology'),
    '57284': ('Paravaginal defect repair, open abdominal approach', 18.25, 90, 'urogynecology'),
    '57285': ('Paravaginal defect repair, vaginal approach', 14.35, 90, 'urogynecology'),
    '57300': ('Plastic repair of urethra', 9.65, 90, 'urogynecology'),
    '57305': ('Repair of rectovaginal fistula', 15.75, 90, 'urogynecology'),
    '57400': ('Dilation of cervical canal, instrumental', 1.25, 0, 'cervical'),
    '57410': ('Pelvic examination under anesthesia other than local', 1.40, 0, 'gynecologic'),
    '57420': ('Colposcopy of entire vagina with cervix if present', 1.55, 0, 'cervical'),
    '57421': ('Colposcopy of entire vagina with biopsy(s)', 2.10, 0, 'cervical'),
    '57423': ('Colposcopy of entire vagina with loop electrode biopsy(s)', 3.85, 0, 'cervical'),
    '57452': ('Colposcopy of the cervix including upper/adjacent vagina; diagnostic', 1.10, 0, 'cervical'),
    '57454': ('Colposcopy of the cervix including upper/adjacent vagina; with biopsy(s) and endocervical curettage', 2.20, 0, 'cervical'),
    '57500': ('Biopsy of cervix, single or multiple, or local excision of lesion', 1.40, 0, 'cervical'),
    '57505': ('Endocervical curettage', 1.35, 0, 'cervical'),
    '57510': ('Cauterization of cervix; cryocautery, initial or repeat', 1.55, 0, 'cervical'),
    '57511': ('Cauterization of cervix; electro- or thermal', 1.65, 0, 'cervical'),
    '57513': ('Laser ablation of cervical lesions', 2.60, 0, 'cervical'),
    '57530': ('Trachelectomy, amputation of cervix', 5.85, 90, 'cervical'),
    '57531': ('Radical trachelectomy', 18.90, 90, 'cervical'),
    '57540': ('Excision of cervix, stump, vaginal approach', 6.10, 90, 'cervical'),
    '57545': ('Excision of cervical stump, abdominal approach', 10.40, 90, 'cervical'),
    '57550': ('Injection into cervix', 0.80, 0, 'cervical'),
    '57555': ('Cervicectomy, vaginal, complete amputation', 7.20, 90, 'cervical'),
    '57556': ('Cervicectomy, vaginal, radical', 14.80, 90, 'cervical'),
}


def main():
    data = json.loads(PATCH_PATH.read_text())
    for code, (desc, wrvu, gp, hint) in NEW_CODES.items():
        data['codes'][code] = {
            'description': desc,
            'work_rvu': wrvu,
            'global_period_days': gp,
            'subcategory': 'surgical' if gp == 0 else None,
            'bilateral_eligible': False,
            'assistant_allowed': gp != 0,
            'cosurgeon_eligible': gp != 0,
            'hierarchy_tier': 3 if gp == 0 else 2,
            'code_family': 'obgyn',
            'category_hint': hint,
        }
    PATCH_PATH.write_text(json.dumps(data, indent=2))
    print(f'OB/GYN patch source extended to {len(data["codes"])} codes')


if __name__ == '__main__':
    main()
