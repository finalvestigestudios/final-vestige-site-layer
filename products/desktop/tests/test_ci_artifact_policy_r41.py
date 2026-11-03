"""R41 evidence-only CI artifact contract; never package or execute EXEs."""
from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import ci_artifact_policy as policy


GOOD = """name: Desktop suite build (internal)
jobs:
  source-tests:
    steps:
      - uses: actions/checkout@v4
      - name: Upload internal source-only evidence
        uses: actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f
        with:
          name: final-vestige-desktop-source-only
          path: ${{ runner.temp }}/fvs-source/offline-source-suite.json
          if-no-files-found: error
          retention-days: 7
  windows-build:
    steps:
      - name: Build six executables
        shell: pwsh
        run: echo building
      - name: Upload internal pre-release evidence only
        uses: actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f
        with:
          name: final-vestige-desktop-windows-internal
          path: |
            dist/SHA256SUMS.txt
            build/offline-candidate-evidence.json
          if-no-files-found: error
          retention-days: 7
"""


class ArtifactPolicyTests(unittest.TestCase):
    def check_bad(self, changed: str) -> None:
        with self.assertRaises(policy.ArtifactPolicyError):
            policy.verify_upload_policy(changed)

    def test_exact_evidence_only_uploads(self):
        self.assertEqual(policy.verify_upload_policy(GOOD), 2)

    def test_reject_wildcard_exes(self):
        self.check_bad(GOOD.replace("dist/SHA256SUMS.txt", "dist/*.exe"))

    def test_reject_whole_distribution_folder(self):
        self.check_bad(GOOD.replace("dist/SHA256SUMS.txt", "dist/"))

    def test_reject_star_wildcard(self):
        self.check_bad(GOOD.replace("dist/SHA256SUMS.txt", "dist/*"))

    def test_reject_premium_executable(self):
        self.check_bad(GOOD.replace("dist/SHA256SUMS.txt", "dist/GrantAuditStudioPro.exe"))

    def test_reject_premium_issuer_secret(self):
        self.check_bad(GOOD.replace("dist/SHA256SUMS.txt", "build/private-issuer.pem"))

    def test_reject_injected_extra_artifact(self):
        injected = """      - name: Upload all
        uses: actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f
        with:
          name: leakage
          path: dist/*
"""
        self.check_bad(GOOD + injected)

    def test_reject_duplicate_action_name(self):
        self.check_bad(GOOD.replace("final-vestige-desktop-windows-internal", "final-vestige-desktop-source-only"))

    def test_reject_renamed_approved_upload(self):
        self.check_bad(GOOD.replace("final-vestige-desktop-source-only", "renamed-source"))

    def test_reject_duplicate_path_key(self):
        self.check_bad(GOOD.replace("            dist/SHA256SUMS.txt", "            dist/SHA256SUMS.txt\n          path: dist/*"))

    def test_reject_expression_in_upload_path(self):
        self.check_bad(GOOD.replace("dist/SHA256SUMS.txt", "${{ github.workspace }}/dist/*"))

    def test_reject_different_upload_action_version(self):
        self.check_bad(GOOD.replace("upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f", "upload-artifact@main"))

    def test_reject_unknown_upload_option(self):
        self.check_bad(GOOD.replace("          retention-days: 7", "          include-hidden-files: true\n          retention-days: 7"))

    def test_reject_missing_upload_artifact_evidence(self):
        self.check_bad(GOOD.replace("if-no-files-found: error", "if-no-files-found: warn"))

    def test_reject_long_retention(self):
        self.check_bad(GOOD.replace("retention-days: 7", "retention-days: 90"))

    def test_reject_duplicate_security_option(self):
        self.check_bad(GOOD.replace("          retention-days: 7", "          retention-days: 7\n          retention-days: 7"))

    def test_reject_commented_out_path(self):
        self.check_bad(GOOD.replace("            dist/SHA256SUMS.txt", "            # dist/SHA256SUMS.txt"))

    def test_reject_missing_window_upload(self):
        self.check_bad(GOOD.split("  windows-build:")[0])

    def test_reject_oversized_workflow(self):
        self.check_bad(GOOD + "#" * (policy.MAX_WORKFLOW_BYTES + 1))

    def test_cli_success_without_sensitive_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "workflow.yml"
            f.write_text(GOOD, encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(policy.main([str(f)]), 0)
            self.assertIn("evidence-only", out.getvalue())
            self.assertIn("NOT release approval", out.getvalue())

    def test_cli_missing_path_sanitizes_private_filename(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(policy.main(["/private/client/payroll.yml"]), 1)
        self.assertNotIn("payroll", err.getvalue())
        self.assertNotIn("/private", err.getvalue())

    def test_actual_workflow_contract_if_checkout_present(self):
        path = Path(__file__).resolve().parents[3] / ".github/workflows/desktop-build.yml"
        if not path.exists():
            self.skipTest("Full Git checkout unavailable: fixture tests still executed")
        self.assertEqual(policy.verify_upload_policy(path.read_text(encoding="utf-8")), 2)


if __name__ == "__main__":
    unittest.main()
