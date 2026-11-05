"""R206: real-child verification that audited regressions do not inherit CI credentials."""
from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.safe_audit_subprocess_r205 import run_private

CANARY = "R206_SYNTHETIC_PRIVATE_VALUE_DO_NOT_LOG"
SENSITIVE = (
    "GITHUB_TOKEN", "GH_TOKEN", "ACTIONS_RUNTIME_TOKEN", "AWS_SECRET_ACCESS_KEY",
    "AZURE_CLIENT_SECRET", "FV_PRIVATE_LICENSE_KEY", "HTTP_PROXY", "HTTPS_PROXY",
    "PYTHONPATH", "PYTHONINSPECT", "HOME", "APPDATA", "USERPROFILE",
)


class PrivateChildEnvironmentR206(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="fv-r206-")
        self.addCleanup(self.tmp.cleanup)
        self.runner = Path(self.tmp.name) / "test_runner.py"

    def attempt(self, source, environ=None):
        self.runner.write_text(source, encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with patch.dict(os.environ, environ or {}):
                result = run_private(self.runner, timeout=7)
        text = out.getvalue() + err.getvalue()
        self.assertNotIn(CANARY, text)
        self.assertNotIn(self.tmp.name, text)
        return result, text

    def test_credentials_not_forwarded_to_real_python_child(self):
        env = {name: CANARY for name in SENSITIVE}
        self.assertTrue(self.attempt(
            "import os,sys\n"
            "blocked = " + repr(SENSITIVE) + "\n"
            "sys.exit(1 if any(os.environ.get(n) == " + repr(CANARY) + " for n in blocked) else 0)\n", env)[0])

    def test_whitelisted_path_remains_available(self):
        self.assertTrue(self.attempt("import os,sys\nsys.exit(0 if os.getenv('PATH') == 'R206_PATH' else 2)\n", {"PATH": "R206_PATH"})[0])

    def test_whitelisted_temp_remains_available(self):
        self.assertTrue(self.attempt("import os,sys\nsys.exit(0 if os.getenv('TMP') == 'R206_TMP' else 2)\n", {"TMP": "R206_TMP"})[0])

    def test_real_child_tempfile_creation_still_works(self):
        self.assertTrue(self.attempt("import tempfile\nwith tempfile.TemporaryFile() as f: f.write(b'local-private-test')\n")[0])

    def test_injected_secret_not_reflected_in_failure_report(self):
        success, report = self.attempt("import os\nraise RuntimeError(os.getenv('GITHUB_TOKEN', 'absent'))\n", {"GITHUB_TOKEN": CANARY})
        self.assertFalse(success)
        self.assertIn("HOLD", report)

    def test_casefolded_secret_names_are_filtered(self):
        from scripts.safe_audit_subprocess_r205 import _child_environment
        with patch.dict(os.environ, {"gItHuB_tOkEn": CANARY, "fV_pRiVaTe": CANARY}):
            clean = _child_environment()
        self.assertFalse(any("github_token" == name.lower() for name in clean))
        self.assertFalse(any("fv_private" == name.lower() for name in clean))

    def test_windows_launch_keys_preserved_without_secrets(self):
        from scripts.safe_audit_subprocess_r205 import _child_environment
        with patch.dict(os.environ, {"SystemRoot": "C:\\Windows", "PATHEXT": ".EXE;.CMD", "GH_TOKEN": CANARY}):
            clean = _child_environment()
        self.assertEqual(clean["SystemRoot"], "C:\\Windows")
        self.assertEqual(clean["PATHEXT"], ".EXE;.CMD")
        self.assertNotIn("GH_TOKEN", clean)

    def test_no_parent_profile_directory_leaked_to_child(self):
        self.assertTrue(self.attempt("import os,sys\nsys.exit(1 if 'USERPROFILE' in os.environ else 0)\n",
                                     {"USERPROFILE": self.tmp.name})[0])

    def test_python_optimization_remains_consistent(self):
        import sys
        expected = "2" if sys.flags.optimize >= 2 else "0"
        self.assertTrue(self.attempt("import sys\nsys.exit(0 if sys.flags.optimize == " + expected + " else 4)\n")[0])

    def test_explicit_allowlist_no_child_credentials(self):
        from scripts.safe_audit_subprocess_r205 import _child_environment
        with patch.dict(os.environ, {name: CANARY for name in SENSITIVE}):
            clean = _child_environment()
        self.assertTrue(set(clean).isdisjoint(SENSITIVE))
        self.assertTrue(set(map(str.upper, clean)).issubset({"PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR"}))

    def test_path_is_not_preferred_over_child_executable(self):
        self.assertTrue(self.attempt("raise SystemExit(0)\n", {"PATH": "/does-not-exist", "GITHUB_TOKEN": CANARY})[0])

    def test_environment_must_be_explicitly_passed(self):
        import subprocess
        original = subprocess.run
        def witness(*args, **kwargs):
            self.assertIn("env", kwargs)
            self.assertNotIn("GITHUB_TOKEN", kwargs["env"])
            return original(*args, **kwargs)
        with patch("scripts.safe_audit_subprocess_r205.subprocess.run", side_effect=witness):
            self.assertTrue(self.attempt("raise SystemExit(0)\n", {"GITHUB_TOKEN": CANARY})[0])


if __name__ == "__main__":
    unittest.main()
