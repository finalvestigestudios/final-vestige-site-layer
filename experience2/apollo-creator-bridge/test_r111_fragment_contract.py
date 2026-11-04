"""R111 exact-source staging contracts. Does NOT replace Playwright or WordPress acceptance."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
HTML = (ROOT / "landing-preview.html").read_text(encoding="utf8")
RUNNER = (ROOT / "qa_r108.py").read_text(encoding="utf8")
NASA_LINKS = (
    "https://www.nasa.gov/image-detail/apollo-1-crew-honored/",
    "https://www.nasa.gov/image-detail/amf-s67-15717/",
    "https://www.nasa.gov/image-detail/amf-s66-58038/",
    "https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/",
    "https://www.nasa.gov/image-detail/amf-s67-21294/",
    "https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/",
)

class R111Contract(unittest.TestCase):
    def test_one_free_primary_cta(self):
        self.assertEqual(HTML.count('data-fv-primary-cta'), 1)
        self.assertIn('href="#classroom-preview" data-fv-primary-cta', HTML)

    def test_keyboard_fragment_focus_target(self):
        self.assertEqual(HTML.count('id="classroom-preview" tabindex="-1"'), 1)
        self.assertIn('aria-labelledby="classroom-title"', HTML)
        self.assertIn('#classroom-preview:target{outline:2px solid var(--gold)', HTML)

    def test_high_contrast_focus(self):
        self.assertIn('#classroom-preview:target{outline-color:Highlight}', HTML)

    def test_source_trail_kept_beside_exercise(self):
        self.assertEqual(HTML.count('href="#source-custody">review the NASA source register</a>'), 1)

    def test_source_custody_is_accessible(self):
        self.assertIn('aria-label="Scrollable NASA source register" tabindex="0"', HTML)
        self.assertIn('SourceDrawer: media provenance and rights limitations', HTML)
        self.assertIn('INDIVIDUAL_REVIEW_REQUIRED', HTML)

    def test_known_and_limit_distinct(self):
        self.assertEqual(HTML.count('data-fv-claim="known"'), 2)
        self.assertEqual(HTML.count('data-fv-claim="limit"'), 2)

    def test_six_photo_sources_not_embedded(self):
        for link in NASA_LINKS:
            self.assertEqual(HTML.count(link), 1)
        self.assertNotIn('<img', HTML)
        self.assertNotIn('<iframe', HTML)

    def test_photo_and_event_chronology_separate(self):
        self.assertIn('ChronologyRail / ground-test event, not photo dates', HTML)
        self.assertIn('Photographic dates and the fire chronology', HTML)
        self.assertIn('provisional', HTML)

    def test_no_implied_sales_or_subscribers(self):
        self.assertNotIn('href="https://payhip.com/', HTML)
        self.assertNotIn('<form', HTML)
        self.assertNotIn('data-fv-checkout', HTML)
        self.assertIn('product hypothesis, not a listing', HTML)

    def test_keyboard_activation_asserted_in_runner(self):
        self.assertIn('primary.press("Enter")', RUNNER)
        self.assertIn('primary.tap()', RUNNER)
        self.assertIn('document.activeElement === e', RUNNER)
        self.assertIn('label + ": the classroom activity has no return source trail"', RUNNER)

    def test_budgets_unchanged(self):
        self.assertIn('0 < lcp <= 2500', RUNNER)
        self.assertIn('0 <= cls <= 0.1', RUNNER)
        self.assertIn('len(receipts) == 14 and len(metrics) == 6 and len(screen) == 6', RUNNER)

    def test_no_new_tracking_script(self):
        self.assertEqual(HTML.count('<script>'), 1)
        self.assertNotIn('analytics.js', HTML)
        self.assertNotIn('googletagmanager', HTML)

if __name__ == "__main__":
    unittest.main()
