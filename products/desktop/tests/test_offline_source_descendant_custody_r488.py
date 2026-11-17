"""R488: real-subprocess source gate tree cleanup and no inherited stdin.

POSIX process-group claims are tested on POSIX only; Windows is not an
asserted process-tree sandbox. Fixture outputs are deliberately synthetic.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import offline_source_gate_r485 as gate


class OfflineSourceDescendantCustodyR488(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.desktop = Path(self.tmp.name) / "products" / "desktop"
        (self.desktop / "tests").mkdir(parents=True)
        (self.desktop / "tests" / gate.CHECKS[0][1]).write_text("# synthetic placeholder\n")

    def child(self, script: str, timeout: int = 8):
        return gate._bounded_child((sys.executable, "-u", "-c", script), self.desktop, timeout)

    def _grandchild_script(self, marker: Path, delay: float = 3.5) -> str:
        return ("import time;from pathlib import Path;time.sleep(%r);"
                "Path(%r).write_text('survived')" % (delay, str(marker)))

    def _spawn_script(self, marker: Path, parent_action: str) -> str:
        # By default, the grandchild inherits its parent's stdout/stderr pipe.
        return ("import subprocess,sys,time;"
                "subprocess.Popen([sys.executable,'-c',%r]);"
                "%s" % (self._grandchild_script(marker), parent_action))

    def test_ordinary_child_receipt_stays_intact(self):
        out = b"----------------------------------------------------------------------\nRan 1 test in 0.001s\n\nOK\n"
        code, data, over = self.child("import sys;sys.stderr.buffer.write(%r)" % out)
        self.assertEqual((code, data, over), (0, out, False))

    def test_child_reads_eof_not_operator_stdin(self):
        # A nested subprocess must never consume credentials or CSV bytes sent
        # to the operator on stdin. DEVNULL returns EOF immediately.
        code, data, over = self.child(
            "import sys;data=sys.stdin.buffer.read();sys.stdout.write('EOF' if not data else 'LEAK')")
        self.assertEqual((code, data, over), (0, b"EOF", False))

    @unittest.skipUnless(os.name == "posix", "POSIX process-group isolation only")
    def test_child_is_in_its_own_process_group(self):
        code, data, over = self.child(
            "import os,sys;sys.stdout.write('isolated' if os.getpgid(0)==os.getpid() else 'shared')")
        self.assertEqual((code, data, over), (0, b"isolated", False))

    @unittest.skipUnless(os.name == "posix", "POSIX process-group isolation only")
    def test_orphaned_pipe_is_blocked_and_grandchild_reaped(self):
        marker = Path(self.tmp.name) / "should-not-appear-orphan.txt"
        cmd = self._spawn_script(marker, "sys.exit(0)")
        start = time.monotonic()
        with self.assertRaisesRegex(OSError, "Source evidence stream unavailable"):
            self.child(cmd)
        self.assertLess(time.monotonic() - start, 6)
        time.sleep(1.8)  # Beyond grandchild's scheduled write if still alive.
        self.assertFalse(marker.exists(), "A grandchild escaped the orphan-pipe cleanup")

    @unittest.skipUnless(os.name == "posix", "POSIX process-group isolation only")
    def test_overflow_kills_stdout_grandchild(self):
        marker = Path(self.tmp.name) / "should-not-appear-flood.txt"
        cmd = self._spawn_script(marker, "sys.stdout.buffer.write(b'X'*%d);sys.stdout.flush();time.sleep(8)" % (gate._MAX_EVIDENCE_BYTES + 8192))
        code, data, over = self.child(cmd)
        self.assertNotEqual(code, 0)
        self.assertTrue(over)
        self.assertEqual(data, b"")
        time.sleep(3.7)
        self.assertFalse(marker.exists(), "Grandchild survived overflow termination")

    @unittest.skipUnless(os.name == "posix", "POSIX process-group isolation only")
    def test_timeout_kills_stdout_grandchild(self):
        marker = Path(self.tmp.name) / "should-not-appear-timeout.txt"
        cmd = self._spawn_script(marker, "time.sleep(8)")
        with self.assertRaises(subprocess.TimeoutExpired):
            self.child(cmd, timeout=1)
        time.sleep(3.7)
        self.assertFalse(marker.exists(), "Grandchild survived the one-second timeout")

    @unittest.skipUnless(os.name == "posix", "POSIX process-group isolation only")
    def test_single_check_redacts_orphan_pipe(self):
        # The public report must remain a fixed-label BLOCKED status; the
        # synthetic child output is never exposed to an operator.
        marker = Path(self.tmp.name) / "never-writes.txt"
        payload = self._spawn_script(marker, "sys.stderr.write('PRIVATE/vendors/file.csv\\n');sys.exit(0)")
        old = gate._bounded_child

        def bound(cmd, desktop, timeout):
            return old((sys.executable, "-u", "-c", payload), desktop, timeout)

        with patch.object(gate, "_bounded_child", side_effect=bound):
            row = gate._single_check(self.desktop, "synthetic", gate.CHECKS[0][1], "normal", (), 8)
        self.assertEqual(row, {"check": "synthetic", "mode": "normal", "result": "BLOCKED", "tests": 0})
        self.assertNotIn("PRIVATE", repr(row))

    def test_no_release_authorization_in_report(self):
        with patch.object(gate, "CHECKS", (("sample", gate.CHECKS[0][1]),)):
            report = gate.verify(self.desktop, timeout=3)
        self.assertIs(report["release_authorized"], False)
        self.assertFalse(report["all_passed"])


if __name__ == "__main__":
    unittest.main()
