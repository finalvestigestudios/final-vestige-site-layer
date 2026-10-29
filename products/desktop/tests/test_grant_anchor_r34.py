"""R34: independent, operator-retained SHA-256 inventory pin verification.

All source fixtures are synthetic; no customer records, network, or encryption
keys are used. This suite intentionally distinguishes unpinned consistency
from evidence anchored to a separately retained digest.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.grant_anchor import verify_inventory_pin
from fvs_suite.grant_verify import main, verify_grant_bundle
from fvs_suite.manifest_guard import inventory_text


class GrantAnchorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = self.root / "grant-evidence-synthetic"
        self.package.mkdir()
        self.claims = self.root / "claims.csv"
        self.ledger = self.root / "ledger.csv"
        self.budgets = self.root / "budgets.csv"
        self.report = self.package / "grant-audit-exceptions-20261029-110000-000001.csv"
        self.review = self.package / "grant-budget-check-20261029-110000-000001.csv"
        self.inventory = self.package / "evidence-manifest-20261029-110000-000001.txt"
        for path, value in (
            (self.claims, b"id,amount\nA,10.00\n"),
            (self.ledger, b"id,amount\nA,10.00\n"),
            (self.budgets, b"program,budget\nG,100.00\n"),
            (self.report, b"exception,status\nA,review\n"),
            (self.review, b"program,amount\nG,10.00\n"),
        ):
            path.write_bytes(value)
        self.make_manifest()
        self.original_pin = hashlib.sha256(self.inventory.read_bytes()).hexdigest()

    def make_manifest(self):
        self.inventory.write_bytes(
            inventory_text(
                [self.claims, self.ledger, self.budgets],
                [self.report, self.review],
            ).encode("utf-8")
        )

    def verify(self, pin=None):
        return verify_grant_bundle(
            self.package, self.claims, self.ledger, self.budgets,
            expected_inventory_sha256=pin,
        )

    def cli(self, *args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main([
                *args, str(self.package), str(self.claims),
                str(self.ledger), str(self.budgets),
            ])
        return exit_code, stdout.getvalue()

    def test_valid_independent_pin_matches(self):
        self.assertIs(self.verify(self.original_pin), True)

    def test_legacy_unpinned_check_remains_consistent(self):
        self.assertIs(self.verify(), True)

    def test_incorrect_well_formed_pin_rejected(self):
        bad = ("0" if self.original_pin[0] != "0" else "1") + self.original_pin[1:]
        with self.assertRaisesRegex(ValueError, "pin does not match"):
            self.verify(bad)

    def test_malformed_pin_rejected_without_leaking_value(self):
        for malformed in ("", "a" * 63, "A" * 64, "f" * 65,
                          "f" * 63 + "\n", "f" * 63 + " ",
                          "f" * 60 + "€€", "f" * 63 + "\x00", 123, b"f" * 64):
            with self.subTest(malformed=type(malformed).__name__):
                with self.assertRaisesRegex(ValueError, "Invalid trusted inventory") as err:
                    self.verify(malformed)
                if malformed:
                    self.assertNotIn(str(malformed), str(err.exception))
                self.assertNotIn(str(self.root), str(err.exception))

    def test_empty_bytes_inventory_rejected_for_incorrect_pin(self):
        with self.assertRaisesRegex(ValueError, "pin does not match"):
            verify_inventory_pin(b"", "0" * 64)

    def test_helper_rejects_nonbytes_inventory(self):
        with self.assertRaisesRegex(ValueError, "Invalid evidence inventory bytes"):
            verify_inventory_pin("private report", self.original_pin)

    def test_anchor_detects_coordinated_evidence_and_manifest_rewrite(self):
        # R33 deliberately accepts a self-consistent rewritten *plaintext*
        # inventory. R34 adds detection only with an independently saved pin.
        self.claims.write_bytes(b"id,amount\nA,90.00\n")
        self.report.write_bytes(b"exception,status\nA,approved\n")
        self.make_manifest()
        self.assertIs(self.verify(), True)
        with self.assertRaisesRegex(ValueError, "pin does not match"):
            self.verify(self.original_pin)

    def test_anchor_rejects_rewritten_manifest_even_when_other_bytes_unchanged(self):
        self.make_manifest()
        self.inventory.write_bytes(self.inventory.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "pin does not match"):
            self.verify(self.original_pin)

    def test_valid_pin_does_not_override_other_evidence_mismatch(self):
        self.report.write_bytes(self.report.read_bytes().replace(b"review", b"accept"))
        with self.assertRaisesRegex(ValueError, "does not match current files"):
            self.verify(self.original_pin)

    def test_valid_pin_cannot_override_missing_source(self):
        self.budgets.unlink()
        with self.assertRaises(ValueError):
            self.verify(self.original_pin)

    def test_validation_does_not_mutate_any_files(self):
        files = [self.claims, self.ledger, self.budgets,
                 self.report, self.review, self.inventory]
        before = [p.read_bytes() for p in files]
        self.verify(self.original_pin)
        self.assertEqual(before, [p.read_bytes() for p in files])

    def test_cli_prints_explicit_pinned_status_without_paths_or_digest(self):
        code, out = self.cli("--expected-inventory-sha256", self.original_pin)
        self.assertEqual(code, 0)
        self.assertIn("CONSISTENT (PINNED)", out)
        self.assertIn("human review", out)
        self.assertNotIn(self.original_pin, out)
        self.assertNotIn(str(self.root), out)

    def test_cli_warns_when_consistency_is_unpinned(self):
        code, out = self.cli()
        self.assertEqual(code, 0)
        self.assertIn("CONSISTENT (UNPINNED)", out)
        self.assertIn("no authenticity anchor", out)
        self.assertNotIn(str(self.root), out)

    def test_cli_rejects_wrong_pin_with_sanitized_output(self):
        code, out = self.cli("--expected-inventory-sha256", "0" * 64)
        self.assertEqual(code, 1)
        self.assertIn("INVALID", out)
        self.assertNotIn(str(self.root), out)

    def test_cli_rejects_malformed_pin_with_sanitized_output(self):
        secret = "THIS_IS_NOT_A_HASH_private-ledger"
        code, out = self.cli("--expected-inventory-sha256", secret)
        self.assertEqual(code, 1)
        self.assertNotIn(secret, out)
        self.assertNotIn(str(self.root), out)

    def test_concurrent_inventory_change_still_rejected_with_valid_pin(self):
        from fvs_suite import grant_verify
        original = grant_verify.inventory_text
        def switch(*args, **kwargs):
            result = original(*args, **kwargs)
            self.inventory.write_bytes(b"tampered after first snapshot")
            return result
        with patch.object(grant_verify, "inventory_text", side_effect=switch):
            with self.assertRaisesRegex(ValueError, "changed during verification"):
                self.verify(self.original_pin)

    def test_anchor_helper_accepts_only_actual_correct_inventory_bytes(self):
        original = self.inventory.read_bytes()
        self.assertIsNone(verify_inventory_pin(original, self.original_pin))
        with self.assertRaisesRegex(ValueError, "pin does not match"):
            verify_inventory_pin(original + b" ", self.original_pin)


if __name__ == "__main__":
    unittest.main()
