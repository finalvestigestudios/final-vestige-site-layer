"""R491 isolated Python pre-assignment gate integration, cross-platform."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from windows_source_start_custody_r491 import guarded_windows_command


class WindowsSourceStartCustodyR491(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="fvs-r491-")
        self.addCleanup(self.tmp.cleanup)
        self.desktop = Path(self.tmp.name)
        (self.desktop / "tests").mkdir()
        (self.desktop / "tests" / "test_fixture.py").write_text(
            "import unittest\n"
            "from pathlib import Path\n"
            "class Fixture(unittest.TestCase):\n"
            "    def test_real_run(self):\n"
            "        Path(__file__).with_suffix('.executed').write_text('ran')\n"
            "        self.assertEqual(2 * 3, 6)\n", encoding="utf-8")

    def command(self, *flags):
        raw = (sys.executable, *flags, "-B", "-W", "error", "-m", "unittest",
               "discover", "-s", str(self.desktop / "tests"), "-p", "test_fixture.py")
        return guarded_windows_command(raw, self.desktop)

    def start(self, *flags):
        return subprocess.Popen(self.command(*flags), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def test_no_test_code_executes_before_authorized_handoff(self):
        p = self.start()
        try:
            # Let a broken no-gate bootstrap reach unittest if it can.
            time.sleep(0.2)
            self.assertIsNone(p.poll())
            self.assertFalse((self.desktop / "tests" / "test_fixture.executed").exists())
            p.stdin.write(b"G")
            out, _ = p.communicate(timeout=15)
            self.assertEqual(p.returncode, 0, out)
            self.assertIn(b"Ran 1 test", out)
            self.assertTrue((self.desktop / "tests" / "test_fixture.executed").exists())
        finally:
            if p.poll() is None: p.kill(); p.communicate()

    def test_closed_stdin_fails_without_running_tests(self):
        p = self.start()
        out, _ = p.communicate(timeout=15)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse((self.desktop / "tests" / "test_fixture.executed").exists())

    def test_wrong_start_byte_fails_without_running_tests(self):
        p = self.start()
        out, _ = p.communicate(input=b"X", timeout=15)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse((self.desktop / "tests" / "test_fixture.executed").exists())

    def test_optimized_mode_keeps_isolated_startup_and_runs_test(self):
        self.assertIn("-OO", self.command("-OO"))
        p = self.start("-OO")
        out, _ = p.communicate(input=b"G", timeout=15)
        self.assertEqual(p.returncode, 0, out)
        self.assertTrue((self.desktop / "tests" / "test_fixture.executed").exists())

    def test_rejects_uncontrolled_python_startup_flags(self):
        with self.assertRaises(ValueError):
            guarded_windows_command((sys.executable, "-c", "print('secret')"), self.desktop)

    def test_rejects_non_test_file_pattern(self):
        raw = (sys.executable, "-B", "-W", "error", "-m", "unittest", "discover",
               "-s", str(self.desktop / "tests"), "-p", "../../secret.py")
        with self.assertRaises(ValueError):
            guarded_windows_command(raw, self.desktop)

    def test_rejects_string_subclass_before_conversion(self):
        class Forged(str):
            def __str__(self): raise RuntimeError("PRIVATE CUSTOMER SECRET")
        with self.assertRaisesRegex(ValueError, "Unsafe Windows source check command"):
            guarded_windows_command((sys.executable, Forged("-B"), "-W", "error", "-m",
                                     "unittest", "discover", "-s", str(self.desktop/"tests"),
                                     "-p", "test_fixture.py"), self.desktop)

    def test_wrapped_source_check_preserves_strict_unittest_receipt(self):
        p = self.start()
        out, _ = p.communicate(input=b"G", timeout=15)
        self.assertEqual(p.returncode, 0, out)
        self.assertRegex(out.decode(), r"(?m)^Ran 1 test in [0-9.]+s$")
        self.assertIn("\nOK\n", out.decode())

if __name__ == '__main__': unittest.main()
