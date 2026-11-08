"""R271 Windows candidate evidence custody tests; mock builds are NOT Win11 verification."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "offline_windows_candidate_r269.py"
spec = importlib.util.spec_from_file_location("r271_candidate", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def source_receipt():
    return {
        "schema": "fvs-offline-source-suite-v1",
        "scope": "FULL_PYTHON_SOURCE_TESTS_ONLY_NOT_WINDOWS_BINARY",
        "released": False, "qd_approved": False,
        "windows_executables_verified": False,
        "premium_download_authorized": False,
        "normal_unittest": "PASS", "optimized_unittest": "PASS",
        "unittest_provenance": {
            "schema": "fvs-unittest-provenance-v2", "test_count": 18,
            "module_count": 8, "skipped_count": 0,
            "test_ids_sha256": "0" * 64, "active_ids_sha256": "1" * 64,
            "skipped_ids_sha256": "2" * 64,
        },
        "test_inventory": [{"path": "products/desktop/tests/test_dummy.py", "sha256": "3" * 64}],
        "source_smoke": {
            "schema": "fvs-source-smoke-v1", "scope": "PYTHON_SOURCE_ONLY_NOT_WINDOWS_BINARY_VERIFICATION",
            "source_inventory": [{"path": "products/desktop/fvs_suite/smoke.py", "sha256": "4" * 64}],
            "released": False, "qd_approved": False, "all_six_passed": True,
            "commit": "",
            "application_results": [
                {"app": name, "result": "PASS", "engine": engine,
                 "synthetic_output_count": 1}
                for name, engine in zip(module.APPS, (
                    "ledger", "invoices", "spend", "policy", "grants", "procurement"
                ))
            ],
        },
    }


class WindowsEvidenceCustodyR271Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.run = Path(self.tmp.name) / "private"
        self.run.mkdir()
        self.report = self.run / "offline-candidate-evidence.json"
        self.report.write_bytes(b'{"evidence":"synthetic-only"}')
        self.receipt = self.run / "source-suite-evidence.json"
        self.receipt.write_text(json.dumps(source_receipt()), encoding="utf-8")
        self.calls = []

    def assert_rejected(self):
        with self.assertRaises(module.CandidateBuildRejected) as err:
            module._private_windows_report_sha256(self.report)
        self.assertEqual(str(err.exception), module.ERROR)

    def runner(self, argv, cwd, timeout):
        self.calls.append(tuple(argv))
        if "defender_candidate_scan_r111.py" in argv[2]:
            Path(argv[-1]).write_text('{"synthetic":"no Defender scan performed"}', encoding="ascii")
        return 0

    def test_valid_report_digest_stable_and_exact(self):
        expected = hashlib.sha256(self.report.read_bytes()).hexdigest()
        self.assertEqual(module._private_windows_report_sha256(self.report), expected)
        self.assertEqual(module._private_windows_report_sha256(self.report), expected)

    def test_one_byte_report_rejected_when_empty(self):
        self.report.write_bytes(b'')
        self.assert_rejected()

    def test_missing_report_rejected(self):
        self.report.unlink()
        self.assert_rejected()

    def test_directory_report_rejected(self):
        self.report.unlink()
        self.report.mkdir()
        self.assert_rejected()

    def test_oversized_report_rejected(self):
        self.report.write_bytes(b'a' * (module.MAX_WINDOWS_REPORT_BYTES + 1))
        self.assert_rejected()

    def test_at_maximum_size_report_allowed(self):
        self.report.write_bytes(b'a' * module.MAX_WINDOWS_REPORT_BYTES)
        self.assertRegex(module._private_windows_report_sha256(self.report), r'^[0-9a-f]{64}$')

    def test_symlink_report_rejected(self):
        target = self.run / 'sensitive_customer.csv'
        target.write_bytes(b'PRIVATE_FINANCIAL_DATA')
        self.report.unlink()
        try:
            self.report.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unavailable')
        self.assert_rejected()

    def test_hardlinked_report_rejected(self):
        alias = self.run / 'alias'
        try:
            alias.hardlink_to(self.report)
        except (OSError, NotImplementedError):
            self.skipTest('hardlink unavailable')
        self.assert_rejected()

    def test_file_open_failure_is_generic(self):
        with mock.patch.object(module.os, 'open', side_effect=PermissionError('CUSTOMER_SSN_PATH')):
            self.assert_rejected()

    def test_os_read_failure_is_generic_and_fd_closed(self):
        with mock.patch.object(module.os, 'read', side_effect=OSError('CUSTOMER_PAYROLL')):
            self.assert_rejected()
        self.assertEqual(module._private_windows_report_sha256(self.report),
                         hashlib.sha256(self.report.read_bytes()).hexdigest())

    def test_descriptor_file_swap_detected_before_hash(self):
        original = module.os.open
        def replace_on_open(path, flags):
            fd = original(path, flags)
            Path(path).unlink()
            Path(path).write_bytes(b'{"forged":"same-size"}')
            return fd
        try:
            with mock.patch.object(module.os, 'open', side_effect=replace_on_open):
                self.assert_rejected()
        except PermissionError:
            self.skipTest('Windows filesystem does not permit replacing an open file')

    def test_report_mutated_while_reading_rejected(self):
        original = module.os.read
        triggered = False
        def mutate_on_read(fd, size):
            nonlocal triggered
            chunk = original(fd, size)
            if not triggered:
                triggered = True
                self.report.write_bytes(b'{"mutated":true}')
            return chunk
        try:
            with mock.patch.object(module.os, 'read', side_effect=mutate_on_read):
                self.assert_rejected()
        except PermissionError:
            self.skipTest('Windows filesystem does not permit modifying an open file')

    def test_plan_six_binaries_and_unchanged_stage_count(self):
        module._execute_plan(self.root, self.run, 'python.exe', self.runner)
        self.assertEqual(len(self.calls), 43)
        self.assertEqual(sum('PyInstaller' in cmd for cmd in self.calls), 6)
        self.assertEqual(sum('report_attestation.py' in cmd[2] for cmd in self.calls), 1)
        att = next(cmd for cmd in self.calls if 'report_attestation.py' in cmd[2])
        self.assertEqual(att[att.index('--expected-report-sha256')+1],
                         hashlib.sha256(self.report.read_bytes()).hexdigest())

    def test_attestation_then_report_rewrite_fails_closed(self):
        def rewrite_after_attestation(argv, cwd, timeout):
            result = self.runner(argv, cwd, timeout)
            if 'report_attestation.py' in argv[2]:
                self.report.write_bytes(b'{"evidence":"changed-after-attestation"}')
            return result
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.run, 'python.exe', rewrite_after_attestation)
        self.assertEqual(len(self.calls), 43)

    def test_attestation_then_report_unlink_fails_closed(self):
        def unlink_after_attestation(argv, cwd, timeout):
            result = self.runner(argv, cwd, timeout)
            if 'report_attestation.py' in argv[2]:
                self.report.unlink()
            return result
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.run, 'python.exe', unlink_after_attestation)
        self.assertEqual(len(self.calls), 43)

    def test_attestation_then_report_symlink_fails_closed(self):
        alternate = self.run / 'alternate'
        alternate.write_bytes(self.report.read_bytes())
        def swap_after_attestation(argv, cwd, timeout):
            result = self.runner(argv, cwd, timeout)
            if 'report_attestation.py' in argv[2]:
                self.report.unlink()
                self.report.symlink_to(alternate)
            return result
        try:
            with self.assertRaises(module.CandidateBuildRejected):
                module._execute_plan(self.root, self.run, 'python.exe', swap_after_attestation)
        except (OSError, NotImplementedError):
            self.skipTest('symlink unavailable')
        self.assertEqual(len(self.calls), 43)

    def test_parent_no_longer_calls_path_read_bytes_on_report(self):
        with mock.patch.object(Path, 'read_bytes', side_effect=RuntimeError('should not call read_bytes')):
            self.assertRegex(module._private_windows_report_sha256(self.report), r'^[0-9a-f]{64}$')


if __name__ == '__main__':
    unittest.main()
