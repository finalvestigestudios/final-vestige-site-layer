"""R33: independent read-only consistency verification for GrantAudit bundles."""
from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.grant_verify import main, verify_grant_bundle
from fvs_suite.manifest_guard import inventory_text


class GrantVerifyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = self.root / "grant-evidence-example"
        self.package.mkdir()
        self.claims = self.root / "claims.csv"
        self.ledger = self.root / "ledger.csv"
        self.budgets = self.root / "budgets.csv"
        for filename, body in (
            (self.claims, "id,amount\nA,10.00\n"),
            (self.ledger, "id,amount\nA,10.00\n"),
            (self.budgets, "program,budget\nG,100.00\n"),
        ):
            filename.write_text(body, encoding="utf-8")
        self.report = self.package / "grant-audit-exceptions-20261029-092000-000001.csv"
        self.review = self.package / "grant-budget-check-20261029-092000-000001.csv"
        self.inventory = self.package / "evidence-manifest-20261029-092000-000001.txt"
        self.report.write_bytes(b"exception,status\nA,review\n")
        self.review.write_bytes(b"program,amount\nG,10.00\n")
        self.refresh_inventory()

    def refresh_inventory(self):
        self.inventory.write_text(
            inventory_text([self.claims, self.ledger, self.budgets], [self.report, self.review]),
            encoding="utf-8", newline="",
        )

    def verify(self):
        return verify_grant_bundle(self.package, self.claims, self.ledger, self.budgets)

    def test_valid_bundle_returns_true(self):
        self.assertIs(self.verify(), True)

    def test_verifier_does_not_edit_any_files(self):
        files = [self.claims, self.ledger, self.budgets, self.report, self.review, self.inventory]
        original = [p.read_bytes() for p in files]
        self.verify()
        self.assertEqual(original, [p.read_bytes() for p in files])

    def test_report_mutation_rejected(self):
        self.report.write_bytes(self.report.read_bytes().replace(b"review", b"accept"))
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_budget_review_mutation_rejected(self):
        self.review.write_bytes(b"program,amount\nG,99.00\n")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_same_length_source_mutation_rejected(self):
        self.claims.write_bytes(self.claims.read_bytes().replace(b"10.00", b"90.00"))
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_missing_original_source_rejected(self):
        self.ledger.unlink()
        with self.assertRaises(ValueError) as caught:
            self.verify()
        self.assertNotIn(str(self.root), str(caught.exception))

    def test_source_reordered_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            verify_grant_bundle(self.package, self.ledger, self.claims, self.budgets)

    def test_manual_manifest_digest_tampering_rejected(self):
        body = self.inventory.read_text()
        self.inventory.write_text(body.replace("a", "b", 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_extra_untracked_file_rejected(self):
        (self.package / "unexpected.csv").write_text("extra")
        with self.assertRaisesRegex(ValueError, "exactly three"):
            self.verify()

    def test_missing_report_rejected(self):
        self.review.unlink()
        with self.assertRaisesRegex(ValueError, "exactly three"):
            self.verify()

    def test_report_name_ambiguity_rejected(self):
        self.review.rename(self.package / "unexpected-review.csv")
        with self.assertRaisesRegex(ValueError, "unexpected file layout"):
            self.verify()

    def test_manifest_file_symlink_rejected(self):
        self.inventory.unlink()
        try:
            self.inventory.symlink_to(self.claims)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks unavailable: {exc}")
        with self.assertRaisesRegex(ValueError, "link or non-file"):
            self.verify()

    def test_package_symlink_rejected(self):
        alias = self.root / "bundle-link"
        try:
            alias.symlink_to(self.package, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks unavailable: {exc}")
        with self.assertRaisesRegex(ValueError, "real directory"):
            verify_grant_bundle(alias, self.claims, self.ledger, self.budgets)

    def test_report_symlink_rejected(self):
        self.report.unlink()
        try:
            self.report.symlink_to(self.claims)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks unavailable: {exc}")
        with self.assertRaisesRegex(ValueError, "link or non-file"):
            self.verify()

    def test_source_symlink_rejected(self):
        alias = self.root / "alias.csv"
        try:
            alias.symlink_to(self.claims)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks unavailable: {exc}")
        with self.assertRaises(ValueError):
            verify_grant_bundle(self.package, alias, self.ledger, self.budgets)

    def test_oversized_manifest_rejected_without_unbounded_read(self):
        with self.inventory.open("wb") as stream:
            stream.truncate(64 * 1024 + 1)
        with self.assertRaises(ValueError):
            self.verify()

    def test_unexpected_directory_member_rejected(self):
        self.report.unlink()
        self.report.mkdir()
        with self.assertRaisesRegex(ValueError, "link or non-file"):
            self.verify()

    def test_filename_control_characters_do_not_inject_inventory(self):
        original = self.claims
        injected = self.root / "claim\tmalicious\nentry.csv"
        original.rename(injected)
        self.claims = injected
        self.refresh_inventory()
        self.assertTrue(self.verify())
        self.assertNotIn("\tmalicious\n", self.inventory.read_text())

    def test_replaced_inventory_during_hashing_rejected(self):
        from fvs_suite import grant_verify
        original = grant_verify.inventory_text
        def mutate(*a, **kw):
            result = original(*a, **kw)
            self.inventory.write_bytes(b"mutated inventory")
            return result
        with patch.object(grant_verify, "inventory_text", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "changed during verification"):
                self.verify()

    def test_directory_changed_during_hashing_rejected(self):
        from fvs_suite import grant_verify
        original = grant_verify.inventory_text
        def mutate(*a, **kw):
            result = original(*a, **kw)
            (self.package / "extra").write_text("x")
            return result
        with patch.object(grant_verify, "inventory_text", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "changed during verification"):
                self.verify()

    def test_cli_exit_code_zero_on_consistent(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([str(self.package), str(self.claims), str(self.ledger), str(self.budgets)])
        self.assertEqual(code, 0)
        self.assertIn("human review", out.getvalue())
        self.assertNotIn(str(self.root), out.getvalue())

    def test_cli_exit_code_one_on_mismatch_without_paths(self):
        self.budgets.write_bytes(b"program,budget\nG,100000.00\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([str(self.package), str(self.claims), str(self.ledger), str(self.budgets)])
        self.assertEqual(code, 1)
        self.assertIn("INVALID", out.getvalue())
        self.assertNotIn(str(self.root), out.getvalue())

    @unittest.skipIf(os.name == "nt", "Hard links not uniformly available on Windows")
    def test_hard_link_source_alias_rejected(self):
        self.ledger.unlink()
        os.link(self.claims, self.ledger)
        with self.assertRaises(ValueError):
            self.verify()


if __name__ == "__main__":
    unittest.main()
