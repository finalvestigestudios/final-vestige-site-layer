"""R32: GrantAudit legacy and linked output bundles (synthetic only)."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fvs_suite import engine


class GrantBundleIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def csv(self, name, headers, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def sources(self, linked):
        claims = self.csv("claims.csv",
                          ("claim_id", "amount", "program", "ledger_reference")
                          if linked else ("claim_id", "amount", "program"),
                          [("C1", "10.00", "G1", "L1")]
                          if linked else [("L1", "10.00", "G1")])
        ledger = self.csv("ledger.csv", ("transaction_id", "amount", "program"),
                          [("L1", "10.00", "G1")])
        budget = self.csv("budgets.csv", ("program", "budget"), [("G1", "100.00")])
        return claims, ledger, budget

    def assert_complete(self, linked):
        result = engine.grant_audit(*self.sources(linked), self.root)
        self.assertEqual(len(result), 3)
        self.assertEqual(len({path.parent for path in result}), 1)
        self.assertTrue(all(path.exists() for path in result))
        self.assertIn("SHA-256 file inventory", result[-1].read_text(encoding="utf-8"))
        self.assertEqual(set(result[0].parent.iterdir()), set(result))
        self.assertFalse(list(self.root.glob(".fvs-grant-pending-*")))

    def test_legacy_package_complete(self):
        self.assert_complete(False)

    def test_linked_package_complete(self):
        self.assert_complete(True)

    def assert_fail_without_orphans(self, linked):
        sources = self.sources(linked)
        original = engine.manifest

        def tamper(folder, inputs, outputs, *, expected_inputs=None):
            source = sources[0]
            source.write_bytes(source.read_bytes().replace(b"10.00", b"99.00"))
            return original(folder, inputs, outputs, expected_inputs=expected_inputs)

        with patch("fvs_suite.engine.manifest", side_effect=tamper):
            with self.assertRaisesRegex(ValueError, "Source bytes changed"):
                engine.grant_audit(*sources, self.root)
        self.assertEqual(list(self.root.glob("grant-evidence-*")), [])
        self.assertEqual(list(self.root.glob(".fvs-grant-pending-*")), [])
        self.assertFalse(list(self.root.glob("grant-audit-exceptions-*.csv")))

    def test_legacy_changed_input_leaves_no_orphans(self):
        self.assert_fail_without_orphans(False)

    def test_linked_changed_input_leaves_no_orphans(self):
        self.assert_fail_without_orphans(True)

    def test_original_sources_unchanged_after_success(self):
        sources = self.sources(False)
        data = [s.read_bytes() for s in sources]
        engine.grant_audit(*sources, self.root)
        self.assertEqual([s.read_bytes() for s in sources], data)


if __name__ == "__main__":
    unittest.main()
