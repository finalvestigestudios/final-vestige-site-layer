"""R492: real isolated Python startup handoff, strict single byte and interpreter."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import tempfile
import time
import unittest

from windows_source_start_custody_r491 import guarded_windows_command


class StrictWindowsSourceProtocolR492(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-r492-")
        self.addCleanup(self.temp.cleanup)
        self.desktop = Path(self.temp.name)
        tests = self.desktop / "tests"
        tests.mkdir()
        self.marker = tests / "test_probe.executed"
        (tests / "test_probe.py").write_text(
            "from pathlib import Path\nimport unittest\n"
            "class Probe(unittest.TestCase):\n"
            "  def test_execution(self):\n"
            "    Path(__file__).with_suffix('.executed').write_text('done')\n"
            "    self.assertEqual(7*6,42)\n", encoding="utf-8")

    def command(self, optimized=False):
        return (sys.executable, *(("-OO",) if optimized else ()),
                "-B", "-W", "error", "-m", "unittest", "discover",
                "-s", str(self.desktop / "tests"), "-p", "test_probe.py")

    def process(self, optimized=False):
        cmd = guarded_windows_command(self.command(optimized), self.desktop)
        return subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def test_exact_single_byte_authorizes_normal_mode(self):
        p = self.process()
        out, _ = p.communicate(input=b"G", timeout=15)
        self.assertEqual(p.returncode, 0, out)
        self.assertIn(b"Ran 1 test", out)
        self.assertTrue(self.marker.exists())

    def test_exact_single_byte_authorizes_optimized_mode(self):
        p = self.process(optimized=True)
        out, _ = p.communicate(input=b"G", timeout=15)
        self.assertEqual(p.returncode, 0, out)
        self.assertTrue(self.marker.exists())

    def test_valid_prefix_with_extra_byte_is_rejected(self):
        p = self.process()
        out, _ = p.communicate(input=b"GX", timeout=15)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.marker.exists())
        self.assertNotIn(b"Ran 1 test", out)

    def test_duplicate_authorization_is_rejected(self):
        p = self.process()
        out, _ = p.communicate(input=b"GG", timeout=15)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.marker.exists())

    def test_optimized_extra_byte_is_rejected(self):
        p = self.process(optimized=True)
        out, _ = p.communicate(input=b"G\x00", timeout=15)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.marker.exists())

    def test_valid_byte_without_eof_does_not_start_test_code(self):
        p = self.process()
        try:
            assert p.stdin is not None
            p.stdin.write(b"G")
            p.stdin.flush()
            time.sleep(0.25)
            self.assertIsNone(p.poll())
            self.assertFalse(self.marker.exists())
            p.stdin.close()
            p.stdin = None
            out, _ = p.communicate(timeout=15)
            self.assertEqual(p.returncode, 0, out)
            self.assertTrue(self.marker.exists())
        finally:
            if p.poll() is None:
                p.kill()
                p.communicate()

    def test_blank_or_wrong_authorization_rejected(self):
        for value in (b"", b"X", b"\n", b"\x00"):
            with self.subTest(value=value):
                p = self.process()
                out, _ = p.communicate(input=value, timeout=15)
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse(self.marker.exists())

    def test_reject_alternate_executable_before_launch(self):
        bad = ("other-python.exe", *self.command()[1:])
        with self.assertRaisesRegex(ValueError, "Unsafe Windows source check command"):
            guarded_windows_command(bad, self.desktop)

    def test_reject_executable_string_subclass_without_hooks(self):
        class Hostile(str):
            def __eq__(self, other):
                raise RuntimeError("private financial filename")
        bad = (Hostile(sys.executable), *self.command()[1:])
        with self.assertRaisesRegex(ValueError, "Unsafe Windows source check command"):
            guarded_windows_command(bad, self.desktop)


if __name__ == "__main__":
    unittest.main()
