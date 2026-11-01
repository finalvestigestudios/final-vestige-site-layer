"""R103: synthetic-only Windows toolchain path/descriptor creation-time parity tests.

No real installer, premium entitlement, secrets, customer records, or release.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from scripts import toolchain_guard as gate


FIELDS = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
          "st_mtime_ns", "st_ctime_ns")


def clone(info, **changes):
    return types.SimpleNamespace(**{name: changes.get(name, getattr(info, name))
                                    for name in FIELDS})


class WindowsToolchainCtimeR103Tests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="fvs-r103-synthetic-")
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.root = self.folder / "checkout"
        self.root.mkdir()
        self.target = self.folder / "synthetic.bin"
        self.target.write_bytes(b"test-only-custody-bytes")

    def windows_parity(self):
        original = gate._same_path_descriptor_identity
        return patch.object(gate, "_same_path_descriptor_identity",
                            side_effect=lambda a, b, **kwargs: original(a, b, windows=True, **kwargs))

    def shifted_fstat(self, *, change_second=False):
        actual = os.fstat
        calls = [0]
        def replacement(fd):
            calls[0] += 1
            stat = actual(fd)
            delta = 123456789 + (1 if change_second and calls[0] > 1 else 0)
            return clone(stat, st_ctime_ns=stat.st_ctime_ns + delta)
        return patch.object(gate.os, "fstat", side_effect=replacement)

    def test_windows_cross_view_ignores_only_ctime(self):
        original = self.target.stat()
        varied = clone(original, st_ctime_ns=original.st_ctime_ns + 100)
        self.assertTrue(gate._same_path_descriptor_identity(original, varied, windows=True))
        self.assertFalse(gate._same_path_descriptor_identity(original, varied, windows=False))

    def test_cross_view_never_ignores_inode_size_mtime_or_links(self):
        before = self.target.stat()
        for name in ("st_dev", "st_ino", "st_mode", "st_nlink",
                     "st_size", "st_mtime_ns"):
            with self.subTest(name=name):
                changed = clone(before, **{name: getattr(before, name) + 1})
                self.assertFalse(gate._same_path_descriptor_identity(
                    before, changed, windows=True))

    def test_windows_file_record_accepts_only_cross_view_ctime_drift(self):
        with self.windows_parity(), self.shifted_fstat():
            digest, identity, length = gate._file_record(self.target)
        self.assertEqual(length, len(self.target.read_bytes()))
        self.assertEqual(identity, gate._identity(self.target.lstat()))
        self.assertEqual(len(digest), 64)

    def test_linux_file_record_still_rejects_cross_view_ctime_drift(self):
        original = gate._same_path_descriptor_identity
        with patch.object(gate, "_same_path_descriptor_identity",
                          side_effect=lambda a,b,**kwargs: original(a,b,windows=False,**kwargs)), self.shifted_fstat():
            with self.assertRaises(ValueError):
                gate._file_record(self.target)

    def test_windows_descriptor_ctime_mutation_still_rejected(self):
        with self.windows_parity(), self.shifted_fstat(change_second=True):
            with self.assertRaisesRegex(ValueError, "modified"):
                gate._file_record(self.target)

    def test_windows_mutated_descriptor_inode_still_rejected(self):
        actual = os.fstat
        def changed(fd):
            record = actual(fd)
            return clone(record, st_ino=record.st_ino + 1,
                         st_ctime_ns=record.st_ctime_ns + 100)
        with self.windows_parity(), patch.object(gate.os, "fstat", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "replaced"):
                gate._file_record(self.target)

    def _synthetic_manifest(self):
        path = self.folder / "synthetic-toolchain.json"
        payload = {"schema": gate.SCHEMA,
                   "scope": "PROCESS_LOCAL_TOOLCHAIN_ONLY_NOT_EXECUTABLE_OR_QD_PROOF",
                   "released": False, "qd_approved": False,
                   "windows_executables_verified": False,
                   "premium_download_authorized": False,
                   "runtime": {}, "distributions": []}
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path, payload

    def test_windows_manifest_reader_accepts_cross_view_ctime_drift(self):
        path, payload = self._synthetic_manifest()
        with self.windows_parity(), self.shifted_fstat():
            self.assertEqual(gate._read_manifest(self.root, path), payload)

    def test_windows_manifest_reader_rejects_descriptor_change(self):
        path, _ = self._synthetic_manifest()
        with self.windows_parity(), self.shifted_fstat(change_second=True):
            with self.assertRaisesRegex(ValueError, "modified"):
                gate._read_manifest(self.root, path)

    def test_windows_manifest_reader_rejects_extra_sql_like_fields(self):
        path, _ = self._synthetic_manifest()
        with path.open("a", encoding="utf-8") as stream:
            stream.write('{"released":true}')
        with self.windows_parity(), self.shifted_fstat():
            with self.assertRaises(ValueError):
                gate._read_manifest(self.root, path)

    def test_windows_mutation_does_not_write_or_replace_original(self):
        before = self.target.read_bytes()
        with self.windows_parity(), self.shifted_fstat(change_second=True):
            with self.assertRaises(ValueError):
                gate._file_record(self.target)
        self.assertEqual(self.target.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
