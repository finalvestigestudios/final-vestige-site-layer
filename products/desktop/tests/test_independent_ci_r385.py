"""R385 static custody tests for an independent, read-only source-evidence workflow.

Tests themselves use only the Python standard library and synthetic strings.
They do not run an EXE, validate Windows packaging, issue licenses, or approve QD.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "desktop-source-evidence-r385.yml"


def _read_workflow() -> str:
    source = WORKFLOW.read_bytes()
    if not source or len(source) > 8192 or b"\x00" in source or b"\t" in source:
        raise ValueError("R385 source CI workflow has unsafe encoding or size")
    return source.decode("utf-8")


class IndependentSourceCIR385(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = _read_workflow()
        cls.lines = cls.text.splitlines()

    def test_small_standalone_workflow(self):
        self.assertLess(len(self.text.encode("utf-8")), 8192)
        self.assertIn("name: Desktop six-engine source evidence", self.text)
        self.assertNotIn("desktop-build.yml'", self.text)

    def test_pr_trigger_only_for_desktop_and_self(self):
        self.assertRegex(self.text, r"(?m)^on:\s*$")
        self.assertIn("  pull_request:\n    paths:\n", self.text)
        self.assertIn("- 'products/desktop/**'", self.text)
        self.assertIn("- '.github/workflows/desktop-source-evidence-r385.yml'", self.text)
        for forbidden in ("pull_request_target:", "push:", "schedule:"):
            self.assertNotIn(forbidden, self.text)

    def test_manual_rerun_allowed_without_deploy(self):
        self.assertIn("  workflow_dispatch:", self.text)
        self.assertNotIn("deployment", self.text.lower())

    def test_permissions_are_read_only(self):
        self.assertRegex(self.text, r"(?m)^permissions:\n  contents: read\n")
        self.assertNotRegex(self.text, r"(?m)^\s+[a-z-]+: write\s*$")
        self.assertNotIn("id-token:", self.text)

    def test_both_independent_hosted_platforms(self):
        self.assertIn("os: [ubuntu-24.04, windows-latest]", self.text)
        self.assertIn("runs-on: ${{ matrix.os }}", self.text)
        self.assertIn("fail-fast: false", self.text)
        self.assertNotIn("self-hosted", self.text)

    def test_checkout_and_python_actions_use_full_sha_pins(self):
        actions = re.findall(r"(?m)^\s+- uses: ([^\s#]+)", self.text)
        self.assertEqual(len(actions), 2)
        for action, expected in zip(actions, ("actions/checkout", "actions/setup-python")):
            self.assertRegex(action, rf"^{expected}@[0-9a-f]{{40}}$")
        self.assertIn("persist-credentials: false", self.text)

    def test_no_artifact_or_public_distribution_path(self):
        for unsafe in ("upload-artifact", "download-artifact", "create-release",
                       "gh release", "deploy", "publish", "release-asset",
                       "premium-download", "artifact-path", "secrets."):
            self.assertNotIn(unsafe, self.text.lower())

    def test_no_masked_failures_or_untrusted_shell_downloads(self):
        for unsafe in ("continue-on-error", "curl ", "wget ",
                       "invoke-webrequest", "|| true", "if: always()"):
            self.assertNotIn(unsafe, self.text.lower())

    def test_python_and_crypto_dependencies_explicit(self):
        self.assertIn("python-version: '3.12'", self.text)
        self.assertIn('"cryptography==46.0.4"', self.text)
        self.assertIn("PYTHONDONTWRITEBYTECODE: '1'", self.text)

    def test_real_six_engine_source_smoke_twice(self):
        script = "products/desktop/scripts/source_smoke_gate.py"
        self.assertIn(f"python -W error {script}", self.text)
        self.assertIn(f"python -OO -W error {script}", self.text)
        self.assertIn("SHA-256 source inventory", self.text)

    def test_all_six_financial_engines_are_covered(self):
        self.assertIn("test_safety_smoke.py", self.text)
        self.assertEqual(self.text.count("-p test_safety_smoke.py"), 2)

    def test_actual_crypto_gate_is_not_replaced_by_stubs(self):
        self.assertEqual(self.text.count("-p test_vault_crypto_gate_r316.py"), 2)
        self.assertIn("22 actual AES-GCM", self.text)

    def test_offline_ed25519_and_sqlite_registry_both_modes(self):
        for case in ("test_offline_entitlement_r11.py", "test_license_issuer_r12.py",
                     "test_license_registry_r13.py"):
            self.assertEqual(self.text.count("-p " + case), 2)

    def test_last_premium_privacy_regressions_both_modes(self):
        self.assertEqual(self.text.count("-p test_entitlement_payload_privacy_r384.py"), 2)

    def test_self_custody_tests_both_modes(self):
        self.assertEqual(self.text.count("-p test_independent_ci_r385.py"), 2)

    def test_no_implicit_build_or_release_success_claims(self):
        self.assertNotIn("pyinstaller", self.text.lower())
        self.assertNotIn("--onefile", self.text.lower())
        self.assertIn("source evidence is not a windows release gate", self.text.lower())


if __name__ == "__main__":
    unittest.main()
