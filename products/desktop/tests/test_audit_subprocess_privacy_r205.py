"""R205 FD-level privacy regression using actual native child processes."""
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.safe_audit_subprocess_r205 import run_private, ROOT

SECRET = "PRIVATE_LEDGER_654321__NO_LOGS"


class PrivateAuditSubprocessR205(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fv-r205-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runner = self.root / "audit.py"

    def script(self, code: str):
        self.runner.write_text(code, encoding="utf-8")

    def attempt(self, *, timeout=5):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            ok = run_private(self.runner, timeout=timeout)
        reported = out.getvalue() + err.getvalue()
        self.assertNotIn(SECRET, reported)
        self.assertNotIn(self.temp.name, reported)
        self.assertNotIn("Traceback", reported)
        return ok, reported

    def test_success_is_explicit_but_not_release_authorization(self):
        self.script("raise SystemExit(0)\n")
        ok, text = self.attempt()
        self.assertTrue(ok)
        self.assertIn("NOT release approval", text)

    def test_raw_fd_stdout_and_stderr_do_not_escape(self):
        self.script("import os\nos.write(1, b'" + SECRET + "')\nos.write(2, b'" + SECRET + "')\n")
        self.assertTrue(self.attempt()[0])

    def test_sys_dunder_stderr_cannot_escape(self):
        self.script("import sys\nsys.__stderr__.write('" + SECRET + "')\n")
        self.assertTrue(self.attempt()[0])

    def test_grandchild_inherited_streams_cannot_escape(self):
        self.script("import subprocess,sys\nsubprocess.run([sys.executable, '-c', \"import os;os.write(1,b'" + SECRET + "');os.write(2,b'" + SECRET + "')\"],check=True)\n")
        self.assertTrue(self.attempt()[0])

    def test_private_failing_exception_rejected_without_traceback(self):
        self.script("raise RuntimeError('" + SECRET + "')\n")
        ok, text = self.attempt()
        self.assertFalse(ok)
        self.assertIn("HOLD", text)

    def test_private_nonzero_exit_rejected(self):
        self.script("raise SystemExit(7)\n")
        self.assertFalse(self.attempt()[0])

    def test_private_timeout_rejected(self):
        self.script("import time\ntime.sleep(5)\n")
        self.assertFalse(self.attempt(timeout=1)[0])

    def test_missing_runner_rejected(self):
        self.assertFalse(self.attempt()[0])

    def test_directory_runner_rejected(self):
        self.runner.mkdir()
        self.assertFalse(self.attempt()[0])

    def test_symlink_runner_rejected_without_executing_target(self):
        target = self.root / "source.py"
        target.write_text("raise SystemExit(0)\n", encoding="utf-8")
        self.script("raise SystemExit(1)\n")
        with patch.object(Path, "is_symlink", lambda p: p == self.runner):
            self.assertFalse(self.attempt()[0])

    def test_non_integer_timeout_rejected(self):
        self.script("raise SystemExit(0)\n")
        self.assertFalse(self.attempt(timeout=True)[0])
        self.assertFalse(self.attempt(timeout=0)[0])

    def test_parent_never_forwards_stdout_or_stderr(self):
        self.script("raise SystemExit(0)\n")
        original = subprocess.run
        def spy(*args, **kwargs):
            self.assertEqual(kwargs["stdout"], subprocess.DEVNULL)
            self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)
            self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
            self.assertIn("-I", args[0])
            self.assertIn("-B", args[0])
            self.assertEqual(kwargs["cwd"], str(ROOT))
            self.assertFalse(kwargs["check"])
            return original(*args, **kwargs)
        with patch("scripts.safe_audit_subprocess_r205.subprocess.run", side_effect=spy):
            self.assertTrue(self.attempt()[0])

    def test_interrupted_spawn_has_no_private_traceback(self):
        self.script("raise SystemExit(0)\n")
        with patch("scripts.safe_audit_subprocess_r205.subprocess.run", side_effect=RuntimeError(SECRET)):
            self.assertFalse(self.attempt()[0])

    def test_child_cannot_receive_pythonpath_under_isolated_flag(self):
        self.script("import os,sys\nassert not any('missing-injected-folder' in p for p in sys.path)\n")
        with patch.dict(os.environ, {"PYTHONPATH": "missing-injected-folder"}):
            self.assertTrue(self.attempt()[0])


if __name__ == "__main__":
    unittest.main()
