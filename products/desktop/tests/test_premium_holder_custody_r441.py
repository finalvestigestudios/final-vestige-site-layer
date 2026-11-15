"""R441: real signed premium holder Unicode, identity, and pre-key-write custody.

All keys are ephemeral in-memory, all paths synthetic. No issuance, activation,
customer identities or public distribution. Full-module tests require the repo.
"""
from __future__ import annotations

import base64
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import license_issuer as issuer
from fvs_suite import offline_entitlement as verifier
from fvs_suite.holder_identity import valid_holder

NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)
STAMP = "2026-10-28T12:00:00Z"
END = "2027-10-28T12:00:00Z"


class PremiumHolderDisplayR441Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="r441-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.key = Ed25519PrivateKey.generate()
        from cryptography.hazmat.primitives import serialization
        self.pub = self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def _signed(self, holder, product):
        item = {"schema": verifier.SCHEMA, "kid": "r441-test-kid",
                "product": product, "license_id": "r441-test-license",
                "holder": holder, "issued_at": STAMP,
                "not_before": STAMP, "expires_at": END}
        sig = self.key.sign(verifier._canonical_payload(item))
        item["signature"] = base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")
        return (json.dumps(item, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False) + "\n").encode("utf-8")

    def _verify(self, holder, product):
        signed = self._signed(holder, product)
        with patch.object(verifier, "_read_signed_entitlement", return_value=signed):
            return verifier.verify_license(self.root / "nonexistent.fvslicense", product,
                                           trusted_keys={"r441-test-kid": self.pub}, now=NOW)

    def test_both_premium_products_accept_signed_visible_international_names(self):
        for product in ("grants", "procurement"):
            for holder in ("Société de recherche", "شركة الأبحاث", "株式会社サンプル"):
                with self.subTest(product=product, holder=holder):
                    self.assertEqual(self._verify(holder, product).holder, holder)

    def test_both_premium_products_refuse_even_validly_signed_hidden_formatting(self):
        for product in ("grants", "procurement"):
            for holder in ("Acme\u202eLtd", "Acme\u200bLtd", "Acme\u2066Ltd",
                           "Acme\u0085Ltd", "Acme\u2028Ltd"):
                with self.subTest(product=product, holder=ascii(holder)):
                    with self.assertRaisesRegex(verifier.EntitlementError, "holder"):
                        self._verify(holder, product)

    def test_issuer_denies_unsafe_holder_before_private_key_or_output(self):
        target = self.root / "synthetic.fvslicense"
        args = dict(key_path=self.root / "nonexistent-key.pem", password=b"test-only",
                    kid="r441-test-kid", product="grants", license_id="r441-test-license",
                    expires_at=END, output=target, now=NOW)
        with patch.object(issuer, "_key_from_encrypted_pem") as signing_key:
            for holder in ("Acme\u202eLtd", "Acme\u200dLtd", "Acme\u2029Ltd", "Acme\u007fLtd"):
                with self.subTest(holder=ascii(holder)):
                    with self.assertRaisesRegex(issuer.IssuanceError, "Invalid holder") as error:
                        issuer.issue_entitlement(holder=holder, **args)
                    self.assertIsNone(error.exception.__context__)
                    self.assertFalse(target.exists())
            signing_key.assert_not_called()

    def test_issuer_refuses_malicious_str_subclass_before_overridden_methods(self):
        class ForgedHolder(str):
            def strip(self, *args, **kwargs):
                raise AssertionError("Must not execute input object's overridden strip")
        with self.assertRaisesRegex(issuer.IssuanceError, "Invalid holder"):
            issuer._validate_text(ForgedHolder("Acme"), "holder")

    def test_issuer_and_verifier_share_same_pure_validation(self):
        self.assertIs(issuer.valid_holder, verifier.valid_holder)
        for name in ("Société de recherche", "شركة الأبحاث"):
            self.assertTrue(valid_holder(name))
            issuer._validate_text(name, "holder")
        self.assertFalse(valid_holder("Acme\u202eLtd"))
        with self.assertRaises(issuer.IssuanceError):
            issuer._validate_text("Acme\u202eLtd", "holder")


if __name__ == "__main__":
    unittest.main()
