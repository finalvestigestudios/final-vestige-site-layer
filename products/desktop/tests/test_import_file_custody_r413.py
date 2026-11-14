"""R413 offline six-source custody: all import-root file types and assets.

Synthetic source launchers only. No real financial data, executables, paid
entitlements or Windows release claims are involved in this regression suite.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class SourceFileCustodyR413(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "desktop"
        self.root.mkdir()
        (self.root / "fvs_suite").mkdir()
        (self.root / "launchers").mkdir()
        (self.root / "fvs_suite" / "__init__.py").write_text("# synthetic\n", encoding="utf-8")
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test']:\n"
            "        raise SystemExit(13)\n", encoding="utf-8")
        for app, name in gate.PRODUCTS:
            (self.root / "launchers" / name).write_text(
                f"from fvs_suite.launcher import launch\nlaunch({app!r})\n",
                encoding="utf-8")
        (self.root / "offline_source_smoke_r408.py").write_bytes(Path(gate.__file__).read_bytes())

    def assert_denied_before_spawn(self):
        with patch.object(gate.subprocess, "run") as run:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(self.root)
            run.assert_not_called()

    def symlink(self, location, target):
        try:
            location.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("No filesystem symlink privilege")

    def test_outside_symlinked_json_asset_fails_before_launch(self):
        outside = self.root.parent / "outside-private-policy.json"
        outside.write_text('{"secret":"PRIVATE"}', encoding="utf-8")
        self.symlink(self.root / "fvs_suite" / "policy.json", outside)
        self.assert_denied_before_spawn()

    def test_inside_symlinked_csv_asset_is_rejected(self):
        source = self.root / "fvs_suite" / "real.csv"
        source.write_text("a,b\n", encoding="utf-8")
        self.symlink(self.root / "fvs_suite" / "alias.csv", source)
        self.assert_denied_before_spawn()

    def test_nested_import_asset_symlink_is_rejected(self):
        nested = self.root / "fvs_suite" / "nested"
        nested.mkdir()
        original = nested / "real.json"
        original.write_text("{}", encoding="utf-8")
        self.symlink(nested / "link.json", original)
        self.assert_denied_before_spawn()

    def test_linked_source_python_file_is_rejected(self):
        external = self.root.parent / "outside.py"
        external.write_text("# external\n", encoding="utf-8")
        self.symlink(self.root / "fvs_suite" / "external.py", external)
        self.assert_denied_before_spawn()

    def test_hardlinked_csv_asset_cannot_alias_outside_checkout(self):
        original = self.root.parent / "private-purchases.csv"
        original.write_text("private,amount\n", encoding="utf-8")
        try:
            os.link(original, self.root / "fvs_suite" / "copy.csv")
        except OSError:
            self.skipTest("No hardlink support")
        self.assert_denied_before_spawn()

    def test_hardlinked_required_launcher_is_rejected(self):
        launcher = self.root / "launchers" / "LedgerDiffLite.py"
        alias = self.root.parent / "outside-launcher.py"
        try:
            os.link(launcher, alias)
        except OSError:
            self.skipTest("No hardlink support")
        self.assert_denied_before_spawn()

    def test_fifo_asset_is_rejected_before_any_process(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO not supported")
        os.mkfifo(self.root / "fvs_suite" / "input.csv")
        self.assert_denied_before_spawn()

    def test_windows_file_reparse_flag_rejected_without_reading_target(self):
        asset = self.root / "fvs_suite" / "template.csv"
        asset.write_text("a,b\n", encoding="utf-8")
        original = Path.lstat
        def lstat(p):
            info = original(p)
            if p == asset:
                return SimpleNamespace(st_mode=info.st_mode, st_nlink=1,
                    st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
            return info
        with patch.object(Path, "lstat", lstat):
            self.assert_denied_before_spawn()

    def test_digest_fingerprints_non_python_policy_asset(self):
        asset = self.root / "fvs_suite" / "policy.json"
        asset.write_text('{"enabled":true}', encoding="utf-8")
        before = gate.source_digest(self.root)
        asset.write_text('{"enabled":false}', encoding="utf-8")
        self.assertNotEqual(before, gate.source_digest(self.root))

    def test_digest_fingerprints_unlisted_launcher_python_module(self):
        extra = self.root / "launchers" / "dynamic.py"
        extra.write_text("value=1\n", encoding="utf-8")
        before = gate.source_digest(self.root)
        extra.write_text("value=2\n", encoding="utf-8")
        self.assertNotEqual(before, gate.source_digest(self.root))

    def test_adding_asset_midrun_stops_after_one_child(self):
        target = self.root / "fvs_suite" / "new.json"
        def inject(*args, **kwargs):
            target.write_text("{}", encoding="utf-8")
            return subprocess.CompletedProcess(args=args[0], returncode=0)
        with patch.object(gate.subprocess, "run", side_effect=inject) as run:
            with self.assertRaisesRegex(gate.SourceGateError, "changed during"):
                gate.run_gate(self.root)
        self.assertEqual(run.call_count, 1)

    def test_oversized_asset_fails_without_launching(self):
        asset = self.root / "fvs_suite" / "large.json"
        asset.write_bytes(b"x" * (gate.MAX_SOURCE_BYTES + 1))
        self.assert_denied_before_spawn()

    def test_private_path_and_content_not_echoed_in_file_error(self):
        private = "CLIENT_ACCT_99177"
        asset = self.root / "fvs_suite" / f"{private}.json"
        outside = self.root.parent / f"{private}.json"
        outside.write_text(private, encoding="utf-8")
        self.symlink(asset, outside)
        with self.assertRaises(gate.SourceGateError) as ctx:
            gate.source_digest(self.root)
        self.assertNotIn(private, str(ctx.exception))

    def test_valid_json_csv_assets_and_six_launchers_pass_both_modes(self):
        (self.root / "fvs_suite" / "policy.json").write_text("{}", encoding="utf-8")
        (self.root / "fvs_suite" / "template.csv").write_text("a,b\n", encoding="utf-8")
        result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 12)
        self.assertEqual(result["required"], 12)
        self.assertFalse(result["release_authorized"])
        self.assertEqual(result["evidence"], "SOURCE_ONLY_NOT_WINDOWS_BINARY")
        self.assertEqual(len(result["tests"]), 6)


if __name__ == "__main__":
    unittest.main()
