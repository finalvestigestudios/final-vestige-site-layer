"""Regression against canonical and optional R44 commercial reviewer routes."""
import importlib.util
import sys
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "r44-click-quarantine" / "route_guard.py"
spec = importlib.util.spec_from_file_location("r44_route_guard", SOURCE)
guard = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = guard
spec.loader.exec_module(guard)

class R44ClickQuarantine(unittest.TestCase):
    def test_eight_existing_renditions_not_rewritten(self):
        self.assertEqual(len(guard.REVIEW_INPUTS), 8)
        self.assertTrue(all((guard.CAMPAIGN / rel).exists()
                            for rel, kind in guard.REVIEW_INPUTS.values()))

    def test_six_drafts_four_editorial_two_commercial(self):
        r = guard.current_report()
        self.assertEqual(r["mix"], {"editorial": 4, "commercial_review_pending": 2})
        self.assertEqual(r["status"], "DRAFT_UNSENT_NO_SCHEDULING")
        self.assertEqual(len(r["release"]), 6)
        self.assertTrue(all(s.startswith("HOLD_UNSENT") for s in r["release"].values()))

    def test_three_original_zen12_renditions_have_two_risky_hrefs_each(self):
        r = guard.current_report()
        self.assertEqual(r["original_commercial_routes"], 6)
        for key in ("03_canonical_markdown", "03_original_html", "03_original_gutenberg"):
            row = r["originals"][key]
            self.assertEqual(row["active_merchant_or_risky_links"], 2)
            self.assertEqual({f["reason"] for f in row["findings"]},
                             {"clickable_merchant_destination"})

    def test_original_issue_five_without_merchant_clicks(self):
        r = guard.current_report()
        for key in ("05_canonical_markdown", "05_original_html", "05_original_gutenberg"):
            self.assertEqual(r["originals"][key]["active_merchant_or_risky_links"], 0)

    def test_optional_preview_candidates_are_clean_but_not_approved(self):
        r = guard.current_report()
        self.assertEqual(len(r["optional_unapproved_candidates"]), 2)
        self.assertTrue(all(x["active_merchant_or_risky_links"] == 0
                            for x in r["optional_unapproved_candidates"].values()))
        self.assertEqual(r["release"]["03"], "HOLD_UNSENT_AND_MERCHANT")
        self.assertEqual(r["release"]["05"], "HOLD_UNSENT_AND_MERCHANT")

    def test_merchant_domains_and_subdomains(self):
        for s in ("https://zen12.com/hnp", "https://WWW.ZEN12.COM/about",
                  "//hypnosislive.com/cart", "https://affiliates.inspire3.com/"):
            with self.subTest(s=s):
                self.assertEqual(guard.classify_link(s), "clickable_merchant_destination")

    def test_no_lookalike_false_positives(self):
        for s in ("https://notzen12.com/", "https://zen12.com.bad.example/",
                  "https://finalvestige.com/zen12-guide/"):
            with self.subTest(s=s):
                self.assertIsNone(guard.classify_link(s))

    def test_redirect_wrappers(self):
        for s in ("https://finalvestige.com/go?next=https%3A%2F%2Fzen12.com%2Fhnp",
                  "/go?redirect=https%253A%252F%252Fhypnosislive.com%2F",
                  "https://finalvestige.com/out?dest=https%3A%2F%2Finspire3.com%2F"):
            with self.subTest(s=s):
                self.assertIn("redirect_to_clickable_merchant_destination", guard.classify_link(s))

    def test_active_scheme_rejection(self):
        for s in ("javAScript:alert(1)", "DATA:text/html,<script>", "vbscript:foo"):
            self.assertEqual(guard.classify_link(s), "active_non_http_scheme")

    def test_safe_evidence_citations(self):
        for s in ("https://www.bmj.com/content/324/7347/1193",
                  "https://finalvestige.com/focus/", "https://www.nasa.gov/",
                  "mailto:editor@example.invalid", "#footnote"):
            self.assertIsNone(guard.classify_link(s))

    def test_html_link_detection_not_plain_vendor_text(self):
        self.assertEqual(guard.inspect_text("<p>Source: https://zen12.com/hnp</p>", "x", "html"), [])
        links = guard.inspect_text('<a href="https://zen12.com/hnp">Seller</a>', "x", "html")
        self.assertEqual(len(links), 1)

    def test_html_entity_decoding(self):
        s = '<a href="https://finalvestige.com/go?next=https%3A%2F%2Fzen12.com&amp;x=1">Go</a>'
        self.assertEqual(len(guard.inspect_text(s, "x", "html")), 1)

    def test_markdown_links_count(self):
        s = "[seller](https://zen12.com/hnp) and [NIH](https://www.nccih.nih.gov/)"
        self.assertEqual(len(guard.inspect_text(s, "x", "md")), 1)

    def test_audience_and_permissions_never_assumed(self):
        missing = " ".join(guard.current_report()["not_verified"])
        for fragment in ("EMAIL", "consent-eligible", "postal", "founder", "buyer guides"):
            self.assertIn(fragment, missing)

    def test_safe_review_board_static_no_checkout(self):
        text = (guard.CAMPAIGN / "r44-click-quarantine" / "REVIEW_BOARD.html").read_text()
        self.assertEqual(guard.inspect_text(text, "board", "html"), [])
        self.assertIn('lang="en"', text)
        self.assertIn("HOLD_UNSENT", text)
        self.assertIn("HOLD_MERCHANT", text)
        self.assertIn('aria-disabled="true"', text)
        self.assertNotIn("<script", text.lower())
        self.assertNotIn("<form", text.lower())

    def test_canonical_all_six_keep_legal_and_send_holds(self):
        for path in sorted((guard.CAMPAIGN / "issues").glob("*.md")):
            content = path.read_text(encoding="utf-8")
            for needle in ("UNSENT DRAFT", "[[VALID_POSTAL_ADDRESS_REQUIRED]]",
                           "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"):
                self.assertIn(needle, content)

if __name__ == "__main__":
    unittest.main()
