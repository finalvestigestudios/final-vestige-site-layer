"""R273 tests of the *actual* private candidate runner's source receipt gate.

All content is synthetic. Tests do not build, sign, distribute, or test Windows EXEs.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / "scripts" / "offline_windows_candidate_r269.py"
spec = importlib.util.spec_from_file_location("r273_candidate", RUNNER)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
from test_offline_windows_candidate_r270 import source_receipt


class SourceReceiptIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.report = Path(self.temp.name) / "source-suite-evidence.json"
        self.valid = json.dumps(source_receipt(), sort_keys=True).encode("utf-8")

    def reject(self, changed):
        self.report.write_bytes(changed)
        with self.assertRaises(candidate.CandidateBuildRejected) as caught:
            candidate._source_receipt_sha256(self.report)
        self.assertEqual(str(caught.exception), candidate.ERROR)
        self.assertIsNone(caught.exception.__cause__)

    def test_existing_receipt_schema_remains_accepted(self):
        self.report.write_bytes(self.valid)
        self.assertRegex(candidate._source_receipt_sha256(self.report), r"^[0-9a-f]{64}$")

    def test_reject_duplicate_root_release_flag_where_last_value_wins(self):
        self.reject(b'{"released":true,' + self.valid[1:])

    def test_reject_duplicate_provenance_test_count(self):
        token = b'"test_count": 18'
        self.assertIn(token, self.valid)
        self.reject(self.valid.replace(token, b'"test_count": 1, "test_count": 18', 1))

    def test_reject_duplicate_nested_app_success(self):
        token = b'"result": "PASS"'
        self.assertIn(token, self.valid)
        self.reject(self.valid.replace(token, b'"result": "FAIL", "result": "PASS"', 1))

    def test_reject_escaped_equivalent_release_flag(self):
        token = b'"released": false'
        self.assertIn(token, self.valid)
        self.reject(self.valid.replace(token,
                    b'"released": true, "rele\\u0061sed": false', 1))

    def test_reject_nonstandard_nan_in_ignored_smoke_count(self):
        token = b'"synthetic_output_count": 1'
        self.assertIn(token, self.valid)
        self.reject(self.valid.replace(token, b'"synthetic_output_count": NaN', 1))

    def test_reject_private_error_content_without_disclosure(self):
        secret = b'C:/private/customer/payroll.csv'
        self.report.write_bytes(b'{"private":"' + secret + b'","private":null}')
        with self.assertRaises(candidate.CandidateBuildRejected) as caught:
            candidate._source_receipt_sha256(self.report)
        self.assertNotIn(secret.decode(), str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_isolated_cli_still_imports_trusted_decoder(self):
        with tempfile.TemporaryDirectory() as location:
            env = os.environ.copy()
            env["PYTHONPATH"] = location
            (Path(location) / "strict_source_receipt_r273.py").write_text(
                "raise RuntimeError('UNTRUSTED_RECEIPT_IMPORT')\n", encoding="ascii")
            for optimized in (False, True):
                with self.subTest(optimized=optimized):
                    command = [sys.executable, "-I"]
                    if optimized:
                        command.append("-OO")
                    result = subprocess.run(
                        [*command, str(RUNNER), "--help"], cwd=location, env=env,
                        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, check=False, timeout=30)
                    self.assertEqual(result.returncode, 0,
                                     "Private runner --help failed in isolated Python")
                    self.assertIn(b"--workspace", result.stdout)
                    self.assertNotIn(b"UNTRUSTED_RECEIPT_IMPORT", result.stderr)


if __name__ == "__main__":
    unittest.main()
