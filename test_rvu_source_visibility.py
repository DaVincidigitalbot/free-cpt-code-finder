#!/usr/bin/env python3
import json
import re
import unittest
from pathlib import Path

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')

class TestRVUSourceVisibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / 'index.html').read_text()
        cls.cpt_db = json.loads((ROOT / 'cpt_database.json').read_text())
        cls.rvu_db = json.loads((ROOT / 'rvu_database.json').read_text())

    def test_ui_contains_cms_badges(self):
        self.assertIn('id="cmsYearBadge"', self.index)
        self.assertIn('id="cmsSourceBadge"', self.index)
        self.assertIn('id="railCmsSource"', self.index)
        self.assertIn('CMS_RVU_RELEASE', self.index)
        self.assertIn('CMS_RVU_SOURCE_FILE', self.index)

    def test_valid_codes_carry_cms_source_metadata_in_public_data(self):
        for code in ['44204', '15734', '66984', '60240']:
            self.assertIn(code, self.cpt_db)
            entry = self.cpt_db[code]
            self.assertEqual(entry.get('rvu_year'), '2026')
            self.assertEqual(entry.get('rvu_release'), 'RVU26B')
            self.assertEqual(entry.get('rvu_source_file'), 'PPRRVU2026_Apr_nonQPP.csv')
            self.assertIn('rvu_status_indicator', entry)
            self.assertIn(code, self.rvu_db['codes'])

    def test_unmatched_codes_are_not_present_in_public_data(self):
        for code in ['49580', '49585', '49652', '49568']:
            self.assertNotIn(code, self.cpt_db)
            self.assertNotIn(code, self.rvu_db['codes'])

    def test_unmatched_label_logic_removed_from_active_ui(self):
        self.assertNotIn('No national CMS work RVU', self.index)
        self.assertNotIn('not_found_in_cms_pfs_rvu_file', self.index)

    def test_valid_search_metadata_pipeline_remains(self):
        self.assertIn('fetch(\'cpt_database.json\')', self.index)
        self.assertIn('searchState.codeMeta=entries.reduce', self.index)
        self.assertRegex(self.index, r'updateCmsBadges\s*\(')

if __name__ == '__main__':
    unittest.main()
