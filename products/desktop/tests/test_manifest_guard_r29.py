"""R29 local-only regression tests for private, unambiguous grant inventories."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import manifest_guard as guard


class ManifestGuardTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        self.claim = self.root / "claim.csv"
        self.report = self.root / "review.csv"
        self.claim.write_bytes(b"id,amount\nA,0.01\n")
        self.report.write_bytes(b"id,status\nA,review\n")

    def test_exact_digests_and_order_preserved(self):
        text = guard.inventory_text([self.claim], [self.report])
        rows = text.splitlines()
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1], f"claim.csv\t{hashlib.sha256(self.claim.read_bytes()).hexdigest()}")
        self.assertEqual(rows[2], f"review.csv\t{hashlib.sha256(self.report.read_bytes()).hexdigest()}")
        self.assertIn("do not certify", rows[0])

    def test_same_basename_from_different_directories_rejected(self):
        other = self.root / "other"
        other.mkdir()
        alias = other / self.claim.name
        alias.write_bytes(b"different accounting evidence")
        with self.assertRaisesRegex(ValueError, "Ambiguous evidence names"):
            guard.inventory_text([self.claim, alias], [])

    def test_casefolded_name_collision_rejected(self):
        upper = self.root / "CLAIM.CSV"
        upper.write_bytes(b"different accounting evidence")
        with self.assertRaisesRegex(ValueError, "Ambiguous evidence names"):
            guard.inventory_text([self.claim, upper], [])

    def test_visually_equivalent_unicode_names_rejected(self):
        composed = self.root / "caf\u00e9.csv"
        decomposed = self.root / "cafe\u0301.csv"
        composed.write_bytes(b"first evidence")
        decomposed.write_bytes(b"second evidence")
        with self.assertRaisesRegex(ValueError, "Ambiguous evidence names"):
            guard.inventory_text([composed, decomposed], [])

    def test_same_input_twice_rejected(self):
        with self.assertRaisesRegex(ValueError, "Ambiguous evidence names"):
            guard.inventory_text([self.claim, self.claim], [])

    @unittest.skipIf(os.name == "nt", "Symlink privileges vary on Windows")
    def test_symlink_source_rejected_without_reading_target(self):
        alias = self.root / "shortcut.csv"
        alias.symlink_to(self.claim)
        with self.assertRaisesRegex(ValueError, "regular file"):
            guard.inventory_text([alias], [])

    @unittest.skipIf(os.name == "nt", "Hardlink behavior varies on Windows")
    def test_hardlinked_alias_rejected(self):
        alias = self.root / "second.csv"
        os.link(self.claim, alias)
        with self.assertRaisesRegex(ValueError, "hard-link"):
            guard.inventory_text([self.claim, alias], [])

    def test_directory_rejected_as_nonregular(self):
        with self.assertRaisesRegex(ValueError, "regular file"):
            guard.inventory_text([self.root], [])

    def test_absent_file_has_sanitized_exception(self):
        secret = self.root / "secret-customer-123.csv"
        with self.assertRaises(FileNotFoundError) as caught:
            guard.inventory_text([secret], [])
        self.assertNotIn(secret.name, str(caught.exception))

    def test_sparse_oversized_file_rejected_before_read(self):
        sparse = self.root / "big.csv"
        with sparse.open("wb") as stream:
            stream.truncate(guard.MAX_INPUT_BYTES + 1)
        with self.assertRaisesRegex(ValueError, "file-size limit"):
            guard.inventory_text([sparse], [])

    def test_input_limit_distinct_from_report_limit(self):
        large = self.root / "large.csv"
        large.write_bytes(b"12345678")
        with patch.object(guard, "MAX_INPUT_BYTES", 7), patch.object(guard, "MAX_REPORT_BYTES", 8):
            with self.assertRaisesRegex(ValueError, "file-size limit"):
                guard.inventory_text([large], [])
            self.assertIn("large.csv\t", guard.inventory_text([], [large]))

    def test_control_characters_escaped_without_leaking_parent(self):
        injected = self.root / "claim\tforged\n\u202e.csv"
        injected.write_bytes(b"synthetic")
        body = guard.inventory_text([injected], [])
        self.assertEqual(len(body.splitlines()), 2)
        self.assertIn(r"claim\tforged\n\u202e.csv", body)
        self.assertNotIn(str(self.root), body)

    def test_empty_report_is_hashable(self):
        empty = self.root / "empty.csv"
        empty.write_bytes(b"")
        body = guard.inventory_text([], [empty])
        self.assertIn(hashlib.sha256(b"").hexdigest(), body)

    def test_changed_open_descriptor_metadata_fails_closed(self):
        signature = guard._signature
        calls = [0]
        def altered(info):
            calls[0] += 1
            original = signature(info)
            return original[:2] + (original[2] + 1,) + original[3:] if calls[0] == 3 else original
        with patch.object(guard, "_signature", side_effect=altered):
            with self.assertRaisesRegex(ValueError, "changed while hashing"):
                guard.inventory_text([self.claim], [])

    def test_earlier_source_mutated_during_later_hash_fails_closed(self):
        hash_regular = guard._hash_regular
        calls = [0]
        def simulate(path, maximum):
            result = hash_regular(path, maximum)
            calls[0] += 1
            if calls[0] == 2:
                self.claim.write_bytes(b"modified before publication")
            return result
        with patch.object(guard, "_hash_regular", side_effect=simulate):
            with self.assertRaisesRegex(ValueError, "changed before publication"):
                guard.inventory_text([self.claim, self.report], [])

    def test_source_path_replaced_during_hash_fails_closed(self):
        hash_regular = guard._hash_regular
        def replace(path, maximum):
            result = hash_regular(path, maximum)
            path.unlink()
            path.write_bytes(b"replacement with different contents")
            return result
        with patch.object(guard, "_hash_regular", side_effect=replace):
            with self.assertRaisesRegex(ValueError, "changed before publication"):
                guard.inventory_text([self.claim], [])


if __name__ == "__main__":
    unittest.main()
