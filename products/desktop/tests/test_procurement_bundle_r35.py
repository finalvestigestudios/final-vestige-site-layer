"""R35: Actual local file tests for all-or-nothing ProcureGuard package visibility."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.procurement_bundle import publish_procurement_bundle


class ProcureBundleR35Tests(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory(prefix="fvs-procure-bundle-r35-")
        self.addCleanup(holder.cleanup)
        self.folder = Path(holder.name)

    def build(self, folder, *, report=b"alpha,5.00\n", manifest=b"SHA-256\n"):
        a = folder / "procurement-three-way-test.csv"
        b = folder / "evidence-manifest-test.txt"
        a.write_bytes(report)
        b.write_bytes(manifest)
        return [a, b]

    def assert_clean(self):
        self.assertEqual(list(self.folder.glob(".fvs-procure-pending-*")), [])
        self.assertEqual(list(self.folder.glob("procurement-evidence-*")), [])

    def test_success_is_one_directory_and_two_files(self):
        result = publish_procurement_bundle(self.folder, self.build)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].parent, result[1].parent)
        self.assertEqual(result[0].read_bytes(), b"alpha,5.00\n")
        self.assertEqual(result[1].read_bytes(), b"SHA-256\n")
        self.assertTrue(result[0].parent.name.startswith("procurement-evidence-"))
        self.assertEqual({p.name for p in result[0].parent.iterdir()},
                         {p.name for p in result})
        self.assertEqual(list(self.folder.glob(".fvs-procure-pending-*")), [])

    def test_output_parent_must_exist(self):
        with self.assertRaisesRegex(ValueError, "existing"):
            publish_procurement_bundle(self.folder / "not-there", self.build)
        self.assert_clean()

    def test_symlink_output_parent_rejected(self):
        link = self.folder / "link"
        try:
            link.symlink_to(self.folder, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks not available on this host")
        with self.assertRaisesRegex(ValueError, "non-symlink"):
            publish_procurement_bundle(link, self.build)
        self.assert_clean()

    def test_failed_builder_never_publishes_report(self):
        def fail(folder):
            (folder / "procurement-three-way-test.csv").write_text("partial")
            raise ValueError("source bytes changed")
        with self.assertRaisesRegex(ValueError, "source bytes changed"):
            publish_procurement_bundle(self.folder, fail)
        self.assert_clean()

    def test_builder_cannot_return_one_file(self):
        with self.assertRaisesRegex(ValueError, "one report"):
            publish_procurement_bundle(self.folder, lambda stage: self.build(stage)[:1])
        self.assert_clean()

    def test_builder_cannot_return_three_files(self):
        with self.assertRaisesRegex(ValueError, "one report"):
            publish_procurement_bundle(self.folder, lambda stage: self.build(stage) + [self.build(stage)[0]])
        self.assert_clean()

    def test_no_files_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "one report"):
            publish_procurement_bundle(self.folder, lambda _: [])
        self.assert_clean()

    def test_extra_file_prevents_publication(self):
        def extra(stage):
            paths = self.build(stage)
            (stage / "private-draft.txt").write_text("not evidence")
            return paths
        with self.assertRaisesRegex(ValueError, "Unexpected files"):
            publish_procurement_bundle(self.folder, extra)
        self.assert_clean()

    def test_wrong_file_order_fails(self):
        with self.assertRaisesRegex(ValueError, "Unexpected procurement"):
            publish_procurement_bundle(self.folder, lambda stage: list(reversed(self.build(stage))))
        self.assert_clean()

    def test_outside_file_path_rejected_and_untouched(self):
        original = self.folder / "procurement-three-way-existing.csv"
        original.write_text("keep", encoding="utf-8")
        def outside(stage):
            return [original, self.build(stage)[1]]
        with self.assertRaisesRegex(ValueError, "Unexpected procurement"):
            publish_procurement_bundle(self.folder, outside)
        self.assertEqual(original.read_text(encoding="utf-8"), "keep")
        self.assert_clean()

    def test_symlink_evidence_rejected(self):
        source = self.folder / "source.txt"
        source.write_text("private")
        def linked(stage):
            files = self.build(stage)
            files[1].unlink()
            files[1].symlink_to(source)
            return files
        try:
            with self.assertRaisesRegex(ValueError, "regular files"):
                publish_procurement_bundle(self.folder, linked)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks not available on this host")
        self.assertTrue(source.exists())
        self.assert_clean()

    def test_hardlinked_files_rejected(self):
        def linked(stage):
            a,b = self.build(stage)
            b.unlink()
            os.link(a,b)
            return [a,b]
        with self.assertRaisesRegex(ValueError, "distinct"):
            publish_procurement_bundle(self.folder, linked)
        self.assert_clean()

    def test_failed_rename_cleans_staging(self):
        with patch("fvs_suite.procurement_bundle.os.rename", side_effect=OSError("disk problem")):
            with self.assertRaisesRegex(ValueError, "Unable to publish"):
                publish_procurement_bundle(self.folder, self.build)
        self.assert_clean()

    def test_destination_collision_preserves_existing_files(self):
        existing = self.folder / "procurement-evidence-preexisting"
        existing.mkdir()
        (existing / "prior.txt").write_text("safe")
        with patch("fvs_suite.procurement_bundle.os.path.lexists", return_value=True):
            with self.assertRaisesRegex(ValueError, "already exists"):
                publish_procurement_bundle(self.folder, self.build)
        self.assertEqual((existing / "prior.txt").read_text(), "safe")
        self.assertEqual(list(self.folder.glob(".fvs-procure-pending-*")), [])
        self.assertEqual(list(self.folder.glob("procurement-evidence-*")), [existing])

    def test_failed_second_write_not_publish_first(self):
        def fail(stage):
            a = stage / "procurement-three-way-test.csv"
            a.write_text("staged")
            raise OSError("manifest disk failure")
        with self.assertRaises(OSError):
            publish_procurement_bundle(self.folder, fail)
        self.assert_clean()

    def test_two_runs_never_replace_evidence(self):
        first = publish_procurement_bundle(self.folder, self.build)
        second = publish_procurement_bundle(self.folder, self.build)
        self.assertNotEqual(first[0].parent, second[0].parent)
        self.assertEqual(first[0].read_bytes(), second[0].read_bytes())
        self.assertEqual(len(list(self.folder.glob("procurement-evidence-*"))), 2)

    def test_created_staging_is_private_on_posix(self):
        if os.name == "nt":
            self.skipTest("POSIX mode check")
        def check(stage):
            self.assertEqual(stage.stat().st_mode & 0o077, 0)
            return self.build(stage)
        publish_procurement_bundle(self.folder, check)


if __name__ == "__main__":
    unittest.main()
