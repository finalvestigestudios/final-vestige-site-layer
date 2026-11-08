"""R278: private six-EXE candidate subprocess credential-inheritance regressions.

No Windows binaries are built by these tests. All secrets are synthetic canaries.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts.candidate_child_environment_r278 import private_child_environment

CANARY = "FVS_R278_SYNTHETIC_CREDENTIAL_DO_NOT_DISCLOSE"
SECRET_KEYS = (
    "GITHUB_TOKEN", "GH_TOKEN", "ACTIONS_RUNTIME_TOKEN", "AWS_SECRET_ACCESS_KEY",
    "AZURE_CLIENT_SECRET", "FV_PREMIUM_LICENSE_KEY", "HTTP_PROXY", "HTTPS_PROXY",
    "ALL_PROXY", "PYTHONPATH", "PYTHONHOME", "PYTHONINSPECT", "PYTHONWARNINGS",
    "PYINSTALLER_CONFIG_DIR", "PIP_INDEX_URL", "PIP_EXTRA_INDEX_URL",
    "APPDATA", "LOCALAPPDATA", "USERPROFILE", "HOME", "CI_JOB_JWT",
)


class CandidateChildEnvironmentTests(unittest.TestCase):
    def test_parent_secrets_and_proxy_configuration_not_forwarded(self):
        with mock.patch.dict(os.environ, {key: CANARY for key in SECRET_KEYS}):
            actual = private_child_environment()
        self.assertTrue(set(actual).isdisjoint(SECRET_KEYS))
        self.assertNotIn(CANARY, actual.values())

    def test_casefolded_secret_keys_are_not_forwarded(self):
        with mock.patch.dict(os.environ, {"gItHuB_tOkEn": CANARY, "pYtHoNpAtH": CANARY}):
            actual = private_child_environment()
        self.assertNotIn("github_token", {key.lower() for key in actual})
        self.assertNotIn("pythonpath", {key.lower() for key in actual})

    def test_only_explicit_launch_keys_and_safe_build_controls_survive(self):
        actual = private_child_environment()
        expected = {"PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR",
                    "GITHUB_SHA", "PYTHONNOUSERSITE", "PYTHONDONTWRITEBYTECODE", "PIP_NO_INDEX"}
        self.assertTrue({key.upper() for key in actual}.issubset(expected))

    def test_control_flags_are_forced_not_inherited(self):
        with mock.patch.dict(os.environ, {"PIP_NO_INDEX": "0", "PYTHONNOUSERSITE": "0",
                                               "PYTHONDONTWRITEBYTECODE": "0"}):
            actual = private_child_environment()
        self.assertEqual({key: actual[key] for key in
                          ("PIP_NO_INDEX", "PYTHONNOUSERSITE", "PYTHONDONTWRITEBYTECODE")},
                         {"PIP_NO_INDEX": "1", "PYTHONNOUSERSITE": "1",
                          "PYTHONDONTWRITEBYTECODE": "1"})

    def test_windows_launch_environment_remains_usable(self):
        with mock.patch.dict(os.environ, {"SystemRoot": r"C:\Windows", "PATHEXT": ".EXE;.CMD",
                                               "TEMP": r"C:\Temp", "FV_KEY": CANARY}):
            actual = private_child_environment()
        self.assertEqual(actual["SystemRoot"], r"C:\Windows")
        self.assertEqual(actual["PATHEXT"], ".EXE;.CMD")
        self.assertEqual(actual["TEMP"], r"C:\Temp")
        self.assertNotIn("FV_KEY", actual)

    def test_no_commit_by_default(self):
        with mock.patch.dict(os.environ, {"GITHUB_SHA": ""}):
            self.assertNotIn("GITHUB_SHA", private_child_environment())

    def test_only_canonical_commit_evidence_is_forwarded(self):
        for n in (40, 64):
            with self.subTest(n=n):
                with mock.patch.dict(os.environ, {"GITHUB_SHA": "a" * n}):
                    self.assertEqual(private_child_environment()["GITHUB_SHA"], "a" * n)

    def test_untrusted_commit_forms_are_removed(self):
        for value in ("a" * 39, "a" * 65, "A" * 40, "é" * 40,
                      "C:/secrets/keys.txt", "f" * 39 + "g", "\n" * 40, "1e400"):
            with self.subTest(value=repr(value)[:15]):
                with mock.patch.dict(os.environ, {"GITHUB_SHA": value}):
                    self.assertNotIn("GITHUB_SHA", private_child_environment())

    def test_never_mutates_parent_environment(self):
        with mock.patch.dict(os.environ, {"GITHUB_TOKEN": CANARY}):
            before = dict(os.environ)
            private_child_environment()
            self.assertEqual(dict(os.environ), before)

    def test_real_python_child_never_receives_synthetic_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            witness = Path(tmp) / "witness.py"
            witness.write_text(
                "import os, sys\n"
                "canary = " + repr(CANARY) + "\n"
                "sys.exit(1 if any(value == canary for value in os.environ.values()) else 0)\n",
                encoding="utf-8")
            with mock.patch.dict(os.environ, {key: CANARY for key in SECRET_KEYS}):
                actual = subprocess.run([sys.executable, "-I", str(witness)],
                                        env=private_child_environment(),
                                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL, check=False, timeout=10)
        self.assertEqual(actual.returncode, 0)

    def test_real_child_can_create_temporary_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            witness = Path(tmp) / "witness.py"
            witness.write_text("import tempfile\nwith tempfile.TemporaryFile() as f: f.write(b'ok')\n", encoding="utf-8")
            actual = subprocess.run([sys.executable, "-I", str(witness)],
                                    env=private_child_environment(),
                                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, check=False, timeout=10)
        self.assertEqual(actual.returncode, 0)

    def test_real_private_runner_uses_explicit_environment_builder(self):
        # Tests source contract against the committed runner; no import of the
        # full Windows execution chain or PyInstaller required.
        runner = (Path(__file__).resolve().parents[1] / "scripts" /
                  "offline_windows_candidate_r269.py").read_text(encoding="utf-8")
        self.assertIn("from candidate_child_environment_r278 import private_child_environment", runner)
        self.assertIn("env=private_child_environment()", runner)
        self.assertNotIn("env = os.environ.copy()", runner)


if __name__ == "__main__":
    unittest.main()
