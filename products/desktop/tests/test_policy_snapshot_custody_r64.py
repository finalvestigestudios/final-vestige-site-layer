"""R64: source snapshot custody and transparent same-source policy review."""
from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import policy_diff as pd
from fvs_suite import csv_snapshot


class PolicySourceCustodyR64Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.before = self.root / "before.txt"
        self.after = self.root / "after.txt"
        self.destination = self.root / "policy-delta-r64.txt"
        self.before.write_bytes(b"Procedure A\n")
        self.after.write_bytes(b"Procedure B\n")

    def allocate(self, folder, stem, extension):
        self.assertEqual((Path(folder), stem, extension),
                         (self.root, "policy-delta", ".txt"))
        return self.destination

    def run_diff(self):
        return pd.compare_policy_files(self.before, self.after, self.root,
                                       self.allocate)

    def rejected(self, message="stable regular file"):
        with self.assertRaisesRegex(ValueError, message):
            self.run_diff()
        self.assertFalse(self.destination.exists())
        self.assertFalse(list(self.root.glob("*.partial")))

    def test_real_files_preserve_diff_sha_and_originals(self):
        old, new = self.before.read_bytes(), self.after.read_bytes()
        self.assertEqual(self.run_diff(), [self.destination])
        report = self.destination.read_text(encoding="utf-8")
        self.assertIn("-Procedure A", report)
        self.assertIn("+Procedure B", report)
        self.assertIn(hashlib.sha256(old).hexdigest(), report)
        self.assertIn(hashlib.sha256(new).hexdigest(), report)
        self.assertNotIn("Both source files have identical bytes", report)
        self.assertEqual(self.before.read_bytes(), old)
        self.assertEqual(self.after.read_bytes(), new)

    def test_identical_paths_are_explicitly_reviewed(self):
        self.after = self.before
        self.run_diff()
        self.assertIn("Both source files have identical bytes",
                      self.destination.read_text())
        self.assertIn("No textual differences found", self.destination.read_text())

    def test_byte_identical_files_have_review_flag_even_if_separate(self):
        self.after.write_bytes(self.before.read_bytes())
        self.run_diff()
        self.assertIn("Both source files have identical bytes", self.destination.read_text())

    def test_bom_only_difference_requires_human_byte_review(self):
        self.after.write_bytes(b"\xef\xbb\xbf" + self.before.read_bytes())
        self.run_diff()
        report = self.destination.read_text()
        self.assertIn("Source bytes differ but decoded text is identical", report)
        self.assertIn("No textual differences found", report)
        self.assertIn(hashlib.sha256(self.after.read_bytes()).hexdigest(), report)

    def test_empty_sources_are_explicitly_reviewed(self):
        self.before.write_bytes(b"")
        self.after.write_bytes(b"")
        self.run_diff()
        self.assertIn("Both source files have identical bytes", self.destination.read_text())

    def test_old_symlink_rejected_without_report(self):
        real = self.root / "real.txt"
        self.before.rename(real)
        try:
            self.before.symlink_to(real)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks unavailable: {type(exc).__name__}")
        self.rejected()

    def test_new_symlink_rejected_without_report(self):
        real = self.root / "real.txt"
        self.after.rename(real)
        try:
            self.after.symlink_to(real)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks unavailable: {type(exc).__name__}")
        self.rejected()

    def test_path_swap_before_descriptor_open_rejected(self):
        original_open = os.open
        initial = self.before.read_bytes()
        switched = False
        def swapped_open(path, flags, *args, **kwargs):
            nonlocal switched
            if Path(path) == self.before and not switched:
                switched = True
                self.before.rename(self.root / "orphan.txt")
                self.before.write_bytes(b"Procedure X\n")
            return original_open(path, flags, *args, **kwargs)
        with patch.object(csv_snapshot.os, "open", side_effect=swapped_open):
            self.rejected()
        self.assertTrue(switched)
        self.assertEqual((self.root / "orphan.txt").read_bytes(), initial)

    def test_path_swap_after_descriptor_open_rejected(self):
        original_fstat = os.fstat
        calls = 0
        def fstat_with_swap(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.before.rename(self.root / "old-identity.txt")
                self.before.write_bytes(b"Procedure X\n")
            return original_fstat(fd)
        with patch.object(csv_snapshot.os, "fstat", side_effect=fstat_with_swap):
            self.rejected()
        self.assertGreaterEqual(calls, 2)

    def test_in_place_mutation_during_read_rejected(self):
        original_fstat = os.fstat
        calls = 0
        def fstat_after_mutation(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.before.write_bytes(b"Procedure X\n")
                os.utime(self.before, ns=(1_000_000_000, 1_000_000_000))
            return original_fstat(fd)
        with patch.object(csv_snapshot.os, "fstat", side_effect=fstat_after_mutation):
            self.rejected()
        self.assertGreaterEqual(calls, 2)

    def test_oversized_file_rejected_with_policy_specific_message(self):
        with patch.object(pd, "MAX_POLICY_BYTES", 4):
            self.rejected("10 MiB")

    def test_exact_limit_still_accepted(self):
        self.before.write_bytes(b"1234")
        self.after.write_bytes(b"4321")
        with patch.object(pd, "MAX_POLICY_BYTES", 4):
            self.run_diff()
        self.assertTrue(self.destination.is_file())

    def test_unsafe_controls_still_rejected(self):
        self.after.write_bytes(b"Policy\x1b[31m\n")
        self.rejected("control characters")

    def test_invalid_utf8_still_rejected_without_echo(self):
        self.after.write_bytes(b"private\xffdata\n")
        with self.assertRaisesRegex(ValueError, "valid UTF-8") as error:
            self.run_diff()
        self.assertNotIn("private", str(error.exception))
        self.assertFalse(self.destination.exists())

    def test_unsupported_extension_rejected(self):
        self.after = self.after.rename(self.root / "after.pdf")
        self.rejected("supports existing TXT")

    def test_no_overwrite_of_existing_report(self):
        self.destination.write_text("operator evidence", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.run_diff()
        self.assertEqual(self.destination.read_text(), "operator evidence")

    def test_reject_new_nonregular_directory(self):
        self.after.unlink()
        self.after.mkdir()
        self.rejected("supports existing TXT")


if __name__ == "__main__":
    unittest.main()
