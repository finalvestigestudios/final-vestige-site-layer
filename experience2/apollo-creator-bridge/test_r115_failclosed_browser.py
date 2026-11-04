"""R115 contract tests for actual staging source; do not claim browser acceptance.

Run with: python -I -m unittest discover -s experience2/apollo-creator-bridge -p 'test_r115_failclosed_browser.py' -v
These source contracts must supplement, not replace, real Chromium and axe-core.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

BASE = Path(__file__).resolve().parent
HTML = (BASE / "landing-preview.html").read_text(encoding="utf-8")
RUN = (BASE / "qa_r113_print.py").read_text(encoding="utf-8")


class DOM(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class R115Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dom = DOM()
        cls.dom.feed(HTML)

    def test_one_free_classroom_action(self):
        self.assertEqual(sum("data-fv-primary-cta" in a for _, a in self.dom.tags), 1)
        self.assertIn('href="#classroom-preview" data-fv-primary-cta', HTML)
        self.assertIn('id="classroom-preview" tabindex="-1"', HTML)

    def test_usable_focus_after_fragment_navigation(self):
        self.assertIn("#classroom-preview:target,#classroom-preview:focus", HTML)
        self.assertIn(".table-scroll tr:target,.table-scroll tr:focus", HTML)
        self.assertIn("document.activeElement===e", RUN)

    def test_source_rows_remain_keyboard_targets(self):
        rows = [a for t, a in self.dom.tags if t == "tr" and a.get("id", "").startswith("photo-source-")]
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(a.get("tabindex") == "-1" for a in rows))

    def test_six_nonembedded_nasa_source_references(self):
        links = [a for t, a in self.dom.tags if t == "a" and a.get("data-fv-photo-record")]
        self.assertEqual(len(links), 6)
        self.assertFalse(any(t == "img" for t, _ in self.dom.tags))
        self.assertIn("S67-19766 (provisional)", HTML)

    def test_no_unapproved_commercial_capture(self):
        self.assertFalse(any(t in {"form", "iframe"} for t, _ in self.dom.tags))
        self.assertNotIn("payhip", HTML.lower())
        self.assertFalse(re.search(r"gtag\\(|fbq\\(|analytics\\.js", HTML, re.I))

    def test_print_custody_is_preserved(self):
        self.assertIn("photograph reuse assessments remain incomplete (0/6)", HTML)
        self.assertIn("S67-19766 crew-portrait association is provisional", HTML)
        self.assertIn("https://www.nasa.gov/nasa-brand-center/", HTML)
        self.assertIn(".print-custody{display:block!important", HTML)
        self.assertIn(".plate[hidden]{display:block!important}", HTML)

    def test_no_js_and_enhancement_fail_open(self):
        self.assertIn("data-fv-lens hidden", HTML)
        self.assertIn("!lens.querySelector('[data-fv-lens-status]')", HTML)
        self.assertIn("for js in (False,True)", RUN)

    def test_width_matrix_is_complete(self):
        self.assertIn("WIDTHS=(320,360,390,768,1024,1440,1920)", RUN)
        self.assertIn("len(record['modes'])==14", RUN)

    def test_touch_and_destination_check_are_real_browser_actions(self):
        self.assertIn("has_touch=True", RUN)
        self.assertIn(".tap()", RUN)
        self.assertIn("real touch activation did not reach classroom", RUN)
        self.assertIn("classroom destination did not receive focus", RUN)

    def test_reduced_motion_and_no_page_wide_overflow(self):
        self.assertIn("reduced_motion='reduce'", RUN)
        self.assertIn("document.documentElement.scrollWidth<=innerWidth+1", RUN)
        self.assertIn("reduced-motion scroll override missing", RUN)

    def test_axe_is_mandatory_for_a_green_receipt(self):
        self.assertIn("AXE_BUNDLE_REQUIRED", RUN)
        self.assertIn("len(record['axe_scans'])==4", RUN)
        self.assertIn("not axe or not axe.is_file()", RUN)
        self.assertNotIn("if axe and axe.is_file():", RUN)

    def test_accessibility_checks_two_widths_two_states(self):
        self.assertIn("for width in (390,1440):", RUN)
        self.assertIn("for state in ('all','limit'):", RUN)
        self.assertIn("axe.run(document)", RUN)
        self.assertIn("require(not violations", RUN)

    def test_perf_not_relabelled_field_vitals(self):
        self.assertIn("for trial in (1,2,3):", RUN)
        self.assertIn("'lab_only':True", RUN)
        self.assertIn("lcp<=2500 and cls<=0.1", RUN)

    def test_receipt_only_green_with_evidence(self):
        self.assertIn("len(record['screenshots'])==2", RUN)
        self.assertIn("record['pdf'] is not None", RUN)
        self.assertIn("record['complete']=True", RUN)
        self.assertIn("record['failure_code']=record['failure_code'] or 'ACCEPTANCE_FAILED'", RUN)


if __name__ == "__main__":
    unittest.main()
