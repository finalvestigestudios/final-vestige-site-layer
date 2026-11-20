"""Offline synthetic regression tests; no provider interactions or production access."""
import unittest

from focus_funnel_contract import audit


def fixture():
    return {
        "pages": {
            "home": "Get the free Focus Fieldbook with your free Dispatch subscription.",
            "focus": "When we publish them. You do not need to sign up again.",
            "library": "52-page PDF. Free with email signup.",
            "collection": "Free with The Dispatch subscription.",
            "dispatch": "New investigations, when we publish them.",
        },
        "newsletter": {"email_new_posts_by_default": False},
        "observations": {},
    }


class OfferFunnelContractTest(unittest.TestCase):
    def test_unwitnessed_signup_is_hold(self):
        self.assertEqual(audit(fixture())["new_confirmed_lead"], "HOLD")

    def test_pdf_click_is_not_signup(self):
        s = fixture()
        s["observations"]["pdf_click_recorded"] = True
        self.assertEqual(audit(s)["new_confirmed_lead"], "HOLD")

    def test_welcome_not_passed_by_settings_alone(self):
        s = fixture()
        s["observations"]["fresh_double_opt_in_verified"] = True
        self.assertEqual(audit(s)["welcome_and_pdf"], "HOLD")

    def test_complete_consent_and_delivery_witness(self):
        s = fixture()
        s["observations"].update(fresh_double_opt_in_verified=True, welcome_received_verified=True, pdf_bytes_verified=True)
        self.assertEqual(audit(s)["welcome_and_pdf"], "PASS")

    def test_public_pdf_only_with_browser_proof(self):
        self.assertEqual(audit(fixture())["direct_pdf_browser"], "HOLD")

    def test_cross_page_gate_copy_detected_if_direct_pdf_proven(self):
        s = fixture()
        s["observations"]["direct_pdf_browser_verified"] = True
        self.assertEqual(audit(s)["cross_page_download_promise"], "REVIEW")

    def test_consistent_copy_passes(self):
        s = fixture()
        s["observations"]["direct_pdf_browser_verified"] = True
        for k in ("home", "library", "collection"):
            s["pages"][k] = "Free 52-page PDF, with optional Dispatch updates."
        self.assertEqual(audit(s)["cross_page_download_promise"], "PASS")

    def test_unsent_publication_promise_reviews_not_hard_fails(self):
        self.assertEqual(audit(fixture())["publication_email_promise"], "REVIEW")

    def test_verified_manual_send_satisfies_publication_promise(self):
        s = fixture()
        s["observations"]["relevant_edition_send_verified"] = True
        self.assertEqual(audit(s)["publication_email_promise"], "PASS")

    def test_explicit_do_not_resubscribe_is_good(self):
        self.assertEqual(audit(fixture())["retry_signup_guidance"], "PASS")

    def test_repeated_signup_instruction_needs_review(self):
        s = fixture()
        s["pages"]["focus"] = "If blocked, sign up again."
        self.assertEqual(audit(s)["retry_signup_guidance"], "REVIEW")

    def test_no_synthetic_revenue_from_clicks(self):
        s = fixture()
        s["observations"].update(affiliate_clicks=90, checkout_starts=20)
        r = audit(s)
        self.assertIsNone(r["net_revenue_per_1000_humans"])
        self.assertEqual(r["paid_revenue_evidence"], "HOLD")

    def test_revenue_only_with_settlement_humans_fees_refunds(self):
        s = fixture()
        s["observations"].update(merchant_settlement_verified=True, qualified_human_sessions=200, settled_gross=120, settled_refunds=20, settled_fees=10)
        self.assertEqual(audit(s)["net_revenue_per_1000_humans"], 450.0)

    def test_zero_humans_is_uncomputable(self):
        s = fixture()
        s["observations"].update(merchant_settlement_verified=True, qualified_human_sessions=0, settled_gross=120, settled_refunds=20, settled_fees=10)
        self.assertIsNone(audit(s)["net_revenue_per_1000_humans"])

    def test_negative_or_fabricated_amounts_rejected(self):
        s = fixture()
        s["observations"].update(merchant_settlement_verified=True, qualified_human_sessions=100, settled_gross=50, settled_refunds=-1, settled_fees=1)
        self.assertEqual(audit(s)["paid_revenue_evidence"], "HOLD")

    def test_missing_page_source_rejected(self):
        s = fixture()
        del s["pages"]["focus"]
        with self.assertRaises(ValueError):
            audit(s)


if __name__ == "__main__":
    unittest.main()
