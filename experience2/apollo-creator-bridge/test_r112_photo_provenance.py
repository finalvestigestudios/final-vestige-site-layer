"""R112 staging source contracts (not a substitute for browser, axe or WP tests)."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

HTML = (Path(__file__).parent / "landing-preview.html").read_text(encoding="utf-8")
HTTP_RUNNER = (Path(__file__).parent / "qa_r108.py").read_text(encoding="utf-8")


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.records = {}
        self.rail_links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "tr" and a.get("id", "").startswith("photo-source-"):
            self.records[a["id"]] = a
        if tag == "a":
            if "data-fv-photo-record" in a:
                self.rail_links.append(a)


class PhotoPeriodContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dom = Collector()
        cls.dom.feed(HTML)

    def test_six_source_row_anchors_unique(self):
        self.assertEqual(len(self.dom.ids), len(set(self.dom.ids)))
        self.assertEqual(set(self.dom.records), {f"photo-source-{n:02}" for n in range(1, 7)})
        for row in self.dom.records.values():
            self.assertEqual(row.get("tabindex"), "-1")

    def test_six_photo_jumps_are_same_page_and_not_tracking(self):
        self.assertEqual(len(self.dom.rail_links), 6)
        for link in self.dom.rail_links:
            record = link["data-fv-photo-record"]
            self.assertRegex(record, r"^0[1-6]$")
            self.assertEqual(link["href"], f"#photo-source-{record}")
            self.assertIn(link["href"][1:], self.dom.records)

    def test_no_false_photo_ordering_or_rights_attestation(self):
        self.assertIn("Photographic reference periods—not the fire timeline", HTML)
        self.assertIn("the crew portrait's January day and catalog association remain uncertain", HTML)
        self.assertIn("INDIVIDUAL_REVIEW_REQUIRED", HTML)
        self.assertIn("0/6", HTML)
        self.assertEqual(HTML.count('data-fv-primary-cta'), 1)
        self.assertEqual(HTML.count("<script>"), 1)
        self.assertNotIn("<img", HTML)
        self.assertNotIn("<form", HTML)

    def test_records_match_pinned_custody_dates(self):
        for date in ("Oct 18, 1966", "Jan 3, 1967", "Jan 28, 1967", "Jan 24, 2017"):
            self.assertIn(date, HTML)
        self.assertIn("Jan 1967; day unconfirmed", HTML)
        self.assertIn("S67-19766 (provisional)", HTML)

    def test_event_and_photo_chronologies_disambiguated(self):
        self.assertEqual(HTML.count('datetime="1967-01-27T23:31:'), 3)
        self.assertIn("not</strong> a measured ignition-to-death interval", HTML)
        self.assertIn("The time of ignition was not established", HTML)
        self.assertIn('aria-labelledby="photo-period-heading"', HTML)

    def test_keyboard_focus_and_high_contrast_table(self):
        self.assertIn(".table-scroll:focus-visible{outline:3px", HTML)
        self.assertIn(".table-scroll tr:target{outline:3px", HTML)
        self.assertIn(".table-scroll tr:target,.table-scroll:focus-visible{outline-color:Highlight}", HTML)

    def test_real_http_runner_exercises_r112_without_js(self):
        self.assertIn("rail.count() == 6", HTTP_RUNNER)
        self.assertIn("period_link.press(\"Enter\")", HTTP_RUNNER)
        self.assertIn("period_link.tap()", HTTP_RUNNER)
        self.assertIn("location.hash === '#photo-source-05'", HTTP_RUNNER)
        self.assertIn("for js in (False, True)", HTTP_RUNNER)
        self.assertIn("0 < lcp <= 2500", HTTP_RUNNER)
        self.assertIn("0 <= cls <= 0.1", HTTP_RUNNER)

    def test_commercial_boundary_unchanged(self):
        self.assertNotIn('payhip.com', HTML.lower())
        self.assertIn("product hypothesis, not a listing", HTML)
        self.assertIn("not affiliated with or endorsed by NASA", HTML)


if __name__ == "__main__":
    unittest.main()
