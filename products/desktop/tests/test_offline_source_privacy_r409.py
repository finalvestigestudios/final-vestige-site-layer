"""R409: deny symlink/junction source trees and never buffer private child output.

Only synthetic launchers and fake filesystem metadata are used in this suite.
"""
from __future__ import annotations

from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class OfflineSourcePrivacyR409(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "desktop"
        self.root.mkdir()
        (self.root / "fvs_suite").mkdir()
        (self.root / "launchers").mkdir()
        (self.root / "fvs_suite" / "__init__.py").write_text("# suite\n", encoding="utf-8")
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test']:\n"
            "        raise SystemExit(12)\n", encoding="utf-8")
        for app, filename in gate.PRODUCTS:
            (self.root / "launchers" / filename).write_text(
                f"from fvs_suite.launcher import launch\nlaunch({app!r})\n", encoding="utf-8")
        (self.root / "offline_source_smoke_r408.py").write_bytes(Path(gate.__file__).read_bytes())

    def assert_no_spawn(self, root: Path | None = None):
        with patch.object(gate.subprocess, "run") as run:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(root or self.root)
            run.assert_not_called()

    def symlink(self, link: Path, target: Path, *, directory: bool = True):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (NotImplementedError, OSError):
            self.skipTest("OS disallows test symlinks")

    def test_symlinked_desktop_root_never_spawns(self):
        link = self.root.parent / "desktop_link"
        self.symlink(link, self.root)
        self.assert_no_spawn(link)

    def test_symlinked_suite_root_never_spawns(self):
        suite = self.root / "fvs_suite"
        suite.rename(self.root / "real_suite")
        self.symlink(suite, self.root / "real_suite")
        self.assert_no_spawn()

    def test_symlinked_launcher_root_never_spawns(self):
        launchers = self.root / "launchers"
        launchers.rename(self.root / "real_launchers")
        self.symlink(launchers, self.root / "real_launchers")
        self.assert_no_spawn()

    def test_nested_symlink_directory_with_python_never_spawns(self):
        target = self.root.parent / "outside"
        target.mkdir()
        (target / "external.py").write_text("raise SystemExit('SECRET')\n", encoding="utf-8")
        self.symlink(self.root / "fvs_suite" / "linked", target)
        self.assert_no_spawn()

    def test_nested_symlink_directory_even_without_python_never_spawns(self):
        target = self.root.parent / "outside"
        target.mkdir()
        (target / "unrelated.txt").write_text("text\n", encoding="utf-8")
        self.symlink(self.root / "fvs_suite" / "linked", target)
        self.assert_no_spawn()

    def test_invalid_source_suite_is_file_never_spawns(self):
        (self.root / "fvs_suite" / "__init__.py").unlink()
        (self.root / "fvs_suite" / "launcher.py").unlink()
        (self.root / "fvs_suite").rmdir()
        (self.root / "fvs_suite").write_text("not a directory", encoding="utf-8")
        self.assert_no_spawn()

    def test_missing_source_directory_never_spawns(self):
        (self.root / "launchers").rename(self.root / "away")
        self.assert_no_spawn()

    def test_windows_directory_junction_reparse_flag_never_spawns(self):
        fake = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755,
                               st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
        with patch.object(Path, "lstat", return_value=fake):
            self.assert_no_spawn()

    def test_directory_reparse_flag_is_checked_not_just_isdir(self):
        fake = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755,
                               st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
        with patch.object(Path, "lstat", return_value=fake):
            with self.assertRaisesRegex(gate.SourceGateError, "Unsafe desktop source directory"):
                gate._require_real_directory(self.root)

    def test_real_nested_directories_remain_valid(self):
        sub = self.root / "fvs_suite" / "nested"
        sub.mkdir()
        (sub / "module.py").write_text("# benign source\n", encoding="utf-8")
        result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 12)
        self.assertFalse(result["release_authorized"])

    def test_all_twelve_children_discard_output_at_os_device_level(self):
        with patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess(
                args=[], returncode=0)) as subprocess_run:
            result = gate.run_gate(self.root)
        self.assertEqual(result["required"], 12)
        self.assertEqual(subprocess_run.call_count, 12)
        self.assertEqual(result["passed"], 12)
        for call in subprocess_run.call_args_list:
            self.assertEqual(call.kwargs["stdin"], subprocess.DEVNULL)
            self.assertEqual(call.kwargs["stdout"], subprocess.DEVNULL)
            self.assertEqual(call.kwargs["stderr"], subprocess.DEVNULL)
            self.assertFalse(call.kwargs["check"])
            self.assertNotIn("shell", call.kwargs)

    def test_large_private_child_output_not_recorded(self):
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    sys.stdout.write('PRIVATE_VENDOR_REF' * 400000)\n"
            "    sys.stderr.write('SECRET_PAYROLL' * 400000)\n", encoding="utf-8")
        result = gate.run_gate(self.root)
        self.assertEqual(result["passed"], 12)
        self.assertNotIn("PRIVATE_VENDOR_REF", repr(result))
        self.assertNotIn("SECRET_PAYROLL", repr(result))
        self.assertFalse(result["release_authorized"])


if __name__ == "__main__":
    unittest.main()
