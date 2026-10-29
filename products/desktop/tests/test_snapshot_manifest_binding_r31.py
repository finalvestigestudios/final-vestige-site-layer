"""R31: bind GrantAudit evidence hashes to exact financial CSV snapshot bytes.

Uses real filesystem IO and synthetic, non-customer data only.
"""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from fvs_suite import manifest_guard as guard


class ParsedInputManifestBindingTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.claim = self.root / "claims.csv"
        self.report = self.root / "audit-review.csv"
        self.claim.write_bytes(b"id,amount\nA,10.00\n")
        self.report.write_bytes(b"id,status\nA,human_review\n")

    def digest(self, path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_matching_snapshot_digest_yields_same_documented_inventory(self):
        text = guard.inventory_text(
            [self.claim], [self.report],
            expected_input_digests={self.claim: self.digest(self.claim)})
        lines = text.splitlines()
        self.assertEqual(lines[1], f"claims.csv\t{self.digest(self.claim)}")
        self.assertEqual(lines[2], f"audit-review.csv\t{self.digest(self.report)}")
        self.assertEqual(len(lines), 3)

    def test_string_keys_equivalent_to_path_keys(self):
        text = guard.inventory_text(
            [self.claim], [self.report],
            expected_input_digests={str(self.claim): self.digest(self.claim)})
        self.assertIn(self.digest(self.claim), text)

    def test_same_length_rewrite_fails_even_if_mtime_is_restored(self):
        parsed_digest = self.digest(self.claim)
        old = self.claim.stat()
        self.claim.write_bytes(b"id,amount\nA,99.00\n")
        os.utime(self.claim, ns=(old.st_atime_ns, old.st_mtime_ns))
        self.assertEqual(self.claim.stat().st_size, old.st_size)
        with self.assertRaisesRegex(ValueError, "Source bytes changed"):
            guard.inventory_text([self.claim], [self.report],
                                 expected_input_digests={self.claim: parsed_digest})

    def test_replaced_file_identical_name_but_different_bytes_fails(self):
        old_digest = self.digest(self.claim)
        replacement = self.root / "replacement.csv"
        replacement.write_bytes(b"id,amount\nB,10.00\n")
        os.replace(replacement, self.claim)
        with self.assertRaisesRegex(ValueError, "Source bytes changed"):
            guard.inventory_text([self.claim], [self.report],
                                 expected_input_digests={self.claim: old_digest})

    def test_missing_digest_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            guard.inventory_text([self.claim], [self.report],
                                 expected_input_digests={})

    def test_extra_digest_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            guard.inventory_text(
                [self.claim], [self.report],
                expected_input_digests={
                    self.claim: self.digest(self.claim),
                    self.root / "unexpected.csv": "a" * 64})

    def test_invalid_digest_type_rejected_without_echoing_path(self):
        with self.assertRaises(ValueError) as caught:
            guard.inventory_text([self.claim], [],
                                 expected_input_digests={self.claim: 123})
        self.assertIn("Invalid source digest", str(caught.exception))
        self.assertNotIn(str(self.root), str(caught.exception))

    def test_invalid_digest_case_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid source digest"):
            guard.inventory_text([self.claim], [],
                                 expected_input_digests={self.claim: "F" * 64})

    def test_truncated_hash_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid source digest"):
            guard.inventory_text([self.claim], [],
                                 expected_input_digests={self.claim: "a" * 63})

    def test_legacy_descriptive_manifest_still_supported(self):
        text = guard.inventory_text([self.claim], [self.report])
        self.assertEqual(len(text.splitlines()), 3)

    def test_both_inputs_must_be_bound_not_only_first(self):
        second = self.root / "ledger.csv"
        second.write_bytes(b"id,amount\nA,10.00\n")
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            guard.inventory_text([self.claim, second], [self.report],
                                 expected_input_digests={self.claim: self.digest(self.claim)})

    def test_correct_two_source_digests_keep_input_order(self):
        second = self.root / "ledger.csv"
        second.write_bytes(b"id,amount\nA,10.00\n")
        result = guard.inventory_text(
            [second, self.claim], [self.report],
            expected_input_digests={
                self.claim: self.digest(self.claim), second: self.digest(second)})
        self.assertEqual(result.splitlines()[1].split("\t")[0], "ledger.csv")
        self.assertEqual(result.splitlines()[2].split("\t")[0], "claims.csv")


if __name__ == "__main__":
    unittest.main()
