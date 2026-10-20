import json
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.import_clinical_case_prep import build_payload, validate_slug

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
        self.assertEqual(233, len(procedures))
        self.assertEqual(20, len(data["categories"]))
        self.assertEqual(1175, data["totals"]["questions"])
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

        tapp = next(item for item in procedures if item["id"] == "robotic-tapp-inguinal-hernia")
        self.assertEqual("Robotic TAPP Inguinal Hernia Repair", tapp["name"])
        self.assertEqual(5, len(tapp["pimpingQuestions"]))
        tapp_content = json.dumps(tapp).lower()
        for marker in [
            "transabdominal", "peritoneal flap", "preperitoneal dissection",
            "myopectineal orifice", "mesh", "complete peritoneal closure",
            "reduce or appropriately manage each hernia sac", "selective transection",
        ]:
            self.assertIn(marker, tapp_content)
        self.assertNotIn("reduce all hernia sacs", tapp_content)
        self.assertNotEqual(
            tapp["id"],
            next(item for item in procedures if item["id"] == "robotic-etep-inguinal-hernia")["id"],
        )

    def test_importer_rejects_unsafe_output_slugs(self):
        with self.assertRaises(ValueError):
            validate_slug("../escape")

    def test_importer_preserves_curated_tapp_procedure_on_future_regeneration(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "procedures.json"
            source.write_text("[]", encoding="utf-8")
            payload = build_payload(source)
        tapp = next(item for item in payload["procedures"] if item["id"] == "robotic-tapp-inguinal-hernia")
        self.assertEqual("Robotic TAPP Inguinal Hernia Repair", tapp["name"])
        self.assertEqual(5, len(tapp["pimpingQuestions"]))

    def test_landing_page_exposes_search_filters_and_full_library(self):
        html = HOME.read_text(encoding="utf-8")
        for marker in [
            "233 surgical procedures",
            "1,175 attending-style questions",
            "Anatomy",
            "Pitfalls",
            "Critical Steps",
            "Complete Case Prep Library",
            'data-library-search',
            'data-library-category',
            'src="/js/case-prep-library.js?v=20261019-tapp-contrast1"',
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

    def test_case_prep_pages_bust_the_production_stylesheet_cache(self):
        expected = '/styles/case-prep.css?v=20261019-tapp-contrast1'
        self.assertIn(expected, HOME.read_text(encoding="utf-8"))
        self.assertIn(expected, DETAIL.read_text(encoding="utf-8"))

    def test_runtime_payloads_are_split_for_fast_detail_pages(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        files = sorted(PROCEDURE_DATA.glob("*.json"))
        self.assertEqual(233, len(index["procedures"]))
        self.assertEqual(233, len(files))
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
            "body:has([data-case-prep-library-home]) .fccf-report-launch",
        ]:
            self.assertIn(marker, css)
        self.assertNotIn("var(--forest)", css)

    def test_prep_sheet_light_panels_have_wcag_aa_text_tokens_in_both_themes(self):
        css = CSS.read_text(encoding="utf-8")
        block = re.search(r"\.prep-sheet\{([^}]+)\}", css)
        self.assertIsNotNone(block)
        declarations = block.group(1) if block else ""
        colors = dict(re.findall(r"--(paper|ink|ink2|line|line2|ox|moss|white):(#[0-9a-fA-F]{6})", declarations))
        self.assertEqual({"paper", "ink", "ink2", "line", "line2", "ox", "moss", "white"}, set(colors))

        def luminance(hex_color):
            channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        def contrast(first, second):
            lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
            return (lighter + 0.05) / (darker + 0.05)

        for foreground, background in [
            ("ink", "white"), ("ink2", "white"), ("ink2", "paper"),
            ("ox", "white"), ("white", "moss"),
        ]:
            self.assertGreaterEqual(contrast(colors[foreground], colors[background]), 4.5)


if __name__ == "__main__":
    unittest.main()
