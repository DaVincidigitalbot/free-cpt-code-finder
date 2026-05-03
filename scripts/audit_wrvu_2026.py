#!/usr/bin/env python3
import csv
import io
import json
import random
import re
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')
AUDIT_DIR = ROOT / 'audit'
CMS_LIST_URL = 'https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files'
CMS_BASE = 'https://www.cms.gov'
TARGET_YEAR = '2026'


def fetch_text(url: str) -> str:
    with urlopen(url, timeout=60) as resp:
        return resp.read().decode('utf-8', 'ignore')


def find_latest_cms_release(year: str):
    html = fetch_text(CMS_LIST_URL)
    matches = re.findall(rf'/medicare/payment/fee-schedules/physician/pfs-relative-value-files/(rvu{year[-2:]}[a-z])', html, re.I)
    if not matches:
        raise RuntimeError(f'No CMS RVU release found for {year}')
    latest_slug = sorted(set(m.lower() for m in matches))[-1]
    release_html = fetch_text(f'{CMS_BASE}/medicare/payment/fee-schedules/physician/pfs-relative-value-files/{latest_slug}')
    zip_matches = re.findall(r'/files/zip/([^"\']+\.zip)', release_html, re.I)
    if not zip_matches:
        # fallback known pattern
        zip_name = f'{latest_slug}.zip'
        zip_url = f'{CMS_BASE}/files/zip/{zip_name}'
    else:
        zip_name = zip_matches[0].split('/')[-1]
        zip_url = f'{CMS_BASE}/files/zip/{zip_name}'
    released = re.search(r'RELEASED\s*(\d{1,2}/\d{1,2}/\d{4})', release_html, re.I)
    updated = re.search(r'updated\s*(\d{1,2}/\d{1,2}/\d{4})', release_html, re.I)
    return {
        'slug': latest_slug.upper(),
        'page_url': f'{CMS_BASE}/medicare/payment/fee-schedules/physician/pfs-relative-value-files/{latest_slug}',
        'zip_url': zip_url,
        'zip_name': zip_name,
        'release_date': released.group(1) if released else None,
        'page_updated_date': updated.group(1) if updated else None,
    }


def download_zip_bytes(url: str) -> bytes:
    with urlopen(url, timeout=120) as resp:
        return resp.read()


def parse_cms(zip_bytes: bytes, year: str):
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    target = None
    for name in zf.namelist():
        low = name.lower()
        if 'pprrvu' in low and 'nonqpp' in low and low.endswith('.csv'):
            target = name
            break
    if not target:
        for name in zf.namelist():
            low = name.lower()
            if 'pprrvu' in low and low.endswith('.csv'):
                target = name
                break
    if not target:
        raise RuntimeError('Could not locate CMS PPRRVU csv')
    lines = zf.read(target).decode('latin1', 'ignore').splitlines()
    rows = list(csv.reader(lines))
    header_top = rows[8]
    header = rows[9]
    data_rows = rows[10:]
    def col_index(name, occurrence=1):
        count = 0
        for idx, val in enumerate(header):
            if val == name:
                count += 1
                if count == occurrence:
                    return idx
        raise KeyError(name)
    idx = {
        'HCPCS': col_index('HCPCS'),
        'MOD': col_index('MOD'),
        'DESCRIPTION': col_index('DESCRIPTION'),
        'STATUS': col_index('CODE'),
        'WORK_RVU': col_index('RVU', 1),
        'MP_RVU': col_index('RVU', 2),
        'GLOBAL_DAYS': col_index('DAYS'),
    }
    cms = {}
    by_code = defaultdict(list)
    for row in data_rows:
        if not row or len(row) <= idx['HCPCS']:
            continue
        code = row[idx['HCPCS']].strip()
        if not code:
            continue
        mod = row[idx['MOD']].strip()
        key = f'{code}|{mod}'
        entry = {
            'code': code,
            'modifier': mod,
            'description': row[idx['DESCRIPTION']].strip(),
            'status_indicator': row[idx['STATUS']].strip(),
            'work_rvu': row[idx['WORK_RVU']].strip(),
            'global_days': row[idx['GLOBAL_DAYS']].strip(),
            'raw_row': row,
        }
        cms[key] = entry
        by_code[code].append(entry)
    return target, cms, by_code


def parse_specs_from_index(path: Path):
    text = path.read_text()
    marker = 'const SPECS='
    start = text.find(marker)
    if start == -1:
        raise RuntimeError('SPECS not found')
    start += len(marker)
    level = 0
    in_str = False
    esc = False
    end = None
    for i, ch in enumerate(text[start:], start):
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == '{':
                level += 1
            elif ch == '}':
                level -= 1
                if level == 0:
                    end = i + 1
                    break
    if end is None:
        raise RuntimeError('Could not parse SPECS object')
    return json.loads(text[start:end])


def gather_site_records():
    records = []
    specs = parse_specs_from_index(ROOT / 'index.html')
    for specialty, items in specs.items():
        for idx, item in enumerate(items):
            if isinstance(item, list) and len(item) >= 4:
                records.append({
                    'source': 'index.html:SPECS',
                    'specialty': specialty,
                    'code': str(item[0]),
                    'modifier': '',
                    'site_wrvu': item[2],
                    'description': item[1],
                    'path_hint': f'{specialty}[{idx}]',
                })
    cpt_db = json.loads((ROOT / 'cpt_database.json').read_text())
    for code, entry in cpt_db.items():
        records.append({
            'source': 'cpt_database.json',
            'specialty': entry.get('specialty', ''),
            'code': str(code),
            'modifier': '',
            'site_wrvu': entry.get('work_rvu'),
            'description': entry.get('description', ''),
            'path_hint': code,
        })
    rvu_db = json.loads((ROOT / 'rvu_database.json').read_text())
    for code, entry in rvu_db.get('codes', {}).items():
        records.append({
            'source': 'rvu_database.json',
            'specialty': '',
            'code': str(code),
            'modifier': '',
            'site_wrvu': entry.get('work_rvu'),
            'description': entry.get('description', ''),
            'path_hint': code,
        })
    return records


def compare_records(records, cms, by_code, meta):
    compared = []
    modifier_ambiguity = []
    missing = []
    excluded_statuses = {'B', 'I', 'N', 'P', 'R', 'T', 'X'}
    for rec in records:
        code = rec['code']
        mod = rec['modifier']
        key = f'{code}|{mod}'
        cms_entry = cms.get(key)
        site_val = rec['site_wrvu']
        site_num = None if site_val in (None, '') else float(site_val)
        row = {
            **rec,
            'cms_year': TARGET_YEAR,
            'cms_source_filename': meta['cms_data_filename'],
            'cms_release': meta['cms_release_slug'],
            'cms_work_rvu': '',
            'cms_status_indicator': '',
            'match_status': '',
            'recommended_action': '',
        }
        if cms_entry:
            row['cms_work_rvu'] = cms_entry['work_rvu']
            row['cms_status_indicator'] = cms_entry['status_indicator']
            cms_num = float(cms_entry['work_rvu']) if cms_entry['work_rvu'] != '' else None
            if site_num == cms_num:
                row['match_status'] = 'exact match'
                row['recommended_action'] = 'none'
            else:
                row['match_status'] = 'mismatch'
                row['recommended_action'] = f"update WRVU to {cms_entry['work_rvu']} and stamp CMS year/source"
        else:
            code_rows = by_code.get(code, [])
            if code_rows:
                mods = sorted({r['modifier'] for r in code_rows if r['modifier']})
                base = next((r for r in code_rows if r['modifier'] == ''), None)
                if base:
                    row['cms_work_rvu'] = base['work_rvu']
                    row['cms_status_indicator'] = base['status_indicator']
                    if mods:
                        row['match_status'] = 'modifier ambiguity'
                        row['recommended_action'] = 'base row exists; preserve base WRVU and review modifier-specific rows/UI'
                        modifier_ambiguity.append({**row, 'available_modifiers': ','.join(mods)})
                    else:
                        cms_num = float(base['work_rvu']) if base['work_rvu'] != '' else None
                        if site_num == cms_num:
                            row['match_status'] = 'exact match'
                            row['recommended_action'] = 'none'
                        else:
                            row['match_status'] = 'mismatch'
                            row['recommended_action'] = f"update WRVU to {base['work_rvu']} and stamp CMS year/source"
                else:
                    row['cms_status_indicator'] = ','.join(sorted({r['status_indicator'] for r in code_rows}))
                    row['match_status'] = 'modifier ambiguity'
                    row['recommended_action'] = 'no blank modifier CMS row; schema/UI review required before assigning base WRVU'
                    modifier_ambiguity.append({**row, 'available_modifiers': ','.join(mods)})
            else:
                row['match_status'] = 'missing from CMS'
                row['recommended_action'] = 'mark as not found in CMS PFS RVU file; do not guess'
                missing.append(row)
        if row['cms_status_indicator'] in excluded_statuses and row['match_status'] != 'missing from CMS':
            row['recommended_action'] = f"flag status {row['cms_status_indicator']} as no/limited national PFS WRVU context review"
        compared.append(row)
    return compared, modifier_ambiguity, missing


def dedupe_for_updates(compared):
    pick = {}
    for row in compared:
        key = (row['source'], row['code'])
        if key not in pick:
            pick[key] = row
    return pick


def update_index_wrvus(compared):
    updates = {(r['code'], r['source']): r for r in compared if r['source'] == 'index.html:SPECS' and r['match_status'] == 'mismatch' and r['cms_work_rvu'] not in ('', None)}
    path = ROOT / 'index.html'
    text = path.read_text()
    specs = parse_specs_from_index(path)
    changed = 0
    for specialty, items in specs.items():
        for item in items:
            if isinstance(item, list) and len(item) >= 4:
                key = (str(item[0]), 'index.html:SPECS')
                row = updates.get(key)
                if row:
                    new_val = float(row['cms_work_rvu'])
                    if item[2] != new_val:
                        item[2] = new_val
                        changed += 1
    old = text
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
    new_specs = json.dumps(specs, separators=(',', ':'))
    text = text[:start] + new_specs + text[end:]
    path.write_text(text)
    return changed


def update_json_file(filename, key_path='work_rvu', compared=None, meta=None):
    path = ROOT / filename
    data = json.loads(path.read_text())
    changes = 0
    by_code = {r['code']: r for r in compared if r['source'] == filename and r['match_status'] == 'mismatch' and r['cms_work_rvu'] not in ('', None)}
    if filename == 'cpt_database.json':
        for code, row in by_code.items():
            if code in data:
                new_val = float(row['cms_work_rvu'])
                if data[code].get('work_rvu') != new_val:
                    data[code]['work_rvu'] = new_val
                    data[code]['rvu_year'] = TARGET_YEAR
                    data[code]['rvu_source_file'] = meta['cms_data_filename']
                    changes += 1
    elif filename == 'rvu_database.json':
        data['year'] = int(TARGET_YEAR)
        data['cms_source_file'] = meta['cms_data_filename']
        data['cms_release'] = meta['cms_release_slug']
        data['imported_at'] = meta['imported_at']
        for code, row in by_code.items():
            if code in data.get('codes', {}):
                new_val = float(row['cms_work_rvu'])
                if data['codes'][code].get('work_rvu') != new_val:
                    data['codes'][code]['work_rvu'] = new_val
                    data['codes'][code]['rvu_year'] = TARGET_YEAR
                    data['codes'][code]['rvu_source_file'] = meta['cms_data_filename']
                    changes += 1
    path.write_text(json.dumps(data, indent=2, sort_keys=True))
    return changes


def write_csv(path: Path, rows, fieldnames):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, '') for k in fieldnames})


def main():
    AUDIT_DIR.mkdir(exist_ok=True)
    source = find_latest_cms_release(TARGET_YEAR)
    zip_bytes = download_zip_bytes(source['zip_url'])
    cms_data_filename, cms, by_code = parse_cms(zip_bytes, TARGET_YEAR)
    imported_at = datetime.now(timezone.utc).isoformat()
    meta = {
        'cms_year': TARGET_YEAR,
        'cms_release_slug': source['slug'],
        'cms_page_url': source['page_url'],
        'cms_zip_url': source['zip_url'],
        'cms_zip_name': source['zip_name'],
        'cms_data_filename': cms_data_filename,
        'cms_release_date': source['release_date'],
        'cms_page_updated_date': source['page_updated_date'],
        'imported_at': imported_at,
    }
    records = gather_site_records()
    compared, modifier_ambiguity, missing = compare_records(records, cms, by_code, meta)

    index_changes = update_index_wrvus(compared)
    cpt_db_changes = update_json_file('cpt_database.json', compared=compared, meta=meta)
    rvu_db_changes = update_json_file('rvu_database.json', compared=compared, meta=meta)

    mismatch_rows = [r for r in compared if r['match_status'] == 'mismatch']
    exact_rows = [r for r in compared if r['match_status'] == 'exact match']

    # reports
    common_fields = ['source','specialty','code','modifier','description','site_wrvu','cms_work_rvu','cms_status_indicator','cms_year','cms_source_filename','match_status','recommended_action','path_hint']
    write_csv(AUDIT_DIR / 'wrvu_audit_all_records.csv', compared, common_fields)
    write_csv(AUDIT_DIR / 'wrvu_mismatch_report.csv', mismatch_rows, common_fields)
    write_csv(AUDIT_DIR / 'wrvu_missing_unmatched_report.csv', missing, common_fields)
    mod_fields = common_fields + ['available_modifiers']
    write_csv(AUDIT_DIR / 'wrvu_modifier_ambiguity_report.csv', modifier_ambiguity, mod_fields)
    changelog = []
    for row in mismatch_rows:
        changelog.append({
            'source': row['source'],
            'code': row['code'],
            'old_wrvu': row['site_wrvu'],
            'new_wrvu': row['cms_work_rvu'],
            'cms_year': TARGET_YEAR,
            'cms_source_filename': cms_data_filename,
            'cms_release': source['slug'],
            'imported_at': imported_at,
        })
    write_csv(AUDIT_DIR / 'wrvu_changelog.csv', changelog, ['source','code','old_wrvu','new_wrvu','cms_year','cms_source_filename','cms_release','imported_at'])

    source_meta = {
        **meta,
        'record_count_compared': len(compared),
        'cms_key_count': len(cms),
        'index_changes': index_changes,
        'cpt_database_changes': cpt_db_changes,
        'rvu_database_changes': rvu_db_changes,
    }
    (AUDIT_DIR / 'wrvu_source_metadata.json').write_text(json.dumps(source_meta, indent=2, sort_keys=True))

    # 100-code spot check sample from unique codes across sources
    unique_codes = sorted({r['code'] for r in compared})
    random.seed(20260501)
    sample_codes = random.sample(unique_codes, min(100, len(unique_codes)))
    sample_rows = []
    for code in sample_codes:
        base = cms.get(f'{code}|') or next(iter(by_code.get(code, [])), None)
        sample_rows.append({
            'code': code,
            'cms_work_rvu': base['work_rvu'] if base else '',
            'cms_status_indicator': base['status_indicator'] if base else '',
            'cms_description': base['description'] if base else '',
        })
    write_csv(AUDIT_DIR / 'wrvu_spotcheck_sample_100.csv', sample_rows, ['code','cms_work_rvu','cms_status_indicator','cms_description'])

    summary = {
        'exact_match': len(exact_rows),
        'mismatch': len(mismatch_rows),
        'missing_from_cms': len([r for r in compared if r['match_status'] == 'missing from CMS']),
        'modifier_ambiguity': len([r for r in compared if r['match_status'] == 'modifier ambiguity']),
        'total_records': len(compared),
        'unique_site_codes': len({r['code'] for r in compared}),
        'unique_cms_codes': len(by_code),
    }
    (AUDIT_DIR / 'wrvu_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps({'meta': source_meta, 'summary': summary}, indent=2))


if __name__ == '__main__':
    main()
