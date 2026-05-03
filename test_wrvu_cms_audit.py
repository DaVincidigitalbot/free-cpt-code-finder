#!/usr/bin/env python3
import csv
import json
import random
import unittest
from pathlib import Path

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')
AUDIT = ROOT / 'audit'


def load_audit_rows():
    with (AUDIT / 'wrvu_audit_all_records.csv').open() as f:
        return list(csv.DictReader(f))


class TestCMSWRVUAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_audit_rows()
        cls.cpt_db = json.loads((ROOT / 'cpt_database.json').read_text())
        cls.rvu_db = json.loads((ROOT / 'rvu_database.json').read_text())
        cls.source_meta = json.loads((AUDIT / 'wrvu_source_metadata.json').read_text())

    def test_source_metadata_present(self):
        self.assertEqual(self.source_meta['cms_year'], '2026')
        self.assertTrue(self.source_meta['cms_data_filename'].startswith('PPRRVU2026_'))
        self.assertEqual(self.source_meta['cms_release_slug'], 'RVU26B')

    def test_no_remaining_mismatches_in_updated_data_stores(self):
        bad = []
        for row in self.rows:
            if row['source'] not in {'index.html:SPECS', 'cpt_database.json', 'rvu_database.json'}:
                continue
            if row['match_status'] != 'mismatch':
                continue
            code = row['code']
            cms = row['cms_work_rvu']
            if row['source'] == 'cpt_database.json' and code in self.cpt_db:
                if f"{self.cpt_db[code].get('work_rvu', ''):.2f}" != f"{float(cms):.2f}":
                    bad.append((row['source'], code, self.cpt_db[code].get('work_rvu'), cms))
            if row['source'] == 'rvu_database.json' and code in self.rvu_db.get('codes', {}):
                if f"{self.rvu_db['codes'][code].get('work_rvu', ''):.2f}" != f"{float(cms):.2f}":
                    bad.append((row['source'], code, self.rvu_db['codes'][code].get('work_rvu'), cms))
        self.assertEqual(bad, [], f'Remaining mismatches: {bad[:10]}')

    def test_high_risk_codes_spotcheck(self):
        high_risk = ['99213','99291','93010','15734','44204','44139','44213','76937','71045','47562']
        index_map = {}
        for row in self.rows:
            if row['source'] == 'cpt_database.json':
                index_map[row['code']] = row
        for code in high_risk:
            if code not in index_map:
                continue
            cms = float(index_map[code]['cms_work_rvu']) if index_map[code]['cms_work_rvu'] else None
            self.assertIsNotNone(cms, code)
            self.assertAlmostEqual(float(self.cpt_db[code]['work_rvu']), cms, places=2)

    def test_zero_wrvu_codes_not_rounded_wrong(self):
        zeros = [r for r in self.rows if r['cms_work_rvu'] == '0.00' and r['source'] == 'cpt_database.json']
        sample = zeros[:50]
        for row in sample:
            self.assertEqual(float(self.cpt_db[row['code']]['work_rvu']), 0.0)

    def test_modifier_base_code_not_overwritten(self):
        # Audit currently stores base rows only. Ensure audited rows do not claim modifier ambiguity.
        ambiguous = [r for r in self.rows if r['match_status'] == 'modifier ambiguity']
        self.assertEqual(ambiguous, [])

    def test_random_100_code_sample_matches_audit_file(self):
        with (AUDIT / 'wrvu_spotcheck_sample_100.csv').open() as f:
            sample_rows = list(csv.DictReader(f))
        self.assertGreaterEqual(len(sample_rows), 100)
        audit_map = {(r['code'], r['source']): r for r in self.rows if r['source'] == 'cpt_database.json'}
        for row in sample_rows[:100]:
            code = row['code']
            if code in self.cpt_db and row['cms_work_rvu']:
                self.assertAlmostEqual(float(self.cpt_db[code]['work_rvu']), float(row['cms_work_rvu']), places=2)


if __name__ == '__main__':
    unittest.main()
