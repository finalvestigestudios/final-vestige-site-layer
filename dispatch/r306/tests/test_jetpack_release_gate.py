"""Synthetic safeguards only: no live WordPress, subscriber, affiliate or payment data."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from jetpack_release_gate import evaluate, evaluate_campaign

SETTINGS = {"subscriptions": True, "email_content_format": "full",
            "email_new_posts_by_default": False, "site_can_send": True}

GOOD = dict(master_original_unchanged=True, founder_reviewed_exact_issue=True,
            subscriber_status_eligible_proven=True, subscriber_consent_proven=True,
            welcome_receipt_proven=True, fieldbook_access_proven=True,
            native_jetpack_preview_verified=True, received_email_mime_verified=True,
            fv_postal_address_in_received_email=True,
            functional_unsubscribe_in_received_email=True,
            subject_matches_actual_post_title=True,
            preheader_in_received_email_verified=True,
            destination_live_and_claim_checked=True,
            single_primary_cta_verified=True,
            post_state="unpublished_draft", post_send_subscription=False,
            founder_final_campaign_send_approval=True,
            approved_audience_and_schedule=True,
            publisher_approval_verified=True,
            product_email_permission_verified=True,
            issued_earning_link_verified=True,
            approved_guide_live_verified=True,
            product_specific_claim_review_current=True,
            price_refund_format_checked=True,
            adjacent_commercial_disclosure_verified=True)

class ReleaseGateTests(unittest.TestCase):
    def test_empty_proof_never_releases(self):
        self.assertTrue(all(x["status"].startswith("HOLD") for x in
                            evaluate_campaign(SETTINGS, {})))

    def test_4_to_2_allocation(self):
        rows = evaluate_campaign(SETTINGS, {})
        self.assertEqual([i["kind"] for i in rows].count("commercial"), 2)
        self.assertEqual([i["kind"] for i in rows].count("editorial"), 4)

    def test_site_can_send_is_not_founder_permission(self):
        self.assertIn("founder_final_send_approval_missing", evaluate(1, SETTINGS, {}).reasons)

    def test_global_default_off_does_not_protect_post_override(self):
        proof = {**GOOD, "post_send_subscription": True}
        out = evaluate(1, SETTINGS, proof)
        self.assertEqual(out.post_email_risk, "WOULD_EMAIL_ON_NEW_POST_PUBLICATION")
        self.assertNotEqual(out.status, "READY_FOR_FOUNDER_MANUAL_RELEASE_CHECK")

    def test_scheduled_post_can_email(self):
        out = evaluate(1, SETTINGS, {**GOOD, "post_state": "scheduled", "post_send_subscription": True})
        self.assertEqual(out.post_email_risk, "WOULD_EMAIL_ON_NEW_POST_PUBLICATION")

    def test_true_preview_not_received_email(self):
        x = evaluate(1, SETTINGS, {**GOOD, "received_email_mime_verified": False})
        self.assertIn("real_received_mime_unverified", x.reasons)

    def test_invalid_postal_footer_blocks(self):
        x = evaluate(1, SETTINGS, {**GOOD, "fv_postal_address_in_received_email": False})
        self.assertIn("publisher_postal_address_unverified", x.reasons)

    def test_unsubscribe_function_required(self):
        x = evaluate(1, SETTINGS, {**GOOD, "functional_unsubscribe_in_received_email": False})
        self.assertIn("unsubscribe_not_verified", x.reasons)

    def test_merchant_email_rights_is_independent_of_affiliate_approval(self):
        x = evaluate(3, SETTINGS, {**GOOD, "product_email_permission_verified": False})
        self.assertEqual(x.status, "HOLD_MERCHANT")
        self.assertIn("merchant_email_promotion_rights_missing", x.reasons)

    def test_merchant_guide_must_be_live(self):
        x = evaluate(5, SETTINGS, {**GOOD, "approved_guide_live_verified": False})
        self.assertIn("first_party_warmup_guide_not_live", x.reasons)

    def test_commercial_near_link_disclosure_required(self):
        x = evaluate(5, SETTINGS, {**GOOD, "adjacent_commercial_disclosure_verified": False})
        self.assertIn("near_offer_disclosure_missing", x.reasons)

    def test_no_merchant_link_inferred(self):
        self.assertEqual(evaluate(3, SETTINGS, {}).verified_paid_orders, None)
        self.assertEqual(evaluate(3, SETTINGS, {}).realized_net_revenue, None)

    def test_unknown_post_toggle_fails_closed(self):
        p = {**GOOD}; del p["post_send_subscription"]
        self.assertEqual(evaluate(2, SETTINGS, p).post_email_risk, "UNKNOWN_FAIL_CLOSED")

    def test_preheader_unverified_blocks(self):
        x = evaluate(2, SETTINGS, {**GOOD, "preheader_in_received_email_verified": False})
        self.assertIn("preheader_not_native_verified", x.reasons)

    def test_cannot_conflate_wp_follower_count_with_eligibility(self):
        x = evaluate(1, SETTINGS, {**GOOD, "subscriber_status_eligible_proven": False,
                                   "wpcom_followers": 3, "confirmed_count": 3})
        self.assertIn("recipient_eligibility_unverified", x.reasons)

    def test_requires_founder_approval_even_with_all_other_gates(self):
        x = evaluate(1, SETTINGS, {**GOOD, "founder_final_campaign_send_approval": False})
        self.assertIn("founder_final_send_approval_missing", x.reasons)

    def test_positive_fixture_does_not_send_anything(self):
        x = evaluate(1, SETTINGS, GOOD)
        self.assertEqual(x.status, "READY_FOR_FOUNDER_MANUAL_RELEASE_CHECK")
        self.assertFalse(x.sender_authorized)
        self.assertEqual(x.post_email_risk, "POST_OPTED_OUT_NO_SEND_EXPECTED")

    def test_merchant_evidence_required_even_in_positive_other_gates(self):
        x = evaluate(3, SETTINGS, {**GOOD, "issued_earning_link_verified": False})
        self.assertIn("issued_earning_link_missing", x.reasons)

    def test_bad_editions_rejected(self):
        for bad in (0, 7, True, "1", None):
            with self.assertRaises(ValueError): evaluate(bad, SETTINGS, {})

    def test_bad_types_rejected(self):
        with self.assertRaises(TypeError): evaluate(1, "bad", {})

if __name__ == "__main__":
    unittest.main()
