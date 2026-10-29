"""R36 ProcureGuard evidence verification: synthetic, local and read-only."""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.manifest_guard import inventory_text
from fvs_suite.procurement_verify import main, verify_procurement_bundle


class ProcurementVerifyR36Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r36-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.package = self.root / "procurement-evidence-synthetic"
        self.package.mkdir()
        self.po = self.root / "po.csv"
        self.invoice = self.root / "invoice.csv"
        self.receipt = self.root / "receipt.csv"
        for path, body in ((self.po, b"po,amount\nP,10.00\n"),
                           (self.invoice, b"po,amount\nP,11.00\n"),
                           (self.receipt, b"po,quantity\nP,2\n")):
            path.write_bytes(body)
        self.report = self.package / "procurement-three-way-20261029-130000-000001.csv"
        self.report.write_bytes(b"po,status\nP,review\n")
        self.inventory = self.package / "evidence-manifest-20261029-130000-000001.txt"
        self.policy = None
        self.refresh_inventory()
        self.original_pin = hashlib.sha256(self.inventory.read_bytes()).hexdigest()

    def refresh_inventory(self):
        sources = [self.po, self.invoice, self.receipt]
        if self.policy is not None:
            sources.append(self.policy)
        self.inventory.write_bytes(inventory_text(sources, [self.report]).encode("utf-8"))

    def verify(self, *, pin=None, policy=None):
        return verify_procurement_bundle(
            self.package, self.po, self.invoice, self.receipt,
            price_policy=self.policy if policy is None else policy,
            expected_inventory_sha256=pin,
        )

    def cli(self, *options):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main([*options, str(self.package), str(self.po),
                         str(self.invoice), str(self.receipt)])
        return code, output.getvalue()

    def test_valid_unpinned_bundle(self):
        self.assertIs(self.verify(), True)

    def test_valid_pinned_bundle(self):
        self.assertIs(self.verify(pin=self.original_pin), True)

    def test_verification_is_read_only(self):
        selected = [self.po, self.invoice, self.receipt, self.report, self.inventory]
        original = [p.read_bytes() for p in selected]
        self.verify(pin=self.original_pin)
        self.assertEqual(original, [p.read_bytes() for p in selected])

    def test_po_same_length_edit_rejected(self):
        self.po.write_bytes(self.po.read_bytes().replace(b"10.00", b"90.00"))
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_invoice_edit_rejected(self):
        self.invoice.write_bytes(b"po,amount\nP,99.99\n")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_receipt_edit_rejected(self):
        self.receipt.write_bytes(b"po,quantity\nP,99\n")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_report_edit_rejected(self):
        self.report.write_bytes(b"po,status\nP,approved\n")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_inventory_edit_rejected(self):
        self.inventory.write_bytes(self.inventory.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_wrong_pin_rejected(self):
        with self.assertRaisesRegex(ValueError, "pin does not match"):
            self.verify(pin="0" * 64)

    def test_malformed_pin_rejected_without_leaking(self):
        secret = "customer-secret-private-audit"
        with self.assertRaisesRegex(ValueError, "Invalid trusted inventory") as caught:
            self.verify(pin=secret)
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn(str(self.root), str(caught.exception))

    def test_coordinated_rewrite_only_pinned_detects(self):
        self.po.write_bytes(b"po,amount\nP,90.00\n")
        self.report.write_bytes(b"po,status\nP,approved\n")
        self.refresh_inventory()
        self.assertIs(self.verify(), True)
        with self.assertRaisesRegex(ValueError, "pin does not match"):
            self.verify(pin=self.original_pin)

    def test_valid_custom_policy_required_to_verify(self):
        self.policy = self.root / "price-policy.json"
        self.policy.write_bytes(b'{"version":1,"price_absolute":"0.01","price_fraction":"0.01"}')
        self.refresh_inventory()
        self.assertIs(self.verify(), True)
        with self.assertRaisesRegex(ValueError, "does not match"):
            verify_procurement_bundle(self.package, self.po, self.invoice, self.receipt)

    def test_custom_policy_mutation_detected(self):
        self.policy = self.root / "price-policy.json"
        self.policy.write_bytes(b'{"version":1,"price_absolute":"0.01","price_fraction":"0.01"}')
        self.refresh_inventory()
        self.policy.write_bytes(self.policy.read_bytes().replace(b'"0.01"}', b'"0.02"}'))
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.verify()

    def test_non_json_policy_rejected(self):
        bad = self.root / "rules.txt"
        bad.write_text("policy")
        with self.assertRaisesRegex(ValueError, "must be a JSON"):
            self.verify(policy=bad)

    def test_oversized_policy_rejected(self):
        self.policy = self.root / "price-policy.json"
        self.policy.write_bytes(b"x" * (8192 + 1))
        with self.assertRaises(ValueError) as caught:
            self.verify()
        self.assertNotIn(str(self.root), str(caught.exception))

    def test_oversized_inventory_rejected(self):
        with self.inventory.open("wb") as stream:
            stream.truncate(65537)
        with self.assertRaises(ValueError):
            self.verify()

    def test_extra_package_file_rejected(self):
        (self.package / "extra.csv").write_text("x")
        with self.assertRaisesRegex(ValueError, "exactly two"):
            self.verify()

    def test_missing_report_rejected(self):
        self.report.unlink()
        with self.assertRaisesRegex(ValueError, "exactly two"):
            self.verify()

    def test_unrecognized_report_name_rejected(self):
        self.report.rename(self.package / "not-a-procurement-report.csv")
        with self.assertRaisesRegex(ValueError, "unexpected file layout"):
            self.verify()

    def test_source_order_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            verify_procurement_bundle(self.package, self.invoice, self.po, self.receipt)

    def test_input_link_rejected(self):
        alias = self.root / "alias.csv"
        try:
            alias.symlink_to(self.po)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not available")
        with self.assertRaises(ValueError):
            verify_procurement_bundle(self.package, alias, self.invoice, self.receipt)

    def test_report_link_rejected(self):
        self.report.unlink()
        try:
            self.report.symlink_to(self.po)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not available")
        with self.assertRaisesRegex(ValueError, "link or non-file"):
            self.verify()

    def test_inventory_link_rejected(self):
        self.inventory.unlink()
        try:
            self.inventory.symlink_to(self.po)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not available")
        with self.assertRaisesRegex(ValueError, "link or non-file"):
            self.verify()

    def test_package_link_rejected(self):
        alias = self.root / "package-link"
        try:
            alias.symlink_to(self.package, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not available")
        with self.assertRaisesRegex(ValueError, "real directory"):
            verify_procurement_bundle(alias, self.po, self.invoice, self.receipt)

    @unittest.skipIf(os.name == "nt", "Hard links unavailable on some Windows volumes")
    def test_hardlinked_sources_rejected(self):
        self.invoice.unlink()
        os.link(self.po, self.invoice)
        with self.assertRaises(ValueError):
            self.verify()

    def test_inventory_changed_during_hashing_rejected(self):
        from fvs_suite import procurement_verify
        real = procurement_verify.inventory_text
        def mutate(*args, **kwargs):
            content = real(*args, **kwargs)
            self.inventory.write_bytes(b"swapped inventory")
            return content
        with patch.object(procurement_verify, "inventory_text", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "inventory changed"):
                self.verify()

    def test_package_changed_during_hashing_rejected(self):
        from fvs_suite import procurement_verify
        real = procurement_verify.inventory_text
        def mutate(*args, **kwargs):
            content = real(*args, **kwargs)
            (self.package / "extra").write_bytes(b"x")
            return content
        with patch.object(procurement_verify, "inventory_text", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "package changed"):
                self.verify()

    def test_cli_unpinned_warns_and_no_path_leak(self):
        code, output = self.cli()
        self.assertEqual(code, 0)
        self.assertIn("CONSISTENT (UNPINNED)", output)
        self.assertIn("human review", output)
        self.assertNotIn(str(self.root), output)

    def test_cli_pinned_is_explicit_and_no_pin_leak(self):
        code, output = self.cli("--expected-inventory-sha256", self.original_pin)
        self.assertEqual(code, 0)
        self.assertIn("CONSISTENT (PINNED)", output)
        self.assertNotIn(self.original_pin, output)
        self.assertNotIn(str(self.root), output)

    def test_cli_wrong_pin_fails_closed(self):
        code, output = self.cli("--expected-inventory-sha256", "0" * 64)
        self.assertEqual(code, 1)
        self.assertIn("INVALID", output)
        self.assertNotIn(str(self.root), output)

    def test_cli_custom_policy(self):
        self.policy = self.root / "price-policy.json"
        self.policy.write_text('{"version":1,"price_absolute":"0.01","price_fraction":"0.01"}')
        self.refresh_inventory()
        code, output = self.cli("--price-policy", str(self.policy))
        self.assertEqual(code, 0, output)
        self.assertIn("UNPINNED", output)

    def test_actual_r35_publisher_package_verifies(self):
        from fvs_suite.procurement_bundle import publish_procurement_bundle
        def build(staging):
            paths = [staging / self.report.name, staging / self.inventory.name]
            paths[0].write_bytes(self.report.read_bytes())
            paths[1].write_bytes(inventory_text(
                [self.po, self.invoice, self.receipt], [paths[0]],
            ).encode("utf-8"))
            return paths
        published = publish_procurement_bundle(self.root, build)
        self.assertEqual(len(published), 2)
        self.assertIs(verify_procurement_bundle(
            published[0].parent, self.po, self.invoice, self.receipt), True)


if __name__ == "__main__":
    unittest.main()
