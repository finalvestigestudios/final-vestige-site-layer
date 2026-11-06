"""R170 zero-send alternative edition source and release-hold tests.
Run in a trusted clone: python -I -m unittest discover -s dispatch/campaign-2026-mind/r170/tests -v
No network, subscriber interaction or WordPress write performed.
"""
import json
import pathlib
import re
import unittest
from urllib.parse import urlsplit

HERE = pathlib.Path(__file__).resolve().parents[1]
CAMPAIGN = HERE.parent

class R170ReviewChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = (HERE / "issue02-franklin-alternative.md").read_text(encoding="utf-8")
        cls.txt = (HERE / "issue02-franklin-alternative.txt").read_text(encoding="utf-8")
        cls.html = (HERE / "issue02-offline-review.html").read_text(encoding="utf-8")
        cls.ev = json.loads((HERE / "evidence-and-release-hold.json").read_text(encoding="utf-8"))
        cls.original = json.loads((CAMPAIGN / "manifest.json").read_text(encoding="utf-8"))

    def test_pilot_keeps_four_two_mix(self):
        self.assertEqual([sum(x["kind"] == "editorial" for x in self.original["issues"]), sum(x["kind"] == "commercial-review-pending" for x in self.original["issues"])], [4, 2])
        self.assertEqual(self.original["status"], "DRAFT_UNSENT_NO_SCHEDULING")

    def test_alternative_never_overrides_approved(self):
        self.assertFalse(self.ev["original_issue02_replacement_approved"])
        self.assertEqual(self.ev["state"], "HOLD_UNSENT_REVIEW_ONLY")
        self.assertEqual(self.ev["campaign_issue"], "02")

    def test_all_formats_have_hold(self):
        for body in (self.md, self.txt, self.html):
            self.assertIn("HOLD_UNSENT", body)

    def test_every_format_requires_actual_legal_footer(self):
        for body in (self.md, self.txt, self.html):
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", body)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", body)

    def test_no_personal_or_live_tracking_links(self):
        for body in (self.md, self.txt, self.html):
            self.assertNotIn("utm_", body.lower())
            self.assertNotIn("awin1.com", body.lower())
            self.assertNotIn("affiliates.inspire3", body.lower())

    def test_html_contains_no_executable_assets(self):
        self.assertNotIn("<script", self.html.lower())
        self.assertNotIn("<iframe", self.html.lower())
        self.assertNotIn("onerror=", self.html.lower())
        self.assertNotIn("<img", self.html.lower())

    def test_html_has_accessible_heading_and_layout(self):
        self.assertIn('lang="en"', self.html)
        self.assertIn("<h1", self.html)
        self.assertIn('role="presentation"', self.html)
        self.assertIn('width="100%"', self.html)
        self.assertIn("max-width:600px", self.html)

    def test_exact_article_destination_all_formats(self):
        url = "https://finalvestige.com/2026/11/02/mesmerism/"
        for body in (self.md, self.txt, self.html):
            self.assertEqual(body.count(url), 1)
        self.assertEqual(urlsplit(url).hostname, "finalvestige.com")

    def test_seller_not_activated(self):
        self.assertEqual(self.ev["merchant_gate"]["zen12_email_permission"], "UNVERIFIED")
        self.assertEqual(self.ev["merchant_gate"]["hypnosislive_email_permission"], "UNVERIFIED")
        self.assertEqual(self.ev["merchant_gate"]["authorized_earning_url"], "UNVERIFIED")

    def test_full_archival_sources_all_formats(self):
        for body in (self.md, self.txt, self.html):
            self.assertIn("https://wellcomecollection.org/works/enhgscmf", body)
            self.assertIn("https://www.gutenberg.org/files/78413/78413-h/78413-h.htm", body)

    def test_subject_precise_and_compact(self):
        self.assertIn("The boy who fainted at the wrong tree", self.md)
        self.assertIn("The boy who fainted at the wrong tree", self.txt)
        self.assertIn("The boy who fainted at the wrong tree", self.html)

    def test_preheader_is_supported(self):
        phrase = "In 1784, a royal commission tested what a magnetic force was supposed to do."
        self.assertIn(phrase, self.md)
        self.assertIn(phrase, self.txt)
        self.assertIn(phrase, self.html)

    def test_primary_claim_has_specific_scope_limit(self):
        for body in (self.md, self.txt):
            self.assertIn("Charles Deslon", body)
            self.assertIn("The commission did not conduct", body)
            self.assertIn("contemporary meditation or hypnosis", body)

    def test_no_exaggerated_therapeutic_claims(self):
        copy = self.md.lower()
        for banned in ("cure", "proven to reprogram", "guaranteed results", "will transform your mind", "refund available", "buy now"):
            self.assertNotIn(banned, copy)

    def test_fresh_provider_count_is_not_inflated(self):
        status = self.ev["current_wordpress_observation"]
        self.assertEqual(status["reported_total"], 3)
        self.assertEqual(status["reported_confirmed"], 3)
        self.assertEqual(status["reported_unconfirmed"], 2)
        self.assertEqual(status["email_eligible_recipients"], "UNKNOWN")
        self.assertEqual(status["welcome_delivered"], "UNKNOWN")

    def test_focus_false_success_not_counted_as_confirmed(self):
        state = self.ev["critical_focus_blocker"]
        self.assertTrue(state["client_only_subscribe_param_reveals_gift"])
        self.assertFalse(state["provider_verified_signup_from_ui"])

    def test_active_conversion_metrics_not_invented(self):
        outcome = self.ev["commercial_result"]
        self.assertEqual(outcome["verified_paid_orders"], "UNKNOWN")
        self.assertEqual(outcome["realized_net_per_1000"], "NOT_COMPUTABLE")

    def test_approval_is_not_derived_from_tests(self):
        self.assertFalse(self.ev["release_checks"]["final_founder_approval"])
        self.assertFalse(self.ev["release_checks"]["genuine_jetpack_email_preview"])
        self.assertFalse(self.ev["release_checks"]["working_received_email_unsubscribe"])
        self.assertTrue(self.ev["no_send_or_live_changes"])

if __name__ == "__main__":
    unittest.main()
