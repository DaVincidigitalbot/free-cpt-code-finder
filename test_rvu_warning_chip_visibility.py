#!/usr/bin/env python3
import json
import re
import unittest
from pathlib import Path

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')

class TestRVUStrictVisibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / 'index.html').read_text()
        cls.cpt_db = json.loads((ROOT / 'cpt_database.json').read_text())
        cls.rvu_db = json.loads((ROOT / 'rvu_database.json').read_text())

    def test_warning_logic_not_tied_to_unmatched_public_codes(self):
        self.assertNotIn('not_found_in_cms_pfs_rvu_file', self.index)
        self.assertNotIn('No national CMS work RVU', self.index)

    def test_unmatched_examples_not_searchable_or_autocompletable(self):
        for code in ['49580', '49585', '49652', '49568']:
            self.assertNotIn(code, self.cpt_db)
            self.assertNotIn(code, self.rvu_db['codes'])
        active_surfaces = [self.cpt_db.keys(), self.rvu_db['codes'].keys(), re.findall(r'"cpt_code":"([A-Z0-9]{4,5})"', (ROOT/'cpt_decision_tree.json').read_text())]
        flattened = set()
        for surface in active_surfaces:
            flattened.update(surface)
        for code in ['49580', '49585', '49652', '49568']:
            self.assertNotIn(code, flattened)

    def test_search_meta_cache_exists_for_valid_codes(self):
        self.assertIn('codeMeta:{}', self.index)
        self.assertIn('searchState.codeMeta=entries.reduce', self.index)
        self.assertIn('addAutocompleteResultToCase', self.index)
        self.assertIn("fetch('cpt_database.json')", self.index)

if __name__ == '__main__':
    unittest.main()
