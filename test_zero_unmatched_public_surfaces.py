#!/usr/bin/env python3
import csv
import io
import json
import re
import unittest
import zipfile
from pathlib import Path
from urllib.request import urlopen

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')


def cms_ref():
    blob = urlopen('https://www.cms.gov/files/zip/rvu26b-updated-03-10-2026.zip', timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(blob))
    name = [n for n in z.namelist() if 'pprrvu' in n.lower() and 'nonqpp' in n.lower() and n.lower().endswith('.csv')][0]
    rows = list(csv.reader(z.read(name).decode('latin1', 'ignore').splitlines()))
    hdr = rows[9]
    code_i, mod_i, wrvu_i = hdr.index('HCPCS'), hdr.index('MOD'), hdr.index('RVU')
    return {f"{r[code_i].strip()}|{r[mod_i].strip()}": r[wrvu_i].strip() for r in rows[10:] if r and r[code_i].strip()}


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
                    end = i + 1; break
    return json.loads(text[start:end])


class TestZeroUnmatchedPublicSurfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = cms_ref()
        cls.index = (ROOT / 'index.html').read_text()
        cls.specs = parse_specs(cls.index)
        cls.tree = (ROOT / 'cpt_decision_tree.json').read_text()
        cls.cpt_db = json.loads((ROOT / 'cpt_database.json').read_text())
        cls.rvu_db = json.loads((ROOT / 'rvu_database.json').read_text())

    def test_specs_all_codes_match_cms(self):
        bad = []
        for specialty, procs in self.specs.items():
            for p in procs:
                if isinstance(p, list) and len(p) >= 3:
                    code = str(p[0])
                    key = f'{code}|'
                    if key not in self.ref or self.ref[key] == '':
                        bad.append((specialty, code))
        self.assertEqual(bad, [])

    def test_decision_tree_all_codes_match_cms(self):
        bad = []
        for code in re.findall(r'"cpt_code":"([A-Z0-9]{4,5})"', self.tree):
            key = f'{code}|'
            if key not in self.ref or self.ref[key] == '':
                bad.append(code)
        self.assertEqual(sorted(set(bad)), [])

    def test_databases_all_codes_match_cms_and_have_metadata(self):
        for db in [self.cpt_db, self.rvu_db['codes']]:
            for code, entry in db.items():
                key = f'{code}|'
                self.assertIn(key, self.ref, code)
                self.assertNotEqual(self.ref[key], '', code)
                self.assertAlmostEqual(float(entry['work_rvu']), float(self.ref[key]), places=2)
                for field in ['rvu_year', 'rvu_source_file', 'rvu_release', 'rvu_modifier', 'rvu_status_indicator']:
                    self.assertIn(field, entry, f'{code} missing {field}')

    def test_no_combo_patterns_in_active_specs(self):
        for specialty, procs in self.specs.items():
            for p in procs:
                if isinstance(p, list) and len(p) >= 1:
                    self.assertRegex(str(p[0]), r'^[A-Z0-9]{4,5}$')

if __name__ == '__main__':
    unittest.main()
