"""R87 tests: preserve consent truth and never invent send authority."""
import copy
import importlib.util
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1] / "r87-consent-consistency"
SPEC = importlib.util.spec_from_file_location("r87_audit", HERE / "audit_consent_surfaces.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
BASE = json.loads((HERE / "snapshot.json").read_text(encoding="utf-8"))


class ConsentTruth(unittest.TestCase):
    def setUp(self):
        self.doc = copy.deepcopy(BASE)

    def run_audit(self):
        return MODULE.audit(self.doc)

    def reject(self):
        with self.assertRaises(MODULE.UnsafeSnapshot):
            self.run_audit()

    def test_snapshot_is_readonly(self):
        self.assertTrue(self.doc["readonly"])

    def test_detects_real_live_consent_mismatch(self):
        self.assertEqual(self.run_audit()["consent_parity"], "MISMATCH_REQUIRES_COPY_REVIEW")

    def test_remains_hold_with_valid_snapshot(self):
        self.assertEqual(self.run_audit()["decision"], "HOLD_UNSENT")

    def test_merchant_slots_stay_blocked(self):
        self.assertEqual(self.run_audit()["offer_03_05"], "HOLD_MERCHANT")

    def test_aggregate_conflict_not_four_people(self):
        self.assertEqual(self.run_audit()["audience"], "UNRECONCILED_DO_NOT_INFER_RECIPIENTS")

    def test_opted_out_posts_not_all_time_zero(self):
        self.assertIn("NOT_ALL_TIME_PROOF", self.run_audit()["delivery_history"])

    def test_no_email_default_is_not_interlock(self):
        self.assertEqual(self.run_audit()["post_send_default"], "OFF_NOT_A_GLOBAL_INTERLOCK")

    def test_welcome_not_a_received_message(self):
        self.assertEqual(self.run_audit()["welcome"], "CONFIGURED_NOT_RECEIPT_PROVEN")

    def test_genuine_received_mail_missing(self):
        self.assertEqual(self.run_audit()["email_render"], "NOT_A_GENUINE_RECEIVED_EMAIL")

    def test_cannot_promote_even_if_flags_forged_true(self):
        self.doc["campaign"]["founder_final_send_approval"] = True
        self.doc["campaign"]["merchant_email_channel_authorization_verified"] = True
        self.assertEqual(self.run_audit()["decision"], "HOLD_UNSENT")

    def test_rejects_wrong_page_id(self):
        self.doc["first_party_evidence"]["dispatch"]["page_id"] = 1579
        self.reject()

    def test_rejects_page_unpublished(self):
        self.doc["first_party_evidence"]["focus"]["status"] = "draft"
        self.reject()

    def test_rejects_new_site(self):
        self.doc["site"] = "someone-else.com"
        self.reject()

    def test_rejects_snapshot_write(self):
        self.doc["readonly"] = False
        self.reject()

    def test_rejects_extra_unexpected_top_level(self):
        self.doc["subscriber_emails"] = ["hidden"]
        self.reject()

    def test_rejects_email_in_page_copy(self):
        self.doc["public_consent_copy"]["focus"] = "privateperson@example.test"
        self.reject()

    def test_rejects_private_affiliate_url(self):
        self.doc["private_affiliate_url"] = "https://vendor.example/test"
        self.reject()

    def test_rejects_pii_nested(self):
        self.doc["campaign"]["access_token"] = "secret"
        self.reject()

    def test_rejects_tracking_query(self):
        self.doc["sources"].append("https://example.com/?email=someone")
        self.reject()

    def test_rejects_boolean_as_aggregate(self):
        self.doc["audience"]["newsletter_total"] = True
        self.reject()

    def test_rejects_negative_count(self):
        self.doc["audience"]["newsletter_total"] = -1
        self.reject()

    def test_rejects_string_false_booleans(self):
        self.doc["campaign"]["founder_final_send_approval"] = "false"
        self.reject()

    def test_rejects_malformed_issue_mix(self):
        self.doc["campaign"]["commercial_reservations"] = [2, 5]
        self.reject()

    def test_rejects_invalid_send_history(self):
        self.doc["recent_posts"]["statuses"].append("sent")
        self.reject()

    def test_rejects_duplicate_post_ids(self):
        self.doc["recent_posts"]["post_ids"][-1] = 1926
        self.reject()

    def test_rejects_unknown_send_status(self):
        self.doc["recent_posts"]["statuses"][0] = "mysteriously_emailed"
        self.reject()

    def test_rejects_wrong_welcome_format(self):
        self.doc["jetpack"]["email_content_format"] = "magic"
        self.reject()

    def test_rejects_missing_editorial_source(self):
        del self.doc["first_party_evidence"]["editorial_standards"]
        self.reject()

    def test_distinguishes_copy_parity_from_consent_verification(self):
        self.doc["first_party_evidence"]["dispatch"]["shows_affiliate_expectations"] = True
        self.doc["public_consent_copy"]["dispatch"] = "Some emails may earn Final Vestige a commission."
        self.assertIn("NOT_PROOF_OF_CONSENT", self.run_audit()["consent_parity"])

    def test_even_all_true_cannot_send(self):
        for field in ("marketing_authorization_verified", "merchant_email_channel_authorization_verified",
                      "approved_commercial_guides_live", "founder_final_send_approval"):
            self.doc["campaign"][field] = True
        for field in ("actual_welcome_receipt_verified", "verified_jetpack_received_eml",
                      "verified_sender_postal_in_received_email", "verified_unsubscribe_functionality"):
            self.doc["jetpack"][field] = True
        self.doc["audience"]["classification_conflict"] = False
        self.doc["audience"]["recipient_count_verified"] = True
        self.assertEqual(self.run_audit()["decision"], "HOLD_UNSENT")

    def test_sensitive_person_data_never_in_json(self):
        text = json.dumps(self.run_audit())
        self.assertNotIn("@", text)
        self.assertNotIn("http", text)


if __name__ == "__main__":
    unittest.main()
