"""Synthetic, on-disk R30 CSV snapshot regression tests; no customer data."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import csv_snapshot


class CsvSnapshotR30Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "input.csv"
        self.source.write_bytes(b"\xef\xbb\xbfid,amount\r\nA,1.00\r\n")

    def snapshot(self, limit=1024):
        return csv_snapshot.read_csv_snapshot(self.source, limit)

    def test_preserves_exact_source_bytes_including_bom(self):
        self.assertEqual(self.snapshot(), self.source.read_bytes())

    def test_accepts_file_at_exact_size_limit(self):
        self.assertEqual(self.snapshot(self.source.stat().st_size), self.source.read_bytes())

    def test_rejects_file_one_byte_beyond_limit(self):
        with self.assertRaisesRegex(ValueError, "file-size limit"):
            self.snapshot(self.source.stat().st_size - 1)

    def test_rejects_large_sparse_input_without_reading(self):
        with self.source.open("r+b") as stream:
            stream.truncate(64 * 1024 * 1024 + 1)
        with self.assertRaisesRegex(ValueError, "file-size limit"):
            self.snapshot(64 * 1024 * 1024)

    def test_empty_file_is_snapshot_not_valid_csv(self):
        self.source.write_bytes(b"")
        self.assertEqual(self.snapshot(0), b"")

    def test_missing_file_rejected_without_path_disclosure(self):
        self.source.unlink()
        with self.assertRaisesRegex(ValueError, "file is missing") as context:
            self.snapshot()
        self.assertNotIn(str(self.root), str(context.exception))

    def test_directory_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "regular file"):
            csv_snapshot.read_csv_snapshot(self.root, 1024)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_input_rejected(self):
        link = self.root / "link.csv"
        try:
            link.symlink_to(self.source)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks require privileges")
        with self.assertRaisesRegex(ValueError, "regular file"):
            csv_snapshot.read_csv_snapshot(link, 1024)

    def test_replacement_between_initial_metadata_and_open_rejected(self):
        replacement = self.root / "replacement.csv"
        replacement.write_bytes(b"id,amount\nB,2\n")
        real_open = csv_snapshot.os.open
        def swap(path, flags):
            os.replace(replacement, self.source)
            return real_open(path, flags)
        with patch("fvs_suite.csv_snapshot.os.open", side_effect=swap):
            with self.assertRaisesRegex(ValueError, "changed while opening"):
                self.snapshot()

    def test_replacement_just_before_final_metadata_rejected(self):
        replacement = self.root / "replacement.csv"
        replacement.write_bytes(b"id,amount\nB,2\n")
        real_metadata = csv_snapshot._metadata
        calls = 0
        def swap(path):
            nonlocal calls
            calls += 1
            if calls == 2:
                os.replace(replacement, self.source)
            return real_metadata(path)
        with patch.object(csv_snapshot, "_metadata", side_effect=swap):
            with self.assertRaisesRegex(ValueError, "path changed"):
                self.snapshot()

    def test_mutation_during_read_rejected(self):
        real_fstat = csv_snapshot.os.fstat
        count = 0
        def mutate(fd):
            nonlocal count
            count += 1
            if count == 2:
                with self.source.open("ab") as target:
                    target.write(b"B,2.00\r\n")
            return real_fstat(fd)
        with patch("fvs_suite.csv_snapshot.os.fstat", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "changed while reading"):
                self.snapshot()

    def test_read_error_is_sanitized(self):
        with patch("fvs_suite.csv_snapshot.os.fdopen", side_effect=OSError("secret path")):
            with self.assertRaisesRegex(ValueError, "Cannot read CSV input") as context:
                self.snapshot()
            self.assertNotIn("secret path", str(context.exception))

    def test_negative_limit_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Invalid CSV input size limit"):
            self.snapshot(-1)

    def test_original_source_is_not_modified(self):
        before = self.source.read_bytes()
        self.snapshot()
        self.assertEqual(self.source.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
