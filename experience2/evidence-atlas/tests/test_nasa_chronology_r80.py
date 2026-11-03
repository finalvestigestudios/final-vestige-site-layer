"""R80: source-photo dates must not visually invent a chronology for unknown days."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from build_nasa_gallery_r79 import AUDIT, validate, render_chronology, render_html


class RailParser(HTMLParser):
    """Identify link membership in the dated list versus the unplaced note."""
    def __init__(self):
        super().__init__()
        self.ordered = 0
        self.unplaced = 0
        self.dated_links = []
        self.unplaced_links = []
        self.date_values = []
        self.nested_dates = []
    def handle_starttag(self, name, attrs):
        a = dict(attrs)
        if name == "ol": self.ordered += 1
        if name == "aside" and a.get("class") == "rail-unplaced": self.unplaced += 1
        if name == "time":
            if self.ordered: self.date_values.append(a.get("datetime"))
            if self.unplaced: self.nested_dates.append(a.get("datetime"))
        if name == "a" and a.get("href", "").startswith("#record-"):
            if self.ordered: self.dated_links.append(a["href"])
            if self.unplaced: self.unplaced_links.append(a["href"])
    def handle_endtag(self, name):
        if name == "ol": self.ordered -= 1
        if name == "aside" and self.unplaced: self.unplaced -= 1


class SourceChronologyCertainty(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = validate(ROOT)

    def test_day_level_dates_are_real_sorted_distinct_milestones(self):
        rail, unresolved = render_chronology(self.rows)
        dom = RailParser()
        dom.feed("<ol>" + rail + "</ol>" + unresolved)
        self.assertEqual(dom.date_values, ["1966-10-18", "1967-01-03", "1967-01-28", "2017-01-24"])
        self.assertEqual(len(dom.date_values), 4)
        self.assertEqual(dom.dated_links, ["#record-03", "#record-02", "#record-05", "#record-04", "#record-06"])
        self.assertEqual(dom.unplaced_links, ["#record-01"])
        self.assertEqual(dom.nested_dates, ["1967-01"])

    def test_unknown_day_cannot_be_between_known_days(self):
        rail, unplaced = render_chronology(self.rows)
        self.assertNotIn("record-01", rail)
        self.assertIn("before or after", unplaced)
        self.assertIn("provisional catalog association", unplaced)
        self.assertIn("Date unresolved within the month", unplaced)

    def test_same_day_2017_tributes_share_one_milestone(self):
        rail, _ = render_chronology(self.rows)
        self.assertEqual(rail.count('datetime="2017-01-24"'), 1)
        self.assertIn('href="#record-04"', rail)
        self.assertIn('href="#record-06"', rail)
        self.assertEqual(rail.count('class="rail-event"'), 4)

    def test_bad_precision_or_inconsistent_day_label_fails_closed(self):
        for mutate in (
            lambda r: r[0].__setitem__("date_precision", "DAY"),
            lambda r: r[0].__setitem__("taken_date", "1967-01-27"),
            lambda r: r[5].__setitem__("date_display", "January 25, 2017"),
            lambda r: r[2].__setitem__("taken_date", "1966-10"),
            lambda r: r[1].__setitem__("date_precision", "MONTH_ONLY"),
            lambda r: r.pop(4),
        ):
            rows = copy.deepcopy(self.rows)
            mutate(rows)
            with self.subTest(mutate=repr(mutate)), self.assertRaises(ValueError):
                render_chronology(rows)

    def test_rendered_page_retains_nojs_custody_and_certain_links(self):
        page = render_html(ROOT)
        self.assertEqual(page.count('class="card'), 6)
        self.assertEqual(page.count('class="source-drawer"'), 6)
        self.assertEqual(page.count('class="rail-event"'), 4)
        self.assertIn('aria-labelledby="rail-unplaced-title"', page)
        self.assertNotIn("<img", page)
        self.assertNotIn("<script", page)
        self.assertNotIn("data-lat=", page)
        self.assertNotIn("data-geo-edge=", page)
        self.assertIn("All six photographs require individual reuse review", page)
        self.assertIn("photographs taken on the same day", page.lower())

    def test_original_source_claims_not_reclassified(self):
        rows = json.loads((ROOT / AUDIT).read_text())["records"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0]["date_precision"], "MONTH_ONLY")
        self.assertIsNone(rows[0]["nasa_page_pia"])
        self.assertTrue(all(r["reuse_status"] == "INDIVIDUAL_REVIEW_REQUIRED" for r in rows))


if __name__ == "__main__":
    unittest.main()
