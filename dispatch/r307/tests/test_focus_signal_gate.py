"""Offline adversarial fixtures. No subscriber account or live delivery touched."""
import unittest
from focus_signal_gate import (
    existing_gift_visibility, classify_client_signal,
    provider_transition_candidate, release_decision,
)

GOOD = dict(provider="jetpack", status="Subscribed", source="authenticated_provider_server",
            consent_scope="dispatch_newsletter", confirmation="confirmed_email_link",
            is_new_transition=True, dedupe_applied=True, opted_out=False,
            bounced=False, emails_paused=False,
            opaque_dedupe_ref="idempotency_fixture_AaBbCcDd001")

class GiftDisplayRegression(unittest.TestCase):
    def test_01_blank_query(self): self.assertFalse(existing_gift_visibility(None, False))
    def test_02_empty_query(self): self.assertFalse(existing_gift_visibility("", False))
    def test_03_happy_query(self): self.assertTrue(existing_gift_visibility("success", False))
    def test_04_pending_query(self): self.assertTrue(existing_gift_visibility("pending", False))
    def test_05_unknown_query(self): self.assertTrue(existing_gift_visibility("totally-unrecognized", False))
    def test_06_zero_query(self): self.assertTrue(existing_gift_visibility("0", False))
    def test_07_invalid_email(self): self.assertFalse(existing_gift_visibility("invalid_email", False))
    def test_08_blocked(self): self.assertFalse(existing_gift_visibility("blocked", False))
    def test_09_opted_out(self): self.assertFalse(existing_gift_visibility("opted_out", False))
    def test_10_css_class(self): self.assertTrue(existing_gift_visibility(None, True))
    def test_11_critical_denylist_bypass(self): self.assertTrue(existing_gift_visibility("BLOCKED", False))

class ConsentClassification(unittest.TestCase):
    def test_12_signals_never_confirm(self):
        for s in ("subscribe_query", "is_subscriber_css", "form_submit", "fieldbook_click", "gift_visible", "page_visit", "email_open", "newsletter_click", "reader_follow", "welcome_configured"):
            with self.subTest(s=s):
                self.assertEqual(classify_client_signal(s, "success").permitted_interpretation, "NO_CONFIRMED_SIGNUP")
    def test_13_unrecognized_signal(self): self.assertEqual(classify_client_signal("unknown").signal, "UNRECOGNIZED_CLIENT_SIGNAL")
    def test_14_not_mapping(self): self.assertEqual(provider_transition_candidate(None).signal, "INVALID_PROVIDER_EVIDENCE")
    def test_15_good_still_requires_auth(self):
        r=provider_transition_candidate(GOOD)
        self.assertEqual(r.signal, "STRUCTURAL_CANDIDATE_ONLY")
        self.assertIsNone(r.event)
    def test_16_unconfirmed(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"status":"Not confirmed"}).signal, "INSUFFICIENT_PROVIDER_EVIDENCE")
    def test_17_reader_only(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"status":"Not subscribed"}).signal, "INSUFFICIENT_PROVIDER_EVIDENCE")
    def test_18_not_new(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"is_new_transition":False}).signal, "INSUFFICIENT_PROVIDER_EVIDENCE")
    def test_19_no_dedupe(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"dedupe_applied":False}).signal, "INSUFFICIENT_PROVIDER_EVIDENCE")
    def test_20_optout(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"opted_out":True}).signal, "INSUFFICIENT_PROVIDER_EVIDENCE")
    def test_21_paused(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"emails_paused":True}).signal, "INSUFFICIENT_PROVIDER_EVIDENCE")
    def test_22_bounced(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"bounced":True}).signal, "INSUFFICIENT_PROVIDER_EVIDENCE")
    def test_23_wrong_scope(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"consent_scope":"merchant_list"}).signal, "INSUFFICIENT_PROVIDER_EVIDENCE")
    def test_24_wrong_source(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"source":"client_query"}).signal, "INSUFFICIENT_PROVIDER_EVIDENCE")
    def test_25_no_private_ref(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"opaque_dedupe_ref":""}).signal, "MISSING_PRIVATE_DEDUP_REF")
    def test_26_pii_email(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"email":"sensitive@example.invalid"}).signal, "PII_IN_EVIDENCE")
    def test_27_pii_subscriber_id(self):
        self.assertEqual(provider_transition_candidate(GOOD|{"subscriber_id":"123"}).signal, "PII_IN_EVIDENCE")
    def test_28_issue_holds_empty(self):
        r=release_decision({})
        self.assertEqual(r["editorial"], "HOLD_UNSENT")
        self.assertEqual(r["commercial"], "HOLD_MERCHANT")
    def test_29_all_flags_not_permission(self):
        # Synthetic all-true flags can never be promoted to live send authority.
        r=release_decision({k:True for k in (
            "founder_final_campaign_approval", "founder_post_publication_approval", "founder_send_approval",
            "native_preview_verified", "received_email_footer_verified", "valid_fv_postal_address_verified",
            "working_unsubscribe_verified", "eligible_provider_status_verified", "welcome_receipt_verified",
            "exact_per_post_toggle_verified", "copy_source_verified", "affiliate_publisher_accepted",
            "email_channel_permission_verified", "issued_earning_url_verified", "approved_live_guide_verified",
            "specific_offer_claims_verified", "adjacent_disclosure_verified")})
        self.assertEqual((r["editorial"],r["commercial"]),("HOLD_UNSENT","HOLD_MERCHANT"))
    def test_30_cannot_fake_event(self):
        self.assertIsNone(classify_client_signal("subscribe_query").event)
        self.assertIsNone(provider_transition_candidate(GOOD).event)

if __name__=="__main__":unittest.main()
