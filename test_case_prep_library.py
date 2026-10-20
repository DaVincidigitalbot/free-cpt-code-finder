import json
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

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
        self.assertEqual(231, len(procedures))
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

    def test_thyroid_education_is_total_thyroidectomy_vs_thyroid_lobectomy(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        procedures = {item["id"]: item for item in data["procedures"]}

        self.assertIn("total-thyroidectomy", procedures)
        self.assertIn("thyroid-lobectomy", procedures)
        self.assertNotIn("robotic-thyroidectomy", procedures)
        self.assertNotIn("hemithyroidectomy", procedures)
        self.assertNotIn("hemithyroidectomy-lobectomy", procedures)

        total = procedures["total-thyroidectomy"]
        lobectomy = procedures["thyroid-lobectomy"]
        self.assertEqual("Total Thyroidectomy", total["name"])
        self.assertEqual("Thyroid Lobectomy", lobectomy["name"])
        self.assertEqual(5, len(total["pimpingQuestions"]))
        self.assertEqual(10, len(lobectomy["pimpingQuestions"]))
        for procedure in (total, lobectomy):
            self.assertEqual(1, len(procedure["approachEducation"]))
            approach = procedure["approachEducation"][0]
            self.assertEqual("remote-access-robotic-thyroid-approach", approach["id"])
            self.assertEqual("Remote-access robotic approach", approach["name"])
            self.assertEqual("Robotic Thyroidectomy", approach["sourceName"])
            self.assertEqual(5, len(approach["pimpingQuestions"]))
            self.assertIn(
                "What is the transaxillary approach for robotic thyroidectomy?",
                {item["question"] for item in approach["pimpingQuestions"]},
            )
        self.assertIn("thyroid-lobectomy", total["relatedProcedures"])

    def test_importer_durably_excludes_robotic_thyroidectomy_and_merges_lobectomy_education(self):
        def source_record(identifier, name, question):
            return {
                "id": identifier,
                "name": name,
                "category": "Endocrine",
                "overview": f"Education for {name}",
                "indications": [f"Indication for {name}"],
                "keyAnatomy": [f"Anatomy for {name}"],
                "preOpConsiderations": [f"Pre-op for {name}"],
                "positioning": "Supine with neck extension",
                "portPlacementOrIncision": ["Low collar incision"],
                "criticalSteps": [f"Critical step for {name}"],
                "commonPitfalls": [f"Pitfall for {name}"],
                "majorComplications": [f"Complication for {name}"],
                "pearlsHighYield": [f"Pearl for {name}"],
                "postOpPriorities": [f"Post-op priority for {name}"],
                "relatedProcedures": ["total-thyroidectomy"],
                "pimpingQuestions": [{"question": question, "answer": f"Answer for {question}"}],
            }

        source_records = [
            source_record("total-thyroidectomy", "Total Thyroidectomy", "Total question"),
            source_record("hemithyroidectomy", "Hemithyroidectomy", "Legacy lobectomy question"),
            source_record(
                "hemithyroidectomy-lobectomy",
                "Hemithyroidectomy/Thyroid Lobectomy",
                "Second lobectomy question",
            ),
            source_record("robotic-thyroidectomy", "Robotic Thyroidectomy", "Robotic question"),
        ]
        with TemporaryDirectory() as directory:
            source = Path(directory) / "procedures.json"
            source.write_text(json.dumps(source_records), encoding="utf-8")
            payload = build_payload(source)

        procedures = {item["id"]: item for item in payload["procedures"]}
        self.assertNotIn("robotic-thyroidectomy", procedures)
        self.assertNotIn("hemithyroidectomy", procedures)
        self.assertNotIn("hemithyroidectomy-lobectomy", procedures)
        lobectomy = procedures["thyroid-lobectomy"]
        self.assertEqual("Thyroid Lobectomy", lobectomy["name"])
        self.assertEqual(
            {"Legacy lobectomy question", "Second lobectomy question"},
            {item["question"] for item in lobectomy["pimpingQuestions"]},
        )
        for field in [
            "indications", "keyAnatomy", "preOpConsiderations", "criticalSteps",
            "commonPitfalls", "majorComplications", "pearlsHighYield", "postOpPriorities",
        ]:
            self.assertEqual(2, len(lobectomy[field]), field)
        for identifier in ["total-thyroidectomy", "thyroid-lobectomy"]:
            approach = procedures[identifier]["approachEducation"][0]
            self.assertEqual("Remote-access robotic approach", approach["name"])
            self.assertEqual(
                {"Robotic question"},
                {item["question"] for item in approach["pimpingQuestions"]},
            )

    def test_withdrawn_thyroid_id_cannot_be_reintroduced_by_curated_content(self):
        robotic = {
            "id": "robotic-thyroidectomy",
            "name": "Robotic Thyroidectomy",
            "category": "Endocrine",
            "overview": "Withdrawn taxonomy fixture",
            "pimpingQuestions": [{"question": "Fixture?", "answer": "Fixture."}],
        }
        with TemporaryDirectory() as directory:
            source = Path(directory) / "procedures.json"
            curated = Path(directory) / "curated-procedures.json"
            source.write_text("[]", encoding="utf-8")
            curated.write_text(json.dumps([robotic]), encoding="utf-8")
            with patch("scripts.import_clinical_case_prep.CURATED_PROCEDURES", curated):
                payload = build_payload(source)
        self.assertNotIn("robotic-thyroidectomy", {item["id"] for item in payload["procedures"]})

    def test_importer_metadata_records_deterministic_source_provenance(self):
        source_record = {
            "id": "source-provenance-fixture",
            "name": "Source Provenance Fixture",
            "category": "General Surgery",
            "overview": "Fixture",
            "pimpingQuestions": [{"question": "Fixture?", "answer": "Fixture."}],
        }
        with TemporaryDirectory() as directory:
            source = Path(directory) / "procedures.json"
            source.write_text(json.dumps([source_record]), encoding="utf-8")
            first = build_payload(source)
            second = build_payload(source)
        self.assertEqual(first, second)
        self.assertEqual(1, first["meta"]["sourceRecords"])
        self.assertRegex(first["meta"]["sourceSha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(["robotic-thyroidectomy"], first["meta"]["excludedSourceIds"])
        self.assertEqual(
            {
                "hemithyroidectomy": "thyroid-lobectomy",
                "hemithyroidectomy-lobectomy": "thyroid-lobectomy",
            },
            first["meta"]["canonicalSourceIds"],
        )

    def test_unapproved_clinical_drafts_are_outside_the_static_publish_tree(self):
        self.assertFalse((ROOT / "case-prep" / "clinical-drafts").exists())

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

    def test_curated_content_overrides_conflicting_imported_content(self):
        curated = json.loads((ROOT / "case-prep" / "curated-procedures.json").read_text(encoding="utf-8"))[0]
        conflicting = dict(curated)
        conflicting["name"] = "SOURCE OVERRIDE WITH A MUCH LONGER NAME THAT MUST NOT WIN"
        conflicting["overview"] = "SOURCE OVERVIEW " * 20
        conflicting["pimpingQuestions"] = [
            {"question": curated["pimpingQuestions"][0]["question"], "answer": "SOURCE ANSWER WINS"}
        ]
        with TemporaryDirectory() as directory:
            source = Path(directory) / "procedures.json"
            source.write_text(json.dumps([conflicting]), encoding="utf-8")
            payload = build_payload(source)
        tapp = next(item for item in payload["procedures"] if item["id"] == curated["id"])
        self.assertEqual(curated["name"], tapp["name"])
        self.assertEqual(curated["overview"], tapp["overview"])
        self.assertEqual(curated["pimpingQuestions"][0]["answer"], tapp["pimpingQuestions"][0]["answer"])

    def test_importer_preserves_explicit_question_difficulty(self):
        procedure = {
            "id": "difficulty-test-procedure",
            "name": "Difficulty Test Procedure",
            "category": "General Surgery",
            "overview": "Test fixture.",
            "positioning": "Supine",
            "pimpingQuestions": [
                {"question": "Judgment question", "answer": "Answer", "level": "attending"},
                {"question": "Foundational question", "answer": "Answer", "level": "medical_student"},
            ],
        }
        with TemporaryDirectory() as directory:
            source = Path(directory) / "procedures.json"
            source.write_text(json.dumps([procedure]), encoding="utf-8")
            payload = build_payload(source)
        imported = next(item for item in payload["procedures"] if item["id"] == procedure["id"])
        self.assertEqual(["attending", "medical_student"], [q["level"] for q in imported["pimpingQuestions"]])

    def test_landing_page_exposes_search_filters_and_full_library(self):
        html = HOME.read_text(encoding="utf-8")
        for marker in [
            "235 searchable resources",
            "1,175 attending-style questions",
            "Anatomy",
            "Pitfalls",
            "Critical Steps",
            "Complete Case Prep Library",
            'data-library-search',
            'data-library-category',
            'src="/js/case-prep-library.js?v=20261020-thyroid1"',
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
            "data-question-bank",
            "data-approach-education",
            'data-question-level-filter',
            'role="group"',
            'data-procedure-retry',
            'role="alert"',
            'data-question-count role="status" aria-live="polite"',
        ]:
            self.assertIn(marker, html)

    def test_case_prep_pages_bust_the_production_stylesheet_cache(self):
        expected = '/styles/case-prep.css?v=20261020-thyroid1'
        chrome = '/js/site-chrome.js?v=20261020-thyroid1'
        for page in (ROOT / "case-prep").rglob("*.html"):
            markup = page.read_text(encoding="utf-8")
            if "/styles/case-prep.css" in markup:
                self.assertIn(expected, markup, page)
                self.assertNotIn('href="/styles/case-prep.css"', markup, page)
            if "/js/site-chrome.js" in markup:
                self.assertIn(chrome, markup, page)
                self.assertNotIn('src="/js/site-chrome.js"', markup, page)

    def test_shared_header_uses_current_conversion_factor(self):
        chrome = (ROOT / "js" / "site-chrome.js").read_text(encoding="utf-8")
        self.assertIn("CMS RVU26C July 2026", chrome)
        self.assertIn("<span>CF 33.4009</span>", chrome)
        self.assertNotIn("CF 32.3465", chrome)
        self.assertIn('js/report-widget.js?v=20261020-thyroid1', chrome)

    def test_runtime_payloads_are_split_for_fast_detail_pages(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        files = sorted(PROCEDURE_DATA.glob("*.json"))
        self.assertEqual(231, len(index["procedures"]))
        self.assertEqual(231, len(files))
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
            "html[data-theme='dark'] .library-filter-panel",
            ".library-search-row:focus-within",
            ".question-answer[hidden]{display:block!important}",
            "body #fccf-report-widget{display:flex",
            "body .fccf-report-launch{position:static!important",
            ".library-hero .case-prep-lede{display:none}",
            ".library-section-heading>p{display:none}",
        ]:
            self.assertIn(marker, css)
        self.assertNotIn("var(--forest)", css)

    def test_search_controls_are_adjacent_to_results_without_duplicate_featured_section(self):
        html = HOME.read_text(encoding="utf-8")
        library_start = html.index('id="complete-library"')
        search_start = html.index('data-library-search')
        grid_start = html.index('data-library-grid')
        self.assertLess(library_start, search_start)
        self.assertLess(search_start, grid_start)
        self.assertNotIn("library-featured", html)

    def test_detail_fetch_error_has_retry_and_clears_busy_state(self):
        js = JS.read_text(encoding="utf-8")
        for marker in [
            "showProcedureError",
            "Unable to load this prep sheet",
            "The case-prep library could not be loaded",
            'setAttribute("aria-busy", "false")',
            "data-procedure-retry",
            "() => window.location.reload()",
        ]:
            self.assertIn(marker, js)

    def test_library_controls_disable_during_loading_and_primary_failure(self):
        html = HOME.read_text(encoding="utf-8")
        js = JS.read_text(encoding="utf-8")
        self.assertIn('data-library-search type="search" disabled', html)
        self.assertIn('data-library-category disabled', html)
        self.assertIn('data-library-reset type="button" disabled', html)
        self.assertIn("setLibraryControlsDisabled", js)
        self.assertIn("setLibraryControlsDisabled(true)", js)
        self.assertIn("setLibraryControlsDisabled(false)", js)

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
