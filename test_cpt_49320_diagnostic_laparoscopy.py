#!/usr/bin/env python3
"""Regression coverage for CPT 49320 diagnostic laparoscopy discoverability."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "cpt_database.json"
TREE_PATH = ROOT / "cpt_decision_tree.json"
INDEX_PATH = ROOT / "index.html"


class DiagnosticLaparoscopy49320Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = json.loads(DB_PATH.read_text())
        cls.tree_text = TREE_PATH.read_text().lower()
        cls.index_text = INDEX_PATH.read_text().lower()

    def test_database_contains_current_active_code(self):
        row = self.db["49320"]
        self.assertEqual(row["code"], "49320")
        self.assertEqual(row["work_rvu"], 5.01)
        self.assertEqual(row["global_period_days"], 10)
        self.assertFalse(row["estimated"])

    def test_description_and_search_terms_find_clinical_phrases(self):
        row = self.db["49320"]
        searchable = " ".join(
            [row.get("description", ""), *row.get("search_terms", [])]
        ).lower()
        for phrase in (
            "diagnostic laparoscopy",
            "laparoscopy abdomen",
            "peritoneum",
            "omentum",
            "specimen collection",
            "brushing",
            "washing",
        ):
            self.assertIn(phrase, searchable)

    def test_guided_workflow_and_bundling_context_remain_connected(self):
        self.assertIn('"cpt_code": "49320"', self.tree_text)
        self.assertIn("diagnostic laparoscopy", self.tree_text)
        self.assertIn("'49320'", self.index_text)

    def test_code_is_within_loaded_external_search_slice(self):
        # index.html currently loads the first 4,000 database rows into search.
        self.assertLess(list(self.db).index("49320"), 4000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
