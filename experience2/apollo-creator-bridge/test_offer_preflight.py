#!/usr/bin/env python3
"""Offline, synthetic security and commercial truth tests for Apollo offer preflight."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from offer_preflight import ContractError, distinct_pairs, payhip_path, validate

BASE = json.loads((Path(__file__).parent / "offer_template.json").read_text())

class OfferPreflightTests(unittest.TestCase):
    def setUp(self):
        self.m = copy.deepcopy(BASE)

    def assert_invalid(self, mutate):
        mutate(self.m)
        with self.assertRaises(ContractError):
            validate(self.m)

    def test_template_is_never_published(self):
        result = validate(self.m)
        self.assertEqual(result["result"], "STAGING_HOLD_REVIEW_REQUIRED")
        self.assertEqual(len(result["unreviewed"]), 6)
        self.assertFalse(result["can_enable_checkout"])
        self.assertFalse(result["can_claim_revenue"])

    def test_even_fully_self_attested_remains_hold(self):
        for c in self.m["checks"].values():
            c.update({"state": "reviewed", "evidence_sha256": "a"*64, "checked_utc": "2026-11-03T12:00:00Z"})
        result = validate(self.m)
        self.assertEqual(result["metadata_checks"], 6)
        self.assertFalse(result["founder_authorization_verified"])
        self.assertFalse(result["can_publish"])

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(ContractError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=distinct_pairs)

    def test_credentials_in_sku_rejected(self):
        self.assert_invalid(lambda m: m["offer"].update({"sku": "user@example.com"}))

    def test_product_purpose_required(self):
        self.assert_invalid(lambda m: m["offer"].update({"product_title": "Unrelated focus workbook"}))

    def test_wrong_seller_rejected(self):
        self.assert_invalid(lambda m: m["offer"].update({"seller": "NASA"}))

    def test_price_float_rejected(self):
        self.assert_invalid(lambda m: m["offer"].update({"price_minor_units": 9.99}))

    def test_zero_price_rejected(self):
        self.assert_invalid(lambda m: m["offer"].update({"price_minor_units": 0}))

    def test_extra_key_rejected(self):
        self.assert_invalid(lambda m: m["offer"].update({"customer_email": "someone@example.com"}))

    def test_false_review_missing_hash_rejected(self):
        self.assert_invalid(lambda m: m["checks"]["fulfillment"].update({"state":"reviewed"}))

    def test_reviewed_date_future_rejected(self):
        self.assert_invalid(lambda m: m["checks"]["rights_media"].update({"state":"reviewed", "evidence_sha256":"a"*64, "checked_utc":"2099-11-03T12:00:00Z"}))

    def test_pending_claims_not_accepted(self):
        self.assert_invalid(lambda m: m["checks"]["founder_release"].update({"evidence_sha256":"a"*64}))

    def test_bad_states_rejected(self):
        self.assert_invalid(lambda m: m["checks"]["seller_listing"].update({"state": "approved"}))

    def test_no_url_query_or_tracking(self):
        for url in ("https://payhip.com/b/a?utm_source=youtube", "http://payhip.com/b/a", "https://payhip.com.evil.test/b/a", "https://payhip.com@evil.test/b/a", "https://PAYHIP.COM/b/a", "https://payhip.com/store/foo", "https://payhip.com/b/a#checkout", "https://payhip.com:443/b/a"):
            with self.subTest(url=url), self.assertRaises(ContractError):
                payhip_path(url)

    def test_allow_only_canonical_product(self):
        self.assertEqual(payhip_path("https://payhip.com/b/abcDEF123"), "https://payhip.com/b/abcDEF123")

if __name__=="__main__":
    unittest.main()
