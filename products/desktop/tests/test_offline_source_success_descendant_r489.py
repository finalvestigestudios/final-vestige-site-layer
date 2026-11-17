"""R489: a clean source-test exit must not leave same-group quiet children alive.

Synthetic POSIX subprocesses, NOT complete production six-app or native Windows proof.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

import offline_source_gate_r485 as gate

SUCCESS = b"----------------------------------------------------------------------\nRan 1 test in 0.001s\n\nOK\n"


class CleanSuccessDescendantCustodyR489(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.desktop = Path(self.tmp.name) / "products" / "desktop"
        (self.desktop / "tests").mkdir(parents=True)
        self.test_file = self.desktop / "tests" / gate.CHECKS[0][1]
        self.test_file.write_text("# synthetic\n")

    def _scripts(self, marker: Path, receipt: bytes) -> tuple[str, str]:
        ready = marker.with_suffix(".ready")
        delayed = (
            "import time;from pathlib import Path;"
            "Path(%r).write_text('ready');time.sleep(1.2);"
            "Path(%r).write_text('escaped')" % (str(ready), str(marker)))
        # The direct parent cannot exit until the quiet child is running.
        # This handshake prevents false PASS on slow Python startup.
        wait_ready = (
            "end=time.monotonic()+20;"
            "\nwhile not Path(%r).exists() and time.monotonic()<end: time.sleep(0.03)\n"
            "if not Path(%r).exists(): sys.exit(9)\n" % (str(ready), str(ready)))
        parent = (
            "import subprocess,sys,time;from pathlib import Path;"
            "subprocess.Popen([sys.executable,'-c',%r],"
            "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);\n"
            "%ssys.stdout.buffer.write(%r)" % (delayed, wait_ready, receipt))
        return delayed, parent

    @unittest.skipUnless(os.name == "posix", "POSIX process-group containment only")
    def test_success_exit_kills_quiet_grandchild(self):
        marker = Path(self.tmp.name) / "success-grandchild.txt"
        _, parent = self._scripts(marker, SUCCESS)
        code, output, overflow = gate._bounded_child(
            (sys.executable, "-u", "-c", parent), self.desktop, 30)
        self.assertEqual((code, output, overflow), (0, SUCCESS, False))
        self.assertTrue(marker.with_suffix(".ready").exists())
        time.sleep(1.65)
        self.assertFalse(marker.exists(), "Same-group child survived successful gate completion")

    @unittest.skipUnless(os.name == "posix", "POSIX process-group containment only")
    def test_invalid_receipt_exit_also_kills_quiet_grandchild(self):
        marker = Path(self.tmp.name) / "invalid-grandchild.txt"
        _, parent = self._scripts(marker, b"invalid receipt\n")
        code, output, overflow = gate._bounded_child(
            (sys.executable, "-u", "-c", parent), self.desktop, 30)
        self.assertEqual((code, output, overflow), (0, b"invalid receipt\n", False))
        self.assertTrue(marker.with_suffix(".ready").exists())
        time.sleep(1.65)
        self.assertFalse(marker.exists(), "Same-group child survived an invalid receipt")

    def _integration(self, flags: tuple[str, ...], mode: str) -> None:
        marker = Path(self.tmp.name) / (mode + "-unittest-grandchild.txt")
        delayed, _ = self._scripts(marker, SUCCESS)
        ready = marker.with_suffix(".ready")
        self.test_file.write_text(
            "import subprocess,sys,unittest,warnings,time\n"
            "from pathlib import Path\n"
            "warnings.filterwarnings('ignore', category=ResourceWarning)\n"
            "class TestSynthetic(unittest.TestCase):\n"
            "  def test_quiet_child(self):\n"
            "    subprocess.Popen([sys.executable,'-c',%r],"
            "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
            "    end=time.monotonic()+20\n"
            "    while not Path(%r).exists() and time.monotonic()<end: time.sleep(0.03)\n"
            "    self.assertTrue(Path(%r).exists(), 'quiet child did not start')\n"
            % (delayed, str(ready), str(ready)))
        outcome = gate._single_check(self.desktop, "synthetic", gate.CHECKS[0][1], mode, flags, 30)
        self.assertEqual(outcome, {"check": "synthetic", "mode": mode, "result": "PASS", "tests": 1})
        self.assertTrue(ready.exists())
        time.sleep(1.65)
        self.assertFalse(marker.exists(), "Quiet child survived a PASS report")

    @unittest.skipUnless(os.name == "posix", "POSIX process-group containment only")
    def test_actual_unittest_normal_receipt_reaps_quiet_child(self):
        self._integration((), "normal")

    @unittest.skipUnless(os.name == "posix", "POSIX process-group containment only")
    def test_actual_unittest_optimized_receipt_reaps_quiet_child(self):
        self._integration(("-OO",), "optimized")

    def test_fixed_receipt_was_not_modified(self):
        self.assertIsNotNone(gate._SUCCESS_TRAILER.search(SUCCESS))
        self.assertEqual(gate._MAX_EVIDENCE_BYTES, 1_048_576)


if __name__ == "__main__":
    unittest.main()
