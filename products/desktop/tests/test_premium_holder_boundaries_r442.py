"""R442: both premium products reject signed visually ambiguous holders.

All keys are ephemeral, names synthetic, and signed files stay in memory.
This suite requires full desktop modules; no real licenses are issued.
"""
from __future__ import annotations

import base64
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import license_issuer as issuer
from fvs_suite import offline_entitlement as verifier
from fvs_suite.holder_identity import valid_holder

NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)
STAMP = "2026-10-28T12:00:00Z"
END = "2027-10-28T12:00:00Z"
UNSAFE = ("Acme\u00a0Ltd", "Acme\u202fLtd", "Acme\u3000Ltd",
          "Acme\ufe0fLtd", "Acme\U000e0100Ltd", "Acme\ufdd0Ltd",
          "Acme\ufffeLtd", "Acme\U0010ffffLtd")


class PremiumHolderBoundariesR442(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="r442-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.private = Ed25519PrivateKey.generate()
        self.public = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def _verify_signed(self, holder: str, product: str):
        item = {"schema": verifier.SCHEMA, "kid": "r442-test-kid",
                "product": product, "license_id": "r442-test-license",
                "holder": holder, "issued_at": STAMP,
                "not_before": STAMP, "expires_at": END}
        signature = self.private.sign(verifier._canonical_payload(item))
        item["signature"] = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
        payload = (json.dumps(item, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":")) + "\n").encode("utf-8")
        with patch.object(verifier, "_read_signed_entitlement", return_value=payload):
            return verifier.verify_license(self.root / "not-on-disk.fvslicense", product,
                                           trusted_keys={"r442-test-kid": self.public}, now=NOW)

    def test_both_products_reject_validly_signed_ambiguous_holders(self):
        for product in ("grants", "procurement"):
            for holder in UNSAFE:
                with self.subTest(product=product, holder=ascii(holder)):
                    with self.assertRaisesRegex(verifier.EntitlementError, "holder") as refused:
                        self._verify_signed(holder, product)
                    self.assertIsNone(refused.exception.__context__)

    def test_both_products_keep_visible_signed_names_without_normalizing(self):
        for product in ("grants", "procurement"):
            for holder in ("Acme Ltd", "Société de recherche", "شركة الأبحاث",
                           "株式会社サンプル", "A\u0301cme"):
                with self.subTest(product=product, holder=holder):
                    self.assertEqual(self._verify_signed(holder, product).holder, holder)

    def test_issuer_refuses_ambiguous_names_before_key_read_and_output(self):
        args = dict(key_path=self.root / "missing-private.pem", password=b"synthetic",
                    kid="r442-test-kid", license_id="r442-test-license",
                    expires_at=END, now=NOW, output=self.root / "never.fvslicense")
        with patch.object(issuer, "_key_from_encrypted_pem") as key_reader:
            for product in ("grants", "procurement"):
                for holder in UNSAFE:
                    with self.subTest(product=product, holder=ascii(holder)):
                        with self.assertRaisesRegex(issuer.IssuanceError, "Invalid holder"):
                            issuer.issue_entitlement(product=product, holder=holder, **args)
                        self.assertFalse(args["output"].exists())
            key_reader.assert_not_called()

    def test_issuer_and_verifier_share_pure_boundary(self):
        self.assertIs(issuer.valid_holder, verifier.valid_holder)
        for holder in UNSAFE:
            with self.subTest(holder=ascii(holder)):
                self.assertFalse(valid_holder(holder))
                with self.assertRaisesRegex(issuer.IssuanceError, "Invalid holder"):
                    issuer._validate_text(holder, "holder")


if __name__ == "__main__":
    unittest.main()
