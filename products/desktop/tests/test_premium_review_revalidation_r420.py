"""R420: product-scoped premium review proof and revocation (synthetic data only).

These tests exercise the shape gate, NOT signature issuance, signed licensing,
premium downloads, payment approval, or a genuine Windows executable.
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
import unittest

from fvs_suite.offline_entitlement import Entitlement
from fvs_suite.review_target import revalidate_or_revoke


def synthetic(product: str) -> Entitlement:
    return Entitlement(product, "SYNTHETIC-NO-SIGNATURE", "Test Holder",
                       datetime(2099, 1, 1, tzinfo=timezone.utc))


class PremiumReviewProofBoundaryR420(unittest.TestCase):
    def test_grant_proof_shape_succeeds_without_scrub(self):
        calls = []
        self.assertTrue(revalidate_or_revoke(lambda: calls.append("check") or synthetic("grants"),
                                             lambda: calls.append("scrub"), product="grants"))
        self.assertEqual(calls, ["check"])

    def test_procurement_proof_shape_succeeds_without_scrub(self):
        calls = []
        self.assertTrue(revalidate_or_revoke(lambda: synthetic("procurement"),
                                             lambda: calls.append("scrub"), product="procurement"))
        self.assertEqual(calls, [])

    def test_opposite_product_denied_and_scrubbed(self):
        for requested, found in (("grants", "procurement"), ("procurement", "grants")):
            with self.subTest(requested=requested):
                scrubs = []
                self.assertFalse(revalidate_or_revoke(lambda: synthetic(found),
                                                      lambda: scrubs.append(True), product=requested))
                self.assertEqual(scrubs, [True])

    def test_truthy_sentinels_denied_even_when_boolean_true(self):
        for proof in (True, 1, "verified", ["entitlement"], {"product": "grants"}, object()):
            with self.subTest(proof_type=type(proof).__name__):
                scrubs = []
                self.assertFalse(revalidate_or_revoke(lambda: proof,
                                                      lambda: scrubs.append(True), product="grants"))
                self.assertEqual(scrubs, [True])

    def test_entitlement_subclass_denied_without_boolean_hooks(self):
        class Forged(Entitlement):
            def __bool__(self):
                raise AssertionError("PRIVATE_LICENSE_TEXT")
        forged = Forged("grants", "FAKE", "Private", datetime(2099, 1, 1, tzinfo=timezone.utc))
        scrubs = []
        self.assertFalse(revalidate_or_revoke(lambda: forged,
                                              lambda: scrubs.append(True), product="grants"))
        self.assertEqual(scrubs, [True])

    def test_truthiness_callback_not_invoked_on_unknown_object(self):
        class Hostile:
            def __bool__(self):
                raise AssertionError("PRIVATE_PATH_FROM_TRUTHINESS")
            def __str__(self):
                raise AssertionError("PRIVATE_PATH_FROM_STRING")
        scrubs = []
        self.assertFalse(revalidate_or_revoke(lambda: Hostile(),
                                              lambda: scrubs.append(True), product="procurement"))
        self.assertEqual(scrubs, [True])

    def test_non_native_and_unknown_product_cannot_authorize(self):
        class ForgedProduct(str):
            def __eq__(self, other):
                raise AssertionError("PRIVATE_PRODUCT_HOOK")
        for requested in ("ledger", "", None, ForgedProduct("grants")):
            with self.subTest(type=type(requested).__name__):
                scrubs = []
                self.assertFalse(revalidate_or_revoke(lambda: synthetic("grants"),
                                                      lambda: scrubs.append(True), product=requested))
                self.assertEqual(scrubs, [True])

    def test_verifier_raises_private_exception_and_scrubs_without_logging(self):
        calls = []
        def broken():
            calls.append("verify")
            raise OSError("PRIVATE_LICENSE_PATH")
        self.assertFalse(revalidate_or_revoke(broken,
                                              lambda: calls.append("scrub"), product="grants"))
        self.assertEqual(calls, ["verify", "scrub"])

    def test_revocation_after_previous_valid_proof_clears_view(self):
        current = [synthetic("grants")]
        view = {"case_id": "SYNTHETIC", "rationale": "Local notes"}
        callback = lambda: current[0]
        self.assertTrue(revalidate_or_revoke(callback, view.clear, product="grants"))
        self.assertTrue(view)
        current[0] = None
        self.assertFalse(revalidate_or_revoke(callback, view.clear, product="grants"))
        self.assertEqual(view, {})

    def test_callback_invoked_only_once_per_check(self):
        calls = []
        self.assertTrue(revalidate_or_revoke(lambda: calls.append(1) or synthetic("grants"),
                                             lambda: None, product="grants"))
        self.assertEqual(calls, [1])

    def test_scrubber_failure_cannot_return_authorized(self):
        def fail():
            raise RuntimeError("UI scrub failed")
        with self.assertRaisesRegex(RuntimeError, "UI scrub failed"):
            revalidate_or_revoke(lambda: True, fail, product="grants")

    def test_missing_product_scope_rejected_before_verifier(self):
        events = []
        with self.assertRaises(TypeError):
            revalidate_or_revoke(lambda: events.append("verify") or synthetic("grants"),
                                 lambda: events.append("scrub"))
        self.assertEqual(events, [])

    def test_real_review_ui_preflight_and_action_checks_both_scope_product(self):
        path = Path(__file__).resolve().parents[1] / "fvs_suite" / "review_ui.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == "revalidate_or_revoke"]
        self.assertEqual(len(calls), 2, "both early window and action checks must be scoped")
        for call in calls:
            product_kw = [kw.value for kw in call.keywords if kw.arg == "product"]
            self.assertEqual(len(product_kw), 1)
            self.assertIsInstance(product_kw[0], ast.Name)
            self.assertEqual(product_kw[0].id, "product")


if __name__ == "__main__":
    unittest.main()
