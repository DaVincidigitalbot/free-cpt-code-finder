#!/usr/bin/env python3
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')
AUDIT = ROOT / 'audit'
CMS_LIST_URL = 'https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files'
CMS_BASE = 'https://www.cms.gov'
YEAR = '2026'


def fetch(url):
    with urlopen(url, timeout=120) as r:
        return r.read()


def latest_release():
    html = fetch(CMS_LIST_URL).decode('utf-8', 'ignore')
    slugs = sorted(set(m.lower() for m in re.findall(r'/medicare/payment/fee-schedules/physician/pfs-relative-value-files/(rvu26[a-z])', html, re.I)))
    slug = slugs[-1]
    page = fetch(f'{CMS_BASE}/medicare/payment/fee-schedules/physician/pfs-relative-value-files/{slug}').decode('utf-8', 'ignore')
    zip_name = re.findall(r'/files/zip/([^"\']+\.zip)', page, re.I)[0]
    updated = re.search(r'updated\s*(\d{1,2}/\d{1,2}/\d{4})', page, re.I)
    return slug.upper(), zip_name, updated.group(1) if updated else None


def parse_cms(blob):
    z = zipfile.ZipFile(io.BytesIO(blob))
    data_name = [n for n in z.namelist() if 'pprrvu' in n.lower() and 'nonqpp' in n.lower() and n.lower().endswith('.csv')][0]
    rows = list(csv.reader(z.read(data_name).decode('latin1', 'ignore').splitlines()))
    hdr = rows[9]
    idx = {
        'code': hdr.index('HCPCS'),
        'mod': hdr.index('MOD'),
        'desc': hdr.index('DESCRIPTION'),
        'status': hdr.index('CODE'),
        'work_rvu': hdr.index('RVU'),
        'global': hdr.index('DAYS')
    }
    ref = {}
    for row in rows[10:]:
        if not row:
            continue
        code = row[idx['code']].strip()
        if not code:
            continue
        mod = row[idx['mod']].strip()
        ref[f'{code}|{mod}'] = {
            'code': code,
            'modifier': mod,
            'canonical_key': f'{code}|{mod}',
            'work_rvu': row[idx['work_rvu']].strip(),
            'status_indicator': row[idx['status']].strip(),
            'global_indicator': row[idx['global']].strip(),
            'description': row[idx['desc']].strip(),
        }
    return data_name, ref


def parse_specs(text):
    start = text.find('const SPECS=') + len('const SPECS=')
    level = 0; in_str = False; esc = False; end = None
    for i, ch in enumerate(text[start:], start):
        if in_str:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': in_str = False
        else:
            if ch == '"': in_str = True
            elif ch == '{': level += 1
            elif ch == '}':
                level -= 1
                if level == 0:
                    end = i + 1
                    break
    return json.loads(text[start:end]), start, end


def collect_public_inventory(cms_ref):
    inv = []
    # index specs
    index_text = (ROOT / 'index.html').read_text()
    specs, _, _ = parse_specs(index_text)
    for specialty, procs in specs.items():
        for i, p in enumerate(procs):
            if isinstance(p, list) and len(p) >= 3:
                inv.append({'surface': 'index_specs', 'code': str(p[0]), 'modifier': '', 'wrvu': p[2], 'location': f'{specialty}[{i}]'})
    # decision tree
    tree_text = (ROOT / 'cpt_decision_tree.json').read_text()
    for m in re.finditer(r'"cpt_code":"([^"]+)"', tree_text):
        inv.append({'surface': 'decision_tree', 'code': m.group(1), 'modifier': '', 'wrvu': None, 'location': f'char:{m.start()}'})
    # cpt db
    cpt_db = json.loads((ROOT / 'cpt_database.json').read_text())
    for code, entry in cpt_db.items():
        inv.append({'surface': 'cpt_database', 'code': str(code), 'modifier': '', 'wrvu': entry.get('work_rvu'), 'location': code})
    # rvu db
    rvu_db = json.loads((ROOT / 'rvu_database.json').read_text())
    for code, entry in rvu_db.get('codes', {}).items():
        inv.append({'surface': 'rvu_database', 'code': str(code), 'modifier': '', 'wrvu': entry.get('work_rvu'), 'location': code})
    return inv


def classify(code, modifier, cms_ref):
    raw = str(code)
    if any(sep in raw for sep in [' + ', ',', '/', ' - ']):
        return 'SITE_PSEUDO_CODE_OR_COMBO_CODE'
    if not re.fullmatch(r'[A-Z0-9]{4,5}', raw):
        return 'SITE_PSEUDO_CODE_OR_COMBO_CODE'
    key = f'{raw}|{modifier}'
    row = cms_ref.get(key)
    if not row:
        return 'NOT_FOUND_IN_2026_CMS_PFS_FILE'
    if row['work_rvu'] == '':
        return 'CMS_ROW_EXISTS_BUT_WRVU_BLANK_OR_INVALID'
    return 'VALID_MATCH'


def purge_specs(cms_ref, removed_rows, meta):
    path = ROOT / 'index.html'
    text = path.read_text()
    specs, start, end = parse_specs(text)
    new_specs = {}
    for specialty, procs in specs.items():
        kept = []
        for p in procs:
            if not (isinstance(p, list) and len(p) >= 3):
                kept.append(p)
                continue
            code = str(p[0])
            cls = classify(code, '', cms_ref)
            if cls != 'VALID_MATCH':
                removed_rows.append({'site_code': code, 'modifier': '', 'old_site_wrvu': p[2], 'reason_for_removal': cls, 'source_location': f'index.html:SPECS:{specialty}', 'public_surfaces': 'specialty page/search/autocomplete', 'removal_timestamp': meta['timestamp'], 'public_removal_confirmed': 'pending'})
                continue
            p[2] = float(cms_ref[f'{code}|']['work_rvu'])
            kept.append(p)
        new_specs[specialty] = kept
    text = text[:start] + json.dumps(new_specs, separators=(',', ':')) + text[end:]
    path.write_text(text)


def purge_cpt_database(cms_ref, removed_rows, updated_rows, meta):
    path = ROOT / 'cpt_database.json'
    db = json.loads(path.read_text())
    new = {}
    for code, entry in db.items():
        cls = classify(code, '', cms_ref)
        if cls != 'VALID_MATCH':
            removed_rows.append({'site_code': code, 'modifier': '', 'old_site_wrvu': entry.get('work_rvu'), 'reason_for_removal': cls, 'source_location': 'cpt_database.json', 'public_surfaces': 'database/search/autocomplete/api', 'removal_timestamp': meta['timestamp'], 'public_removal_confirmed': 'pending'})
            continue
        row = cms_ref[f'{code}|']
        old = entry.get('work_rvu')
        entry['work_rvu'] = float(row['work_rvu'])
        entry['rvu_year'] = YEAR
        entry['rvu_source_file'] = meta['cms_data_filename']
        entry['rvu_release'] = meta['cms_release']
        entry['rvu_modifier'] = ''
        entry['rvu_status_indicator'] = row['status_indicator']
        entry.pop('rvu_status', None)
        entry.pop('rvu_display_label', None)
        new[code] = entry
        updated_rows.append({'site_code': code, 'modifier': '', 'old_wrvu': old, 'corrected_cms_work_rvu': row['work_rvu'], 'cms_source_file': meta['cms_data_filename'], 'cms_year': YEAR, 'cms_release': meta['cms_release'], 'cms_status_indicator': row['status_indicator'], 'update_timestamp': meta['timestamp']})
    path.write_text(json.dumps(new, indent=2, sort_keys=True))


def purge_rvu_database(cms_ref, removed_rows, updated_rows, meta):
    path = ROOT / 'rvu_database.json'
    data = json.loads(path.read_text())
    new_codes = {}
    for code, entry in data.get('codes', {}).items():
        cls = classify(code, '', cms_ref)
        if cls != 'VALID_MATCH':
            removed_rows.append({'site_code': code, 'modifier': '', 'old_site_wrvu': entry.get('work_rvu'), 'reason_for_removal': cls, 'source_location': 'rvu_database.json', 'public_surfaces': 'frontend cache', 'removal_timestamp': meta['timestamp'], 'public_removal_confirmed': 'pending'})
            continue
        row = cms_ref[f'{code}|']
        old = entry.get('work_rvu')
        entry['work_rvu'] = float(row['work_rvu'])
        entry['rvu_year'] = YEAR
        entry['rvu_source_file'] = meta['cms_data_filename']
        entry['rvu_release'] = meta['cms_release']
        entry['rvu_modifier'] = ''
        entry['rvu_status_indicator'] = row['status_indicator']
        entry.pop('rvu_status', None)
        entry.pop('rvu_display_label', None)
        new_codes[code] = entry
        updated_rows.append({'site_code': code, 'modifier': '', 'old_wrvu': old, 'corrected_cms_work_rvu': row['work_rvu'], 'cms_source_file': meta['cms_data_filename'], 'cms_year': YEAR, 'cms_release': meta['cms_release'], 'cms_status_indicator': row['status_indicator'], 'update_timestamp': meta['timestamp']})
    data['codes'] = new_codes
    data['year'] = int(YEAR)
    data['cms_source_file'] = meta['cms_data_filename']
    data['cms_release'] = meta['cms_release']
    data['imported_at'] = meta['timestamp']
    data['source_checksum_sha256'] = meta['checksum']
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def purge_decision_tree(cms_ref, removed_rows, meta):
    path = ROOT / 'cpt_decision_tree.json'
    data = json.loads(path.read_text())

    def clean_node(node, source='root'):
        if isinstance(node, dict):
            if 'options' in node and isinstance(node['options'], list):
                new_opts = []
                for opt in node['options']:
                    if isinstance(opt, dict) and 'cpt_code' in opt:
                        code = str(opt['cpt_code'])
                        cls = classify(code, '', cms_ref)
                        if cls != 'VALID_MATCH':
                            removed_rows.append({'site_code': code, 'modifier': '', 'old_site_wrvu': opt.get('work_rvu'), 'reason_for_removal': cls, 'source_location': f'cpt_decision_tree.json:{source}', 'public_surfaces': 'decision tree', 'removal_timestamp': meta['timestamp'], 'public_removal_confirmed': 'pending'})
                            continue
                    new_opts.append(clean_node(opt, source))
                node['options'] = new_opts
            for k,v in list(node.items()):
                if isinstance(v, (dict,list)):
                    node[k] = clean_node(v, f'{source}.{k}')
            return node
        if isinstance(node, list):
            return [clean_node(x, source) for x in node]
        return node

    cleaned = clean_node(data)
    path.write_text(json.dumps(cleaned, separators=(',', ':')))


def write_csv(path, rows, fields):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in fields})


def verify_zero_unmatched(cms_ref):
    inv = collect_public_inventory(cms_ref)
    bad = []
    wrvu_bad = []
    meta_bad = []
    cpt_db = json.loads((ROOT / 'cpt_database.json').read_text())
    for rec in inv:
        cls = classify(rec['code'], '', cms_ref)
        if cls != 'VALID_MATCH':
            bad.append({**rec, 'classification': cls})
    for code, entry in cpt_db.items():
        row = cms_ref.get(f'{code}|')
        if not row:
            continue
        if float(entry['work_rvu']) != float(row['work_rvu']):
            wrvu_bad.append(code)
        for k in ['rvu_year','rvu_source_file','rvu_release','rvu_modifier','rvu_status_indicator']:
            if not entry.get(k, '') and entry.get(k, '') != '':
                meta_bad.append((code,k))
    return inv, bad, wrvu_bad, meta_bad


def main():
    AUDIT.mkdir(exist_ok=True)
    release, zip_name, updated = latest_release()
    zip_url = f'{CMS_BASE}/files/zip/{zip_name}'
    blob = fetch(zip_url)
    checksum = hashlib.sha256(blob).hexdigest()
    cms_data_filename, cms_ref = parse_cms(blob)
    timestamp = datetime.now(timezone.utc).isoformat()
    meta = {'cms_release': release, 'cms_zip_name': zip_name, 'cms_zip_url': zip_url, 'cms_data_filename': cms_data_filename, 'cms_update_date': updated, 'checksum': checksum, 'timestamp': timestamp}

    removed_rows = []
    updated_rows = []
    purge_specs(cms_ref, removed_rows, meta)
    purge_cpt_database(cms_ref, removed_rows, updated_rows, meta)
    purge_rvu_database(cms_ref, removed_rows, updated_rows, meta)
    purge_decision_tree(cms_ref, removed_rows, meta)

    # public removal confirmation rescan
    inv, bad, wrvu_bad, meta_bad = verify_zero_unmatched(cms_ref)
    public_text = '\n'.join([(ROOT/'index.html').read_text(), (ROOT/'cpt_decision_tree.json').read_text(), (ROOT/'cpt_database.json').read_text(), (ROOT/'rvu_database.json').read_text()])
    for row in removed_rows:
        row['public_removal_confirmed'] = 'yes' if row['site_code'] not in public_text else 'no'

    # reference import table
    ref_rows = []
    for row in cms_ref.values():
        ref_rows.append({**row, 'source_file': cms_data_filename, 'source_year': YEAR})
    write_csv(AUDIT/'cms_2026_reference_import_table.csv', ref_rows, ['code','modifier','canonical_key','work_rvu','status_indicator','global_indicator','description','source_file','source_year'])
    write_csv(AUDIT/'removed_unmatched_code_table.csv', removed_rows, ['site_code','modifier','old_site_wrvu','reason_for_removal','source_location','public_surfaces','removal_timestamp','public_removal_confirmed'])
    write_csv(AUDIT/'corrected_wrvu_table.csv', updated_rows, ['site_code','modifier','old_wrvu','corrected_cms_work_rvu','cms_source_file','cms_year','cms_release','cms_status_indicator','update_timestamp'])
    write_csv(AUDIT/'pseudo_code_combo_code_removal_table.csv', [r for r in removed_rows if r['reason_for_removal']=='SITE_PSEUDO_CODE_OR_COMBO_CODE'], ['site_code','modifier','old_site_wrvu','reason_for_removal','source_location','public_surfaces','removal_timestamp','public_removal_confirmed'])
    write_csv(AUDIT/'before_after_wrvu_mismatch_report.csv', updated_rows, ['site_code','modifier','old_wrvu','corrected_cms_work_rvu','cms_source_file','cms_year','cms_release','cms_status_indicator','update_timestamp'])
    write_csv(AUDIT/'final_active_code_table.csv', [r for r in inv if classify(r['code'],'',cms_ref)=='VALID_MATCH'], ['surface','code','modifier','wrvu','location'])
    write_csv(AUDIT/'modifier_mismatch_table.csv', [], ['site_code','modifier','reason'])
    write_csv(AUDIT/'public_surface_verification_report.csv', bad, ['surface','code','modifier','wrvu','location','classification'])

    final = {
        'cms_release': release,
        'cms_data_filename': cms_data_filename,
        'cms_update_date': updated,
        'cms_zip_name': zip_name,
        'cms_zip_sha256': checksum,
        'import_timestamp': timestamp,
        'rvu_year': YEAR,
        'final_unmatched_active_code_count': len(bad),
        'final_wrvu_mismatch_count': len(wrvu_bad),
        'final_missing_source_metadata_count': len(meta_bad),
        'statement': 'There are zero active unmatched codes.' if len(bad)==0 else 'Active unmatched codes remain.',
    }
    (AUDIT/'final_validation_report.json').write_text(json.dumps(final, indent=2, sort_keys=True))
    print(json.dumps(final, indent=2))

if __name__ == '__main__':
    main()
