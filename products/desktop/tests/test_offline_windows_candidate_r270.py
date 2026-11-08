"""R270 private source-test receipt custody; no native Windows acceptance implied."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "offline_windows_candidate_r269.py"
spec = importlib.util.spec_from_file_location("r270_candidate", SCRIPT)
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
            "commit": "",
            "released": False,
            "qd_approved": False, "all_six_passed": True,
            "application_results": [
                {"app": name, "result": "PASS", "engine": engine,
                 "synthetic_output_count": 1}
                for name, engine in zip(module.APPS, (
                    "ledger", "invoices", "spend", "policy", "grants", "procurement"))
            ],
        },
    }


class SourceReceiptCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.session = Path(self.temp.name) / "private-session"
        self.session.mkdir()
        self.receipt = self.session / "source-suite-evidence.json"
        self.calls = []
        self.save_receipt()

    def save_receipt(self, record=None):
        self.receipt.write_text(json.dumps(source_receipt() if record is None else record), encoding="utf-8")

    def assert_rejected(self):
        with self.assertRaises(module.CandidateBuildRejected) as cm:
            module._source_receipt_sha256(self.receipt)
        self.assertEqual(str(cm.exception), module.ERROR)

    def runner(self, argv, cwd, timeout):
        self.calls.append(tuple(argv))
        if "offline_source_gate.py" in argv[2]:
            self.assertEqual(argv[3], "--report")
            self.assertEqual(Path(argv[4]), self.receipt)
        if "release_gate.py" in argv[2]:
            Path(argv[-1]).write_text('{"synthetic":"not real Windows evidence"}', encoding="ascii")
        if "defender_candidate_scan_r111.py" in argv[2]:
            Path(argv[-1]).write_text('{"synthetic":"not real Defender evidence"}', encoding="ascii")
        return 0

    def test_valid_six_app_receipt_has_stable_digest(self):
        first = module._source_receipt_sha256(self.receipt)
        self.assertEqual(first, module._source_receipt_sha256(self.receipt))
        self.assertRegex(first, r"^[0-9a-f]{64}$")

    def test_source_report_missing_after_child_zero_exit_rejected(self):
        self.receipt.unlink()
        self.assert_rejected()

    def test_unparseable_receipt_rejected(self):
        self.receipt.write_bytes(b"{bad")
        self.assert_rejected()

    def test_empty_and_oversized_receipts_rejected(self):
        self.receipt.write_bytes(b"")
        self.assert_rejected()
        self.receipt.write_bytes(b"X" * (module.MAX_SOURCE_RECEIPT_BYTES + 1))
        self.assert_rejected()

    def test_symlink_receipt_rejected(self):
        other = self.session / "other"
        other.write_text("{}")
        self.receipt.unlink()
        try:
            self.receipt.symlink_to(other)
        except (OSError, NotImplementedError):
            self.skipTest("symlink privilege unavailable")
        self.assert_rejected()

    def test_hardlinked_receipt_rejected(self):
        alias = self.session / "alias"
        try:
            alias.hardlink_to(self.receipt)
        except (OSError, NotImplementedError):
            self.skipTest("hardlink unavailable")
        self.assert_rejected()

    def test_false_release_flags_rejected(self):
        for key in ("released", "qd_approved", "windows_executables_verified", "premium_download_authorized"):
            with self.subTest(key=key):
                receipt = source_receipt()
                receipt[key] = True
                self.save_receipt(receipt)
                self.assert_rejected()

    def test_incomplete_or_forged_source_smoke_rejected(self):
        for mutation in ("remove", "duplicate", "failed", "false_true"):
            with self.subTest(mutation=mutation):
                receipt = source_receipt()
                records = receipt["source_smoke"]["application_results"]
                if mutation == "remove":
                    records.pop()
                elif mutation == "duplicate":
                    records[0]["app"] = records[1]["app"]
                elif mutation == "failed":
                    records[2]["result"] = "SKIPPED"
                else:
                    receipt["source_smoke"]["all_six_passed"] = 1
                self.save_receipt(receipt)
                self.assert_rejected()

    def test_optimized_regression_suite_must_pass(self):
        receipt = source_receipt()
        receipt["optimized_unittest"] = "SKIPPED"
        self.save_receipt(receipt)
        self.assert_rejected()

    def test_invalid_or_missing_provenance_rejected(self):
        for prov in ({}, {"schema": "wrong", "test_count": 18},
                     {"schema": "fvs-unittest-provenance-v2", "test_count": True},
                     {"schema": "fvs-unittest-provenance-v2", "test_count": 0}):
            with self.subTest(prov=prov):
                receipt = source_receipt()
                receipt["unittest_provenance"] = prov
                self.save_receipt(receipt)
                self.assert_rejected()

    def test_unexpected_top_level_key_rejected(self):
        receipt = source_receipt()
        receipt["private_path"] = "C:/customer/data"
        self.save_receipt(receipt)
        self.assert_rejected()

    def test_candidate_plan_passes_with_retained_source_receipt(self):
        module._execute_plan(self.root, self.session, "python.exe", self.runner)
        self.assertEqual(len(self.calls), 43)
        self.assertEqual(self.calls[0][2].split("/")[-1], "offline_source_gate.py")
        self.assertTrue(self.receipt.is_file())
        self.assertEqual(len([cmd for cmd in self.calls if "PyInstaller" in cmd]), 6)

    def test_missing_receipt_blocks_before_any_toolchain_or_exe(self):
        self.receipt.unlink()
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.session, "python.exe", self.runner)
        self.assertEqual(len(self.calls), 1)

    def test_mutation_during_build_blocks_final_success(self):
        original = source_receipt()
        def evil_runner(argv, cwd, timeout):
            code = self.runner(argv, cwd, timeout)
            if "report_attestation.py" in argv[2]:
                changed = source_receipt()
                changed["unittest_provenance"]["test_count"] += 1
                self.save_receipt(changed)
            return code
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.session, "python.exe", evil_runner)
        self.assertEqual(original["unittest_provenance"]["test_count"], 18)
        self.assertEqual(len(self.calls), 43)

    def test_failure_of_source_suite_blocks_all_other_steps(self):
        def fail_first(argv, cwd, timeout):
            self.calls.append(tuple(argv))
            return 1
        with self.assertRaises(module.CandidateBuildRejected):
            module._execute_plan(self.root, self.session, "python.exe", fail_first)
        self.assertEqual(len(self.calls), 1)

    def test_no_windows_artifacts_or_distribution_from_local_regressions(self):
        self.assertEqual([p for p in self.session.iterdir() if p.suffix.lower() == ".exe"], [])


if __name__ == "__main__":
    unittest.main()
