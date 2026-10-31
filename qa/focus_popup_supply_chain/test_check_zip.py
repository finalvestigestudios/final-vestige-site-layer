"""Adversarial archive tests; all operate on temporary synthetic ZIPs."""
import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from check_zip import ROOT, git_blob, inspect, MAX_FILE

FILES = {
    "fv-focus-popup.php": b"<?php\n/**\n * Version: 0.1.1\n */\n",
    "focus-popup.html": b"<a href='/focus/'>Fieldbook</a>",
    "focus-popup.css": b".focus{display:block}",
    "focus-popup.js": b"'use strict';",
}
PINS = {k: git_blob(v) for k, v in FILES.items()}


class ArchiveIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "candidate.zip"

    def write(self, entries, symlink=None):
        with zipfile.ZipFile(self.path, "w", zipfile.ZIP_DEFLATED) as z:
            for name, contents in entries:
                if name == symlink:
                    entry = zipfile.ZipInfo(name)
                    entry.create_system = 3
                    entry.external_attr = 0o120777 << 16
                    z.writestr(entry, contents)
                else:
                    z.writestr(name, contents)
        return self.path

    def baseline(self):
        return [(ROOT + name, data) for name, data in FILES.items()]

    def check(self, entries, expected):
        self.write(entries)
        self.assertIn(expected, inspect(self.path, PINS))

    def test_01_exact_identity(self):
        self.write(self.baseline())
        self.assertEqual(inspect(self.path, PINS), [])

    def test_02_changed_javascript_same_filename(self):
        a = self.baseline()
        a[3] = (a[3][0], a[3][1] + b";")
        self.check(a, "blob_mismatch:focus-popup.js")

    def test_03_modified_php_same_version(self):
        a = self.baseline()
        a[0] = (a[0][0], a[0][1] + b"// altered\n")
        self.check(a, "blob_mismatch:fv-focus-popup.php")

    def test_04_missing_file(self):
        self.check(self.baseline()[:-1], "unexpected_or_missing_file")

    def test_05_extra_php(self):
        self.check(self.baseline() + [(ROOT + "extra.php", b"<?php")], "unexpected_or_missing_file")

    def test_06_sibling_root(self):
        self.check([(n.replace(ROOT, "other/"), v) for n, v in self.baseline()], "unexpected_or_missing_file")

    def test_07_parent_directory(self):
        self.check(self.baseline() + [(ROOT + "../unsafe", b"data")], "unsafe_path_or_extra_file")

    def test_08_absolute_path(self):
        self.check(self.baseline() + [("/tmp/out", b"data")], "unsafe_path_or_extra_file")

    def test_09_backslash_path(self):
        self.check(self.baseline() + [(ROOT + "..\\bad", b"data")], "unsafe_path_or_extra_file")

    def test_10_duplicate_name(self):
        self.check(self.baseline() + [self.baseline()[2]], "duplicate_entry")

    def test_11_symlink_rejected(self):
        a = self.baseline()
        self.write(a, symlink=a[0][0])
        self.assertIn("symlink_forbidden", inspect(self.path, PINS))

    def test_12_version_mismatch(self):
        self.write(self.baseline())
        self.assertIn("plugin_version_mismatch", inspect(self.path, PINS, version="0.1.2"))

    def test_13_oversize_member(self):
        a = self.baseline()
        a[1] = (a[1][0], b"X" * (MAX_FILE + 1))
        self.check(a, "file_limit_exceeded")

    def test_14_high_compression_ratio(self):
        a = self.baseline()
        a[1] = (a[1][0], b"X" * 25000)
        self.check(a, "excessive_compression_ratio")

    def test_15_not_zip(self):
        self.path.write_bytes(b"not zip")
        self.assertTrue(inspect(self.path, PINS)[0].startswith("unreadable_archive"))

    def test_16_missing_archive(self):
        self.assertEqual(inspect(self.path, PINS), ["missing_or_oversize_archive"])

    def test_17_archive_does_not_require_network(self):
        self.write(self.baseline())
        self.assertEqual(inspect(self.path, PINS), [])


if __name__ == "__main__":
    unittest.main()
