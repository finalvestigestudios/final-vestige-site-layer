"""R202 synthetic tests: every audited case must genuinely pass; no private exceptions in logs."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.safe_recent_regressions_r200 import TARGETS, run_matrix

SECRET = 'SENSITIVE-VENDOR-REF-REDACT-ME-202'


class StrictResultsR202(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='fv-r202-synthetic-')
        self.addCleanup(temp.cleanup)
        self.tests = Path(temp.name)
        self.addCleanup(lambda: sys.modules.pop('test_r202_probe', None))
        sys.modules.pop('test_r202_probe', None)

    def write(self, body):
        (self.tests / 'test_r202_probe.py').write_text(body, encoding='utf-8')

    def run_gate(self, minimum=1):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            passed = run_matrix(self.tests, (('test_r202_probe.py', minimum),))
        output = stdout.getvalue() + stderr.getvalue()
        self.assertNotIn(SECRET, output)
        self.assertNotIn(str(self.tests), output)
        self.assertNotIn('Traceback', output)
        return passed, output

    def test_manifest_retained(self):
        self.assertEqual(sum(n for _, n in TARGETS), 148)
        self.assertEqual(len(TARGETS), 6)

    def test_clean_pass_still_green(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n def test_ok(self): self.assertEqual(1, 1)\n')
        passed, report = self.run_gate()
        self.assertTrue(passed)
        self.assertIn('1 executed', report)

    def test_multiple_clean_cases_still_green(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n def test_a(self): pass\n def test_b(self): pass\n')
        self.assertTrue(self.run_gate(minimum=2)[0])

    def test_mixed_success_and_skipped_method_holds(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n def test_a(self): pass\n @unittest.skip(%r)\n def test_b(self): pass\n' % SECRET)
        passed, report = self.run_gate(minimum=2)
        self.assertFalse(passed)
        self.assertIn('HOLD:', report)

    def test_mixed_success_and_skipped_class_holds(self):
        self.write('import unittest\n@unittest.skip(%r)\nclass A(unittest.TestCase):\n def test_a(self): pass\nclass B(unittest.TestCase):\n def test_b(self): pass\n' % SECRET)
        self.assertFalse(self.run_gate(minimum=2)[0])

    def test_only_skips_holds(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n @unittest.skip(%r)\n def test_a(self): pass\n' % SECRET)
        self.assertFalse(self.run_gate()[0])

    def test_expected_failure_alone_holds(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n @unittest.expectedFailure\n def test_a(self): self.fail(%r)\n' % SECRET)
        self.assertFalse(self.run_gate()[0])

    def test_expected_failure_mixed_with_pass_holds(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n @unittest.expectedFailure\n def test_a(self): self.fail(%r)\n def test_b(self): pass\n' % SECRET)
        self.assertFalse(self.run_gate(minimum=2)[0])

    def test_unexpected_success_holds(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n @unittest.expectedFailure\n def test_a(self): pass\n')
        self.assertFalse(self.run_gate()[0])

    def test_keyboard_interrupt_no_secret_traceback(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n def test_a(self): raise KeyboardInterrupt(%r)\n' % SECRET)
        self.assertFalse(self.run_gate()[0])

    def test_system_exit_no_secret_traceback(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n def test_a(self): raise SystemExit(%r)\n' % SECRET)
        self.assertFalse(self.run_gate()[0])

    def test_import_keyboard_interrupt_no_secret_traceback(self):
        self.write('raise KeyboardInterrupt(%r)\n' % SECRET)
        self.assertFalse(self.run_gate()[0])

    def test_import_system_exit_no_secret_traceback(self):
        self.write('raise SystemExit(%r)\n' % SECRET)
        self.assertFalse(self.run_gate()[0])

    def test_setup_class_system_exit_holds(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n @classmethod\n def setUpClass(cls): raise SystemExit(%r)\n def test_a(self): pass\n' % SECRET)
        self.assertFalse(self.run_gate()[0])

    def test_teardown_keyboard_interrupt_holds(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n def test_a(self): pass\n def tearDown(self): raise KeyboardInterrupt(%r)\n' % SECRET)
        self.assertFalse(self.run_gate()[0])

    def test_unhandled_regular_exception_still_holds(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n def test_a(self): raise ValueError(%r)\n' % SECRET)
        self.assertFalse(self.run_gate()[0])

    def test_silent_skip_reason_and_no_financial_exception_text(self):
        self.write('import unittest\nclass C(unittest.TestCase):\n def test_a(self): pass\n @unittest.skip(%r)\n def test_b(self): pass\n' % SECRET)
        _, report = self.run_gate(minimum=2)
        self.assertIn('1 skipped', report)


if __name__ == '__main__':
    unittest.main()
