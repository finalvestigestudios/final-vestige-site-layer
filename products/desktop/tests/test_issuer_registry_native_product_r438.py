"""R438: both premium issuer paths must reject nonnative product identity.

All files, identities and hashes are synthetic. No signing keys, customers,
payment flow, entitlement delivery or approved premium distribution involved.
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import license_issuer as issuer
import license_registry as registry


NOW = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)
EXPIRES = "2027-11-14T12:00:00Z"


class SameText(str):
    """Equal text is not equivalent to an approved built-in identifier."""


class PoisonProduct(str):
    def __hash__(self):
        raise AssertionError("FORBIDDEN_PRODUCT_HASH_HOOK")

    def __eq__(self, other):
        raise AssertionError("FORBIDDEN_PRODUCT_EQUALITY_HOOK")

    def __format__(self, spec):
        raise AssertionError("FORBIDDEN_PRODUCT_FORMAT_HOOK")


class ForgedEqual(str):
    """Would impersonate 'grants' if a frozenset invokes custom equality."""
    def __hash__(self):
        return hash("grants")

    def __eq__(self, other):
        return True

    def __format__(self, spec):
        raise AssertionError("FORBIDDEN_PRODUCT_FORMAT_HOOK")


class R438NativeIssuerRegistryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        if os.name == "posix":
            self.root.chmod(0o700)
        self.destination = self.root / "synthetic.fvslicense"
        self.ledger = registry.IssuanceRegistry(self.root / "synthetic.sqlite3")
        self.issuer_args = {
            "key_path": self.root / "NO-KEY-READ.pem",
            "password": b"synthetic-only",
            "kid": "issuer-r438",
            "license_id": "license-r438",
            "holder": "Synthetic Operator",
            "expires_at": EXPIRES,
            "output": self.destination,
            "now": NOW,
        }
        self.registry_args = {
            "license_id": "license-r438",
            "kid": "issuer-r438",
            "output": self.destination,
        }

    def rejected(self, exception, cls, phrase):
        self.assertIs(type(exception), cls)
        self.assertIn(phrase, str(exception))
        self.assertIsNone(exception.__cause__)
        self.assertIsNone(exception.__context__)

    def test_issuer_rejects_equal_text_subclasses_before_private_key(self):
        for name in ("grants", "procurement"):
            with self.subTest(name=name):
                with patch.object(issuer, "_key_from_encrypted_pem",
                                  side_effect=AssertionError("KEY_MUST_NOT_BE_TOUCHED")) as key:
                    with self.assertRaises(issuer.IssuanceError) as caught:
                        issuer.issue_entitlement(product=SameText(name), **self.issuer_args)
                    self.rejected(caught.exception, issuer.IssuanceError, "Unknown premium product")
                    key.assert_not_called()
                self.assertFalse(self.destination.exists())

    def test_issuer_rejects_hostile_hash_and_equality_without_calling_hooks(self):
        for value in (PoisonProduct("grants"), ForgedEqual("unrecognized")):
            with self.subTest(kind=type(value).__name__):
                with patch.object(issuer, "_key_from_encrypted_pem",
                                  side_effect=AssertionError("MUST_NOT_ACCESS_KEY")) as key:
                    with self.assertRaises(issuer.IssuanceError) as caught:
                        issuer.issue_entitlement(product=value, **self.issuer_args)
                    self.rejected(caught.exception, issuer.IssuanceError, "Unknown premium product")
                    key.assert_not_called()
                self.assertFalse(self.destination.exists())

    def test_issuer_rejects_non_strings_without_accessing_private_material(self):
        for value in (None, 0, False, b"grants", ["grants"], {"product": "grants"}):
            with self.subTest(kind=type(value).__name__):
                with patch.object(issuer, "_key_from_encrypted_pem",
                                  side_effect=AssertionError("MUST_NOT_ACCESS_KEY")) as key:
                    with self.assertRaises(issuer.IssuanceError) as caught:
                        issuer.issue_entitlement(product=value, **self.issuer_args)
                    self.rejected(caught.exception, issuer.IssuanceError, "Unknown premium product")
                    key.assert_not_called()

    def test_issuer_rejects_unknown_native_identifiers(self):
        for value in ("", "GRANTS", "grants ", "ledger", "grant/../procurement"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(issuer.IssuanceError, "Unknown premium product"):
                    issuer.issue_entitlement(product=value, **self.issuer_args)
                self.assertFalse(self.destination.exists())

    def test_issuer_native_products_reach_guarded_key_loading(self):
        class KeyReached(Exception):
            pass
        for value in ("grants", "procurement"):
            with self.subTest(value=value):
                with patch.object(issuer, "_key_from_encrypted_pem",
                                  side_effect=KeyReached) as key:
                    with self.assertRaises(KeyReached):
                        issuer.issue_entitlement(product=value, **self.issuer_args)
                    key.assert_called_once()
                self.assertFalse(self.destination.exists())

    def test_reserve_rejects_built_in_text_subclasses_before_db(self):
        for value in (SameText("grants"), SameText("procurement")):
            with self.subTest(value=str(value)):
                with patch.object(self.ledger, "_db",
                                  side_effect=AssertionError("DB_MUST_NOT_OPEN")) as db:
                    with self.assertRaises(registry.RegistryError) as caught:
                        self.ledger.reserve(product=value, **self.registry_args)
                    self.rejected(caught.exception, registry.RegistryError, "Unknown premium product")
                    db.assert_not_called()
                self.assertFalse(self.ledger.path.exists())

    def test_reserve_does_not_call_forged_hash_or_equality(self):
        for value in (PoisonProduct("grants"), ForgedEqual("not-a-premium-product")):
            with self.subTest(kind=type(value).__name__):
                with patch.object(self.ledger, "_db",
                                  side_effect=AssertionError("DB_MUST_NOT_OPEN")) as db:
                    with self.assertRaises(registry.RegistryError) as caught:
                        self.ledger.reserve(product=value, **self.registry_args)
                    self.rejected(caught.exception, registry.RegistryError, "Unknown premium product")
                    db.assert_not_called()

    def test_reserve_rejects_non_string_and_unknown_values_before_db(self):
        for value in (None, True, ["grants"], {"x": "grants"}, b"grants", "free"):
            with self.subTest(kind=type(value).__name__):
                with patch.object(self.ledger, "_db",
                                  side_effect=AssertionError("DB_MUST_NOT_OPEN")) as db:
                    with self.assertRaises(registry.RegistryError) as caught:
                        self.ledger.reserve(product=value, **self.registry_args)
                    self.rejected(caught.exception, registry.RegistryError, "Unknown premium product")
                    db.assert_not_called()

    def test_finalize_rejects_forged_product_before_reading_issued_file(self):
        for value in (SameText("grants"), SameText("procurement"),
                      PoisonProduct("grants"), ForgedEqual("other")):
            with self.subTest(kind=type(value).__name__):
                with patch.object(registry, "fingerprint_issued_entitlement",
                                  side_effect=AssertionError("MUST_NOT_READ_FILE")) as read:
                    with self.assertRaises(registry.RegistryError) as caught:
                        self.ledger.finalize(product=value, expected_sha256="0" * 64,
                                             **self.registry_args)
                    self.rejected(caught.exception, registry.RegistryError, "Unknown premium product")
                    read.assert_not_called()
                self.assertFalse(self.ledger.path.exists())

    def test_finalize_rejects_non_string_and_unknown_products_without_io(self):
        for value in (None, False, b"grants", ["grants"], {"x": "grants"}, "free"):
            with self.subTest(kind=type(value).__name__):
                with patch.object(registry, "fingerprint_issued_entitlement",
                                  side_effect=AssertionError("MUST_NOT_READ_FILE")) as read:
                    with self.assertRaises(registry.RegistryError) as caught:
                        self.ledger.finalize(product=value, expected_sha256="0" * 64,
                                             **self.registry_args)
                    self.rejected(caught.exception, registry.RegistryError, "Unknown premium product")
                    read.assert_not_called()

    def test_both_native_products_reserve_and_finalize_synthetic_bytes(self):
        # This proves registry custody, NOT a signed license or distribution.
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                destination = self.root / (product + ".fvslicense")
                license_id = "synthetic-" + product
                self.ledger.reserve(product=product, kid="issuer-r438",
                                    license_id=license_id, output=destination)
                payload = ("offline-r438-" + product).encode("ascii")
                destination.write_bytes(payload)
                digest = self.ledger.finalize(product=product, kid="issuer-r438",
                                              license_id=license_id, output=destination,
                                              expected_sha256=hashlib.sha256(payload).hexdigest())
                self.assertEqual(digest, hashlib.sha256(payload).hexdigest())

    def test_invalid_finalization_still_requires_exact_signed_hash(self):
        destination = self.root / "grants.fvslicense"
        self.ledger.reserve(product="grants", kid="issuer-r438",
                            license_id="synthetic-grants", output=destination)
        destination.write_bytes(b"synthetic-not-a-license")
        with self.assertRaisesRegex(registry.RegistryError, "differs"):
            self.ledger.finalize(product="grants", kid="issuer-r438",
                                 license_id="synthetic-grants", output=destination,
                                 expected_sha256="0" * 64)

    def test_issuer_and_registry_share_builtin_products(self):
        self.assertEqual(issuer.verifier.PRODUCTS, registry.PRODUCTS)
        self.assertEqual(issuer.verifier.PRODUCTS, frozenset({"grants", "procurement"}))


if __name__ == "__main__":
    unittest.main()
