"""R201: synthetic financial test failures never leak text into CI logs."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.safe_recent_regressions_r200 import TARGETS, run_matrix

SECRET = "PRIVATE-INVOICE-9815-CLIENT-NAME-NOT-FOR-LOGS"


class RecentRegressionPrivacyR201(unittest.TestCase):
    def setUp(self):
        box = tempfile.TemporaryDirectory(prefix="fv-private-audit-")
        self.addCleanup(box.cleanup)
        self.tests = Path(box.name)
        self.addCleanup(lambda: sys.modules.pop("test_private", None))
        sys.modules.pop("test_private", None)

    def write(self, body):
        (self.tests / "test_private.py").write_text(body, encoding="utf-8")

    def run_gate(self, minimum=1):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            passed = run_matrix(self.tests, (("test_private.py", minimum),))
        output = out.getvalue() + err.getvalue()
        self.assertNotIn(SECRET, output)
        self.assertNotIn(str(self.tests), output)
        self.assertNotIn("Traceback", output)
        return passed, output

    def test_audited_manifest_is_unchanged(self):
        self.assertEqual(sum(size for _, size in TARGETS), 148)

    def test_simple_pass_reports_static_count(self):
        self.write("import unittest\nclass C(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n")
        passed, output = self.run_gate()
        self.assertTrue(passed)
        self.assertIn("1 executed, 0 skipped", output)

    def test_stdout_from_success_is_suppressed(self):
        self.write(f"import unittest\nclass C(unittest.TestCase):\n def test_ok(self): print({SECRET!r})\n")
        self.assertTrue(self.run_gate()[0])

    def test_stderr_from_success_is_suppressed(self):
        self.write(f"import unittest,sys\nclass C(unittest.TestCase):\n def test_ok(self): sys.stderr.write({SECRET!r})\n")
        self.assertTrue(self.run_gate()[0])

    def test_import_time_stdout_is_suppressed(self):
        self.write(f"print({SECRET!r})\nimport unittest\nclass C(unittest.TestCase):\n def test_ok(self): pass\n")
        self.assertTrue(self.run_gate()[0])

    def test_import_time_stderr_is_suppressed(self):
        self.write(f"import sys\nsys.stderr.write({SECRET!r})\nimport unittest\nclass C(unittest.TestCase):\n def test_ok(self): pass\n")
        self.assertTrue(self.run_gate()[0])

    def test_failure_assertion_details_are_suppressed(self):
        self.write(f"import unittest\nclass C(unittest.TestCase):\n def test_bad(self): self.assertEqual({SECRET!r}, 'other')\n")
        passed, output = self.run_gate()
        self.assertFalse(passed)
        self.assertIn("HOLD:", output)

    def test_exception_message_is_suppressed(self):
        self.write(f"import unittest\nclass C(unittest.TestCase):\n def test_bad(self): raise RuntimeError({SECRET!r})\n")
        self.assertFalse(self.run_gate()[0])

    def test_set_up_class_exception_is_suppressed(self):
        self.write(f"import unittest\nclass C(unittest.TestCase):\n @classmethod\n def setUpClass(cls): raise ValueError({SECRET!r})\n def test_ok(self): pass\n")
        self.assertFalse(self.run_gate()[0])

    def test_tear_down_class_exception_is_suppressed(self):
        self.write(f"import unittest\nclass C(unittest.TestCase):\n @classmethod\n def tearDownClass(cls): raise ValueError({SECRET!r})\n def test_ok(self): pass\n")
        self.assertFalse(self.run_gate()[0])

    def test_import_failure_is_suppressed(self):
        self.write(f"raise RuntimeError({SECRET!r})\n")
        self.assertFalse(self.run_gate()[0])

    def test_all_skipped_reason_is_suppressed(self):
        self.write(f"import unittest\nclass C(unittest.TestCase):\n @unittest.skip({SECRET!r})\n def test_skip(self): pass\n")
        passed, output = self.run_gate()
        self.assertFalse(passed)
        self.assertIn("1 skipped", output)

    def test_partial_skip_reason_is_suppressed(self):
        self.write(f"import unittest\nclass C(unittest.TestCase):\n @unittest.skip({SECRET!r})\n def test_skip(self): pass\n def test_ok(self): pass\n")
        passed, output = self.run_gate(minimum=2)
        self.assertTrue(passed)
        self.assertIn("2 executed, 1 skipped", output)

    def test_subtest_failure_is_suppressed(self):
        self.write(f"import unittest\nclass C(unittest.TestCase):\n def test_sub(self):\n  with self.subTest(key={SECRET!r}): self.fail({SECRET!r})\n")
        self.assertFalse(self.run_gate()[0])

    def test_missing_test_file_fails_closed_without_path(self):
        self.assertFalse(self.run_gate()[0])

    def test_zero_discovery_fails_closed(self):
        self.write("def helper(): pass\n")
        self.assertFalse(self.run_gate()[0])

    def test_tampered_minimum_fails_closed(self):
        self.write("import unittest\nclass C(unittest.TestCase):\n def test_ok(self): pass\n")
        self.assertFalse(self.run_gate(minimum=2)[0])


if __name__ == "__main__":
    unittest.main()
