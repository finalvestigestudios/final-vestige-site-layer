"""R417: offline six-app source hashing retains verified open-file custody.

These synthetic source-only probes do NOT validate packaged Windows binaries.
"""
from __future__ import annotations

from pathlib import Path
import os
import tempfile
import types
import unittest
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class DescriptorBoundSourceCustodyR417(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "desktop"
        self.root.mkdir()
        (self.root / "fvs_suite").mkdir()
        (self.root / "launchers").mkdir()
        self.source = self.root / "fvs_suite" / "__init__.py"
        self.source.write_text("# stable source\n", encoding="utf-8")
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test']:\n"
            "        raise SystemExit(13)\n", encoding="utf-8")
        (self.root / "offline_source_smoke_r408.py").write_bytes(
            Path(gate.__file__).read_bytes())
        for app, filename in gate.PRODUCTS:
            (self.root / "launchers" / filename).write_text(
                f"from fvs_suite.launcher import launch\nlaunch({app!r})\n",
                encoding="utf-8")

    def test_all_six_synthetic_apps_still_run_both_modes(self):
        result = gate.run_gate(self.root, timeout=30)
        self.assertEqual(result["passed"], 12)
        self.assertEqual(result["required"], 12)
        self.assertFalse(result["release_authorized"])

    def test_stable_file_bytes_and_digest_are_repeatable(self):
        self.assertEqual(gate._read_verified_source_bytes(self.source),
                         b"# stable source\n")
        self.assertEqual(gate.source_digest(self.root), gate.source_digest(self.root))

    def test_fingerprint_never_uses_unchecked_path_read_bytes(self):
        with patch.object(Path, "read_bytes", side_effect=AssertionError(
                "unsafe path reopening")) as unchecked:
            self.assertEqual(gate._read_verified_source_bytes(self.source),
                             b"# stable source\n")
            gate.source_digest(self.root)
        unchecked.assert_not_called()

    def test_rejects_descriptor_redirected_to_another_regular_file(self):
        external = Path(self.temp.name) / "CLIENT_PRIVATE_REDIRECT.txt"
        external.write_bytes(self.source.read_bytes())
        real_open = os.open

        def redirect(path, flags, *args, **kwargs):
            if Path(path) == self.source:
                return real_open(external, flags, *args, **kwargs)
            return real_open(path, flags, *args, **kwargs)

        with patch.object(gate.os, "open", side_effect=redirect):
            with self.assertRaisesRegex(gate.SourceGateError, "changed during hashing"):
                gate.source_digest(self.root)

    def test_rejects_same_length_write_during_descriptor_read(self):
        original_read = os.read
        triggered = False

        def alter_after_read(fd, amount):
            nonlocal triggered
            chunk = original_read(fd, amount)
            if not triggered:
                triggered = True
                self.source.write_bytes(b"# private edit!\n")
            return chunk

        with patch.object(gate.os, "read", side_effect=alter_after_read):
            with self.assertRaises(gate.SourceGateError):
                gate.source_digest(self.root)
        self.assertTrue(triggered)

    def test_rejects_inode_replacement_between_lstat_and_open(self):
        staged = Path(self.temp.name) / "replacement.txt"
        staged.write_bytes(b"# altered file\n")
        real_open = os.open
        replaced = False

        def swap_then_open(path, flags, *args, **kwargs):
            nonlocal replaced
            if not replaced and Path(path) == self.source:
                replaced = True
                os.replace(staged, self.source)
            return real_open(path, flags, *args, **kwargs)

        with patch.object(gate.os, "open", side_effect=swap_then_open):
            with self.assertRaisesRegex(gate.SourceGateError, "changed during hashing"):
                gate.source_digest(self.root)
        self.assertTrue(replaced)

    def test_rejects_symlink_swap_at_source_open(self):
        external = Path(self.temp.name) / "PRIVATE_EXTERNAL_FILE.txt"
        external.write_bytes(self.source.read_bytes())
        real_open = os.open
        changed = False

        def swap_to_symlink(path, flags, *args, **kwargs):
            nonlocal changed
            if not changed and Path(path) == self.source:
                changed = True
                self.source.unlink()
                try:
                    self.source.symlink_to(external)
                except (NotImplementedError, OSError):
                    self.skipTest("symlink creation unavailable")
            return real_open(path, flags, *args, **kwargs)

        with patch.object(gate.os, "open", side_effect=swap_to_symlink):
            with self.assertRaises(gate.SourceGateError):
                gate.source_digest(self.root)

    def test_rejects_short_read_from_open_descriptor(self):
        with patch.object(gate.os, "read", return_value=b"") as reader:
            with self.assertRaisesRegex(gate.SourceGateError, "changed during hashing"):
                gate._read_verified_source_bytes(self.source)
        reader.assert_called()

    def test_rejects_extra_bytes_appended_during_read(self):
        original_read = os.read
        added = False

        def append_during_read(fd, size):
            nonlocal added
            chunk = original_read(fd, size)
            if not added:
                added = True
                with self.source.open("ab") as target:
                    target.write(b"SECRET_APPEND")
            return chunk

        with patch.object(gate.os, "read", side_effect=append_during_read):
            with self.assertRaisesRegex(gate.SourceGateError, "changed during hashing"):
                gate._read_verified_source_bytes(self.source)
        self.assertTrue(added)

    def test_private_os_open_error_redacted(self):
        private = "PRIVATE_CLIENT_Q21_PATH"
        with patch.object(gate.os, "open", side_effect=OSError(private)):
            with self.assertRaises(gate.SourceGateError) as caught:
                gate._read_verified_source_bytes(self.source)
        self.assertNotIn(private, str(caught.exception))
        self.assertEqual(str(caught.exception),
                         "Cannot verify local desktop source inventory")

    def test_nonregular_descriptor_is_rejected(self):
        real_open = os.open
        def open_directory(path, flags, *args, **kwargs):
            if Path(path) == self.source:
                return real_open(self.root, os.O_RDONLY)
            return real_open(path, flags, *args, **kwargs)
        with patch.object(gate.os, "open", side_effect=open_directory):
            with self.assertRaises(gate.SourceGateError):
                gate._read_verified_source_bytes(self.source)

    def test_windows_cross_api_ctime_difference_only_ignored_across_views(self):
        a = types.SimpleNamespace(st_dev=1, st_ino=2, st_mode=3,
                                  st_nlink=1, st_size=12, st_mtime_ns=9,
                                  st_ctime_ns=100)
        b = types.SimpleNamespace(**{**vars(a), "st_ctime_ns": 101})
        with patch.object(gate.os, "name", "nt"):
            self.assertEqual(gate._file_identity(a, cross_view=True),
                             gate._file_identity(b, cross_view=True))
            self.assertNotEqual(gate._file_identity(a), gate._file_identity(b))
        with patch.object(gate.os, "name", "posix"):
            self.assertNotEqual(gate._file_identity(a, cross_view=True),
                                gate._file_identity(b, cross_view=True))


if __name__ == "__main__":
    unittest.main()
