"""R31 full-engine GrantAudit provenance contracts (synthetic data, no telemetry)."""
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine
from fvs_suite.grant_allocations import reconcile_allocations


class GrantManifestBindingIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def csv(self, name, header, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
        return path

    def sources(self, linked=False):
        claim_header = ("claim_id", "amount", "program", "ledger_reference") if linked else ("claim_id", "amount", "program")
        claim = self.csv("claims.csv", claim_header,
                         [("C1", "10.00", "G1", "L1")] if linked else [("L1", "10.00", "G1")])
        ledger = self.csv("ledger.csv", ("transaction_id", "amount", "program"),
                          [("L1", "10.00", "G1")])
        budget = self.csv("budgets.csv", ("program", "budget"), [("G1", "100.00")])
        return claim, ledger, budget

    def test_table_snapshot_digest_matches_parsed_bytes(self):
        source, _, _ = self.sources()
        rows, digest = engine.table(source, ("id", "amount"), include_digest=True)
        self.assertEqual(rows[0]["amount"], "10.00")
        self.assertEqual(digest, hashlib.sha256(source.read_bytes()).hexdigest())

    def test_table_header_and_snapshot_digest_together(self):
        source, _, _ = self.sources(linked=True)
        rows, names, digest = engine.table(
            source, ("id", "amount"), ("ledger_reference",),
            include_headers=True, include_digest=True)
        self.assertEqual(rows[0]["ledger_reference"], "L1")
        self.assertIn("ledger_reference", names)
        self.assertEqual(digest, hashlib.sha256(source.read_bytes()).hexdigest())

    def test_existing_table_api_is_unchanged(self):
        source, _, _ = self.sources()
        self.assertIsInstance(engine.table(source, ("id", "amount")), list)
        rows, names = engine.table(source, ("id", "amount"), include_headers=True)
        self.assertIsInstance(rows, list)
        self.assertIsInstance(names, set)

    def test_legacy_grant_manifest_has_all_verified_source_digests(self):
        sources = self.sources()
        reports = engine.grant_audit(*sources, self.root)
        self.assertEqual(len(reports), 3)
        body = reports[-1].read_text(encoding="utf-8")
        for source in sources:
            self.assertIn(source.name + "\t" +
                          hashlib.sha256(source.read_bytes()).hexdigest(), body)

    def test_linked_grant_manifest_has_all_verified_source_digests(self):
        sources = self.sources(linked=True)
        reports = engine.grant_audit(*sources, self.root)
        self.assertEqual(len(reports), 3)
        body = reports[-1].read_text(encoding="utf-8")
        for source in sources:
            self.assertIn(source.name + "\t" +
                          hashlib.sha256(source.read_bytes()).hexdigest(), body)

    def assert_modified_source_blocks_manifest(self, linked, index):
        sources = self.sources(linked=linked)
        original = engine.manifest

        def tamper_then_inventory(folder, inputs, outputs, *, expected_inputs=None):
            self.assertEqual(set(expected_inputs), set(sources))
            target = sources[index]
            data = target.read_bytes()
            self.assertIn(b"10.00" if index != 2 else b"100.00", data)
            target.write_bytes(data.replace(b"10.00", b"99.00") if index != 2
                               else data.replace(b"100.00", b"900.00"))
            return original(folder, inputs, outputs, expected_inputs=expected_inputs)

        with patch("fvs_suite.engine.manifest", side_effect=tamper_then_inventory):
            with self.assertRaisesRegex(ValueError, "Source bytes changed"):
                engine.grant_audit(*sources, self.root)
        # Reports may already have been written; they are NEVER certified by
        # an inventory that no longer corresponds to the parsed source.
        self.assertEqual(list(self.root.glob("evidence-manifest-*.txt")), [])

    def test_legacy_changed_claim_rejected_before_inventory(self):
        self.assert_modified_source_blocks_manifest(linked=False, index=0)

    def test_legacy_changed_ledger_rejected_before_inventory(self):
        self.assert_modified_source_blocks_manifest(linked=False, index=1)

    def test_legacy_changed_budget_rejected_before_inventory(self):
        self.assert_modified_source_blocks_manifest(linked=False, index=2)

    def test_linked_changed_claim_rejected_before_inventory(self):
        self.assert_modified_source_blocks_manifest(linked=True, index=0)

    def test_linked_changed_ledger_rejected_before_inventory(self):
        self.assert_modified_source_blocks_manifest(linked=True, index=1)

    def test_linked_changed_budget_rejected_before_inventory(self):
        self.assert_modified_source_blocks_manifest(linked=True, index=2)

    def test_direct_linked_reconciliation_uses_own_verified_claim_snapshot(self):
        sources = self.sources(linked=True)
        paths = reconcile_allocations(*sources, self.root)
        self.assertEqual(len(paths), 3)
        self.assertTrue(paths[-1].is_file())

    def test_preparsed_claims_without_digest_not_accepted(self):
        sources = self.sources(linked=True)
        parsed = engine.table(sources[0], ("id", "amount", "program"),
                              ("ledger_reference",))
        with self.assertRaisesRegex(ValueError, "require source-byte provenance"):
            reconcile_allocations(*sources, self.root, claim_rows=parsed)
        self.assertEqual(list(self.root.glob("evidence-manifest-*.txt")), [])


if __name__ == "__main__":
    unittest.main()
