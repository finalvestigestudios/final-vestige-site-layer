"""R99: real subprocess checks for private unittest discovery diagnostics.

All fixtures are invented; no financial data, customer filenames, or real keys.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import offline_source_gate as gate
from scripts import unittest_provenance as child

RUNNER = Path(child.__file__).resolve()


def _child(root: Path, optimized: bool = False):
    command = [sys.executable] + (["-OO"] if optimized else []) + [str(RUNNER)]
    return subprocess.run(command, cwd=root, capture_output=True, timeout=30, check=False)


class DiscoveryMarkerR99Tests(unittest.TestCase):
    def test_import_failure_marker_survives_private_io_redirection_in_both_modes(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r99-") as directory:
            root = Path(directory)
            tests = root / "products" / "desktop" / "tests"
            tests.mkdir(parents=True)
            (tests / "test_broken.py").write_text(
                "raise ImportError('PRIVATE_CLIENT_FILE_SHOULD_NOT_APPEAR')\n",
                encoding="utf-8",
            )
            for optimized in (False, True):
                with self.subTest(optimized=optimized):
                    result = _child(root, optimized)
                    self.assertNotEqual(result.returncode, 0)
                    diagnostic = gate._safe_child_diagnostic(result.stdout)
                    self.assertIsNotNone(diagnostic)
                    self.assertIn('"phase":"discovery"', diagnostic)
                    self.assertIn('"modules":["test_broken"]', diagnostic)
                    self.assertNotIn(b"PRIVATE_CLIENT_FILE", result.stdout + result.stderr)
                    self.assertIn(b"REJECTED: desktop unittest provenance unavailable", result.stderr)

    def test_discovery_failure_prevents_running_other_valid_tests(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r99-") as directory:
            root = Path(directory)
            tests = root / "products" / "desktop" / "tests"
            tests.mkdir(parents=True)
            sentinel = root / "SHOULD_NOT_EXIST"
            (tests / "test_good.py").write_text(
                "import unittest\nfrom pathlib import Path\n"
                "class TestGood(unittest.TestCase):\n"
                " def test_must_not_execute(self):\n"
                f"  Path({str(sentinel)!r}).write_text('unexpected')\n",
                encoding="utf-8",
            )
            (tests / "test_bad.py").write_text(
                "raise ImportError('PRIVATE_ACCOUNT_NUMBER')\n", encoding="utf-8",
            )
            result = _child(root)
            self.assertNotEqual(result.returncode, 0)
            diagnostic = gate._safe_child_diagnostic(result.stdout)
            self.assertIsNotNone(diagnostic)
            self.assertIn('"modules":["test_bad"]', diagnostic)
            self.assertFalse(sentinel.exists(), "Valid tests must not run after incomplete discovery")
            self.assertNotIn(b"PRIVATE_ACCOUNT_NUMBER", result.stdout + result.stderr)

    def test_eighteen_failed_imports_are_sorted_and_bounded(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r99-") as directory:
            root = Path(directory)
            tests = root / "products" / "desktop" / "tests"
            tests.mkdir(parents=True)
            for i in range(18):
                (tests / f"test_{i:02d}.py").write_text(
                    "raise ImportError('PRIVATE_FIXTURE')\n", encoding="utf-8",
                )
            result = _child(root)
            self.assertNotEqual(result.returncode, 0)
            diagnostic = gate._safe_child_diagnostic(result.stdout)
            self.assertIsNotNone(diagnostic)
            self.assertIn('"omitted_module_count":6', diagnostic)
            self.assertIn('"modules":[' + ','.join(
                f'"test_{i:02d}"' for i in range(12)) + ']', diagnostic)
            self.assertNotIn(b"PRIVATE_FIXTURE", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
