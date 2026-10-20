import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "js" / "report-widget.js"


class ReportWidgetAccessibilityTests(unittest.TestCase):
    def test_report_dialog_traps_focus_and_restores_the_opener(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for marker in [
            "function focusableElements",
            'event.key === "Tab"',
            "background.inert = true",
            "backgroundInertStates",
            "close.focus()",
            "launch.focus()",
        ]:
            self.assertIn(marker, source)

    def test_report_widget_is_hidden_when_printing(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("@media print{#fccf-report-widget{display:none!important}}", source)


if __name__ == "__main__":
    unittest.main()
