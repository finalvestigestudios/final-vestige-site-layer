"""R484: refuse six-app checksum staging through unsafe parents or reparse paths.

Synthetic file bytes only; no executable is run and no distribution is approved.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import inventory_staging_ancestry_r484 as custody
import build_inventory as inventory

NAMES = ("LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe",
         "PolicyDeltaDesk.exe", "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe")


class InventoryStageAncestryR484Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        self.root = self.home / "dist"
        self.root.mkdir()
        self.source = {}
        for position, name in enumerate(NAMES, 1):
            value = b"MZ-not-an-executable-" + bytes([position])
            (self.root / name).write_bytes(value)
            self.source[name] = value

    def assert_pristine(self):
        self.assertEqual({p.name for p in self.root.iterdir()}, set(NAMES))
        for name, value in self.source.items():
            self.assertEqual((self.root / name).read_bytes(), value)

    def test_clean_six_app_staging(self):
        self.assertTrue(custody.preflight_inventory_stage(self.root, NAMES, maximum=1024))
        self.assert_pristine()

    def test_safe_fully_flushed_private_temp_is_accepted(self):
        stage = self.root / ".fvs-inventory-abc"
        stage.write_bytes(b"digest data")
        self.assertTrue(custody.preflight_inventory_stage(
            self.root, NAMES, maximum=1024, stage_name=stage.name))
        stage.unlink()
        self.assert_pristine()

    def test_symlinked_ancestor_rejected_without_stage_write(self):
        outer = self.home / "link"
        try:
            outer.symlink_to(self.home, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Local symlinks unavailable")
        with self.assertRaises(custody.InventoryStagePathError):
            custody.preflight_inventory_stage(outer / "dist", NAMES, maximum=1024)
        self.assert_pristine()

    def test_root_symlink_rejected(self):
        alias = self.home / "alias"
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Local symlinks unavailable")
        with self.assertRaises(custody.InventoryStagePathError):
            custody.preflight_inventory_stage(alias, NAMES, maximum=1024)
        self.assert_pristine()

    def test_parent_traversal_rejected(self):
        with self.assertRaises(custody.InventoryStagePathError):
            custody.preflight_inventory_stage(self.home / "dummy" / ".." / "dist", NAMES, maximum=1024)
        self.assert_pristine()

    def test_unexpected_hidden_file_rejected(self):
        extra = self.root / ".secrets"
        extra.write_bytes(b"private")
        with self.assertRaises(custody.InventoryStagePathError):
            custody.preflight_inventory_stage(self.root, NAMES, maximum=1024)
        self.assertEqual(extra.read_bytes(), b"private")

    def test_missing_candidate_rejected(self):
        (self.root / NAMES[0]).unlink()
        with self.assertRaises(custody.InventoryStagePathError):
            custody.preflight_inventory_stage(self.root, NAMES, maximum=1024)

    def test_empty_candidate_rejected(self):
        (self.root / NAMES[0]).write_bytes(b"")
        with self.assertRaises(custody.InventoryStagePathError):
            custody.preflight_inventory_stage(self.root, NAMES, maximum=1024)

    def test_oversized_candidate_rejected(self):
        with self.assertRaises(custody.InventoryStagePathError):
            custody.preflight_inventory_stage(self.root, NAMES, maximum=2)

    def test_binary_hardlink_rejected(self):
        one = self.root / NAMES[0]
        one.unlink()
        try:
            one.hardlink_to(self.root / NAMES[1])
        except (OSError, NotImplementedError):
            self.skipTest("Local hardlinks unavailable")
        with self.assertRaises(custody.InventoryStagePathError):
            custody.preflight_inventory_stage(self.root, NAMES, maximum=1024)

    def test_simulated_windows_root_reparse_rejected(self):
        target_inode = self.root.lstat().st_ino
        original = custody.unsafe_windows_reparse
        with patch.object(custody, "unsafe_windows_reparse",
                          side_effect=lambda x: x.st_ino == target_inode or original(x)):
            with self.assertRaises(custody.InventoryStagePathError):
                custody.preflight_inventory_stage(self.root, NAMES, maximum=1024)
        self.assert_pristine()

    def test_simulated_windows_binary_reparse_rejected(self):
        target_inode = (self.root / NAMES[2]).lstat().st_ino
        original = custody.unsafe_windows_reparse
        with patch.object(custody, "unsafe_windows_reparse",
                          side_effect=lambda x: x.st_ino == target_inode or original(x)):
            with self.assertRaises(custody.InventoryStagePathError):
                custody.preflight_inventory_stage(self.root, NAMES, maximum=1024)
        self.assert_pristine()

    def test_simulated_windows_private_stage_reparse_rejected(self):
        stage = self.root / ".fvs-inventory-abc"
        stage.write_bytes(b"private")
        target_inode = stage.lstat().st_ino
        original = custody.unsafe_windows_reparse
        with patch.object(custody, "unsafe_windows_reparse",
                          side_effect=lambda x: x.st_ino == target_inode or original(x)):
            with self.assertRaises(custody.InventoryStagePathError):
                custody.preflight_inventory_stage(self.root, NAMES, maximum=1024,
                                                  stage_name=stage.name)
        self.assertEqual(stage.read_bytes(), b"private")

    def test_bad_stage_name_rejected(self):
        for stage in ("../private", "secret", ".fvs-inventory-../../foo", "", NAMES[0]):
            with self.subTest(stage=stage):
                with self.assertRaises(custody.InventoryStagePathError):
                    custody.preflight_inventory_stage(self.root, NAMES, maximum=1024, stage_name=stage)
        self.assert_pristine()

    def test_hostile_exception_is_redacted_and_unchained(self):
        with patch.object(custody, "snapshot_candidate_parents",
                          side_effect=OSError("/private/buyer/grant-ledger.csv")):
            with self.assertRaises(custody.InventoryStagePathError) as caught:
                custody.preflight_inventory_stage(self.root, NAMES, maximum=1024)
        self.assertEqual(str(caught.exception), "Unsafe six-app inventory staging path")
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)

    def test_parent_identity_drift_rejected(self):
        original = custody.snapshot_candidate_parents
        counter = 0
        def drift(root):
            nonlocal counter
            counter += 1
            return original(root) if counter == 1 else (("foreign",),)
        with patch.object(custody, "snapshot_candidate_parents", drift):
            with self.assertRaises(custody.InventoryStagePathError):
                custody.preflight_inventory_stage(self.root, NAMES, maximum=1024)
        self.assert_pristine()

    def test_refuse_non_native_contract_and_surplus_names(self):
        for names in (("wrong.exe",), NAMES + (NAMES[0],), list(NAMES)):
            with self.subTest(names=names):
                with self.assertRaises(custody.InventoryStagePathError):
                    custody.preflight_inventory_stage(self.root, names, maximum=1024)


class InventoryWriterIntegrationR484Tests(unittest.TestCase):
    """The REAL writer, full repository only; synthetic EXE-named bytes."""

    setUp = InventoryStageAncestryR484Tests.setUp
    assert_pristine = InventoryStageAncestryR484Tests.assert_pristine
    def test_real_writer_clean_path_unchanged(self):
        self.assertEqual(inventory.build_inventory(self.root), inventory.MANIFEST)
        canonical = b"".join(
            hashlib.sha256(self.source[name]).hexdigest().encode("ascii")
            + b"  " + name.encode("ascii") + b"\n" for name in NAMES)
        self.assertEqual((self.root / inventory.MANIFEST).read_bytes(), canonical)
        self.assertEqual({p.name for p in self.root.iterdir()},
                         set(NAMES) | {inventory.MANIFEST})

    def test_real_writer_rejects_symlinked_ancestor_before_mkstemp(self):
        alias = self.home / "link"
        try:
            alias.symlink_to(self.home, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Local symlinks unavailable")
        with patch.object(inventory.tempfile, "mkstemp",
                          side_effect=AssertionError("unsafe staging write occurred")):
            with self.assertRaises(inventory.InventoryBuildError):
                inventory.build_inventory(alias / "dist")
        self.assert_pristine()

    def test_real_writer_rejects_lexical_dotdot_before_mkstemp(self):
        with patch.object(inventory.tempfile, "mkstemp",
                          side_effect=AssertionError("unsafe staging write occurred")):
            with self.assertRaises(inventory.InventoryBuildError):
                inventory.build_inventory(self.home / "fake" / ".." / "dist")
        self.assert_pristine()

    def test_real_writer_rejects_reparse_root_before_mkstemp(self):
        inode = self.root.lstat().st_ino
        original = custody.unsafe_windows_reparse
        with patch.object(custody, "unsafe_windows_reparse",
                          side_effect=lambda info: info.st_ino == inode or original(info)):
            with patch.object(inventory.tempfile, "mkstemp",
                              side_effect=AssertionError("unsafe staging write occurred")):
                with self.assertRaises(inventory.InventoryBuildError):
                    inventory.build_inventory(self.root)
        self.assert_pristine()

    def test_real_writer_rejects_poststage_ancestor_change_before_link(self):
        original = custody.snapshot_candidate_parents
        count = 0
        def drifting(path):
            nonlocal count
            count += 1
            return original(path) if count <= 2 else (("changed-parent",),)
        with patch.object(custody, "snapshot_candidate_parents", drifting):
            with patch.object(inventory.os, "link",
                              side_effect=AssertionError("unsafe manifest publication")):
                with self.assertRaises(inventory.InventoryBuildError):
                    inventory.build_inventory(self.root)
        self.assert_pristine()


if __name__ == "__main__":
    unittest.main()
