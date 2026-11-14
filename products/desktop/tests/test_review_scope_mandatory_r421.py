"""R421: mandatory product-bound premium review gate. Synthetic proofs only.

No signing keys, customer data, payment approvals, or native executables used.
These tests do not validate Ed25519 signatures or distribution entitlements.
"""
from __future__ import annotations

import ast
import contextlib
from datetime import datetime, timezone
import io
from pathlib import Path
import unittest

from fvs_suite.offline_entitlement import Entitlement
from fvs_suite.premium_launch_proof import has_verified_premium_proof
from fvs_suite.review_target import revalidate_or_revoke


def proof(product="grants"):
    return Entitlement(product, "SYNTHETIC-NOT-SIGNED", "Test Holder",
                       datetime(2099, 1, 1, tzinfo=timezone.utc))


class MandatoryPremiumReviewScopeR421(unittest.TestCase):
    def test_unscoped_access_raises_before_verifier_or_scrubber(self):
        calls = []
        with self.assertRaises(TypeError):
            revalidate_or_revoke(lambda: calls.append("verify") or proof(),
                                 lambda: calls.append("scrub"))
        self.assertEqual(calls, [])

    def test_both_products_admit_exact_synthetic_result_once(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                events = []
                self.assertTrue(revalidate_or_revoke(
                    lambda: events.append("verify") or proof(product),
                    lambda: events.append("scrub"), product=product))
                self.assertEqual(events, ["verify"])

    def test_wrong_product_denied_and_view_scrubbed(self):
        for product in ("grants", "procurement"):
            events = []
            other = "procurement" if product == "grants" else "grants"
            self.assertFalse(revalidate_or_revoke(
                lambda: proof(other), lambda: events.append("scrub"), product=product))
            self.assertEqual(events, ["scrub"])

    def test_invalid_product_is_denied_without_invoking_verifier(self):
        class Hostile(str):
            def __eq__(self, other):
                raise AssertionError("PRIVATE_LICENSE_DATA")
        for product in (None, "ledger", "", Hostile("grants")):
            with self.subTest(kind=type(product).__name__):
                events = []
                self.assertFalse(revalidate_or_revoke(
                    lambda: events.append("verify") or proof(),
                    lambda: events.append("scrub"), product=product))
                self.assertEqual(events, ["scrub"])

    def test_truthy_results_and_other_classes_do_not_authorize(self):
        for result in (True, 1, "approved", object(), {"product": "grants"}):
            with self.subTest(kind=type(result).__name__):
                events = []
                self.assertFalse(revalidate_or_revoke(
                    lambda: result, lambda: events.append("scrub"), product="grants"))
                self.assertEqual(events, ["scrub"])

    def test_native_entitlement_with_hostile_product_subclass_is_denied(self):
        class EvilProduct(str):
            def __eq__(self, other):
                return True
        forged = proof(EvilProduct("procurement"))
        self.assertFalse(has_verified_premium_proof(forged, "grants", Entitlement))
        view = {"private": "local data"}
        self.assertFalse(revalidate_or_revoke(lambda: forged, view.clear, product="grants"))
        self.assertEqual(view, {})

    def test_non_native_product_field_rejected_even_if_equal(self):
        class SameText(str):
            pass
        self.assertFalse(has_verified_premium_proof(proof(SameText("grants")),
                                                    "grants", Entitlement))

    def test_proof_field_read_exception_is_denial_not_crash(self):
        class PropertyProof:
            @property
            def product(self):
                raise RuntimeError("PRIVATE_LICENSE_ID")
        self.assertFalse(has_verified_premium_proof(PropertyProof(),
                                                    "grants", PropertyProof))

    def test_hostile_bool_not_evaluated(self):
        class Hostile:
            def __bool__(self):
                raise AssertionError("PRIVATE_DATA")
        events = []
        self.assertFalse(revalidate_or_revoke(lambda: Hostile(),
                                              lambda: events.append("scrub"), product="grants"))
        self.assertEqual(events, ["scrub"])

    def test_verifier_crash_does_not_log_customer_filename(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        events = []
        def bad():
            raise OSError("SECRET_CUSTOMER.csv")
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertFalse(revalidate_or_revoke(
                bad, lambda: events.append("scrub"), product="procurement"))
        self.assertEqual(events, ["scrub"])
        self.assertEqual(stdout.getvalue() + stderr.getvalue(), "")

    def test_revoked_proof_clears_existing_notes(self):
        slot = [proof()]
        state = {"private_notes": "never export automatically"}
        callback = lambda: slot[0]
        self.assertTrue(revalidate_or_revoke(callback, state.clear, product="grants"))
        slot[0] = None
        self.assertFalse(revalidate_or_revoke(callback, state.clear, product="grants"))
        self.assertEqual(state, {})

    def test_invalid_callbacks_rejected_before_data_access(self):
        with self.assertRaisesRegex(ValueError, "Invalid premium authorization callbacks"):
            revalidate_or_revoke(None, lambda: None, product="grants")

    def test_scrub_fault_propagates_and_never_permits(self):
        def bad_scrub():
            raise RuntimeError("Scrub must be repaired")
        with self.assertRaisesRegex(RuntimeError, "Scrub must be repaired"):
            revalidate_or_revoke(lambda: None, bad_scrub, product="grants")

    def test_review_ui_auth_calls_use_scope_in_both_positions(self):
        ui = Path(__file__).resolve().parents[1] / "fvs_suite" / "review_ui.py"
        tree = ast.parse(ui.read_text(encoding="utf-8"))
        checks = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                  and isinstance(n.func, ast.Name) and n.func.id == "revalidate_or_revoke"]
        self.assertEqual(len(checks), 2)
        for call in checks:
            scope = [k.value for k in call.keywords if k.arg == "product"]
            self.assertEqual(len(scope), 1)
            self.assertIsInstance(scope[0], ast.Name)
            self.assertEqual(scope[0].id, "product")

    def test_no_unscoped_compatibility_path_remains_in_gate(self):
        path = Path(__file__).resolve().parents[1] / "fvs_suite" / "review_target.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        gate = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                    and n.name == "revalidate_or_revoke")
        self.assertEqual([a.arg for a in gate.args.kwonlyargs], ["product"])
        self.assertEqual(gate.args.kw_defaults, [None])
        self.assertNotIn("_LEGACY_UNSCOPED", source)
        self.assertNotIn("bool(proof)", source)


if __name__ == "__main__":
    unittest.main()
