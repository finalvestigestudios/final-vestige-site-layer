"""Native Python regression tests against the immutable anonymous WordPress snapshot."""
import copy
import json
import pathlib
import unittest
from consent_snapshot_gate import assess

SOURCE = pathlib.Path(__file__).with_name("consent_snapshot.json")

class ConsentSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(SOURCE.read_text())

    def test_current_snapshot_fails_closed(self):
        r = assess(self.d)
        self.assertEqual(r["release"], "HOLD_UNSENT")
        self.assertFalse(r["send_allowed"])
        self.assertIsNone(r["confirmed_signup_events"])
        self.assertIsNone(r["eligible_distinct_inboxes"])

    def test_count_conflict_not_added(self):
        r = assess(self.d)
        self.assertTrue(r["newsletter_counts_not_a_partition"])
        self.assertEqual((r["newsletter_total"], r["newsletter_confirmed_aggregate"], r["newsletter_unconfirmed_aggregate"]), (3,3,2))

    def test_reader_not_email_audience(self):
        r = assess(self.d)
        self.assertEqual((r["stats_reader_followers"], r["stats_email_followers"]), (3,0))
        self.assertIsNone(r["eligible_distinct_inboxes"])

    def test_even_consistent_counts_cannot_prove_eligible_inboxes(self):
        self.d["newsletter"]["total"] = 5
        r = assess(self.d)
        self.assertFalse(r["newsletter_counts_not_a_partition"])
        self.assertIsNone(r["eligible_distinct_inboxes"])

    def test_download_exists_not_receipt(self):
        self.assertTrue(assess(self.d)["media_library_pdf_exists_not_inbox_receipt"])
        self.assertIsNone(assess(self.d)["actual_welcome_deliveries"])

    def test_platform_sendable_is_not_founder_approval(self):
        self.assertTrue(self.d["newsletter"]["can_send_platform"])
        self.assertFalse(assess(self.d)["send_allowed"])

    def test_no_personal_email_in_inputs(self):
        self.d["source"]["editor"] = "someone@example.com"
        with self.assertRaises(ValueError): assess(self.d)

    def test_no_private_email_field_even_without_value(self):
        self.d["source"]["subscriber_email"] = None
        with self.assertRaises(ValueError): assess(self.d)

    def test_no_raw_hash_that_can_expose_email(self):
        self.d["source"]["subscriber_token"] = "a"*40
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_synthetic_merchant_email_permission(self):
        self.d["acceptance_evidence"]["named_zen12_affiliate_email_permission"] = True
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_claimed_received_welcome_without_witness(self):
        self.d["fieldbook"]["actual_received_welcome"] = True
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_mismatched_pdf(self):
        self.d["fieldbook"]["media_source_url"] = "https://finalvestige.com/other.pdf"
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_not_a_pdf(self):
        self.d["fieldbook"]["media_mime"] = "image/jpeg"
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_zero_size_pdf(self):
        self.d["fieldbook"]["media_size_bytes"] = 0
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_negative_count(self):
        self.d["newsletter"]["unconfirmed"] = -1
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_float_count(self):
        self.d["followers"]["wpcom"] = 3.0
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_bool_count(self):
        self.d["newsletter"]["total"] = True
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_false_live_release(self):
        self.d["release"] = "APPROVED_SEND"
        with self.assertRaises(ValueError): assess(self.d)

    def test_rejects_unknown_extra_schema_field(self):
        self.d["subscriber_rows"] = []
        with self.assertRaises(ValueError): assess(self.d)

    def test_json_output_no_subscriber_identifiers(self):
        output = json.dumps(assess(self.d))
        self.assertNotIn("@", output)
        self.assertNotIn("subscriber_token", output)

if __name__ == "__main__": unittest.main()
