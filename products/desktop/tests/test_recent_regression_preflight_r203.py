"""R203: structurally invalid late suites never import earlier audit suites."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.safe_recent_regressions_r200 import run_matrix, TARGETS


class MatrixPreflightR203(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory(prefix="fv-r203-preflight-")
        self.addCleanup(self.dir.cleanup)
        self.tests = Path(self.dir.name)
        self.sentinel = self.tests / "imported.txt"
        self.addCleanup(self._clear_imports)
        self._clear_imports()

    def _clear_imports(self):
        for name in ("test_first", "test_second", "test_third"):
            sys.modules.pop(name, None)

    def write(self, name, *, private=False):
        body = "import unittest\n"
        if private:
            body += "from pathlib import Path\nPath({!r}).write_text('imported')\n".format(str(self.sentinel))
        body += "class Sample(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n"
        (self.tests / name).write_text(body, encoding="utf-8")

    def attempt(self, targets):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            passed = run_matrix(self.tests, targets)
        combined = out.getvalue() + err.getvalue()
        self.assertNotIn(str(self.tests), combined)
        self.assertNotIn("Traceback", combined)
        return passed, combined

    def test_all_six_contracts_unchanged(self):
        self.assertEqual(len(TARGETS), 6)
        self.assertEqual(sum(value for _, value in TARGETS), 148)

    def test_complete_matrix_passes_and_executes_first(self):
        self.write("test_first.py", private=True)
        self.write("test_second.py")
        ok, result = self.attempt((("test_first.py", 1), ("test_second.py", 1)))
        self.assertTrue(ok)
        self.assertIn("2 passing audit cases", result)
        self.assertTrue(self.sentinel.exists())

    def test_late_missing_file_blocks_before_first_import(self):
        self.write("test_first.py", private=True)
        ok, result = self.attempt((("test_first.py", 1), ("test_second.py", 1)))
        self.assertFalse(ok)
        self.assertIn("HOLD:", result)
        self.assertFalse(self.sentinel.exists())

    def test_late_directory_blocks_before_first_import(self):
        self.write("test_first.py", private=True)
        (self.tests / "test_second.py").mkdir()
        self.assertFalse(self.attempt((("test_first.py", 1), ("test_second.py", 1)))[0])
        self.assertFalse(self.sentinel.exists())

    def test_late_duplicate_blocks_before_first_import(self):
        self.write("test_first.py", private=True)
        self.assertFalse(self.attempt((("test_first.py", 1), ("test_first.py", 1)))[0])
        self.assertFalse(self.sentinel.exists())

    def test_late_invalid_filename_blocks_before_first_import(self):
        self.write("test_first.py", private=True)
        self.assertFalse(self.attempt((("test_first.py", 1), ("../bad.py", 1)))[0])
        self.assertFalse(self.sentinel.exists())

    def test_late_glob_blocks_before_first_import(self):
        self.write("test_first.py", private=True)
        self.assertFalse(self.attempt((("test_first.py", 1), ("test_*.py", 1)))[0])
        self.assertFalse(self.sentinel.exists())

    def test_late_invalid_minimum_blocks_before_first_import(self):
        self.write("test_first.py", private=True)
        self.write("test_second.py")
        self.assertFalse(self.attempt((("test_first.py", 1), ("test_second.py", True)))[0])
        self.assertFalse(self.sentinel.exists())

    def test_late_symlink_detected_by_guard_without_os_privileges(self):
        self.write("test_first.py", private=True)
        self.write("test_second.py")
        original = Path.is_symlink
        def simulate_symlink(path):
            return path == self.tests / "test_second.py" or original(path)
        with patch.object(Path, "is_symlink", simulate_symlink):
            self.assertFalse(self.attempt((("test_first.py", 1), ("test_second.py", 1)))[0])
        self.assertFalse(self.sentinel.exists())

    def test_late_below_minimum_is_execution_failure_not_structural_preflight(self):
        self.write("test_first.py", private=True)
        self.write("test_second.py")
        self.assertFalse(self.attempt((("test_first.py", 1), ("test_second.py", 2)))[0])
        self.assertTrue(self.sentinel.exists())

    def test_single_valid_module_passes(self):
        self.write("test_first.py", private=True)
        self.assertTrue(self.attempt((("test_first.py", 1),))[0])


if __name__ == "__main__":
    unittest.main()
