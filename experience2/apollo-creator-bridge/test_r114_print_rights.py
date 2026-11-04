"""Apollo R114 source custody and print-release contracts.

These deterministic stdlib tests are source checks, NOT a substitute for
real Chromium, axe, WordPress/Assembler, manual rights review or merchant QA.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "landing-preview.html").read_text(encoding="utf-8")
RUN = (ROOT / "qa_r113_print.py").read_text(encoding="utf-8")


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class R114PrintRights(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = Elements()
        cls.tree.feed(HTML)

    def test_unique_print_notice(self):
        self.assertEqual(sum("print-custody" in x.get("class", "").split()
                             for _, x in self.tree.tags), 1)

    def test_source_custody_not_claimed_cleared(self):
        self.assertIn("individual photograph reuse assessments remain incomplete (0/6)", HTML)
        self.assertIn("S67-19766 crew-portrait association is provisional", HTML)
        self.assertIn("not NASA-endorsed", HTML)

    def test_print_only_css(self):
        self.assertIn(".print-custody{display:none}", HTML)
        self.assertRegex(HTML, r"@media print\{\.print-custody\{display:block!important")

    def test_print_full_findings(self):
        self.assertIn(".plate[hidden]{display:block!important}", HTML)
        self.assertIn(".table-scroll{overflow:visible!important", HTML)

    def test_browser_runner_checks_print_and_screen(self):
        self.assertIn("PRINT RIGHTS NOTICE MISSING", RUN)
        self.assertIn("PRINT RIGHTS NOTICE INCOMPLETE", RUN)
        self.assertIn("print-only rights notice leaked onto screen", RUN)
        self.assertIn("page.emulate_media(media='print')", RUN)

    def test_six_references_and_no_embedded_images(self):
        self.assertEqual(sum(x.get("data-fv-photo-record") is not None
                             for _, x in self.tree.tags), 6)
        self.assertEqual(sum(x.get("id", "").startswith("photo-source-")
                             for _, x in self.tree.tags), 6)
        self.assertFalse(any(t == "img" for t, _ in self.tree.tags))

    def test_no_paid_offer_or_signup(self):
        self.assertFalse(any(t == "form" for t, _ in self.tree.tags))
        self.assertFalse(any("payhip" in x.get("href", "").lower()
                             for t, x in self.tree.tags if t == "a"))
        self.assertEqual(sum("data-fv-primary-cta" in x
                             for _, x in self.tree.tags), 1)

    def test_event_and_photo_chronology_are_separate(self):
        self.assertEqual(sum(t == "time" and "1967-01-27" in x.get("datetime", "")
                             for t, x in self.tree.tags), 3)
        self.assertIn("Photographic reference periods—not the fire timeline", HTML)

    def test_fails_open_without_javascript(self):
        self.assertIn('data-fv-lens hidden', HTML)
        self.assertIn("if(!lens||plates.length!==4)return;", HTML)
        self.assertIn("page.set_content(body", RUN)
        self.assertIn("for js in (False,True)", RUN)

    def test_no_unapproved_instrumentation(self):
        self.assertNotIn("gtag(", HTML)
        self.assertNotIn("fbq(", HTML)
        self.assertNotIn("analytics.js", HTML)
        self.assertFalse(re.search(r"(<iframe|<form|https://payhip)", HTML, re.I))


if __name__ == "__main__":
    unittest.main()
