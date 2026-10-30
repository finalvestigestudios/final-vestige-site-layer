"""R50: entitlement signature verification must use stable local file bytes.

Synthetic test-only Ed25519 keys, no production credentials/customer records.
"""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fvs_suite import offline_entitlement as license
from fvs_suite import journal_io

NOW = datetime(2026, 10, 28, tzinfo=timezone.utc)


class EntitlementCustodyR50Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-license-r50-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.path = self.root / "entitlement.fvslicense"
        self.key = Ed25519PrivateKey.generate()
        self.keys = {"r50-test-only-key": self.key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )}
        self.product = "grants"
        self.write_signed()

    def write_signed(self, *, product="grants", license_id="r50-test-license-01"):
        item = {
            "schema": license.SCHEMA,
            "kid": "r50-test-only-key",
            "product": product,
            "license_id": license_id,
            "holder": "Synthetic Offline Test User",
            "issued_at": "2026-10-01T00:00:00Z",
            "not_before": "2026-10-01T00:00:00Z",
            "expires_at": "2027-10-01T00:00:00Z",
        }
        signed = self.key.sign(license._canonical_payload(item))
        item["signature"] = base64.urlsafe_b64encode(signed).decode("ascii").rstrip("=")
        self.path.write_text(json.dumps(item, sort_keys=True), encoding="utf-8")
        return self.path

    def verify(self, path=None, *, product=None):
        return license.verify_license(
            self.path if path is None else path,
            self.product if product is None else product,
            trusted_keys=self.keys,
            now=NOW,
        )

    def test_real_ed25519_license_still_passes_for_grants(self):
        self.assertEqual(self.verify().license_id, "r50-test-license-01")

    def test_real_ed25519_license_still_passes_for_procurement(self):
        self.write_signed(product="procurement")
        self.assertEqual(self.verify(product="procurement").product, "procurement")

    def test_license_bytes_are_exact_and_not_modified(self):
        before = self.path.read_bytes()
        self.assertEqual(license._read_signed_entitlement(self.path), before)
        self.verify()
        self.assertEqual(self.path.read_bytes(), before)

    def test_empty_license_fails_closed(self):
        self.path.write_bytes(b"")
        with self.assertRaises(license.EntitlementError):
            self.verify()

    def test_missing_file_is_rejected_as_entitlement_error(self):
        self.path.unlink()
        with self.assertRaises(license.EntitlementError):
            self.verify()

    def test_directory_is_not_an_entitlement(self):
        with self.assertRaisesRegex(license.EntitlementError, "regular file"):
            self.verify(self.root)

    def test_oversized_license_is_rejected_before_parsing(self):
        self.path.write_bytes(b"z" * (license.MAX_BYTES + 1))
        with self.assertRaisesRegex(license.EntitlementError, "size limit"):
            self.verify()

    def test_symlink_is_not_a_licensed_document(self):
        target = self.root / "real.fvslicense"
        self.path.rename(target)
        try:
            self.path.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        with self.assertRaisesRegex(license.EntitlementError, "regular file"):
            self.verify()
        self.assertTrue(target.exists())

    def test_hardlink_alias_is_not_a_licensed_document(self):
        alias = self.root / "extra-hardlink.fvslicense"
        try:
            os.link(self.path, alias)
        except OSError:
            self.skipTest("hardlink creation unavailable")
        with self.assertRaisesRegex(license.EntitlementError, "regular file"):
            self.verify()
        self.assertEqual(alias.read_bytes(), self.path.read_bytes())

    @unittest.skipIf(os.name == "nt", "Windows may deny pathname replacement while open")
    def test_same_size_replacement_between_stat_and_open_is_rejected(self):
        backup = self.root / "old.fvslicense"
        alternate = self.root / "alternate.fvslicense"
        original = self.path.read_bytes()
        self.write_signed(license_id="r50-test-license-02")
        self.path.rename(alternate)
        self.path.write_bytes(original)
        actual_open = os.open
        swapped = False

        def swap_before_open(path, flags, *args):
            nonlocal swapped
            if Path(path) == self.path and not swapped:
                swapped = True
                self.path.rename(backup)
                os.replace(alternate, self.path)
            return actual_open(path, flags, *args)

        with patch.object(journal_io.os, "open", side_effect=swap_before_open):
            with self.assertRaises(license.EntitlementError):
                self.verify()
        self.assertTrue(swapped)
        self.assertEqual(backup.read_bytes(), original)

    @unittest.skipIf(os.name == "nt", "Windows may deny a concurrent write to an open file")
    def test_same_bytes_rewritten_during_read_are_rejected(self):
        original = self.path.read_bytes()
        actual_fdopen = os.fdopen
        modified = False

        def rewrite_during_read(*args, **kwargs):
            nonlocal modified
            if not modified:
                modified = True
                with self.path.open("wb") as stream:
                    stream.write(original)
                    stream.flush()
                    os.fsync(stream.fileno())
            return actual_fdopen(*args, **kwargs)

        with patch.object(journal_io.os, "fdopen", side_effect=rewrite_during_read):
            with self.assertRaises(license.EntitlementError):
                self.verify()
        self.assertTrue(modified)

    def test_open_permission_errors_do_not_expose_private_paths(self):
        secret = "PRIVATE_FINANCIAL_CUSTOMER_99177"
        with patch.object(journal_io.os, "open", side_effect=PermissionError(secret)):
            with self.assertRaises(license.EntitlementError) as found:
                self.verify()
        self.assertNotIn(secret, str(found.exception))
        self.assertNotIn(str(self.root), str(found.exception))

    def test_missing_authority_rejects_before_any_disk_read(self):
        with patch.object(license, "_read_signed_entitlement", side_effect=AssertionError("must not read")):
            with self.assertRaisesRegex(license.EntitlementError, "not activated"):
                license.verify_license(self.path, "grants", now=NOW)

    def test_mismatched_signed_product_remains_rejected(self):
        self.write_signed(product="procurement")
        with self.assertRaisesRegex(license.EntitlementError, "product does not match"):
            self.verify(product="grants")

    def test_malformed_license_has_no_signature_bypass(self):
        self.path.write_bytes(b'{"schema":"untrusted"}')
        with self.assertRaises(license.EntitlementError):
            self.verify()

    def test_reader_is_called_once_with_fixed_bounded_kind(self):
        payload = self.path.read_bytes()
        with patch.object(license, "read_regular_bytes", return_value=payload) as read:
            self.verify()
        read.assert_called_once_with(self.path, license.MAX_BYTES, "Entitlement file")


if __name__ == "__main__":
    unittest.main()
