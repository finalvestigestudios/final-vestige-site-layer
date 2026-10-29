"""R35 end-to-end ProcureGuard provenance tests (requires complete desktop checkout)."""
from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine
from fvs_suite.procurement import load_price_policy


class ProcureProvenanceR35Tests(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory(prefix="fvs-procure-provenance-r35-")
        self.addCleanup(holder.cleanup)
        self.folder = Path(holder.name)
        self.po = self.csv("po.csv", ["po_number", "line", "quantity", "unit_price"],
                           [["P-1", "1", "10", "5"]])
        self.invoices = self.csv("invoice.csv", ["po_number", "line", "quantity", "unit_price"],
                                 [["P-1", "1", "10", "5"]])
        self.receipts = self.csv("receipt.csv", ["po_number", "line", "quantity"],
                                 [["P-1", "1", "10"]])

    def csv(self, filename, headers, rows):
        path = self.folder / filename
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def run_engine(self, **kwargs):
        return engine.procure_guard(str(self.po), str(self.invoices),
                                   str(self.receipts), self.folder, **kwargs)

    def assert_unpublished(self):
        self.assertEqual(list(self.folder.glob("procurement-evidence-*")), [])
        self.assertEqual(list(self.folder.glob(".fvs-procure-pending-*")), [])
        self.assertEqual(list(self.folder.glob("procurement-three-way-*.csv")), [])

    def test_complete_package_and_source_bytes_are_in_manifest(self):
        expected = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (self.po, self.invoices, self.receipts)}
        outputs = self.run_engine()
        self.assertEqual(len(outputs), 2)
        self.assertEqual(outputs[0].parent, outputs[1].parent)
        self.assertTrue(outputs[0].parent.name.startswith("procurement-evidence-"))
        self.assertEqual({p.name for p in outputs[0].parent.iterdir()},
                         {p.name for p in outputs})
        manifest = outputs[1].read_text(encoding="utf-8")
        for name, digest in expected.items():
            self.assertIn(f"{name}\t{digest}\n", manifest)
        self.assertIn(f"{outputs[0].name}\t"
                      f"{hashlib.sha256(outputs[0].read_bytes()).hexdigest()}\n",
                      manifest)
        with outputs[0].open(encoding="utf-8-sig", newline="") as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual(row["status"], "matched")
        self.assertEqual(row["invoice_total"], "50.00")
        self.assertEqual(list(self.folder.glob(".fvs-procure-pending-*")), [])

    def test_mutated_purchase_order_after_parsing_cannot_publish(self):
        actual = engine.manifest

        def mutate(*args, **kwargs):
            self.po.write_bytes(self.po.read_bytes().replace(b"10,5", b"11,5"))
            return actual(*args, **kwargs)

        with patch("fvs_suite.engine.manifest", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "Source bytes changed"):
                self.run_engine()
        self.assert_unpublished()

    def test_same_length_invoice_edit_after_parsing_cannot_publish(self):
        actual = engine.manifest

        def mutate(*args, **kwargs):
            old = self.invoices.read_bytes()
            new = old.replace(b"10,5", b"11,5")
            self.assertEqual(len(old), len(new))
            self.assertNotEqual(old, new)
            self.invoices.write_bytes(new)
            return actual(*args, **kwargs)

        with patch("fvs_suite.engine.manifest", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "Source bytes changed"):
                self.run_engine()
        self.assert_unpublished()

    def test_receipt_edit_after_parsing_cannot_publish(self):
        actual = engine.manifest

        def mutate(*args, **kwargs):
            self.receipts.write_bytes(self.receipts.read_bytes().replace(b"10", b"11"))
            return actual(*args, **kwargs)

        with patch("fvs_suite.engine.manifest", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "Source bytes changed"):
                self.run_engine()
        self.assert_unpublished()

    def test_custom_policy_exact_bytes_in_manifest(self):
        policy = self.folder / "rules.json"
        policy.write_text(json.dumps({"version":1, "price_absolute":"0.01",
                                      "price_fraction":"0.01"}), encoding="utf-8")
        expected = hashlib.sha256(policy.read_bytes()).hexdigest()
        output = self.run_engine(policy_path=str(policy))
        manifest = output[1].read_text(encoding="utf-8")
        self.assertIn(f"{policy.name}\t{expected}\n", manifest)
        with output[0].open(encoding="utf-8-sig", newline="") as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual(row["price_policy_sha256"], expected)

    def test_custom_policy_changes_after_load_fail_closed(self):
        policy = self.folder / "rules.json"
        policy.write_text('{"version":1,"price_absolute":"0.01","price_fraction":"0.02"}')
        actual = engine.manifest

        def mutate(*args, **kwargs):
            policy.write_text('{"version":1,"price_absolute":"0.01","price_fraction":"0.03"}')
            return actual(*args, **kwargs)

        with patch("fvs_suite.engine.manifest", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "Source bytes changed"):
                self.run_engine(policy_path=str(policy))
        self.assert_unpublished()

    def test_manifest_failure_leaves_no_complete_or_partial_report(self):
        with patch("fvs_suite.engine.manifest", side_effect=OSError("simulated disk error")):
            with self.assertRaises(OSError):
                self.run_engine()
        self.assert_unpublished()

    def test_invalid_policy_symlink_rejected(self):
        original = self.folder / "trusted.json"
        original.write_text('{"version":1,"price_absolute":"0.01","price_fraction":"0.02"}')
        path = self.folder / "rules.json"
        try:
            path.symlink_to(original)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks not available on this host")
        with self.assertRaisesRegex(ValueError, "stable regular JSON"):
            self.run_engine(policy_path=str(path))
        self.assert_unpublished()

    def test_policy_duplicate_key_error_does_not_echo_private_key(self):
        policy = self.folder / "rules.json"
        policy.write_text('{"PRIVATE-CUSTOMER-123":1,"PRIVATE-CUSTOMER-123":2}')
        with self.assertRaises(ValueError) as caught:
            load_price_policy(policy)
        self.assertIn("Duplicate JSON price policy key", str(caught.exception))
        self.assertNotIn("PRIVATE-CUSTOMER-123", str(caught.exception))
        self.assert_unpublished()


if __name__ == "__main__":
    unittest.main()
