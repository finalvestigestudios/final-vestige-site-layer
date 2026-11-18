"""R509: audit immutable source-test inventory, redaction and runner custody."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import re
import subprocess
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



class SourceEvidenceR511(unittest.TestCase):
    """Source script, manifest and interpreter-startup custody (synthetic files)."""

    SCRIPT = "products/desktop/scripts/source_smoke_gate.py"
    LINE = ("python -W error " + SCRIPT + "\n").encode("ascii")
    MANIFEST_PARTS = ("products", "desktop", "ci", "source_evidence_commands_r509.txt")

    @classmethod
    def validate_script(cls, root: Path):
        return runner.load_commands(
            cls.LINE, root, expected_sha=runner.git_blob_sha(cls.LINE), expected_count=1
        )

    def test_all_four_approved_script_commands_resolve_in_real_checkout(self):
        raw = ("\n".join(sorted(runner.SCRIPT_COMMANDS)) + "\n").encode("ascii")
        self.assertEqual(
            len(runner.load_commands(
                raw, ROOT, expected_sha=runner.git_blob_sha(raw), expected_count=4
            )), 4
        )

    def test_regular_source_script_accepted(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            leaf = root / self.SCRIPT
            leaf.parent.mkdir(parents=True)
            leaf.write_text("pass\n")
            self.assertEqual(len(self.validate_script(root)), 1)

    def test_missing_approved_source_script_rejected(self):
        with TemporaryDirectory() as d, self.assertRaises(runner.EvidenceRejected):
            self.validate_script(Path(d))

    def test_symlinked_source_script_leaf_rejected(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            real = root / "private.py"
            real.write_text("pass")
            leaf = root / self.SCRIPT
            leaf.parent.mkdir(parents=True)
            try:
                leaf.symlink_to(real)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"File symlink unavailable: {type(exc).__name__}")
            with self.assertRaises(runner.EvidenceRejected):
                self.validate_script(root)

    def test_symlinked_source_scripts_directory_rejected(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            outside = root / "outside"
            outside.mkdir()
            (outside / "source_smoke_gate.py").write_text("pass")
            script_dir = root / "products/desktop/scripts"
            script_dir.parent.mkdir(parents=True)
            try:
                script_dir.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Directory symlink unavailable: {type(exc).__name__}")
            with self.assertRaises(runner.EvidenceRejected):
                self.validate_script(root)

    def test_offline_script_symlinked_desktop_ancestor_rejected(self):
        line = b"python -I products/desktop/offline_source_smoke_r408.py\n"
        with TemporaryDirectory() as d:
            root = Path(d)
            outside = root / "outside"
            outside.mkdir()
            (outside / "offline_source_smoke_r408.py").write_text("pass")
            parent = root / "products"
            parent.mkdir()
            try:
                (parent / "desktop").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Directory symlink unavailable: {type(exc).__name__}")
            with self.assertRaises(runner.EvidenceRejected):
                runner.load_commands(line, root, expected_sha=runner.git_blob_sha(line),
                                     expected_count=1)

    def test_bad_repository_path_components_rejected(self):
        with TemporaryDirectory() as d:
            for parts in ((), ("..",), ("products/desktop",), ("\\\\server",), ("foo", "")):
                with self.subTest(parts=parts):
                    self.assertFalse(runner._is_unlinked_repo_file(Path(d), parts))

    def test_regular_manifest_path_accepted(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            leaf = root.joinpath(*self.MANIFEST_PARTS)
            leaf.parent.mkdir(parents=True)
            leaf.write_text("synthetic inventory")
            self.assertTrue(runner._is_unlinked_repo_file(root, self.MANIFEST_PARTS))

    def test_symlinked_manifest_leaf_rejected(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            outside = root / "private.txt"
            outside.write_text("secret")
            leaf = root.joinpath(*self.MANIFEST_PARTS)
            leaf.parent.mkdir(parents=True)
            try:
                leaf.symlink_to(outside)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"File symlink unavailable: {type(exc).__name__}")
            self.assertFalse(runner._is_unlinked_repo_file(root, self.MANIFEST_PARTS))

    def test_symlinked_manifest_parent_rejected(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            outside = root / "outside"
            outside.mkdir()
            (outside / "source_evidence_commands_r509.txt").write_text("private")
            parent = root / "products/desktop/ci"
            parent.parent.mkdir(parents=True)
            try:
                parent.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"Directory symlink unavailable: {type(exc).__name__}")
            self.assertFalse(runner._is_unlinked_repo_file(root, self.MANIFEST_PARTS))

    def test_entrypoint_refuses_linked_manifest_without_reading_private_target(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            outside = root / "customer-payment-records.csv"
            outside.write_text("private")
            leaf = root.joinpath(*self.MANIFEST_PARTS)
            leaf.parent.mkdir(parents=True)
            try:
                leaf.symlink_to(outside)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"File symlink unavailable: {type(exc).__name__}")
            errors = io.StringIO()
            with patch.object(runner, "ROOT", root), patch.object(runner, "MANIFEST", leaf), \
                 patch.object(Path, "read_bytes", side_effect=AssertionError("read forbidden")), \
                 redirect_stderr(errors):
                self.assertEqual(runner.main(), 1)
            self.assertIn("immutable source evidence unavailable", errors.getvalue())
            self.assertNotIn("customer-payment-records", errors.getvalue())

    def test_hostile_python_startup_and_loader_environment_removed(self):
        injected = {
            "PYTHONOPTIMIZE": "2", "PYTHONWARNINGS": "ignore",
            "PYTHONBREAKPOINT": "attacker.hook",
            "PYTHONPYCACHEPREFIX": "/private/cache",
            "LD_PRELOAD": "/private/lib.so",
            "LD_LIBRARY_PATH": "/private",
            "DYLD_INSERT_LIBRARIES": "/private/inject.dylib",
            "DYLD_LIBRARY_PATH": "/private",
            "CI": "true",
        }
        with patch.dict(os.environ, injected):
            child = runner._child_environment(ROOT)
        for name in injected:
            if name != "CI":
                self.assertNotIn(name, child)
        self.assertEqual(child["CI"], "true")
        self.assertEqual(child["PYTHONDONTWRITEBYTECODE"], "1")



class SourceEvidenceR512(unittest.TestCase):
    """Defend the child-process environment, with no private data fixtures."""

    def test_unreviewed_python_startup_knobs_stripped(self):
        injected = {key: "poison" for key in (
            "PYTHONPATH", "PYTHONHOME", "PYTHONINSPECT", "PYTHONWARNINGS",
            "PYTHONOPTIMIZE", "PYTHONSAFEPATH", "PYTHONUTF8",
            "PYTHONIOENCODING", "PYTHONHASHSEED", "PYTHONDEVMODE",
            "PYTHONPROFILEIMPORTTIME", "PYTHONTRACEMALLOC",
        )}
        with patch.dict(os.environ, injected):
            child = runner._child_environment(ROOT)
        for key in injected:
            if key not in ("PYTHONPATH", "PYTHONHASHSEED"):
                self.assertNotIn(key, child)
        self.assertEqual(child["PYTHONHASHSEED"], "0")
        self.assertEqual(child["PYTHONPATH"], str(ROOT / "products" / "desktop"))

    def test_case_insensitive_python_startup_poisoning_rejected(self):
        with patch.dict(os.environ, {
            "PythonWarnings": "ignore", "pythoninspect": "1",
        }):
            child = runner._child_environment(ROOT)
        self.assertNotIn("PythonWarnings", child)
        self.assertNotIn("pythoninspect", child)

    def test_github_command_files_and_event_payloads_stripped(self):
        injected = {
            "GITHUB_STEP_SUMMARY": "/private/summary",
            "GITHUB_STATE": "/private/state",
            "GITHUB_EVENT_PATH": "/private/event",
            "GITHUB_ENV": "/private/env",
            "GITHUB_OUTPUT": "/private/output",
            "GITHUB_PATH": "/private/path",
            "GITHUB_TOKEN": "synthetic-token",
            "GITHUB_ACTIONS": "true",
            "CI": "true",
        }
        with patch.dict(os.environ, injected):
            child = runner._child_environment(ROOT)
        for key in injected:
            if key not in ("GITHUB_ACTIONS", "CI"):
                self.assertNotIn(key, child)
        self.assertEqual(child["GITHUB_ACTIONS"], "true")
        self.assertEqual(child["CI"], "true")

    def test_git_and_ssh_injection_and_agent_handles_stripped(self):
        injected = {
            "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "credential.helper",
            "GIT_CONFIG_VALUE_0": "!private",
            "SSH_AUTH_SOCK": "/private/agent",
            "GIT_ASKPASS": "/private/askpass",
            "SSH_ASKPASS": "/private/askpass2",
        }
        with patch.dict(os.environ, injected):
            child = runner._child_environment(ROOT)
        for key in injected:
            self.assertNotIn(key, child)

    def test_credential_suffixes_and_loader_flags_remain_blocked(self):
        injected = {
            "PAYMENT_COOKIE": "synthetic", "GRANT_SESSION": "synthetic",
            "AWS_ACCESS_KEY_ID": "synthetic", "AZURE_CLIENT_SECRET": "synthetic",
            "LD_PRELOAD": "/private/lib.so", "DYLD_LIBRARY_PATH": "/private",
        }
        with patch.dict(os.environ, injected):
            child = runner._child_environment(ROOT)
        for key in injected:
            self.assertNotIn(key, child)

    def test_nonsensitive_host_basics_and_ci_marker_preserved(self):
        injected = {
            "PATH": "/usr/bin", "CI": "true", "LANG": "en_US.UTF-8",
            "FV_NONSECRET_FLAG": "enabled",
        }
        with patch.dict(os.environ, injected):
            child = runner._child_environment(ROOT)
        for key in ("PATH", "CI", "LANG"):
            self.assertEqual(child[key], injected[key])
        # R514 is allowlist-only, even for a plausibly benign unknown name.
        self.assertNotIn("FV_NONSECRET_FLAG", child)

    def test_real_child_process_ignores_hostile_python_settings(self):
        import subprocess
        with TemporaryDirectory() as d, patch.dict(os.environ, {
            "PYTHONHASHSEED": "random", "PYTHONOPTIMIZE": "2",
        }):
            child = runner._child_environment(Path(d))
            check = subprocess.run(
                [sys.executable, "-B", "-c",
                 "import os,sys; sys.exit(0 if sys.flags.optimize == 0 "
                 "and os.getenv('PYTHONHASHSEED') == '0' else 7)"],
                env=child, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=30, check=False,
            )
        self.assertEqual(check.returncode, 0, check.stderr.decode("utf-8", "replace"))

    def test_environment_generation_is_repeatable(self):
        with patch.dict(os.environ, {
            "PYTHONHASHSEED": "random", "GITHUB_STEP_SUMMARY": "/private",
        }):
            first = runner._child_environment(ROOT)
            second = runner._child_environment(ROOT)
        self.assertEqual(first, second)




class SourceEvidenceR513(unittest.TestCase):
    """Synthetic provider-configuration disclosure regressions for source children."""

    def assert_names_filtered(self, names):
        values = {name: f"synthetic-r513-{i}" for i, name in enumerate(names)}
        with patch.dict(os.environ, values):
            child = runner._child_environment(ROOT)
        for name in names:
            self.assertNotIn(name, child, name)
        for value in values.values():
            self.assertNotIn(value, tuple(child.values()))

    def test_aws_and_azure_config_paths_do_not_escape(self):
        self.assert_names_filtered((
            "AWS_PROFILE", "AWS_CONFIG_FILE", "AWS_SHARED_CREDENTIALS_FILE",
            "AZURE_CONFIG_DIR", "AZURE_SUBSCRIPTION_ID",
        ))

    def test_google_cloud_config_paths_do_not_escape(self):
        self.assert_names_filtered((
            "GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT",
            "GCLOUD_AUTH_TOKEN", "CLOUDSDK_CONFIG",
        ))

    def test_gh_container_and_kubernetes_configuration_do_not_escape(self):
        self.assert_names_filtered((
            "GH_HOST", "GH_CONFIG_DIR", "DOCKER_CONFIG", "DOCKER_HOST",
            "KUBECONFIG", "KUBE_CONFIG",
        ))

    def test_package_registry_config_and_embedded_urls_do_not_escape(self):
        self.assert_names_filtered((
            "NPM_CONFIG_USERCONFIG", "PIP_INDEX_URL", "PIP_CONFIG_FILE",
            "PYPI_USERNAME", "TWINE_USERNAME", "POETRY_HTTP_BASIC_FOO_USERNAME",
            "UV_INDEX_URL",
        ))

    def test_gpg_and_terraform_configuration_do_not_escape(self):
        self.assert_names_filtered((
            "GNUPGHOME", "GPG_AGENT_INFO", "TF_VAR_registry_auth",
            "TERRAFORM_CLI_CONFIG_FILE",
        ))

    def test_case_insensitive_provider_names_are_blocked(self):
        self.assert_names_filtered((
            "Aws_Profile", "gH_Config_dir", "pIp_ConfIg_fIle",
            "kuBE_config", "gnuPGhome",
        ))

    def test_sensitive_values_absent_but_host_path_preserved(self):
        with patch.dict(os.environ, {
            "AWS_PROFILE": "SYNTHETIC_AWS_PRIVATE",
            "PIP_INDEX_URL": "SYNTHETIC_PIP_PRIVATE",
            "PATH": "/usr/bin",
        }):
            child = runner._child_environment(ROOT)
        self.assertNotIn("SYNTHETIC_AWS_PRIVATE", tuple(child.values()))
        self.assertNotIn("SYNTHETIC_PIP_PRIVATE", tuple(child.values()))
        self.assertEqual(child["PATH"], "/usr/bin")

    def test_public_ci_and_fixed_interpreter_settings_survive(self):
        with patch.dict(os.environ, {
            "CI": "true", "LANG": "en_US.UTF-8", "GITHUB_ACTIONS": "true",
            "PYTHONHASHSEED": "random",
        }):
            child = runner._child_environment(ROOT)
        self.assertEqual(child["CI"], "true")
        self.assertEqual(child["LANG"], "en_US.UTF-8")
        self.assertEqual(child["GITHUB_ACTIONS"], "true")
        self.assertEqual(child["PYTHONHASHSEED"], "0")
        self.assertEqual(child["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertEqual(child["PYTHONPATH"], str(ROOT / "products" / "desktop"))

    def test_actual_child_process_cannot_read_injected_provider_settings(self):
        import subprocess
        with patch.dict(os.environ, {
            "AWS_PROFILE": "SYNTHETIC_AWS_PRIVATE",
            "PIP_INDEX_URL": "SYNTHETIC_PIP_PRIVATE",
        }):
            child = runner._child_environment(ROOT)
            result = subprocess.run([
                sys.executable, "-B", "-c",
                "import os,sys;sys.exit(0 if (not os.getenv('AWS_PROFILE') "
                "and not os.getenv('PIP_INDEX_URL') "
                "and os.getenv('PYTHONHASHSEED')=='0') else 7)",
            ], env=child, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=30, check=False)
        self.assertEqual(result.returncode, 0)

    def test_environment_generation_stays_deterministic(self):
        with patch.dict(os.environ, {
            "DOCKER_CONFIG": "SYNTHETIC_DOCKER_PRIVATE",
            "AWS_PROFILE": "SYNTHETIC_AWS_PRIVATE",
        }):
            self.assertEqual(runner._child_environment(ROOT),
                             runner._child_environment(ROOT))


from source_child_env_r514 import _SAFE_HOST_NAMES, child_environment


class SourceChildEnvironmentR514(unittest.TestCase):
    """Ten real module regressions, exercised by BOTH pinned matrix modes."""
    ROOT = Path("/synthetic")

    def test_unknown_financial_configuration_does_not_escape(self):
        host = {"FV_LICENSE_FILE": "private", "GRANTS_AUDIT_DIR": "private2",
                "FINANCE_VAULT_URL": "private3", "CLIENT_BILLING_ENDPOINT": "private4"}
        self.assertFalse(set(host).intersection(child_environment(self.ROOT, host)))

    def test_arbitrary_unsuffixed_variable_no_longer_passes(self):
        self.assertNotIn("FV_NONSECRET_FLAG", child_environment(self.ROOT,
                         {"FV_NONSECRET_FLAG": "enabled"}))

    def test_cloud_and_registry_configuration_no_longer_passes(self):
        host = {"AWS_PROFILE": "private", "KUBECONFIG": "private",
                "PIP_INDEX_URL": "private", "GH_CONFIG_DIR": "private"}
        self.assertFalse(set(host).intersection(child_environment(self.ROOT, host)))

    def test_os_and_ci_bootstrap_survive(self):
        host = {"PATH": "/usr/bin", "CI": "true", "LANG": "en_US.UTF-8",
                "GITHUB_ACTIONS": "true", "SystemRoot": "C:\\Windows",
                "TEMP": "C:\\Temp", "LOCALAPPDATA": "C:\\Local"}
        child = child_environment(self.ROOT, host)
        for key, value in host.items():
            self.assertEqual(child[key], value)

    def test_python_controls_are_fixed_not_inherited(self):
        host = {"PYTHONHASHSEED": "random", "PYTHONOPTIMIZE": "2",
                "PYTHONPATH": "/private", "PYTHONWARNINGS": "ignore"}
        child = child_environment(self.ROOT, host)
        self.assertEqual(child["PYTHONHASHSEED"], "0")
        self.assertEqual(child["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertEqual(child["PYTHONPATH"], str(self.ROOT / "products/desktop"))
        self.assertNotIn("PYTHONOPTIMIZE", child)
        self.assertNotIn("PYTHONWARNINGS", child)

    def test_loader_and_pythonuserbase_not_allowed(self):
        host = {"LD_PRELOAD": "/private", "LD_AUDIT": "/private",
                "DYLD_INSERT_LIBRARIES": "/private", "PYTHONUSERBASE": "/private"}
        self.assertFalse(set(host).intersection(child_environment(self.ROOT, host)))

    def test_duplicate_case_folded_windows_name_dropped(self):
        child = child_environment(self.ROOT, {"Path": "private", "PATH": "/safe", "CI": "true"})
        self.assertNotIn("Path", child)
        self.assertNotIn("PATH", child)
        self.assertEqual(child["CI"], "true")

    def test_synthetic_subprocess_cannot_see_unknown_host_variable(self):
        env = child_environment(self.ROOT, {"PATH": "/usr/bin",
                  "FINANCE_PRIVATE_ENDPOINT": "synthetic-never-inherit"})
        result = subprocess.run([sys.executable, "-B", "-c",
             "import os,sys;sys.exit(0 if 'FINANCE_PRIVATE_ENDPOINT' not in os.environ "
             "and os.environ.get('PYTHONHASHSEED') == '0' else 9)"],
             env=env, capture_output=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0)

    def test_mapping_is_never_mutated(self):
        host = {"CI": "true", "PIP_INDEX_URL": "synthetic"}
        before = dict(host)
        child_environment(self.ROOT, host)
        self.assertEqual(host, before)

    def test_deterministic_and_no_unknown_keys(self):
        host = {"CI": "true", "PAYMENT_URL": "synthetic", "PATH": "/usr/bin"}
        a = child_environment(self.ROOT, host)
        self.assertEqual(a, child_environment(self.ROOT, host))
        self.assertEqual(set(a) - {"PYTHONPATH", "PYTHONHASHSEED", "PYTHONDONTWRITEBYTECODE"},
                         {"CI", "PATH"})
        self.assertTrue({"PATH", "CI"}.issubset(_SAFE_HOST_NAMES))


from source_path_snapshot_r515 import (
    SourceSnapshotRejected, matches_source_fingerprint, source_fingerprint,
)


class SourcePrelaunchR515(unittest.TestCase):
    """R515: pin bytes once, detect later test replacement before launch."""

    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.a_parts = ("products", "desktop", "tests", "test_r515_a.py")
        self.b_parts = ("products", "desktop", "tests", "test_r515_b.py")
        self.a = self.root.joinpath(*self.a_parts)
        self.b = self.root.joinpath(*self.b_parts)
        self.a.parent.mkdir(parents=True)
        self.a.write_bytes(b"print('a')\n")
        self.b.write_bytes(b"print('b')\n")
        prefix = ("-B", "-W", "error", "-m", "unittest",
                  "discover", "-s", "products/desktop/tests", "-p")
        self.commands = (prefix + ("test_r515_a.py",),
                         prefix + ("test_r515_b.py",))

    def test_snapshot_is_stable_and_digest_only(self):
        receipt = source_fingerprint(self.root, self.a_parts)
        self.assertEqual(len(receipt), 32)
        self.assertTrue(matches_source_fingerprint(self.root, self.a_parts, receipt))
        self.assertNotIn(b"print", receipt)

    def test_regular_file_replacement_is_detected(self):
        receipt = source_fingerprint(self.root, self.a_parts)
        self.a.write_bytes(b"print('changed')\n")
        self.assertFalse(matches_source_fingerprint(self.root, self.a_parts, receipt))

    def test_missing_file_fails_closed(self):
        receipt = source_fingerprint(self.root, self.a_parts)
        self.a.unlink()
        self.assertFalse(matches_source_fingerprint(self.root, self.a_parts, receipt))

    def test_file_symlink_fails_closed(self):
        receipt = source_fingerprint(self.root, self.a_parts)
        self.a.unlink()
        try:
            self.a.symlink_to(self.b)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlink creation unavailable: {type(exc).__name__}")
        self.assertFalse(matches_source_fingerprint(self.root, self.a_parts, receipt))

    def test_parent_symlink_fails_closed(self):
        self.a.unlink()
        self.b.unlink()
        self.a.parent.rmdir()
        external = self.root / "outside"
        external.mkdir()
        (external / "test_r515_a.py").write_bytes(b"print('not trusted')\n")
        try:
            self.a.parent.symlink_to(external, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlink creation unavailable: {type(exc).__name__}")
        with self.assertRaises(SourceSnapshotRejected):
            source_fingerprint(self.root, self.a_parts)

    def test_oversized_source_fails_closed(self):
        self.a.write_bytes(b"x" * 1_048_577)
        with self.assertRaises(SourceSnapshotRejected):
            source_fingerprint(self.root, self.a_parts)

    def test_traversal_and_invalid_receipts_fail_closed(self):
        for parts in (("..",), ("untrusted/test.py",), ("",), ()):
            with self.subTest(parts=parts), self.assertRaises(SourceSnapshotRejected):
                source_fingerprint(self.root, parts)
        self.assertFalse(matches_source_fingerprint(self.root, self.a_parts, b"short"))

    def test_private_filename_is_not_in_error(self):
        self.a.unlink()
        with self.assertRaises(SourceSnapshotRejected) as seen:
            source_fingerprint(self.root, self.a_parts)
        self.assertNotIn(self.directory.name, str(seen.exception))
        self.assertNotIn("test_r515_a.py", str(seen.exception))

    def test_runner_stable_prelaunch_two_checks_pass(self):
        calls = []
        def fake(argv, **kwargs):
            calls.append(argv)
            return SimpleNamespace(returncode=0)
        out = io.StringIO()
        with redirect_stdout(out):
            status = runner.execute(self.commands, self.root, spawn=fake,
                                    verify_source_snapshots=True)
        self.assertEqual(status, 0)
        self.assertEqual(len(calls), 2)
        self.assertIn("2 source commands", out.getvalue())

    def test_runner_rejects_later_regular_file_tampering(self):
        calls = []
        def mutate_after_first(argv, **kwargs):
            calls.append(argv)
            self.b.write_bytes(b"print('replaced')\n")
            return SimpleNamespace(returncode=0)
        errors = io.StringIO()
        with redirect_stderr(errors):
            status = runner.execute(self.commands, self.root, spawn=mutate_after_first,
                                    verify_source_snapshots=True)
        self.assertEqual(status, 1)
        self.assertEqual(len(calls), 1)
        self.assertIn("source check 2/2 changed", errors.getvalue())
        self.assertNotIn(self.root.as_posix(), errors.getvalue())

    def test_runner_rejects_missing_before_any_launch(self):
        self.b.unlink()
        calls = []
        with redirect_stderr(io.StringIO()):
            status = runner.execute(self.commands, self.root,
                                    spawn=lambda *args, **kw: calls.append(args),
                                    verify_source_snapshots=True)
        self.assertEqual(status, 1)
        self.assertFalse(calls)

    def test_runner_rejects_unreviewed_command_before_any_launch(self):
        calls = []
        with redirect_stderr(io.StringIO()):
            status = runner.execute((("-c", "print('private')"),), self.root,
                                    spawn=lambda *a, **kw: calls.append(a),
                                    verify_source_snapshots=True)
        self.assertEqual(status, 1)
        self.assertFalse(calls)

    def test_main_enables_prelaunch_receipts_not_just_manifest_check(self):
        manifest = self.root / "products/desktop/ci/source_evidence_commands_r509.txt"
        manifest.parent.mkdir(parents=True)
        manifest.write_bytes(b"synthetic inventory\n")
        with patch.object(runner, "ROOT", self.root), patch.object(runner, "MANIFEST", manifest), \
             patch.object(runner, "load_commands", return_value=self.commands), \
             patch.object(runner, "execute", return_value=0) as do_execute:
            self.assertEqual(runner.main(), 0)
        do_execute.assert_called_once_with(self.commands, verify_source_snapshots=True)

if __name__ == "__main__":
    unittest.main()
