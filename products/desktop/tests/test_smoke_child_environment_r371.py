"""R371: six-app Windows smoke subprocesses must not inherit credentials.

All inputs are synthetic canaries. No real Windows binary is launched or
approved; the only real child test starts an isolated local Python interpreter.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from smoke_runner_r336 import SmokeRunError, run_smoke_checked

CANARY = "FVS_R371_SYNTHETIC_SECRET_NOT_FOR_CHILD"
SECRET_KEYS = (
    "GITHUB_TOKEN", "GH_TOKEN", "ACTIONS_RUNTIME_TOKEN", "AWS_SECRET_ACCESS_KEY",
    "AZURE_CLIENT_SECRET", "FV_PREMIUM_LICENSE_KEY", "FV_PREMIUM_CUSTOMER_PATH",
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "PYTHONPATH", "PYTHONHOME",
    "PYTHONINSPECT", "PYTHONWARNINGS", "PYINSTALLER_CONFIG_DIR",
    "PIP_INDEX_URL", "PIP_EXTRA_INDEX_URL", "APPDATA", "LOCALAPPDATA",
    "USERPROFILE", "HOME", "CI_JOB_JWT",
)
OS_LAUNCH = {"PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR"}
CONTROL = {"PYTHONNOUSERSITE", "PYTHONDONTWRITEBYTECODE", "PIP_NO_INDEX"}


class SmokeChildEnvironmentR371(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r371-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.exe = self.root / "GrantAuditStudioPro.exe"

    def launch(self, runner):
        return run_smoke_checked(runner, self.exe, self.root,
                                 name="GrantAuditStudioPro.exe", timeout=10)

    def capture(self):
        runner = Mock(return_value=SimpleNamespace(returncode=0))
        self.launch(runner)
        return runner.call_args.kwargs

    def test_all_parent_secrets_excluded(self):
        with patch.dict(os.environ, {key: CANARY for key in SECRET_KEYS}):
            kwargs = self.capture()
        child = kwargs["env"]
        self.assertFalse({key.upper() for key in child} & set(SECRET_KEYS))
        self.assertNotIn(CANARY, child.values())

    def test_case_insensitive_secret_keys_excluded(self):
        with patch.dict(os.environ, {"gItHuB_tOkEn": CANARY,
                                         "pYtHoNpAtH": CANARY,
                                         "hTtP_pRoXy": CANARY}):
            child = self.capture()["env"]
        self.assertNotIn(CANARY, child.values())
        self.assertTrue({key.upper() for key in child}.isdisjoint(
            {"GITHUB_TOKEN", "PYTHONPATH", "HTTP_PROXY"}))

    def test_minimal_allowlist_not_parent_copy(self):
        child = self.capture()["env"]
        self.assertTrue({key.upper() for key in child}.issubset(
            OS_LAUNCH | CONTROL | {"GITHUB_SHA"}))
        self.assertIsNot(child, os.environ)

    def test_control_flags_forced_safe(self):
        with patch.dict(os.environ, {"PIP_NO_INDEX": "0", "PYTHONNOUSERSITE": "0",
                                         "PYTHONDONTWRITEBYTECODE": "0"}):
            child = self.capture()["env"]
        self.assertEqual({key: child[key] for key in CONTROL},
                         {key: "1" for key in CONTROL})

    def test_parent_environment_not_mutated(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": CANARY}):
            before = dict(os.environ)
            self.capture()
            self.assertEqual(dict(os.environ), before)

    def test_safe_windows_boot_environment_preserved(self):
        with patch.dict(os.environ, {"SystemRoot": "C:\\Windows", "PATHEXT": ".EXE;.CMD",
                                         "TEMP": "C:\\Scratch", "FV_PRIVATE": CANARY}):
            child = {key.upper(): value for key, value in self.capture()["env"].items()}
        self.assertEqual(child["SYSTEMROOT"], "C:\\Windows")
        self.assertEqual(child["PATHEXT"], ".EXE;.CMD")
        self.assertEqual(child["TEMP"], "C:\\Scratch")
        self.assertNotIn("FV_PRIVATE", child)

    def test_canonical_source_commit_allowed(self):
        with patch.dict(os.environ, {"GITHUB_SHA": "a" * 40}):
            self.assertEqual(self.capture()["env"]["GITHUB_SHA"], "a" * 40)

    def test_noncanonical_source_commit_rejected(self):
        for bad in ("", "a" * 39, "A" * 40, "z" * 40, "bank/password", "\n" * 40):
            with self.subTest(candidate=repr(bad)[:16]), patch.dict(os.environ, {"GITHUB_SHA": bad}):
                self.assertNotIn("GITHUB_SHA", self.capture()["env"])

    def test_launch_called_with_explicit_env_and_closed_stdio(self):
        args = Mock(return_value=SimpleNamespace(returncode=0))
        self.launch(args)
        (argv,), kwargs = args.call_args
        self.assertEqual(argv, [str(self.exe.resolve()), "--smoke-test"])
        self.assertEqual(kwargs["cwd"], str(self.root.resolve()))
        for key in ("stdin", "stdout", "stderr"):
            self.assertEqual(kwargs[key], subprocess.DEVNULL)
        self.assertIs(kwargs["check"], False)
        self.assertEqual(kwargs["timeout"], 10)
        self.assertIn("env", kwargs)

    def test_explicit_env_for_injected_runner_too(self):
        seen = []
        def runner(argv, **kwargs):
            seen.append(kwargs["env"])
            return SimpleNamespace(returncode=0)
        with patch.dict(os.environ, {"GITHUB_TOKEN": CANARY}):
            self.launch(runner)
        self.assertEqual(len(seen), 1)
        self.assertNotIn(CANARY, seen[0].values())

    def test_bad_timeout_never_constructs_environment_or_launches(self):
        runner = Mock()
        with patch("smoke_runner_r336.private_child_environment") as builder:
            with self.assertRaises(SmokeRunError):
                run_smoke_checked(runner, self.exe, self.root,
                                  name="GrantAuditStudioPro.exe", timeout=0)
        builder.assert_not_called()
        runner.assert_not_called()

    def test_environment_builder_failure_redacted_before_launch(self):
        runner = Mock()
        with patch("smoke_runner_r336.private_child_environment",
                   side_effect=OSError("PRIVATE CLIENT CREDENTIALS")):
            with self.assertRaises(SmokeRunError) as caught:
                self.launch(runner)
        self.assertEqual(str(caught.exception),
                         "GrantAuditStudioPro.exe: could not execute packaged EXE")
        self.assertIsNone(caught.exception.__cause__)
        runner.assert_not_called()

    def test_synthetic_child_failure_still_rejected(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": CANARY}):
            with self.assertRaises(SmokeRunError) as caught:
                self.launch(lambda *_a, **_kw: SimpleNamespace(returncode=7))
        self.assertIn("exit code 7", str(caught.exception))
        self.assertNotIn(CANARY, str(caught.exception))

    def test_real_python_child_cannot_see_parent_canary(self):
        witness = self.root / "witness.py"
        witness.write_text("import os,sys\nsys.exit(1 if " + repr(CANARY)
                           + " in os.environ.values() else 0)\n", encoding="utf-8")
        def runner(_argv, **kwargs):
            return subprocess.run([sys.executable, "-I", str(witness)],
                                  cwd=kwargs["cwd"], env=kwargs["env"],
                                  check=False, timeout=kwargs["timeout"],
                                  stdin=kwargs["stdin"], stdout=kwargs["stdout"],
                                  stderr=kwargs["stderr"])
        with patch.dict(os.environ, {key: CANARY for key in SECRET_KEYS}):
            self.assertIsNone(self.launch(runner))

    def test_real_child_can_access_sanitized_temp(self):
        witness = self.root / "temp_check.py"
        witness.write_text("import tempfile,sys\n"
                           "with tempfile.TemporaryFile() as f: f.write(b'ok')\n"
                           "sys.exit(0)\n", encoding="utf-8")
        def runner(_argv, **kwargs):
            return subprocess.run([sys.executable, "-I", str(witness)],
                                  env=kwargs["env"], cwd=kwargs["cwd"],
                                  timeout=kwargs["timeout"], check=False,
                                  stdin=kwargs["stdin"], stdout=kwargs["stdout"],
                                  stderr=kwargs["stderr"])
        self.assertIsNone(self.launch(runner))


if __name__ == "__main__":
    unittest.main()
