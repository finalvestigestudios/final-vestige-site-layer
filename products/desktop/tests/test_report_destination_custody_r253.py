"""R253: six-app report destination custody and premium bundle completeness.

Synthetic filesystem evidence only. No customer data, telemetry, keys, or
payments. A source path is evidence navigation, never compliance approval.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
from fvs_suite.report_completion import confirm_report_files

STAMP = "20261107-005400-123456"
BUNDLE_STAMP = "20261107T085400Z-" + "a" * 32
FREE = {
    "ledger": ("ledger-diff", ".csv"),
    "invoices": ("invoice-twins", ".csv"),
    "spend": ("spend-map", ".csv"),
    "policy": ("policy-delta", ".txt"),
}
PREMIUM = {
    "grants": ("grant-evidence-", (("grant-audit-exceptions", ".csv"),
                                  ("grant-budget-check", ".csv"),
                                  ("evidence-manifest", ".txt"))),
    "procurement": ("procurement-evidence-", (("procurement-three-way", ".csv"),
                                              ("evidence-manifest", ".txt"))),
}


class ReportDestinationCustodyR253(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.output = self.root / "selected"
        self.output.mkdir()

    def artifact(self, root, stem, extension):
        path = root / f"{stem}-{STAMP}{extension}"
        path.write_text("synthetic source SHA\n", encoding="utf-8")
        return path

    def free(self, app):
        stem, ext = FREE[app]
        return [self.artifact(self.output, stem, ext)]

    def premium(self, app):
        prefix, layout = PREMIUM[app]
        package = self.output / (prefix + BUNDLE_STAMP)
        package.mkdir()
        files = [self.artifact(package, stem, ext) for stem, ext in layout]
        # The real premium publisher inventories source files first, then
        # reports in their returned order. Keep inherited R253 fixtures honest.
        report_lines = [
            f"{json.dumps(p.name, ensure_ascii=True)[1:-1]}\t"
            f"{hashlib.sha256(p.read_bytes()).hexdigest()}\n"
            for p in files[:-1]
        ]
        source_lines = [f"source-{i}.csv\t" + "a" * 64 + "\n" for i in range(3)]
        files[-1].write_text(
            "SHA-256 file inventory. Hashes do not certify accuracy or compliance.\n"
            + "".join(source_lines + report_lines), encoding="ascii"
        )
        return files

    def verify(self, files, app):
        return confirm_report_files(files, folder=str(self.output), app_id=app)

    def test_all_four_free_apps_validate_real_filename_contract(self):
        for app in FREE:
            with self.subTest(app=app):
                files = self.free(app)
                self.assertEqual(self.verify(files, app), tuple(files))

    def test_both_premium_bundles_require_full_manifest(self):
        for app in PREMIUM:
            with self.subTest(app=app):
                files = self.premium(app)
                self.assertEqual(self.verify(files, app), tuple(files))

    def test_legacy_direct_helper_stays_compatible(self):
        file = self.root / "any.csv"
        file.write_text("old caller\n")
        self.assertEqual(confirm_report_files([file]), (file,))

    def test_missing_folder_or_product_pair_fails_closed(self):
        files = self.free("ledger")
        for kwargs in ({"folder": str(self.output)}, {"app_id": "ledger"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                confirm_report_files(files, **kwargs)

    def test_rejects_report_from_entirely_different_folder(self):
        file = self.artifact(self.root, "ledger-diff", ".csv")
        with self.assertRaisesRegex(ValueError, "location"):
            self.verify([file], "ledger")

    def test_rejects_existing_file_from_private_sibling_folder(self):
        private = self.root / "PRIVATE_CLIENT"
        private.mkdir()
        file = self.artifact(private, "spend-map", ".csv")
        with self.assertRaises(ValueError) as caught:
            self.verify([file], "spend")
        self.assertNotIn("PRIVATE_CLIENT", str(caught.exception))

    def test_rejects_wrong_free_product_artifact(self):
        file = self.free("ledger")[0]
        with self.assertRaises(ValueError):
            self.verify([file], "invoices")

    def test_rejects_free_product_with_extra_unrelated_artifact(self):
        file = self.free("spend")[0]
        other = self.artifact(self.output, "invoice-twins", ".csv")
        with self.assertRaises(ValueError):
            self.verify([file, other], "spend")

    def test_rejects_free_output_with_replaced_report_name(self):
        file = self.artifact(self.output, "report", ".csv")
        with self.assertRaises(ValueError):
            self.verify([file], "ledger")

    def test_rejects_free_bad_extension_and_fake_timestamp(self):
        for name in ("ledger-diff-20261107-005400-123456.txt",
                     "ledger-diff-unsigned.csv",
                     "ledger-diff-20261107-005400-123456.csv.exe"):
            with self.subTest(name=name):
                file = self.output / name
                file.write_text("synthetic")
                with self.assertRaises(ValueError):
                    self.verify([file], "ledger")

    def test_rejects_empty_output_directory(self):
        self.free("ledger")
        with self.assertRaises(ValueError):
            confirm_report_files([self.output / f"ledger-diff-{STAMP}.csv"],
                                 folder="", app_id="ledger")

    def test_rejects_unknown_and_subclassed_product_identity(self):
        files = self.free("ledger")
        class AppAlias(str):
            pass
        for product in ("unknown", "", AppAlias("ledger"), 7, True):
            with self.subTest(product=str(product)), self.assertRaises(ValueError):
                confirm_report_files(files, folder=str(self.output), app_id=product)

    def test_rejects_non_native_directory_type(self):
        files = self.free("ledger")
        class PathAlias(type(self.output)):
            pass
        with self.assertRaises(ValueError):
            confirm_report_files(files, folder=PathAlias(self.output), app_id="ledger")

    def test_rejects_symlink_selected_directory_without_modifying_file(self):
        files = self.free("ledger")
        alias = self.root / "alias"
        try:
            alias.symlink_to(self.output, target_is_directory=True)
        except (OSError, NotImplementedError) as err:
            self.skipTest(f"No symlink capability: {type(err).__name__}")
        original = files[0].read_bytes()
        with self.assertRaises(ValueError):
            confirm_report_files(files, folder=str(alias), app_id="ledger")
        self.assertEqual(files[0].read_bytes(), original)

    def test_rejects_premium_bundle_misplaced_under_other_directory(self):
        files = self.premium("grants")
        other = self.root / "other"
        other.mkdir()
        with self.assertRaises(ValueError):
            confirm_report_files(files, folder=str(other), app_id="grants")

    def test_rejects_premium_missing_manifest(self):
        files = self.premium("procurement")
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            self.verify(files[:1], "procurement")

    def test_rejects_premium_missing_budget_report(self):
        files = self.premium("grants")
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            self.verify([files[0], files[2]], "grants")

    def test_rejects_premium_package_with_wrong_artifact_order(self):
        files = self.premium("grants")
        with self.assertRaises(ValueError):
            self.verify(files[::-1], "grants")

    def test_rejects_mixed_package_files_even_when_each_exists(self):
        files = self.premium("grants")
        second = self.output / ("grant-evidence-20261107T095400Z-" + "b" * 32)
        second.mkdir()
        fake = self.artifact(second, "evidence-manifest", ".txt")
        with self.assertRaises(ValueError):
            self.verify([files[0], files[1], fake], "grants")

    def test_rejects_wrong_premium_package_prefix(self):
        files = self.premium("grants")
        new = self.output / ("procurement-evidence-" + BUNDLE_STAMP)
        files[0].parent.rename(new)
        with self.assertRaises(ValueError):
            self.verify([new / f.name for f in files], "grants")

    def test_rejects_premium_package_name_without_random_suffix(self):
        files = self.premium("procurement")
        new = self.output / "procurement-evidence-20261107T085400Z"
        files[0].parent.rename(new)
        with self.assertRaises(ValueError):
            self.verify([new / f.name for f in files], "procurement")

    def test_rejects_symlinked_premium_bundle(self):
        files = self.premium("procurement")
        target = files[0].parent
        alias = self.output / ("procurement-evidence-20261107T095400Z-" + "b" * 32)
        try:
            alias.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError) as err:
            self.skipTest(f"No symlink capability: {type(err).__name__}")
        with self.assertRaises(ValueError):
            self.verify([alias / f.name for f in files], "procurement")

    def test_rejects_hardlinked_duplicate_evidence(self):
        files = self.premium("grants")
        files[1].unlink()
        try:
            os.link(files[0], files[1])
        except (OSError, NotImplementedError) as err:
            self.skipTest(f"No hardlink capability: {type(err).__name__}")
        with self.assertRaisesRegex(ValueError, "aliased"):
            self.verify(files, "grants")

    def test_never_deletes_existing_outputs_on_failed_validation(self):
        files = self.premium("grants")
        before = [f.read_bytes() for f in files]
        with self.assertRaises(ValueError):
            self.verify([files[0], files[2]], "grants")
        self.assertEqual([f.read_bytes() for f in files], before)

    def test_paths_are_native_and_do_not_trigger_custom_hooks(self):
        files = self.free("ledger")
        class ForgedPath(type(files[0])):
            def __str__(self):
                raise AssertionError("untrusted __str__")
        with self.assertRaises(ValueError):
            self.verify([ForgedPath(files[0])], "ledger")

    def test_second_file_missing_still_fails_before_any_success(self):
        files = self.premium("procurement")
        files[1].unlink()
        with self.assertRaises(FileNotFoundError):
            self.verify(files, "procurement")


if __name__ == "__main__":
    unittest.main()
