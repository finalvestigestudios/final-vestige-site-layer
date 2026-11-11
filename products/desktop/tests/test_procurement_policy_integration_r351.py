"""R351 full ProcureGuard review_line custody (requires complete private suite)."""
from __future__ import annotations

from decimal import Decimal
import unittest

from fvs_suite.identity_inputs import normalize_key
from fvs_suite.procurement import PricePolicy, review_line

SHA = "a" * 64
ERROR = "Procurement review requires a native bounded price policy"


def row(*, amount="2", price="10.00", doc="DOC1"):
    return {"quantity": amount, "unit_price": price, "event_type": "",
            "document_id": doc, "related_document": "", "row": "2"}


def review(policy=None, unit_cost=Decimal, invoice_price="10.00"):
    return review_line(
        [row()], [row(price=invoice_price, doc="INV1")], [row(doc="REC1")],
        quantity=Decimal, unit_cost=unit_cost,
        identifier=normalize_key, policy=PricePolicy() if policy is None else policy)


class HostilePolicy(PricePolicy):
    def outside(self, *_):
        raise RuntimeError("PRIVATE_CUSTOMER_PATH")


class ProcureGuardPolicyIntegrationR351(unittest.TestCase):
    def reject(self, policy):
        with self.assertRaises(ValueError) as caught:
            review(policy=policy)
        self.assertEqual(str(caught.exception), ERROR)
        self.assertNotIn("PRIVATE_CUSTOMER_PATH", str(caught.exception))

    def test_default_policy_still_operates(self):
        data, flags = review()
        self.assertEqual(data["price_policy_absolute"], "0.01")
        self.assertNotIn("price_variance_above_2pct", flags)

    def test_widened_policy_remains_review_only(self):
        policy = PricePolicy(Decimal("1.00"), Decimal("0.05"), SHA)
        data, flags = review(policy=policy, invoice_price="10.50")
        self.assertEqual(data["price_policy_sha256"], SHA)
        self.assertIn("widened_price_policy_review", flags)
        self.assertNotIn("price_variance_above_policy", flags)

    def test_invalid_absolute_rejected(self):
        self.reject(PricePolicy(Decimal("-0.01"), Decimal("0.02"), SHA))

    def test_invalid_fraction_rejected(self):
        self.reject(PricePolicy(Decimal("0.01"), Decimal("1.00"), SHA))

    def test_forged_policy_subclass_rejected_before_hook(self):
        self.reject(HostilePolicy())

    def test_private_policy_digest_rejected_without_echo(self):
        self.reject(PricePolicy(source_sha256="C:/PRIVATE_CUSTOMER_PATH"))

    def test_nonfinite_absolute_rejected(self):
        self.reject(PricePolicy(Decimal("NaN"), Decimal("0.02"), SHA))

    def test_hostile_float_fraction_rejected(self):
        self.reject(PricePolicy(Decimal("0.01"), 0.2, SHA))

    def test_parser_cannot_widen_threshold_mid_review(self):
        policy = PricePolicy()
        def parse_price(value):
            object.__setattr__(policy, "absolute", Decimal("100"))
            return Decimal(value)
        data, flags = review(policy=policy, unit_cost=parse_price, invoice_price="10.50")
        self.assertEqual(data["price_policy_absolute"], "0.01")
        self.assertIn("price_variance_above_2pct", flags)
        self.assertNotIn("widened_price_policy_review", flags)

    def test_parser_cannot_forge_digest_mid_review(self):
        policy = PricePolicy()
        baseline = policy.source_sha256
        def parse_price(value):
            object.__setattr__(policy, "source_sha256", "b" * 64)
            return Decimal(value)
        data, _ = review(policy=policy, unit_cost=parse_price)
        self.assertEqual(data["price_policy_sha256"], baseline)

    def test_parser_cannot_reclassify_price_policy_fraction(self):
        policy = PricePolicy()
        def parse_price(value):
            object.__setattr__(policy, "fraction", Decimal("0.10"))
            return Decimal(value)
        data, flags = review(policy=policy, unit_cost=parse_price, invoice_price="10.50")
        self.assertEqual(data["price_policy_fraction"], "0.02")
        self.assertIn("price_variance_above_2pct", flags)

    def test_review_is_deterministic_for_valid_policy(self):
        policy = PricePolicy(Decimal("0.03"), Decimal("0.04"), SHA)
        self.assertEqual(review(policy), review(policy))


if __name__ == "__main__":
    unittest.main()
