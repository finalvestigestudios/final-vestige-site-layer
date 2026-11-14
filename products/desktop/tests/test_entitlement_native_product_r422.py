"""R422: protect signed-license product selection from forged Python text objects.

Tests use ephemeral Ed25519 keys and synthetic documents, never release keys,
customer data, actual license issuance, paid downloads or an EXE.
"""
from __future__ import annotations

import ast
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fvs_suite import offline_entitlement as license


NOW = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)


class NativeLicenseProductR422(unittest.TestCase):
    def test_both_native_products_preserve_exact_identity(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                self.assertIs(license._require_native_premium_product(product), product)

    def test_unknown_native_products_fail_closed(self):
        for product in ("", "ledger", "GRANTS", "grants ", "../grants"):
            with self.subTest(product=product):
                with self.assertRaisesRegex(license.EntitlementError, "Unknown premium application"):
                    license._require_native_premium_product(product)

    def test_non_string_values_fail_without_coercion(self):
        for product in (None, False, True, 1, b"grants", ["grants"], {"product": "grants"}):
            with self.subTest(kind=type(product).__name__):
                with self.assertRaises(license.EntitlementError):
                    license._require_native_premium_product(product)

    def test_subclass_with_equivalent_text_is_not_native(self):
        class SameText(str):
            pass
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                with self.assertRaises(license.EntitlementError):
                    license._require_native_premium_product(SameText(product))

    def test_subclass_hash_equality_and_format_hooks_are_not_invoked(self):
        class Hostile(str):
            def __hash__(self):
                raise AssertionError("PRIVATE_HASH_HOOK")
            def __eq__(self, other):
                raise AssertionError("PRIVATE_EQUALITY_HOOK")
            def __format__(self, spec):
                raise AssertionError("PRIVATE_FORMAT_HOOK")
        product = Hostile("grants")
        for action in (
            lambda: license._require_native_premium_product(product),
            lambda: license.installed_license_path(product),
            lambda: license.verify_license("DO_NOT_READ", product, trusted_keys={"test": b"x" * 32},
                                           now=NOW),
        ):
            with self.subTest(action=action.__code__.co_firstlineno):
                with self.assertRaisesRegex(license.EntitlementError, "Unknown premium application"):
                    action()

    def test_equal_hash_forgery_cannot_redirect_installed_path(self):
        class Forged(str):
            def __hash__(self):
                return hash("grants")
            def __eq__(self, other):
                return True
            def __ne__(self, other):
                return False
            def __format__(self, spec):
                return "../redirected"
        with self.assertRaisesRegex(license.EntitlementError, "Unknown premium application"):
            license.installed_license_path(Forged("attacker-controlled"))

    def test_forged_product_denied_before_reader_even_with_trusted_keys(self):
        class Forged(str):
            def __hash__(self):
                return hash("grants")
            def __eq__(self, other):
                return True
            def __ne__(self, other):
                return False
        with patch.object(license, "_read_signed_entitlement",
                          side_effect=AssertionError("MUST_NOT_READ_LICENSE")) as read:
            with self.assertRaisesRegex(license.EntitlementError, "Unknown premium application"):
                license.verify_license("DO_NOT_READ", Forged("other"), now=NOW,
                                       trusted_keys={"test": b"x" * 32})
            read.assert_not_called()

    def test_invalid_native_product_denied_before_reader(self):
        with patch.object(license, "_read_signed_entitlement",
                          side_effect=AssertionError("MUST_NOT_READ_LICENSE")) as read:
            with self.assertRaisesRegex(license.EntitlementError, "Unknown premium application"):
                license.verify_license("DO_NOT_READ", "ledger", now=NOW,
                                       trusted_keys={"test": b"x" * 32})
            read.assert_not_called()

    def test_invalid_non_native_product_denied_even_when_unactivated(self):
        class Forged(str):
            def __hash__(self):
                return hash("grants")
            def __eq__(self, other):
                return True
        with self.assertRaisesRegex(license.EntitlementError, "Unknown premium application"):
            license.verify_license("DO_NOT_READ", Forged("other"), now=NOW)

    def test_native_install_paths_remain_unchanged(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                path = license.installed_license_path(product)
                self.assertIsInstance(path, Path)
                self.assertEqual(path.name, f"{product}.fvslicense")
                self.assertEqual(path.parent.name, "licenses")
                self.assertEqual(path.parent.parent.name, "FinalVestige")

    def test_native_products_still_verify_real_ephemeral_ed25519_signatures(self):
        key = Ed25519PrivateKey.generate()
        pub = key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        document = {
            "schema": license.SCHEMA, "kid": "ephemeral-r422",
            "product": "grants", "license_id": "demo-r422", "holder": "Synthetic Buyer",
            "issued_at": "2026-11-01T00:00:00Z", "not_before": "2026-11-01T00:00:00Z",
            "expires_at": "2027-11-01T00:00:00Z",
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "synthetic.fvslicense"
            for product in ("grants", "procurement"):
                with self.subTest(product=product):
                    document["product"] = product
                    signed = {**document, "signature": base64.urlsafe_b64encode(
                        key.sign(license._canonical_payload(document))).decode("ascii").rstrip("=")}
                    path.write_text(json.dumps(signed, sort_keys=True), encoding="utf-8")
                    result = license.verify_license(path, product,
                                                    trusted_keys={"ephemeral-r422": pub}, now=NOW)
                    self.assertIs(type(result.product), str)
                    self.assertEqual(result.product, product)

    def test_legitimate_signature_is_not_interchangeable_across_products(self):
        key = Ed25519PrivateKey.generate()
        pub = key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        data = {"schema": license.SCHEMA, "kid": "ephemeral-r422", "product": "grants",
                "license_id": "demo-r422", "holder": "Synthetic Buyer",
                "issued_at": "2026-11-01T00:00:00Z", "not_before": "2026-11-01T00:00:00Z",
                "expires_at": "2027-11-01T00:00:00Z"}
        signature = base64.urlsafe_b64encode(key.sign(
            license._canonical_payload(data))).decode("ascii").rstrip("=")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "synthetic.fvslicense"
            path.write_text(json.dumps({**data, "signature": signature}), encoding="utf-8")
            with self.assertRaisesRegex(license.EntitlementError, "product does not match"):
                license.verify_license(path, "procurement",
                                       trusted_keys={"ephemeral-r422": pub}, now=NOW)

    def test_both_production_paths_call_the_same_guard_first(self):
        source = Path(license.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        for method in ("installed_license_path", "verify_license"):
            with self.subTest(method=method):
                body = functions[method].body
                self.assertIsInstance(body[0], ast.Expr)  # Docstring
                self.assertIsInstance(body[1], ast.Assign)
                call = body[1].value
                self.assertIsInstance(call, ast.Call)
                self.assertIsInstance(call.func, ast.Name)
                self.assertEqual(call.func.id, "_require_native_premium_product")

    def test_issuer_authority_remains_unconfigured(self):
        self.assertEqual(license.TRUSTED_PUBLIC_KEYS, {})


if __name__ == "__main__":
    unittest.main()
