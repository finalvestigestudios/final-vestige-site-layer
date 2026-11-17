"""Independent offline contract tests; no network, no recipient data, no sends."""
import copy
import json
import pathlib
import unittest
from merchant_drift_gate import audit

BASE = json.loads(pathlib.Path(__file__).with_name("OFFER_SURFACE_SNAPSHOT.json").read_text())


class MerchantDriftSafety(unittest.TestCase):
    def test_real_snapshot_holds_both(self):
        report = audit(BASE)
        self.assertEqual(report["decision"], "HOLD_UNSENT")
        self.assertEqual(set(report["offers"]), {"issue03_zen12", "issue05_total_focus"})
        self.assertTrue(all(v["decision"] == "HOLD_MERCHANT" for v in report["offers"].values()))

    def test_finds_two_distinct_public_price_contexts(self):
        report = audit(BASE)
        for offer in report["offers"].values():
            self.assertIn("MULTIPLE_PUBLIC_PRICE_CONTEXTS_NOT_REFERRED_CHECKOUT", offer["problems"])

    def test_missing_all_private_permissions(self):
        for v in audit(BASE)["offers"].values():
            self.assertTrue(any("EMAIL_CHANNEL_AUTHORIZATION" in p for p in v["problems"]))
            self.assertTrue(any("EARNING_LINK" in p for p in v["problems"]))

    def test_issue_swapping_is_rejected(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue03_zen12"]["issue"] = 5
        with self.assertRaises(ValueError): audit(x)

    def test_third_commercial_slot_rejected(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue07_unapproved"] = {}
        with self.assertRaises(ValueError): audit(x)

    def test_price_promotion_triggers_hold(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue03_zen12"]["price_message_allowed"] = True
        self.assertIn("PRICE_CANNOT_BE_CLAIMED_FROM_PUBLIC_SURFACE", audit(x)["offers"]["issue03_zen12"]["problems"])

    def test_refund_promotion_triggers_hold(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue05_total_focus"]["refund_message_allowed"] = True
        self.assertIn("REFUND_NOT_VERIFIED_AT_REFERRED_CHECKOUT", audit(x)["offers"]["issue05_total_focus"]["problems"])

    def test_efficacy_promotion_triggers_hold(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue03_zen12"]["efficacy_claim_allowed"] = True
        self.assertIn("SKU_SPECIFIC_EFFICACY_NOT_VERIFIED", audit(x)["offers"]["issue03_zen12"]["problems"])

    def test_accountless_public_link_does_not_unlock(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue03_zen12"]["earning_link"] = "https://zen12.com/"
        v = audit(x)["offers"]["issue03_zen12"]
        self.assertIn("PUBLIC_URL_IS_NOT_AFFILIATE_ACCOUNT_EVIDENCE", v["problems"])

    def test_fake_authenticated_link_still_holds_without_other_proofs(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue03_zen12"]["earning_link"] = {"authenticated": True, "verified_by": "synthetic-fixture"}
        self.assertEqual(audit(x)["decision"], "HOLD_UNSENT")

    def test_even_optimistically_all_proofs_cannot_send(self):
        x = copy.deepcopy(BASE)
        for offer in x["offers"].values():
            for field in ("first_party_guide", "earning_link", "affiliate_acceptance_document", "email_channel_authorization", "named_account_owner", "referred_checkout_capture", "merchant_payout_record"):
                offer[field] = {"authenticated": True, "verified_by": "synthetic-fixture"}
        x["global_release_proofs"] = {k: True for k in x["global_release_proofs"]}
        self.assertEqual(audit(x)["decision"], "HOLD_UNSENT")
        self.assertTrue(all(v["decision"] == "HOLD_MERCHANT" for v in audit(x)["offers"].values()))

    def test_offdomain_source_rejected(self):
        x = copy.deepcopy(BASE)
        x["sources"]["zen12_main"] = "https://example.com/fake"
        with self.assertRaises(ValueError): audit(x)

    def test_http_source_rejected(self):
        x = copy.deepcopy(BASE)
        x["sources"]["zen12_main"] = "http://zen12.com/"
        with self.assertRaises(ValueError): audit(x)

    def test_price_decimal_format_rejected(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue05_total_focus"]["surfaces"][0]["displayed_prices_usd"] = ["free"]
        with self.assertRaises(ValueError): audit(x)

    def test_missing_surface_context_is_a_hold(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue05_total_focus"]["surfaces"][0]["description"] = ""
        self.assertIn("MISSING_SURFACE_CONTEXT", audit(x)["offers"]["issue05_total_focus"]["problems"])

    def test_no_sources_is_a_hold(self):
        x = copy.deepcopy(BASE)
        x["offers"]["issue05_total_focus"]["surfaces"] = []
        self.assertIn("NO_MERCHANT_SURFACE_OBSERVATIONS", audit(x)["offers"]["issue05_total_focus"]["problems"])

    def test_wrong_schema_rejected(self):
        x = copy.deepcopy(BASE)
        x["schema"] = "unknown"
        with self.assertRaises(ValueError): audit(x)

    def test_real_snapshot_safely_serializable_without_subscriber_data(self):
        raw = json.dumps(BASE).lower()
        self.assertNotIn("@gmail", raw)
        self.assertNotIn("@yahoo", raw)
        self.assertNotIn("subscriber_id", raw)


if __name__ == "__main__": unittest.main()
