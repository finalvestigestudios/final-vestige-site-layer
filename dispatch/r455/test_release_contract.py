import unittest
from release_contract import (
    MUST_WITNESS, PARTNER_WITNESS, release_review, classify_audience,
    validate_grok_attribution, realized_net_revenue_per_thousand,
)

class ReleaseTest(unittest.TestCase):
    def test_all_six_default_hold(self):
        for i in range(1, 7):
            with self.subTest(i=i):
                self.assertEqual(release_review(i, {}).status, "HOLD_UNSENT")

    def test_editorial_complete_still_human_only(self):
        proof = {x: True for x in MUST_WITNESS}
        for i in (1, 2, 4, 6):
            self.assertEqual(release_review(i, proof).status, "HUMAN_REVIEW_CANDIDATE_ONLY")

    def test_editorial_requires_footer_and_native_preview(self):
        proof = {x: True for x in MUST_WITNESS}
        for absent in MUST_WITNESS:
            with self.subTest(absent=absent):
                d = proof | {absent: False}
                self.assertIn(absent, release_review(1, d).reasons)

    def test_commercial_specific_product(self):
        proof = {x: True for x in MUST_WITNESS + PARTNER_WITNESS}
        self.assertEqual(release_review(3, proof, product="Zen12").status, "HUMAN_REVIEW_CANDIDATE_ONLY")
        self.assertEqual(release_review(5, proof, product="Hypnosis Live").status, "HUMAN_REVIEW_CANDIDATE_ONLY")
        self.assertIn("incorrect_exact_offer_product", release_review(3, proof, product="Hypnosis Live").reasons)

    def test_partner_proof_each_required(self):
        proof = {x: True for x in MUST_WITNESS + PARTNER_WITNESS}
        for absent in PARTNER_WITNESS:
            with self.subTest(absent=absent):
                self.assertIn(absent, release_review(3, proof | {absent: False}, product="Zen12").reasons)

    def test_prohibit_auto_send_and_data_exports(self):
        proof = {x: True for x in MUST_WITNESS}
        self.assertIn("prohibited_subscriber_export", release_review(2, proof | {"subscriber_data_exported": True}).reasons)
        self.assertIn("prohibited_automatic_post_send", release_review(2, proof | {"new_post_auto_send_enabled": True}).reasons)

    def test_no_commercial_placement_in_editorial(self):
        proof = {x: True for x in MUST_WITNESS}
        self.assertIn("unsanctioned_commercial_placement", release_review(6, proof, product="Zen12").reasons)
        self.assertIn("unsanctioned_commercial_placement", release_review(6, proof | {"affiliate_url_active": True}).reasons)

    def test_outside_campaign_disallowed(self):
        with self.assertRaises(ValueError): release_review(7, {})

    def test_source_counts_disagree(self):
        result = classify_audience({"confirmed":3,"unconfirmed":2},{"email":3,"reader":0},{"email":0,"reader":3})
        self.assertEqual(result["status"], "SOURCE_CLASSIFICATION_DISAGREEMENT")
        self.assertIsNone(result["new_external_confirmed_signups"])
        self.assertIsNone(result["welcome_received"])

    def test_agreement_not_delivery_proof(self):
        r=classify_audience({"confirmed":3,"unconfirmed":2},{"email":3,"reader":0},{"email":3,"reader":0})
        self.assertEqual(r["status"], "SURFACES_AGREE_NOT_DELIVERY_PROOF")
        self.assertIsNone(r["welcome_received"])

    def test_missing_count_not_forged_zero(self):
        r=classify_audience({"confirmed":None,"unconfirmed":2},{"email":3,"reader":0},{"email":0,"reader":3})
        self.assertEqual(r["status"], "INVALID_SOURCE_COUNTS")

    def test_bool_counts_invalid(self):
        r=classify_audience({"confirmed":True,"unconfirmed":2},{"email":3,"reader":0},{"email":0,"reader":3})
        self.assertEqual(r["status"], "INVALID_SOURCE_COUNTS")

    def test_valid_grok_url(self):
        good="https://finalvestige.com/focus/?utm_source=youtube&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=yt_20261118_case1"
        self.assertTrue(validate_grok_attribution(good))

    def test_utm_duplicates_rejected(self):
        good="https://finalvestige.com/focus/?utm_source=youtube&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=yt1"
        self.assertFalse(validate_grok_attribution(good + "&utm_content=yt2"))

    def test_wrong_utm_source_or_domain(self):
        self.assertFalse(validate_grok_attribution("https://example.com/focus/?utm_source=youtube&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=yt1"))

    def test_proof_absence_not_zero_revenue(self):
        for sessions in (None, 0, -1, True):
            self.assertIsNone(realized_net_revenue_per_thousand(sessions, 123))
        self.assertIsNone(realized_net_revenue_per_thousand(100, None))
        self.assertIsNone(realized_net_revenue_per_thousand(100, True))

    def test_synthetic_settlement_formula_only(self):
        self.assertEqual(realized_net_revenue_per_thousand(250, 12.5), 50.0)
        self.assertEqual(realized_net_revenue_per_thousand(1000, -2.0), -2.0)

if __name__ == "__main__": unittest.main()
