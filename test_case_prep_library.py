import json
import re
import unittest
from pathlib import Path

from scripts.import_clinical_case_prep import validate_slug

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "case-prep" / "clinical-library.json"
INDEX = ROOT / "case-prep" / "clinical-library-index.json"
PROCEDURE_DATA = ROOT / "case-prep" / "library-data"
HOME = ROOT / "case-prep" / "index.html"
DETAIL = ROOT / "case-prep" / "library" / "index.html"
JS = ROOT / "js" / "case-prep-library.js"
CSS = ROOT / "styles" / "case-prep.css"
LEGACY_QUESTION_BANK = ROOT / "js" / "pimp-question-bank.js"


class ClinicalCasePrepLibraryTests(unittest.TestCase):
    def test_complete_clinical_case_log_library_is_migrated(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        procedures = data["procedures"]
        self.assertEqual(232, len(procedures))
        self.assertEqual(20, len(data["categories"]))
        self.assertEqual(1170, data["totals"]["questions"])
        self.assertEqual(len(procedures), len({item["id"] for item in procedures}))

        required = {
            "id", "name", "category", "overview", "indications", "keyAnatomy",
            "preOpConsiderations", "positioning", "portPlacementOrIncision",
            "criticalSteps", "commonPitfalls", "majorComplications", "pearlsHighYield",
            "postOpPriorities", "relatedProcedures", "pimpingQuestions",
        }
        for procedure in procedures:
            self.assertTrue(required.issubset(procedure), procedure["id"])
            self.assertTrue(procedure["pimpingQuestions"], procedure["id"])

        levels = [
            question["level"]
            for procedure in procedures
            for question in procedure["pimpingQuestions"]
        ]
        self.assertEqual({"medical_student", "resident", "attending"}, set(levels))
        for level in {"medical_student", "resident", "attending"}:
            self.assertGreaterEqual(levels.count(level), 100)

        nuss = next(item for item in procedures if item["id"] == "nuss-procedure")
        self.assertIn("Supine with arms abducted", nuss["positioning"])
        self.assertIn("Supine with arms extended", nuss["positioning"])

    def test_importer_rejects_unsafe_output_slugs(self):
        with self.assertRaises(ValueError):
            validate_slug("../escape")

    def test_landing_page_exposes_search_filters_and_full_library(self):
        html = HOME.read_text(encoding="utf-8")
        for marker in [
            "232 surgical procedures",
            "1,170 attending-style questions",
            "Anatomy",
            "Pitfalls",
            "Critical Steps",
            "Complete Case Prep Library",
            'data-library-search',
            'data-library-category',
            'src="/js/case-prep-library.js"',
        ]:
            self.assertIn(marker, html)

    def test_detail_page_contains_every_educational_section(self):
        html = DETAIL.read_text(encoding="utf-8")
        for marker in [
            "Case Prep Sheet",
            "Key Anatomy",
            "Preoperative Considerations",
            "Positioning",
            "Port Placement / Incision",
            "Critical Operative Steps",
            "Common Pitfalls",
            "Major Complications",
            "High-Yield Pearls",
            "Postoperative Priorities",
            "Pimp Questions",
            "Medical Student",
            "Resident",
            "Attending",
            'data-procedure-detail',
            'data-question-bank',
            'data-question-level-filter',
            'role="group"',
        ]:
            self.assertIn(marker, html)

    def test_runtime_payloads_are_split_for_fast_detail_pages(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        files = sorted(PROCEDURE_DATA.glob("*.json"))
        self.assertEqual(232, len(index["procedures"]))
        self.assertEqual(232, len(files))
        self.assertEqual(
            {item["id"] for item in index["procedures"]},
            {path.stem for path in files},
        )

    def test_client_renderer_escapes_content_and_supports_shareable_routes(self):
        js = JS.read_text(encoding="utf-8")
        for marker in [
            "function escapeHtml",
            "URLSearchParams",
            "procedure=",
            "renderLibraryHome",
            "renderProcedureDetail",
            "aria-expanded",
            "history.replaceState",
            "INDEX_URL",
            "procedureDataUrl",
            "filterQuestionsByLevel",
            "humanizeSlug",
            "prep-related-unavailable",
            "meta[property=",
        ]:
            self.assertIn(marker, js)
        self.assertNotRegex(js, re.compile(r"\.innerHTML\s*=\s*(?:procedure|question)\.", re.I))

    def test_existing_question_bank_uses_the_same_attending_label(self):
        js = LEGACY_QUESTION_BANK.read_text(encoding="utf-8")
        self.assertIn('oral_boards: "🔴 Attending"', js)
        self.assertIn('data-filter="oral_boards" type="button">Attending</button>', js)
        self.assertNotIn("Advanced Decision-Making", js)

    def test_visual_system_has_responsive_explore_and_reading_surfaces(self):
        css = CSS.read_text(encoding="utf-8")
        for marker in [
            ".library-command",
            ".library-layout",
            ".library-card",
            ".prep-sheet",
            ".prep-section",
            ".question-card",
            "@media(max-width:800px)",
            "prefers-reduced-motion",
            ".site-page[data-site-header]{min-height:",
            ".app-mode-toggle__label{color:",
            ".prep-sheet[aria-busy=\"true\"]",
            "body[data-case-prep-library-detail] .fccf-report-launch",
        ]:
            self.assertIn(marker, css)
        self.assertNotIn("var(--forest)", css)


if __name__ == "__main__":
    unittest.main()
