"""R40 no-network reviewer-board integrity, excerpt parity and accessibility guard."""
import importlib.util
import re
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parents[1] / "r40-native-post-proof"
BOARD = DIR / "REVIEW_BOARD.html"
MODULE = DIR / "native_post_field_gate.py"
spec = importlib.util.spec_from_file_location("r40_board_source_gate", MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class BoardIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = BOARD.read_text(encoding="utf-8")
        cls.entries = gate.packets()

    def test_board_six_expected_articles(self):
        self.assertEqual(len(re.findall(r"<article class=\"card\"", self.page)), 6)

    def test_exact_six_proposed_excerpts(self):
        for issue in self.entries:
            self.assertIn(issue["custom_excerpt_required"], self.page)

    def test_exact_six_native_subjects(self):
        for issue in self.entries:
            self.assertIn(issue["post_title_required_as_native_subject"], self.page)

    def test_risk_explicit_in_review_board(self):
        self.assertIn("HOLD_UNSENT", self.page)
        self.assertIn("HOLD_MERCHANT", self.page)
        self.assertIn("not a Jetpack preview", self.page)

    def test_no_script_or_asset_loader(self):
        self.assertNotRegex(self.page, r"<script\b|<iframe\b|<img\b|<link\b[^>]+stylesheet")

    def test_no_live_vendor_links_even_from_citations(self):
        self.assertNotRegex(self.page, r"https?://(?:[a-z0-9-]+\.)*(?:zen12\.com|hypnosislive\.com)")

    def test_no_unapproved_affiliate_tracker(self):
        self.assertNotRegex(self.page, r"hop\.clickbank\.net|affiliates\.inspire3\.com")

    def test_mobile_and_reduced_motion_care(self):
        self.assertIn('name="viewport"', self.page)
        self.assertIn("@media(max-width:650px)", self.page)
        self.assertIn("prefers-reduced-motion", self.page)

    def test_accessibility_landmarks(self):
        self.assertIn('<html lang="en">', self.page)
        self.assertIn("<main>", self.page)
        self.assertIn("<h1>", self.page)
        self.assertIn('role="status"', self.page)
        self.assertIn('scope="col"', self.page)

    def test_no_test_email_or_subscriber_identifier(self):
        self.assertNotRegex(self.page, r"mailto:|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        self.assertNotIn("utm_source=", self.page)

    def test_no_placeholders_in_reader_facing_excerpt(self):
        for x in self.entries:
            self.assertNotIn("[[", x["custom_excerpt_required"])
            self.assertNotIn("DO NOT PUBLISH", x["custom_excerpt_required"])

    def test_explicit_proof_limitations(self):
        for phrase in ("UNVERIFIED", "Excerpt", "custom excerpt",
                       "first screen", "actual", "postal address"):
            self.assertIn(phrase.lower(), self.page.lower())


if __name__ == "__main__":
    unittest.main()
