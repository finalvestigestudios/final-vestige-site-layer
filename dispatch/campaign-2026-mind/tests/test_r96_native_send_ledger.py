"""R96: source-based tests for historical WordPress non-send reconciliation."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "r96-native-ledger"
SPEC = importlib.util.spec_from_file_location("delivery_truth_r96", PKG / "delivery_truth.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
SNAP = json.loads((PKG / "wordpress_2026-11-03.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))


class DeliveryEvidenceTests(unittest.TestCase):
    def run_inspection(self, snap=None, manifest=None):
        return MOD.inspect(copy.deepcopy(SNAP if snap is None else snap),
                           copy.deepcopy(MANIFEST if manifest is None else manifest))

    def test_current_evidence_holds_all_issues(self):
        self.assertEqual(self.run_inspection()["campaign"], "HOLD_UNSENT")

    def test_commercial_issues_03_05_double_held(self):
        self.assertEqual(self.run_inspection()["commercial_editions"],
                         {"03": "HOLD_MERCHANT", "05": "HOLD_MERCHANT"})

    def test_recent_records_not_falsely_reported_as_zero_records(self):
        self.assertEqual(self.run_inspection()["observed_recent_record_count"], 5)

    def test_five_opted_out_records_are_not_sends(self):
        a = self.run_inspection()
        self.assertEqual(a["observed_recent_opted_out_non_sends"], 5)
        self.assertEqual(a["observed_recent_successful_sends"], 0)

    def test_only_sampled_records_no_historical_zero_claim(self):
        self.assertIn("does NOT establish historical zero", MOD.render_text(self.run_inspection()))

    def test_subscriber_categories_not_added_together(self):
        a = self.run_inspection()
        self.assertTrue(a["subscriber_counts_inconsistent"])
        self.assertIsNone(a["verified_email_eligible_recipients"])

    def test_follower_categories_are_not_recipient_proof(self):
        a = self.run_inspection()
        self.assertEqual(a["follower_stats_email"], 0)
        self.assertEqual(a["follower_stats_wordpress_com"], 2)
        self.assertIsNone(a["verified_email_eligible_recipients"])

    def test_welcome_configuration_is_not_a_delivery_receipt(self):
        self.assertTrue(self.run_inspection()["welcome_configured_not_delivered"])

    def test_post_default_email_is_disabled_in_source(self):
        self.assertIs(MOD.inspect(SNAP, MANIFEST)["publish_or_send_authorized"], False)
        self.assertIs(SNAP["newsletter_settings"]["email_new_posts_by_default"], False)

    def test_received_email_still_unverified(self):
        a = self.run_inspection()
        for key in ("received_email_html_verified", "received_email_plaintext_verified",
                    "final_vestige_postal_footer_verified",
                    "functional_unsubscribe_in_received_email_verified"):
            self.assertFalse(a[key])

    def test_html_is_readable_and_explicitly_unsent(self):
        content = MOD.render_html(self.run_inspection())
        for marker in ('lang="en"', 'name="viewport"', "<main>", "<h1>",
                       "Nothing here authorizes sending", "HOLD_UNSENT", "</html>"):
            self.assertIn(marker, content)

    def test_plaintext_has_no_address_or_pii(self):
        content = MOD.render_text(self.run_inspection())
        self.assertNotIn("@", content)
        self.assertIn("UNKNOWN", content)

    def test_observed_send_event_cannot_become_success(self):
        d = copy.deepcopy(SNAP)
        d["last_five_delivery_records"][0]["status"] = "sent"
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(snap=d)

    def test_dispatched_timestamp_cannot_be_injected(self):
        d = copy.deepcopy(SNAP)
        d["last_five_delivery_records"][1]["dispatched_at"] = "2026-11-03T18:00:00Z"
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(snap=d)

    def test_recipient_total_cannot_be_invented(self):
        d = copy.deepcopy(SNAP)
        d["last_five_delivery_records"][0]["recipients"] = 2
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(snap=d)

    def test_capture_date_must_not_be_silently_refreshed(self):
        d = copy.deepcopy(SNAP)
        d["evidence_date"] = "2026-11-04T18:36:42Z"
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(snap=d)

    def test_any_real_world_proof_flip_needs_new_independent_evidence(self):
        for proof in MOD.REQUIRED_PROOFS:
            d = copy.deepcopy(SNAP)
            d["unverified_real_world_proofs"][proof] = True
            with self.subTest(proof=proof), self.assertRaises(MOD.EvidenceError):
                self.run_inspection(snap=d)

    def test_analytics_flag_must_be_whole_snapshot(self):
        d = copy.deepcopy(SNAP)
        d["follower_stats"]["partial"] = True
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(snap=d)

    def test_stored_subscriber_email_is_forbidden(self):
        d = copy.deepcopy(SNAP)
        d["audit_notes"][0] = "Address is subscriber@example.test"
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(snap=d)

    def test_stored_personal_fields_are_forbidden(self):
        d = copy.deepcopy(SNAP)
        d["follower_stats"]["buyer_name"] = "Individual shopper"
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(snap=d)

    def test_merchant_activation_cannot_change_master(self):
        m = copy.deepcopy(MANIFEST)
        m["issues"][2]["merchant_affiliate_url"] = "https://zen12.com/hnp"
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(manifest=m)

    def test_misclassified_commercial_editorial_cannot_pass(self):
        m = copy.deepcopy(MANIFEST)
        m["issues"][4]["kind"] = "editorial"
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(manifest=m)

    def test_master_scheduled_or_sent_cannot_pass(self):
        m = copy.deepcopy(MANIFEST)
        m["status"] = "APPROVED_TO_SEND"
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(manifest=m)

    def test_not_a_network_or_send_utility(self):
        source = (PKG / "delivery_truth.py").read_text(encoding="utf-8")
        for forbidden in ("import requests", "import smtplib", "urllib.request",
                          "subprocess", "wpcom_mcp_posts_create",
                          "wpcom_jetpack_newsletter", "send_email("):
            self.assertNotIn(forbidden, source)

    def test_five_delivery_records_are_exactly_named(self):
        d = copy.deepcopy(SNAP)
        d["last_five_delivery_records"][0]["post_id"] = 0
        with self.assertRaises(MOD.EvidenceError):
            self.run_inspection(snap=d)

    def test_preheader_unverified_not_promoted_to_received_evidence(self):
        a = self.run_inspection()
        self.assertFalse(a["received_email_html_verified"])
        self.assertTrue(a["native_email_excerpt_mode"])


if __name__ == "__main__":
    unittest.main()
