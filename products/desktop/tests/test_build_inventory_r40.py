"""R40 canonical six-candidate inventory; synthetic bytes are NEVER executed."""
from __future__ import annotations

import hashlib
import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import build_inventory as inv


class BuildInventoryR40Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r40-")
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.dist = self.base / "dist"
        self.dist.mkdir()
        self.samples = {}
        for i, name in enumerate(inv.EXPECTED):
            self.samples[name] = b"MZ" + bytes([i + 1]) * (20 + i)
            (self.dist / name).write_bytes(self.samples[name])

    def manifest(self):
        return self.dist / inv.MANIFEST

    def assert_pristine(self):
        self.assertFalse(self.manifest().exists())
        self.assertEqual({p.name for p in self.dist.iterdir()}, set(inv.EXPECTED))
        for name, content in self.samples.items():
            self.assertEqual((self.dist / name).read_bytes(), content)

    def test_publishes_exact_canonical_lf_ascii_inventory(self):
        self.assertEqual(inv.build_inventory(self.dist), inv.MANIFEST)
        expected = b"".join(
            hashlib.sha256(self.samples[name]).hexdigest().encode() + b"  "
            + name.encode() + b"\n" for name in inv.EXPECTED
        )
        self.assertEqual(self.manifest().read_bytes(), expected)
        self.assertEqual(len(list(self.dist.iterdir())), 7)
        self.assertFalse(any(p.name.startswith(".fvs-inventory-") for p in self.dist.iterdir()))

    def test_deterministic_manifest_from_identical_source_bytes(self):
        inv.build_inventory(self.dist)
        original = self.manifest().read_bytes()
        self.manifest().unlink()
        inv.build_inventory(self.dist)
        self.assertEqual(self.manifest().read_bytes(), original)

    def test_repeat_cannot_clobber_published_manifest(self):
        inv.build_inventory(self.dist)
        original = self.manifest().read_bytes()
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.dist)
        self.assertEqual(self.manifest().read_bytes(), original)

    def test_missing_any_one_of_six_rejected(self):
        for name in inv.EXPECTED:
            with self.subTest(name=name):
                src = self.dist / name
                content = src.read_bytes()
                src.unlink()
                with self.assertRaises(inv.InventoryBuildError):
                    inv.build_inventory(self.dist)
                self.assertFalse(self.manifest().exists())
                src.write_bytes(content)

    def test_rejects_unapproved_file_without_deleting_it(self):
        for name in ("issuer-secret.pem", "extra.exe", "README.txt", ".hidden"):
            with self.subTest(name=name):
                p = self.dist / name
                p.write_bytes(b"private")
                with self.assertRaises(inv.InventoryBuildError):
                    inv.build_inventory(self.dist)
                self.assertEqual(p.read_bytes(), b"private")
                p.unlink()
        self.assert_pristine()

    def test_rejects_extra_folder(self):
        extra = self.dist / "bonus"
        extra.mkdir()
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.dist)
        self.assertTrue(extra.is_dir())

    def test_rejects_wrong_case_binary_name(self):
        original = self.dist / inv.EXPECTED[0]
        wrong = self.dist / inv.EXPECTED[0].lower()
        original.rename(wrong)
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.dist)
        self.assertFalse(self.manifest().exists())

    def test_rejects_empty_binary(self):
        src = self.dist / inv.EXPECTED[2]
        src.write_bytes(b"")
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.dist)
        self.assertFalse(self.manifest().exists())

    def test_rejects_symlinked_binary(self):
        src = self.dist / inv.EXPECTED[0]
        src.unlink()
        try:
            src.symlink_to(self.dist / inv.EXPECTED[1])
        except (OSError, NotImplementedError):
            self.skipTest("No symlink support")
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.dist)
        self.assertFalse(self.manifest().exists())

    def test_rejects_hardlinked_binary(self):
        src = self.dist / inv.EXPECTED[0]
        src.unlink()
        try:
            os.link(self.dist / inv.EXPECTED[1], src)
        except (OSError, NotImplementedError):
            self.skipTest("No hardlink support")
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.dist)
        self.assertFalse(self.manifest().exists())

    def test_rejects_root_symlink(self):
        alias = self.base / "alias"
        try:
            alias.symlink_to(self.dist, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("No symlink support")
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(alias)
        self.assert_pristine()

    def test_rejects_regular_file_root(self):
        p = self.base / "file"
        p.write_bytes(b"fake")
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(p)
        self.assertEqual(p.read_bytes(), b"fake")

    def test_rejects_nonexistent_root_without_creating_it(self):
        p = self.base / "unbuilt"
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(p)
        self.assertFalse(p.exists())

    def test_rejects_candidate_over_size_limit(self):
        with patch.object(inv, "MAX_EXE_BYTES", 10):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.dist)
        self.assert_pristine()

    def test_drift_during_second_hash_pass_keeps_no_manifest(self):
        original_hash = inv.sha256_candidate
        counter = 0
        def drift(path, **kwargs):
            nonlocal counter
            counter += 1
            if counter == len(inv.EXPECTED) + 2:
                (self.dist / inv.EXPECTED[0]).write_bytes(b"tampered")
            return original_hash(path, **kwargs)
        with patch.object(inv, "sha256_candidate", side_effect=drift):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.dist)
        self.assertFalse(self.manifest().exists())
        self.assertFalse(any(p.name.startswith(".fvs-") for p in self.dist.iterdir()))

    def test_drift_after_publication_preserves_manifest_for_review(self):
        original_hash = inv.sha256_candidate
        counter = 0
        def drift(path, **kwargs):
            nonlocal counter
            counter += 1
            if counter == len(inv.EXPECTED) * 2 + 1:
                (self.dist / inv.EXPECTED[1]).write_bytes(b"tampered")
            return original_hash(path, **kwargs)
        with patch.object(inv, "sha256_candidate", side_effect=drift):
            with self.assertRaises(inv.InventoryBuildError):
                inv.build_inventory(self.dist)
        self.assertTrue(self.manifest().is_file(), "keep failed build evidence for review")
        self.assertFalse(any(p.name.startswith(".fvs-") for p in self.dist.iterdir()))

    def test_link_collision_does_not_overwrite_someone_elses_manifest(self):
        def concurrent_create(_staging, output):
            Path(output).write_bytes(b"another writer's manifest")
            raise FileExistsError("/private/ledger/source")
        with patch.object(inv.os, "link", side_effect=concurrent_create):
            with self.assertRaises(inv.InventoryBuildError) as ctx:
                inv.build_inventory(self.dist)
        self.assertNotIn("/private", str(ctx.exception))
        self.assertEqual(self.manifest().read_bytes(), b"another writer's manifest")
        self.assertFalse(any(p.name.startswith(".fvs-") for p in self.dist.iterdir()))

    def test_fsync_failure_leaves_no_manifest_or_temp(self):
        with patch.object(inv.os, "fsync", side_effect=OSError("/private/test")):
            with self.assertRaises(inv.InventoryBuildError) as ctx:
                inv.build_inventory(self.dist)
        self.assertNotIn("/private", str(ctx.exception))
        self.assert_pristine()

    def test_external_evidence_file_in_dist_rejected(self):
        report = self.dist / "internal-report.json"
        report.write_text("{}")
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.dist)
        self.assertTrue(report.exists())
        self.assertFalse(self.manifest().exists())

    def test_external_symlinked_manifest_rejected_without_removal(self):
        outside = self.base / "external.txt"
        outside.write_bytes(b"evidence")
        try:
            self.manifest().symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("No symlink support")
        with self.assertRaises(inv.InventoryBuildError):
            inv.build_inventory(self.dist)
        self.assertEqual(outside.read_bytes(), b"evidence")
        self.assertTrue(self.manifest().is_symlink())

    def test_cli_success_is_explicitly_not_approval(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            status = inv.main([str(self.dist)])
        self.assertEqual(status, 0)
        self.assertIn("NOT release authorized", buf.getvalue())
        self.assertTrue(self.manifest().exists())

    def test_cli_error_redacts_private_path(self):
        secret = self.dist / "private-payroll.csv"
        secret.write_text("secret")
        buf = io.StringIO()
        with redirect_stderr(buf):
            status = inv.main([str(self.dist)])
        self.assertEqual(status, 1)
        self.assertNotIn("private-payroll", buf.getvalue())
        self.assertFalse(self.manifest().exists())

    def test_dist_files_never_modified_on_success(self):
        inv.build_inventory(self.dist)
        for name, data in self.samples.items():
            self.assertEqual((self.dist / name).read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
