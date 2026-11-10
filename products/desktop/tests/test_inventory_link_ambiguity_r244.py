"""R244: preserve ambiguous post-link evidence without pathname rollback.

Synthetic non-PE payloads, genuine local hardlinks, no distribution/production.
"""
from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_inventory as inv


class ManifestLinkAmbiguityR244(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r244-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "candidates"
        self.root.mkdir()
        self.data = {}
        for index, name in enumerate(inv.EXPECTED):
            payload = b"MZ-SYNTHETIC-ONLY-" + bytes([index + 1]) * (45 + index)
            (self.root / name).write_bytes(payload)
            self.data[name] = payload
        self.target = self.root / inv.MANIFEST
        self.real_link = os.link

    def assert_originals(self):
        for name, data in self.data.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        self.assertEqual(
            [p.name for p in self.root.iterdir() if p.name.startswith(".fvs-inventory-")], []
        )

    def assert_pristine(self):
        self.assertEqual({p.name for p in self.root.iterdir()}, set(inv.EXPECTED))
        self.assertFalse(os.path.lexists(self.target))
        self.assert_originals()

    def assert_preserved_manifest(self):
        self.assertEqual({p.name for p in self.root.iterdir()},
                         set(inv.EXPECTED) | {inv.MANIFEST})
        self.assertTrue(self.target.is_file())
        self.assertEqual(len(self.target.read_bytes().splitlines()), 6)
        self.assert_originals()

    def after_link_error(self, error, *, replacement=None):
        """Inject a fault after the kernel operation has already succeeded."""
        calls = []

        def link_then_fail(stage, target, *args, **kwargs):
            self.real_link(stage, target, *args, **kwargs)
            calls.append((Path(stage), Path(target)))
            if replacement is not None:
                Path(target).unlink()
                if replacement == "regular":
                    Path(target).write_bytes(b"independent foreign evidence")
                elif replacement == "symlink":
                    os.symlink(self.root.parent / "outside.txt", target)
                elif replacement == "directory":
                    Path(target).mkdir()
                else:
                    raise AssertionError("bad test setup")
            raise error

        with patch("build_inventory.os.link", side_effect=link_then_fail):
            with self.assertRaises(inv.InventoryBuildError if isinstance(error, OSError)
                                   else type(error)) as caught:
                inv.build_inventory(self.root)
        self.assertEqual(len(calls), 1)
        self.assert_originals()
        if isinstance(error, OSError):
            self.assertIsInstance(caught.exception, inv.InventoryBuildError)
            self.assertNotIn(str(self.root), str(caught.exception))
            self.assertNotIn("private", str(caught.exception))
            self.assertIsNone(caught.exception.__cause__)

    def test_postlink_permission_error_rolls_back_link(self):
        self.after_link_error(PermissionError(errno.EACCES, "private path", str(self.root)))
        self.assert_preserved_manifest()

    def test_postlink_disk_io_error_rolls_back_link(self):
        self.after_link_error(OSError(errno.EIO, "private path", str(self.root)))
        self.assert_preserved_manifest()

    def test_postlink_no_space_error_rolls_back_link(self):
        self.after_link_error(OSError(errno.ENOSPC, "private path", str(self.root)))
        self.assert_preserved_manifest()

    def test_postlink_already_exists_error_rolls_back_own_link(self):
        self.after_link_error(FileExistsError(errno.EEXIST, "private path", str(self.root)))
        self.assert_preserved_manifest()

    def test_postlink_interrupt_rolls_back_link_and_propagates(self):
        self.after_link_error(KeyboardInterrupt())
        self.assert_preserved_manifest()

    def test_postlink_exit_rolls_back_link_and_propagates(self):
        self.after_link_error(SystemExit(73))
        self.assert_preserved_manifest()

    def test_postlink_error_preserves_foreign_replacement(self):
        self.after_link_error(OSError(errno.EIO, "private path"), replacement="regular")
        self.assertEqual(self.target.read_bytes(), b"independent foreign evidence")

    def test_postlink_interrupt_preserves_foreign_replacement(self):
        self.after_link_error(KeyboardInterrupt(), replacement="regular")
        self.assertEqual(self.target.read_bytes(), b"independent foreign evidence")

    def test_postlink_error_preserves_foreign_symlink(self):
        secret = self.root.parent / "outside.txt"
        secret.write_text("must not mutate", encoding="utf-8")
        self.after_link_error(OSError(errno.EIO, "private path"), replacement="symlink")
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(secret.read_text(encoding="utf-8"), "must not mutate")

    def test_postlink_error_preserves_foreign_directory(self):
        self.after_link_error(OSError(errno.EIO, "private path"), replacement="directory")
        self.assertTrue(self.target.is_dir())

    def test_prelink_failure_leaves_pristine_root(self):
        with patch("build_inventory.os.link", side_effect=OSError(errno.EIO, "private path")):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.root)
        self.assert_pristine()

    def test_success_creates_canonical_manifest_without_temp_files(self):
        self.assertEqual(inv.build_inventory(self.root), inv.MANIFEST)
        self.assertEqual({p.name for p in self.root.iterdir()}, set(inv.EXPECTED) | {inv.MANIFEST})
        self.assertEqual(len(self.target.read_bytes().splitlines()), 6)
        self.assert_originals()


if __name__ == "__main__":
    unittest.main()
