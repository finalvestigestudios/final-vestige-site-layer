import unittest
from dataclasses import replace
from subscriber_truth import Snapshot, classify, commercial_release


BASE = Snapshot(total=3, confirmed=3, unconfirmed=2, wpcom_followers=3,
                direct_email_followers=0, auto_send=False, newsletter_enabled=True)


class AudienceTruthTests(unittest.TestCase):
    def test_real_summary_is_not_audience_proof(self):
        d = classify(BASE)
        self.assertTrue(d["classification_overlap_or_denominator_mismatch"])
        self.assertIsNone(d["eligible_inboxes"])
        self.assertFalse(d["safe_to_send"])

    def test_no_addition_of_overlapping_counts(self):
        self.assertEqual(classify(BASE)["total_displayed"], 3)
        self.assertNotEqual(classify(BASE)["total_displayed"], BASE.confirmed + BASE.unconfirmed)

    def test_wpcom_followers_are_not_recipient_proof(self):
        self.assertFalse(classify(BASE)["email_eligibility_verified"])

    def test_zero_email_followers_is_not_zero_eligible_inboxes(self):
        self.assertIsNone(classify(BASE)["eligible_inboxes"])

    def test_boolean_rejected_as_integer(self):
        with self.assertRaises(ValueError):
            classify(replace(BASE, total=True))

    def test_negative_summary_rejected(self):
        with self.assertRaises(ValueError):
            classify(replace(BASE, confirmed=-1))

    def test_unattributed_eligible_count_rejected(self):
        with self.assertRaises(ValueError):
            classify(replace(BASE, eligible_inboxes=3))

    def test_proof_without_count_rejected(self):
        with self.assertRaises(ValueError):
            classify(replace(BASE, eligible_source="provider_eligibility_attestation"))

    def test_private_provider_count_not_release(self):
        d = classify(replace(BASE, eligible_inboxes=2,
                             eligible_source="provider_eligibility_attestation"))
        self.assertTrue(d["email_eligibility_verified"])
        self.assertFalse(d["safe_to_send"])

    def test_auto_send_drift_not_release(self):
        self.assertFalse(classify(replace(BASE, auto_send=True))["safe_to_send"])

    def test_bool_toggle_rejected(self):
        with self.assertRaises(ValueError):
            classify(replace(BASE, auto_send="false"))

    def test_empty_proofs_hold(self):
        d = commercial_release({})
        self.assertEqual(len(d["missing"]), 12)
        self.assertFalse(d["safe_to_send"])

    def test_truthy_string_cannot_fake_receipt(self):
        d = commercial_release({"email_permission": {"verified": "true", "opaque_proof_id": "a-merchant-proof-id"}})
        self.assertIn("email_permission", d["missing"])

    def test_short_or_unanchored_receipt_cannot_pass(self):
        d = commercial_release({"email_permission": {"verified": True, "opaque_proof_id": "yes"}})
        self.assertIn("email_permission", d["missing"])

    def test_all_synthetic_proofs_still_require_founder_release(self):
        keys = commercial_release({})["missing"]
        d = commercial_release({k: {"verified": True, "opaque_proof_id": "synthetic-proof-id"} for k in keys})
        self.assertTrue(d["evidence_complete"])
        self.assertFalse(d["safe_to_send"])
        self.assertEqual(d["decision"], "FOUNDER_RELEASE_REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
