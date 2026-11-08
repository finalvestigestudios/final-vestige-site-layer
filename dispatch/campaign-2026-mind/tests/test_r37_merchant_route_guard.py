"""R37: known merchant bypass, exact source parity, adversarial URL parsing.

These tests deliberately PASS while reporting the legacy problem as HOLD.
No payment links, analytics, WordPress, SMTP or network actions.
"""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "r37-merchant-route-proof" / "merchant_route_guard.py"
spec = importlib.util.spec_from_file_location("fv_dispatch_r37", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class R37MerchantRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.inspect(ROOT)
        cls.candidate_dir = ROOT / "r37-merchant-route-proof"

    def test_exact_campaign_six(self):
        self.assertEqual(len(self.report["legacy_risks"]), 6)

    def test_campaign_still_held(self):
        self.assertFalse(self.report["send_authorized"])
        self.assertEqual(self.report["status"], "HOLD_UNSENT_AND_MERCHANT")
        self.assertTrue(self.report["current_legacy_route_requires_editorial_repair"])

    def test_known_legacy_three_surface_bypass(self):
        self.assertEqual(self.report["existing_legacy_issue_03_seller_links_across_three_surfaces"], 6)
        row = self.report["legacy_risks"][2]
        for k in ("source", "email_preview", "gutenberg_candidate"):
            with self.subTest(surface=k):
                self.assertEqual(row[k]["merchant_route_count"], 2)

    def test_others_do_not_have_sales_hrefs(self):
        for n in (1, 2, 4, 5, 6):
            row = self.report["legacy_risks"][n-1]
            with self.subTest(issue=n):
                self.assertEqual(row["source"]["merchant_route_count"], 0)
                self.assertEqual(row["email_preview"]["merchant_route_count"], 0)

    def test_release_authorization_false_for_all(self):
        for row in self.report["legacy_risks"]:
            with self.subTest(issue=row["issue"]):
                self.assertFalse(row["send_authorized"])

    def test_no_fake_approval_on_review_candidate(self):
        self.assertFalse(self.report["merchant_permission_verified"])
        self.assertFalse(self.report["live_warmup_guide_verified"])
        self.assertFalse(self.report["founder_send_approval"])
        self.assertFalse(self.report["postal_unsubscribe_in_received_email_verified"])

    def test_no_regression_errors(self):
        self.assertEqual(self.report["regression_errors"], [])

    def test_merchant_domain_adversarial_cases(self):
        cases = [
            ("https://zen12.com/", True),
            ("https://zen12.com/about?src=mail", True),
            ("HTTPS://WWW.ZEN12.COM/path", True),
            ("http://hypnosislive.com/mental-skills/total-focus", True),
            ("https://go.inspire3.com/path", True),
            ("https://hop.clickbank.net/tracking", True),
            ("https://zen12.com.evil.example/", False),
            ("https://notzen12.com/", False),
            ("https://www.nccih.nih.gov/health/hypnosis", False),
            ("https://finalvestige.com/focus/", False),
            ("https://user@zen12.com/", True),
            ("javascript:alert(1)", False),
            ("https://xn--zen12-fake.example/", False),
            ("https://", False),
        ]
        for url, want in cases:
            with self.subTest(url=url):
                self.assertEqual(mod.is_merchant_url(url), want)

    def test_html_anchor_parser_variants(self):
        s = '<a class="a" HREF="https://zen12.com/">Buy</a><a href="https://www.nccih.nih.gov/health/hypnosis">Research</a>'
        self.assertEqual(mod.route_report(s, "html")["merchant_route_count"], 1)

    def test_plaintext_autolink_is_treated_as_route(self):
        x = "See (https://zen12.com/about)."
        self.assertEqual(mod.route_report(x, "txt")["merchant_route_count"], 1)

    def test_nonlink_merchant_label_is_not_href(self):
        s = "Zen12's public product descriptions contain seller claims."
        self.assertEqual(mod.route_report(s, "md")["merchant_route_count"], 0)

    def test_candidates_have_no_seller_route(self):
        for name, data in self.report["no_merchant_link_review_candidate"].items():
            with self.subTest(name=name):
                self.assertEqual(data["merchant_route_count"], 0)
                self.assertEqual(data["merchant_hosts"], [])

    def test_candidate_mime_safety_words(self):
        for suffix in (".md", ".html", ".txt"):
            f = self.candidate_dir / ("ISSUE_03_NO_MERCHANT_ROUTE_REVIEW"+suffix)
            t = f.read_text(encoding="utf-8")
            with self.subTest(suffix=suffix):
                self.assertIn("Zen12", t)
                self.assertIn("Commercial disclosure", t)
                self.assertIn("APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED", t)
                self.assertIn("www.nccih.nih.gov", t)
                self.assertNotIn("https://zen12.com/", t)
                self.assertNotIn("https://zen12.com/about", t)

    def test_no_false_price_or_metrics_in_candidate(self):
        s = (self.candidate_dir / "ISSUE_03_NO_MERCHANT_ROUTE_REVIEW.md").read_text(encoding="utf-8")
        for forbidden in ("$2", "$67.77", "guaranteed results", "90% conversion", "affiliate approval confirmed"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, s)

    def test_commercial_disclosure_before_prospective_cta(self):
        for suffix in (".md", ".html", ".txt"):
            s = (self.candidate_dir / ("ISSUE_03_NO_MERCHANT_ROUTE_REVIEW"+suffix)).read_text(encoding="utf-8")
            with self.subTest(suffix=suffix):
                self.assertLess(s.index("Commercial disclosure"), s.index("APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED"))

    def test_seller_source_register_separate_from_email(self):
        reg=json.loads((self.candidate_dir/"SOURCE_ROUTE_LEDGER.json").read_text(encoding="utf-8"))
        self.assertEqual(reg["source_of_truth"]["merchant_research_urls"], ["https://zen12.com/", "https://zen12.com/about", "https://zen12.com/hnp"])
        self.assertEqual(reg["email_merchandise_links_active"], 0)
        self.assertEqual(reg["candidate_route_release"], "HOLD_UNSENT_HOLD_MERCHANT")


if __name__ == "__main__":
    unittest.main()
