"""R487: actual child output is bounded while the process runs, not afterward."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import offline_source_gate_r485 as gate

SEP = "-" * 70 + "\nRan 1 test in 0.001s\n\nOK\n"


class OfflineSourceStreamBudgetR487(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.desktop = Path(self.tmp.name) / "products" / "desktop"
        (self.desktop / "tests").mkdir(parents=True)
        (self.desktop / "tests" / gate.CHECKS[0][1]).write_text("# placeholder\n")

    def run_child(self, script: str, timeout: int = 10):
        return gate._bounded_child((sys.executable, "-u", "-c", script), self.desktop, timeout)

    def test_real_success_stderr_to_same_private_capture(self):
        cmd = "import sys;sys.stderr.write(%r);sys.stderr.flush()" % SEP
        code, output, over = self.run_child(cmd)
        self.assertEqual((code, output, over), (0, SEP.encode(), False))

    def test_exact_capacity_is_allowed_for_collection(self):
        code, data, over = self.run_child(
            "import sys;sys.stdout.buffer.write(b'X' * %d)" % gate._MAX_EVIDENCE_BYTES)
        self.assertEqual(code, 0)
        self.assertEqual(len(data), gate._MAX_EVIDENCE_BYTES)
        self.assertFalse(over)

    def test_flood_is_killed_before_following_sleep(self):
        script = "import sys,time;sys.stdout.buffer.write(b'X' * %d);sys.stdout.flush();time.sleep(20)" % (gate._MAX_EVIDENCE_BYTES + 8192)
        start = time.monotonic()
        code, data, over = self.run_child(script, timeout=10)
        self.assertTrue(over)
        self.assertEqual(data, b"")
        self.assertNotEqual(code, 0)
        self.assertLess(time.monotonic() - start, 6)

    def test_overflow_never_trusted_even_if_trailer_says_ok(self):
        code, data, over = self.run_child(
            "import sys;sys.stdout.buffer.write(b'P' * %d + %r)" % (
                gate._MAX_EVIDENCE_BYTES, SEP.encode()))
        self.assertTrue(over)
        self.assertEqual(data, b"")
        self.assertNotEqual(over, False)

    def test_quiet_child_times_out_and_is_reaped(self):
        start = time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired):
            self.run_child("import time;time.sleep(20)", timeout=1)
        self.assertLess(time.monotonic() - start, 6)

    def test_nonzero_child_still_fails_canonical_unittest_output(self):
        code, data, over = self.run_child("import sys;sys.stdout.write(%r);sys.exit(3)" % SEP)
        self.assertEqual(code, 3)
        self.assertFalse(over)
        self.assertEqual(data, SEP.encode())
        with patch.object(gate, "_bounded_child", return_value=(code, data, over)):
            row = gate._single_check(self.desktop, "sample", gate.CHECKS[0][1], "normal", (), 10)
        self.assertEqual(row["result"], "FAIL")

    def test_private_flood_never_enters_json_evidence(self):
        secret = "PRIVATE/CUSTOMER/2026/claims.csv"
        cmd = "import sys;sys.stderr.buffer.write(%r + b'Q'*%d)" % (
            secret.encode(), gate._MAX_EVIDENCE_BYTES)
        code, data, over = self.run_child(cmd)
        self.assertTrue(over)
        self.assertNotIn(secret.encode(), data)
        with patch.object(gate, "_bounded_child", return_value=(code, data, over)):
            row = gate._single_check(self.desktop, "sample", gate.CHECKS[0][1], "normal", (), 10)
        self.assertEqual(row["result"], "FAIL")
        self.assertNotIn(secret, repr(row))

    def test_unsupported_child_execution_is_blocked_without_traceback(self):
        with patch.object(gate.subprocess, "Popen", side_effect=OSError("PRIVATE/path.csv")):
            row = gate._single_check(self.desktop, "sample", gate.CHECKS[0][1], "normal", (), 1)
        self.assertEqual(row["result"], "BLOCKED")
        self.assertNotIn("PRIVATE", repr(row))


if __name__ == "__main__":
    unittest.main()
