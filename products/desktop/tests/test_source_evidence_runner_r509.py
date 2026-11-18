"""R509: audit immutable source-test inventory, redaction and runner custody."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "products" / "desktop" / "scripts"))
import source_evidence_runner_r509 as runner


class SourceEvidenceR509(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = runner.MANIFEST.read_bytes()
        cls.lines = cls.raw.decode("ascii").splitlines()

    def test_workflow_below_reviewed_eight_kib_ceiling(self):
        raw = (ROOT / ".github/workflows/desktop-source-evidence-r385.yml").read_bytes()
        self.assertLess(len(raw), 8192)
        self.assertIn(b"permissions:\n  contents: read", raw)
        self.assertIn(b"source_evidence_runner_r509.py", raw)
        self.assertNotIn(b"continue-on-error", raw)

    def test_exact_github_blob_pin_and_legacy_414_command_parity(self):
        self.assertEqual(runner.git_blob_sha(self.raw), runner.MANIFEST_GIT_SHA1)
        original = ("\n".join(self.lines[:runner.ORIGINAL_COUNT]) + "\n").encode("ascii")
        self.assertEqual(runner.git_blob_sha(original), runner.ORIGINAL_GIT_SHA1)
        self.assertEqual(len(self.lines), 416)
        self.assertTrue(self.lines[-2].endswith("-p test_source_evidence_runner_r509.py"))
        self.assertIn("-OO", self.lines[-1])

    def test_all_original_205_unittest_pairs_preserved(self):
        originals = self.lines[:runner.ORIGINAL_COUNT]
        tests = [x for x in originals if " -m unittest discover " in x]
        self.assertEqual(len(tests), 410)
        self.assertEqual(sum(" -OO " in t for t in tests), 205)
        self.assertEqual(sum(" -OO " not in t for t in tests), 205)
        paths = {re.search(r"-p (test_[a-z0-9_]+\.py)$", t).group(1) for t in tests}
        self.assertTrue({"test_safety_smoke.py", "test_independent_ci_r385.py",
                         "test_vault_crypto_gate_r316.py",
                         "test_entitlement_payload_privacy_r384.py"} <= paths)

    def test_all_416_commands_are_validated_against_real_checkout(self):
        self.assertEqual(len(runner.load_commands(self.raw)), 416)

    def test_arbitrary_shell_or_python_expression_is_rejected(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            for line in ("python -c print(1)", "python -m pip install attacker",
                         "python -OO -W error -m unittest discover -s ../../ -p test_x.py"):
                raw = (line + "\n").encode()
                with self.subTest(line=line), self.assertRaises(runner.EvidenceRejected):
                    runner.load_commands(raw, root, expected_sha=runner.git_blob_sha(raw),
                                         expected_count=1)

    def test_missing_required_test_is_rejected_before_process_launch(self):
        line = b"python -W error -m unittest discover -s products/desktop/tests -p test_absent.py\n"
        with TemporaryDirectory() as d, self.assertRaises(runner.EvidenceRejected):
            runner.load_commands(line, Path(d), expected_sha=runner.git_blob_sha(line),
                                 expected_count=1)

    def test_changed_and_truncated_manifest_rejected(self):
        for raw in (self.raw[:-1], self.raw + b"python -c 9\n",
                    self.raw.replace(b"test_safety_smoke.py", b"test_untrusted_abc.py")):
            with self.subTest(length=len(raw)), self.assertRaises(runner.EvidenceRejected):
                runner.load_commands(raw)

    def test_valid_mock_run_has_no_shell_and_cleans_credentials(self):
        invocations = []
        def fake(argv, **kwargs):
            invocations.append((argv, kwargs))
            return SimpleNamespace(returncode=0)
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(runner.execute((("-B", "-W", "error"),),
                                            spawn=fake), 0)
        self.assertEqual(len(invocations), 1)
        argv, args = invocations[0]
        self.assertEqual(argv[0], sys.executable)
        self.assertEqual(argv[1:], ["-B", "-W", "error"])
        self.assertNotIn("shell", args)
        self.assertEqual(args["stdout"], runner.subprocess.DEVNULL)
        self.assertEqual(args["stderr"], runner.subprocess.DEVNULL)
        self.assertEqual(args["timeout"], 600)
        self.assertNotIn("GITHUB_TOKEN", args["env"])

    def test_nonzero_exit_stops_before_next_check_with_private_error_redacted(self):
        secret = "/home/private/grants/customer-name.csv"
        calls = []
        def fail(argv, **kwargs):
            calls.append(argv)
            raise OSError(secret)
        errors = io.StringIO()
        with redirect_stderr(errors):
            result = runner.execute((("first",), ("second",)), spawn=fail)
        self.assertEqual(result, 1)
        self.assertEqual(len(calls), 1)
        self.assertNotIn(secret, errors.getvalue())
        self.assertIn("source check 1/2 blocked", errors.getvalue())

    def test_test_failure_fails_closed_even_without_exception(self):
        errors = io.StringIO()
        with redirect_stderr(errors):
            result = runner.execute((("first",), ("second",)),
                                    spawn=lambda *a, **k: SimpleNamespace(returncode=1))
        self.assertEqual(result, 1)
        self.assertIn("source check 1/2 failed", errors.getvalue())

    def test_valid_unlinked_synthetic_test_path_is_accepted(self):
        raw = b"python -B -W error -m unittest discover -s products/desktop/tests -p test_valid.py\n"
        with TemporaryDirectory() as d:
            root = Path(d)
            directory = root / "products/desktop/tests"
            directory.mkdir(parents=True)
            (directory / "test_valid.py").write_text("pass\n")
            result = runner.load_commands(raw, root, expected_sha=runner.git_blob_sha(raw),
                                          expected_count=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][-1], "test_valid.py")

    def test_symlinked_test_directory_rejected_even_when_leaf_is_regular(self):
        raw = b"python -W error -m unittest discover -s products/desktop/tests -p test_link.py\n"
        with TemporaryDirectory() as d:
            root = Path(d)
            real = root / "outside"
            real.mkdir()
            (real / "test_link.py").write_text("pass")
            parent = root / "products/desktop"
            parent.mkdir(parents=True)
            try:
                (parent / "tests").symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Directory symlink unavailable: {type(exc).__name__}")
            with self.assertRaises(runner.EvidenceRejected):
                runner.load_commands(raw, root, expected_sha=runner.git_blob_sha(raw),
                                     expected_count=1)

    def test_linked_products_ancestor_directory_rejected(self):
        raw = b"python -W error -m unittest discover -s products/desktop/tests -p test_link.py\n"
        with TemporaryDirectory() as d:
            root = Path(d)
            actual = root / "outside"
            testdir = actual / "desktop/tests"
            testdir.mkdir(parents=True)
            (testdir / "test_link.py").write_text("pass")
            try:
                (root / "products").symlink_to(actual, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Directory symlink unavailable: {type(exc).__name__}")
            with self.assertRaises(runner.EvidenceRejected):
                runner.load_commands(raw, root, expected_sha=runner.git_blob_sha(raw),
                                     expected_count=1)

    def test_sensitive_child_environment_and_github_command_paths_are_stripped(self):
        secret_env = {
            "AWS_ACCESS_KEY_ID": "id-private",
            "AWS_SECRET_ACCESS_KEY": "key-private",
            "GOOGLE_APPLICATION_CREDENTIALS": "/secret/service-account.json",
            "CLIENT_SESSION": "session-private",
            "GRANTS_API_KEY": "key-private",
            "PAYMENT_COOKIE": "cookie-private",
            "GIT_ASKPASS": "/secret/helper",
            "SSH_ASKPASS": "/secret/helper2",
            "GITHUB_ENV": "/private/action-env",
            "GITHUB_OUTPUT": "/private/action-output",
            "GITHUB_PATH": "/private/action-path",
            "GITHUB_TOKEN": "token-private",
            "CI": "true",
        }
        with patch.dict(os.environ, secret_env):
            child = runner._child_environment(ROOT)
        for name in secret_env:
            if name != "CI":
                self.assertNotIn(name, child, name)
        self.assertEqual(child["CI"], "true")
        self.assertEqual(child["PYTHONDONTWRITEBYTECODE"], "1")

    def test_legacy_aes_custody_checks_real_manifest_not_obsolete_yaml_text(self):
        source = (ROOT / "products/desktop/tests/test_independent_ci_r385.py").read_text()
        self.assertNotIn('self.assertIn("22 actual AES-GCM", self.text)', source)
        self.assertIn('self.commands.count("python -OO -W error -m unittest discover', source)

    def test_no_manifest_or_zero_checks_is_never_success(self):
        self.assertEqual(runner.execute(tuple()), 1)
        with self.assertRaises(runner.EvidenceRejected):
            runner.load_commands(b"", expected_sha=runner.MANIFEST_GIT_SHA1)


if __name__ == "__main__":
    unittest.main()
