"""R200: no missing, empty, symlinked or failing audit suite may silently pass."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.safe_recent_regressions_r200 import TARGETS, run_matrix


class RecentAuditMatrixR200(unittest.TestCase):
    def setUp(self):
        box = tempfile.TemporaryDirectory(prefix="fv-r200-matrix-")
        self.addCleanup(box.cleanup)
        self.tests = Path(box.name)
        for name in ("test_good", "test_next", "test_source"):
            sys.modules.pop(name, None)

    def tearDown(self):
        for name in ("test_good", "test_next", "test_source"):
            sys.modules.pop(name, None)

    def module(self, name="test_good.py", body="import unittest\nclass Sample(unittest.TestCase):\n    def test_ok(self):\n        self.assertEqual(1 + 1, 2)\n"):
        (self.tests / name).write_text(body, encoding="utf-8")

    def execute(self, targets=(("test_good.py", 1),)):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return run_matrix(self.tests, targets)

    def test_production_matrix_has_all_six_named_suites(self):
        self.assertEqual(tuple(x[0].split("_r")[-1] for x in TARGETS),
                         ("194.py", "195.py", "196.py", "197.py", "198.py", "199.py"))
        self.assertEqual(sum(count for _, count in TARGETS), 148)

    def test_one_real_synthetic_test_passes(self):
        self.module()
        self.assertTrue(self.execute())

    def test_multiple_distinct_modules_pass(self):
        self.module()
        self.module("test_next.py", "import unittest\nclass Sample(unittest.TestCase):\n    def test_next(self):\n        self.assertTrue(True)\n")
        self.assertTrue(self.execute((("test_good.py", 1), ("test_next.py", 1))))

    def test_missing_test_module_fails_closed(self):
        self.assertFalse(self.execute())

    def test_zero_test_module_fails_closed(self):
        self.module(body="def helper():\n    pass\n")
        self.assertFalse(self.execute())

    def test_fewer_than_contract_tests_fails_closed(self):
        self.module()
        self.assertFalse(self.execute((("test_good.py", 2),)))

    def test_failing_assertion_fails_closed(self):
        self.module(body="import unittest\nclass Sample(unittest.TestCase):\n    def test_bad(self):\n        self.assertEqual(1, 2)\n")
        self.assertFalse(self.execute())

    def test_raised_exception_fails_closed(self):
        self.module(body="import unittest\nclass Sample(unittest.TestCase):\n    def test_bad(self):\n        raise RuntimeError('synthetic')\n")
        self.assertFalse(self.execute())

    def test_symlinked_test_fails_closed(self):
        self.module("test_source.py")
        try:
            (self.tests / "test_good.py").symlink_to(self.tests / "test_source.py")
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        self.assertFalse(self.execute())

    def test_duplicate_module_fails_closed(self):
        self.module()
        self.assertFalse(self.execute((("test_good.py", 1), ("test_good.py", 1))))

    def test_path_traversal_fails_closed(self):
        self.module()
        self.assertFalse(self.execute((("../test_good.py", 1),)))

    def test_glob_pattern_fails_closed(self):
        self.module()
        self.assertFalse(self.execute((("test_*.py", 1),)))

    def test_missing_directory_fails_closed(self):
        self.assertFalse(run_matrix(self.tests / "absent", (("test_good.py", 1),)))

    def test_boolean_count_is_not_a_number_of_tests(self):
        self.module()
        self.assertFalse(self.execute((("test_good.py", True),)))

    def test_zero_count_is_invalid(self):
        self.module()
        self.assertFalse(self.execute((("test_good.py", 0),)))

    def test_skip_is_visible_and_not_counted_as_pass(self):
        self.module(body="import unittest\n@unittest.skip('synthetic unsupported platform')\nclass Sample(unittest.TestCase):\n    def test_skipped(self):\n        pass\n")
        stream = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stream):
            self.assertFalse(run_matrix(self.tests, (("test_good.py", 1),)))
        self.assertIn("1 skipped", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
