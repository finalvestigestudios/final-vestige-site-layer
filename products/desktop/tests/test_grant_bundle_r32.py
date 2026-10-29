"""R32: a failed GrantAudit export must not publish orphaned reports."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.grant_bundle import publish_grant_bundle


class GrantBundleTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def builder(self, staging):
        paths = [staging / "grant-audit-exceptions-001.csv",
                 staging / "grant-budget-check-001.csv",
                 staging / "evidence-manifest-001.txt"]
        for index, path in enumerate(paths):
            path.write_text(f"synthetic {index}\n", encoding="utf-8")
        return paths

    def test_all_three_outputs_visible_in_one_subfolder(self):
        result = publish_grant_bundle(self.root, self.builder)
        self.assertEqual(len(result), 3)
        self.assertEqual({p.parent for p in result}, {result[0].parent})
        self.assertTrue(result[0].parent.name.startswith("grant-evidence-"))
        self.assertEqual({p.name for p in result}, {p.name for p in result[0].parent.iterdir()})
        self.assertTrue(all(p.is_file() for p in result))
        self.assertEqual(result[0].read_text(encoding="utf-8"), "synthetic 0\n")
        self.assertEqual(list(self.root.glob(".fvs-grant-pending-*")), [])

    def test_preexisting_report_not_overwritten(self):
        protected = self.root / "grant-audit-exceptions-001.csv"
        protected.write_text("historical report", encoding="utf-8")
        self.assertEqual(len(publish_grant_bundle(self.root, self.builder)), 3)
        self.assertEqual(protected.read_text(encoding="utf-8"), "historical report")

    def test_two_successive_packages_have_distinct_destinations(self):
        first = publish_grant_bundle(self.root, self.builder)
        second = publish_grant_bundle(self.root, self.builder)
        self.assertNotEqual(first[0].parent, second[0].parent)
        self.assertTrue(first[0].is_file() and second[0].is_file())

    def test_manifest_failure_removes_both_staged_csvs(self):
        def fails(staging):
            self.builder(staging)[:2]
            raise ValueError("Source bytes changed after reconciliation")
        with self.assertRaisesRegex(ValueError, "Source bytes changed"):
            publish_grant_bundle(self.root, fails)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_build_error_does_not_touch_existing_package(self):
        existing = publish_grant_bundle(self.root, self.builder)
        with self.assertRaisesRegex(RuntimeError, "simulated"):
            publish_grant_bundle(self.root, lambda stage: (_ for _ in ()).throw(RuntimeError("simulated")))
        self.assertTrue(all(p.exists() for p in existing))
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_reject_missing_manifest(self):
        def no_manifest(staging):
            return self.builder(staging)[:2]
        with self.assertRaisesRegex(ValueError, "two reports"):
            publish_grant_bundle(self.root, no_manifest)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reject_swapped_report_order(self):
        with self.assertRaisesRegex(ValueError, "layout"):
            publish_grant_bundle(self.root, lambda stage: list(reversed(self.builder(stage))))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reject_nested_report_path(self):
        def nested(staging):
            paths = self.builder(staging)
            sub = staging / "nested"
            sub.mkdir()
            outside = sub / paths[0].name
            paths[0].rename(outside)
            paths[0] = outside
            return paths
        with self.assertRaisesRegex(ValueError, "layout"):
            publish_grant_bundle(self.root, nested)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reject_extra_untracked_file(self):
        def extra(staging):
            p = self.builder(staging)
            (staging / "untracked.csv").write_text("x")
            return p
        with self.assertRaisesRegex(ValueError, "Unexpected files"):
            publish_grant_bundle(self.root, extra)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reject_symlink_report(self):
        def link(staging):
            paths = self.builder(staging)
            paths[0].unlink()
            try:
                paths[0].symlink_to(paths[1])
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Symlink unavailable: {exc}")
            return paths
        with self.assertRaisesRegex(ValueError, "regular files"):
            publish_grant_bundle(self.root, link)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reject_output_symlink_directory(self):
        alias = self.root.parent / (self.root.name + "-link")
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlink unavailable: {exc}")
        self.addCleanup(alias.unlink)
        with self.assertRaisesRegex(ValueError, "non-symlink"):
            publish_grant_bundle(alias, self.builder)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_failed_atomic_rename_leaves_no_orphans(self):
        with patch("fvs_suite.grant_bundle.os.rename", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(ValueError, "Unable to publish complete"):
                publish_grant_bundle(self.root, self.builder)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_collision_does_not_touch_preexisting_directory(self):
        existing = self.root / ("grant-evidence-fixed-" + "a" * 32)
        existing.mkdir()
        (existing / "do-not-touch").write_text("untouched")
        with patch("fvs_suite.grant_bundle.secrets.token_hex", return_value="a" * 32), \
             patch("fvs_suite.grant_bundle.datetime") as fake:
            fake.now.return_value.strftime.return_value = "fixed-"
            with self.assertRaisesRegex(ValueError, "already exists"):
                publish_grant_bundle(self.root, self.builder)
        self.assertEqual((existing / "do-not-touch").read_text(), "untouched")
        self.assertEqual(list(self.root.iterdir()), [existing])

    def test_no_report_external_to_staging(self):
        external = self.root / "outside.csv"
        external.write_text("protected")
        def outside(staging):
            paths = self.builder(staging)
            paths[0] = external
            return paths
        with self.assertRaisesRegex(ValueError, "layout"):
            publish_grant_bundle(self.root, outside)
        self.assertEqual(external.read_text(), "protected")
        self.assertEqual(list(self.root.iterdir()), [external])

    def test_private_directory_on_posix(self):
        result = publish_grant_bundle(self.root, self.builder)
        if os.name == "posix":
            self.assertEqual(result[0].parent.stat().st_mode & 0o077, 0)


if __name__ == "__main__":
    unittest.main()
