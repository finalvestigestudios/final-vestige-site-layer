import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "r64-authorization-first"
MANIFEST = ROOT / "manifest.json"

class AuthorizationFirstR64Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = (D / "README.md").read_text(encoding="utf-8")
        cls.requests = (D / "two-merchant-permission-requests-unsent.md").read_text(encoding="utf-8")
        cls.preview = (D / "jetpack-native-preview-and-footer-runbook.md").read_text(encoding="utf-8")
        cls.consent = (D / "consent-postal-and-purpose-audit.md").read_text(encoding="utf-8")
        cls.founder = (D / "founder-release-decisions.md").read_text(encoding="utf-8")
        cls.claims = json.loads((D / "merchant-claim-crosswalk.json").read_text(encoding="utf-8"))
        cls.metrics = json.loads((D / "privacy-safe-metrics-plan.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_01_six_original_issues(self):
        self.assertEqual(len(self.manifest["issues"]), 6)
    def test_02_editorial_four_commercial_two(self):
        self.assertEqual([i["number"] for i in self.manifest["issues"] if i["kind"]=="editorial"], [1,2,4,6])
        self.assertEqual([i["number"] for i in self.manifest["issues"] if i["kind"]=="commercial-review-pending"], [3,5])
    def test_03_all_canonicals_hold(self):
        self.assertTrue(all(i["publish_state"]=="hold" for i in self.manifest["issues"]))
    def test_04_vendor_permissions_both_denied_as_evidence(self):
        self.assertFalse(self.claims["publisher_specific_partner_approval"])
        self.assertFalse(self.claims["allowed_email_marketing_verified"])
        self.assertIsNone(self.claims["approved_tracking_url"])
    def test_05_two_distinct_offer_records(self):
        self.assertEqual([o["issue"] for o in self.claims["offers"]],[3,5])
        self.assertTrue(all(o["release"]=="HOLD_MERCHANT" for o in self.claims["offers"]))
    def test_06_no_live_guides_or_purchase_routes(self):
        self.assertTrue(all(o["guide_url"] is None and o["merchant_url"] is None for o in self.claims["offers"]))
    def test_07_false_named_product_rights(self):
        self.assertTrue(all(o["permission_email"] is False and o["creative_rights"] is False for o in self.claims["offers"]))
    def test_08_no_unsupported_effectiveness(self):
        self.assertTrue(all(len(o["claims_not_independently_proven"])>=3 for o in self.claims["offers"]))
    def test_09_specific_sales_pages(self):
        self.assertEqual(self.claims["offers"][0]["official_landing"],"https://zen12.com/hnp")
        self.assertEqual(self.claims["offers"][1]["official_landing"],"https://hypnosislive.com/mental-skills/total-focus")
    def test_10_email_permission_requests_not_sent(self):
        self.assertIn("templates ONLY, never sent", self.requests)
        self.assertIn("DRAFT_NOT_SENT", self.requests)
        self.assertIn("existing Jetpack", self.requests)
    def test_11_merchant_questions_include_critical_rights(self):
        for term in ("email", "affiliate", "refund", "tracking", "creative", "consent", "Final Vestige Studios"):
            self.assertIn(term.lower(), self.requests.lower())
    def test_12_wp_native_visual_distinct_from_received(self):
        for term in ("WP_NATIVE_VISUAL_PREVIEW", "REAL_RECEIVED_EMAIL_MIME", "VERIFIED_OPT_OUT_FUNCTION"):
            self.assertIn(term, self.preview)
    def test_13_no_test_send_approved(self):
        self.assertIn("NO EMAIL SEND AUTHORIZED", self.preview)
        self.assertIn("a second **explicit founder authorization**", self.preview)
    def test_14_excerpt_first55_rule(self):
        self.assertIn("first 55 words", self.preview)
    def test_15_true_sender_address_missing(self):
        self.assertIn("No Final Vestige qualifying postal address is verified", self.consent)
        self.assertIn("not", self.consent.lower())
    def test_16_nonadditive_wp_counts(self):
        for term in ('total **2**','confirmed **2**','unconfirmed **2**'):
            self.assertIn(term, self.consent)
    def test_17_opt_out_legal_windows(self):
        self.assertIn("30 days", self.consent)
        self.assertIn("10 business days", self.consent)
    def test_18_no_active_collection(self):
        self.assertFalse(self.metrics["data_collection_active"])
        self.assertFalse(self.metrics["merchant_outbound_links_active"])
        self.assertFalse(self.metrics["new_mailing_list"])
    def test_19_no_external_pixel_or_pii(self):
        self.assertFalse(self.metrics["external_pixel"])
        self.assertFalse(self.metrics["personal_user_ids"])
        self.assertFalse(self.metrics["subscriber_export"])
    def test_20_no_opaque_ab_metrics(self):
        self.assertIn("no defensible statistical A/B", self.metrics["small_list_rule"])
    def test_21_all_metric_observations_unknown_or_disabled(self):
        self.assertTrue(all(d["status"] in ("UNKNOWN","DISABLED","UNVERIFIED","NOT_OBSERVED") for d in self.metrics["definitions"]))
    def test_22_first_party_source_tags_disabled(self):
        self.assertEqual(self.metrics["source_tag_activation"],"DISABLED")
        self.assertEqual(len(self.metrics["permitted_coarse_source_tags"]),6)
    def test_23_separate_authorization_levels(self):
        self.assertIn("Approval of a WordPress preview does NOT approve sending a test", self.founder)
        self.assertIn("approval of one merchant does NOT approve the other", self.founder)
    def test_24_commercial_is_held(self):
        self.assertIn("ALL SIX HOLD_UNSENT", self.doc)
        self.assertIn("03/05 HOLD_MERCHANT", self.doc)
    def test_25_no_active_monetary_platform(self):
        self.assertFalse(self.metrics["new_paid_service"])
        self.assertIn("no new costs", self.founder)
    def test_26_editorial_source_identity(self):
        self.assertIn("Editorial Standards #17", self.doc)
        self.assertIn("Issue #174", self.doc)
        self.assertIn("Issue #171", self.doc)
    def test_27_no_contact_or_publish(self):
        self.assertIn("No requests were transmitted",self.requests)
        self.assertIn("No email was sent or test-sent",self.consent)
    def test_28_source_urls_present(self):
        for url in ("https://wordpress.com/support/newsletter/email-appearance/","https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business"):
            self.assertIn(url,self.doc)
    def test_29_only_parent_canonical_exists(self):
        for i in range(1,7):
            self.assertTrue(any(p.name.startswith(f"{i:02d}-") for p in (ROOT/"issues").glob("*.md")))
    def test_30_decision_packet_no_automerge(self):
        self.assertIn("Final SEND",self.founder)
        self.assertIn("NO SEND AUTHORIZED",self.founder)

if __name__=="__main__":
    unittest.main()
