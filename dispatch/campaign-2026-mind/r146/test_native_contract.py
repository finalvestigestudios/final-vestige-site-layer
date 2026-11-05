"""Dependency-free adversarial tests; no live WordPress/merchant/email calls."""
import copy
import json
import unittest
from pathlib import Path
from native_contract import audit, ContractError

SOURCE = Path(__file__).with_name("native_contract.json")


def fixture():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


class NativeDeliveryContractTests(unittest.TestCase):
    def test_report_is_explicitly_unsent(self):
        r = audit(fixture())
        self.assertEqual(r["status"], "HOLD_UNSENT")
        self.assertFalse(r["sent_email"])
        self.assertFalse(r["wrote_wordpress"])

    def test_six_distinct_issues(self):
        r = audit(fixture())
        self.assertEqual([i["number"] for i in r["issues"]], ["01", "02", "03", "04", "05", "06"])

    def test_founded_4_2_allocation(self):
        r = audit(fixture())
        self.assertEqual([i["kind"] for i in r["issues"]].count("editorial"), 4)
        self.assertEqual([i["kind"] for i in r["issues"]].count("commercial"), 2)

    def test_commercial_stays_disabled(self):
        self.assertEqual([i["number"] for i in audit(fixture())["issues"] if i["merchant_decision"] == "HOLD_MERCHANT"], ["03", "05"])

    def test_no_synthetic_native_approval(self):
        s = fixture()
        for field in s["actual_delivery"]: s["actual_delivery"][field] = True
        for field in ("counter_sets_reconciled", "email_eligible_verified", "consent_provenance_verified"):
            s["subscribers"][field] = True
        s["subscribers"]["provider_eligible_count"] = 2
        s["welcome"]["real_received_welcome_verified"] = True
        s["welcome"]["live_pdf_http_and_pagecount_verified"] = True
        self.assertTrue(all(x["release_decision"] == "HOLD_UNSENT" for x in audit(s)["issues"]))

    def test_overlap_does_not_sum_counts(self):
        r = audit(fixture())
        self.assertIsNone(r["capability"]["email_eligible_recipient_count"])

    def test_provider_verified_count_required(self):
        s = fixture()
        for field in ("counter_sets_reconciled", "email_eligible_verified", "consent_provenance_verified"):
            s["subscribers"][field] = True
        self.assertIsNone(audit(s)["capability"]["email_eligible_recipient_count"])
        s["subscribers"]["provider_eligible_count"] = 2
        self.assertEqual(audit(s)["capability"]["email_eligible_recipient_count"], 2)

    def test_string_flags_are_never_proof(self):
        s = fixture()
        s["actual_delivery"]["native_visual_preview_verified"] = "true"
        self.assertIn("REAL_JETPACK_MIME_AND_LAYOUT_UNVERIFIED", audit(s)["global_blockers"])

    def test_consent_cannot_be_just_a_success_screen(self):
        s = fixture()
        s["subscribers"]["success_page_seen"] = True
        self.assertIsNone(audit(s)["capability"]["email_eligible_recipient_count"])

    def test_landing_does_not_equal_purchase(self):
        self.assertIsNone(audit(fixture())["capability"]["independent_paid_orders"])

    def test_revenue_unknown_not_zero(self):
        self.assertIsNone(audit(fixture())["capability"]["net_revenue_per_1000_qualified_human_sessions"])

    def test_current_mode_full(self):
        self.assertEqual(audit(fixture())["capability"]["current_content_format"], "full")

    def test_reply_to_no_reply(self):
        self.assertEqual(audit(fixture())["capability"]["sender_reply_to"], "no-reply")

    def test_current_email_default_off(self):
        self.assertTrue(audit(fixture())["capability"]["default_send_disabled"])

    def test_fails_if_default_send_on(self):
        s = fixture(); s["jetpack"]["email_new_posts_by_default"] = True
        self.assertIn("DEFAULT_SEND_MUST_REMAIN_OFF", audit(s)["global_blockers"])

    def test_fails_if_delivery_mode_unknown(self):
        s = fixture(); s["jetpack"]["email_content_format"] = "both"
        self.assertIn("DELIVERY_FORMAT_UNKNOWN", audit(s)["global_blockers"])

    def test_fails_if_newsletter_disabled(self):
        s = fixture(); s["jetpack"]["subscriptions"] = False
        self.assertIn("NEWSLETTER_DISABLED", audit(s)["global_blockers"])

    def test_fails_if_missing_footer(self):
        s = fixture(); s["actual_delivery"]["rendered_fv_postal_address_verified"] = False
        self.assertIn("PUBLISHER_POSTAL_AND_OPTOUT_UNVERIFIED", audit(s)["global_blockers"])

    def test_fails_if_pdf_not_verified(self):
        s = fixture(); s["welcome"]["live_pdf_http_and_pagecount_verified"] = False
        self.assertIn("FIELD_BOOK_ACTUAL_RECEIPT_OR_PDF_UNKNOWN", audit(s)["global_blockers"])

    def test_fails_commercial_destination_activation(self):
        s = fixture(); s["issues"][2]["destination"] = "https://finalvestige.com/mind/zen12-guide/"
        with self.assertRaises(ContractError): audit(s)

    def test_rejects_third_party_url(self):
        s = fixture(); s["issues"][0]["destination"] = "https://example.com/affiliate"
        with self.assertRaises(ContractError): audit(s)

    def test_rejects_query_tracking_on_draft(self):
        s = fixture(); s["issues"][0]["destination"] += "?utm_content=pixel"
        with self.assertRaises(ContractError): audit(s)

    def test_rejects_bad_list_size(self):
        s = fixture(); s["issues"].pop()
        with self.assertRaises(ContractError): audit(s)

    def test_rejects_duplicate_issue(self):
        s = fixture(); s["issues"][0]["number"] = "02"
        with self.assertRaises(ContractError): audit(s)

    def test_rejects_changed_commercial_allocation(self):
        s = fixture(); s["issues"][1]["kind"] = "commercial"
        with self.assertRaises(ContractError): audit(s)

    def test_rejects_relocated_merchant_issue(self):
        s = fixture(); s["issues"][2]["kind"] = "editorial"; s["issues"][1]["kind"] = "commercial"
        with self.assertRaises(ContractError): audit(s)

    def test_rejects_invalid_subject(self):
        s = fixture(); s["issues"][1]["subject"] = ""
        with self.assertRaises(ContractError): audit(s)

    def test_rejects_truthy_string_count(self):
        s = fixture(); s["subscribers"]["reported_total"] = "3"
        with self.assertRaises(ContractError): audit(s)

    def test_rejects_negative_follower_count(self):
        s = fixture(); s["subscribers"]["jetpack_wpcom_followers"] = -2
        with self.assertRaises(ContractError): audit(s)

    def test_no_personal_data_in_result(self):
        s = fixture(); s["subscriber_email"] = "do_not_emit@example.com"
        self.assertNotIn("do_not_emit@example.com", json.dumps(audit(s)))

    def test_no_merchant_earning_url_in_result(self):
        s = fixture(); s["merchant_tracking_url"] = "https://vendor.example?ref=FAKE"
        self.assertNotIn("vendor.example", json.dumps(audit(s)))

    def test_no_customer_segment_personalization_claim(self):
        self.assertEqual(audit(fixture())["capability"]["topic_or_behavioral_recipient_segmentation"], "NOT_VERIFIED")

    def test_never_conflates_post_publish_and_send(self):
        self.assertEqual(audit(fixture())["capability"]["native_delivery_model"], "WORDPRESS_POST_NOTIFICATION_NOT_VERIFIED_DRIP")


if __name__ == "__main__": unittest.main()
