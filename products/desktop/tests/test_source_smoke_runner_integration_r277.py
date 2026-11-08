"""R277: real private-runner receipt integration; synthetic evidence, no PE proof."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from test_offline_windows_candidate_r270 import source_receipt

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
runner_spec = importlib.util.spec_from_file_location(
    "r277_private_runner", SCRIPTS / "offline_windows_candidate_r269.py")
candidate = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(candidate)


class SourceSmokeRunnerIntegrationTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.receipt_path = Path(work.name) / "source-suite-evidence.json"
        self.receipt = source_receipt()

    def validate(self):
        self.receipt_path.write_bytes(
            json.dumps(self.receipt, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        return candidate._source_receipt_sha256(self.receipt_path)

    def rejected(self):
        with self.assertRaises(candidate.CandidateBuildRejected) as raised:
            self.validate()
        self.assertEqual(str(raised.exception), candidate.ERROR)
        self.assertIsNone(raised.exception.__cause__)
        self.assertIsNone(raised.exception.__context__)

    def test_inherited_r270_fixture_is_valid_against_r276_real_runner(self):
        self.assertTrue(candidate.valid_source_smoke_records(
            self.receipt["source_smoke"]["application_results"]))
        self.assertRegex(self.validate(), r"^[0-9a-f]{64}$")

    def test_genuine_source_producer_outer_field_contract(self):
        self.assertEqual(set(self.receipt["source_smoke"]), {
            "schema", "scope", "released", "qd_approved", "commit",
            "source_inventory", "application_results", "all_six_passed"})

    def test_empty_local_commit_is_valid(self):
        self.assertEqual(self.receipt["source_smoke"]["commit"], "")
        self.assertRegex(self.validate(), r"^[0-9a-f]{64}$")

    def test_40_and_64_character_git_commit_evidence_accepted(self):
        for count in (40, 64):
            with self.subTest(count=count):
                self.receipt["source_smoke"]["commit"] = "a" * count
                self.assertRegex(self.validate(), r"^[0-9a-f]{64}$")

    def test_missing_producer_field_is_rejected(self):
        for field in tuple(self.receipt["source_smoke"]):
            with self.subTest(field=field):
                self.receipt = source_receipt()
                del self.receipt["source_smoke"][field]
                self.rejected()

    def test_extra_private_paths_and_license_secrets_rejected_without_echo(self):
        for field in ("private_path", "private_license_key", "unrecognized_receipt"):
            with self.subTest(field=field):
                self.receipt = source_receipt()
                self.receipt["source_smoke"][field] = "C:/private/payroll/clients.csv"
                self.rejected()

    def test_commit_rejects_unsafe_values(self):
        invalid = (None, True, 1, 0, [], {}, "C:/private/payroll.csv",
                   "abc123", "a" * 39, "a" * 41, "a" * 65,
                   "Z" * 40, "é" * 40, "A" * 40, "\n" * 40)
        for value in invalid:
            with self.subTest(kind=type(value).__name__, length=len(str(value))):
                self.receipt = source_receipt()
                self.receipt["source_smoke"]["commit"] = value
                self.rejected()

    def test_false_release_or_qd_flag_is_rejected(self):
        for key in ("released", "qd_approved"):
            for value in (True, 0, 1, None, "false"):
                with self.subTest(key=key, value=value):
                    self.receipt = source_receipt()
                    self.receipt["source_smoke"][key] = value
                    self.rejected()

    def test_wrong_engine_and_zero_output_rejected_by_actual_runner(self):
        self.receipt["source_smoke"]["application_results"][0]["engine"] = "procurement"
        self.receipt["source_smoke"]["application_results"][0]["synthetic_output_count"] = 0
        self.rejected()

    def test_unexpected_app_record_field_rejected_by_actual_runner(self):
        self.receipt["source_smoke"]["application_results"][0]["customer_path"] = "C:/private"
        self.rejected()

    def test_boolean_success_label_is_rejected(self):
        self.receipt["source_smoke"]["all_six_passed"] = 1
        self.rejected()

    def test_mutating_receipt_changes_digest(self):
        first = self.validate()
        self.receipt["source_smoke"]["commit"] = "f" * 40
        self.assertNotEqual(first, self.validate())

    def test_no_distribution_or_executables_from_synthetic_tests(self):
        self.assertEqual(list(self.receipt_path.parent.glob("*.exe")), [])


if __name__ == "__main__":
    unittest.main()
