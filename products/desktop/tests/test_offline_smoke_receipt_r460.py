"""R460: source-only fallback rejects fabricated or contradictory R408 receipts."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import offline_regression_gate_r459 as gate
from offline_smoke_receipt_r460 import (
    EXPECTED_APPS, MAX_RECEIPT_BYTES, SourceSmokeReceiptError,
    require_six_app_smokes,
)


class SourceSmokeReceiptR460(unittest.TestCase):
    def receipt(self):
        return {
            "schema": "fvs-source-smoke-r408-v1",
            "source_sha256": "a" * 64,
            "evidence": "SOURCE_ONLY_NOT_WINDOWS_BINARY",
            "tests": [
                {"app": app, "normal": "pass", "optimized": "pass"}
                for app in EXPECTED_APPS
            ],
            "passed": 12, "required": 12, "release_authorized": False,
        }

    def encode(self, item):
        return json.dumps(item, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def rejects(self, item):
        with self.assertRaises(SourceSmokeReceiptError):
            require_six_app_smokes(self.encode(item))

    def test_exact_six_apps_in_two_modes_pass(self):
        self.assertEqual(require_six_app_smokes(self.encode(self.receipt())), 12)

    def test_zero_statuses_cannot_be_hidden_by_zero_process_exit(self):
        item = self.receipt()
        item["tests"] = []
        self.rejects(item)

    def test_claimed_twelve_with_a_failed_app_rejected(self):
        item = self.receipt()
        item["tests"][4]["optimized"] = "fail"
        self.rejects(item)

    def test_claimed_twelve_with_skipped_app_rejected(self):
        item = self.receipt()
        item["tests"][0]["normal"] = "skip"
        self.rejects(item)

    def test_wrong_app_or_order_rejected(self):
        for change in ("unknown", "ledger"):
            item = self.receipt()
            item["tests"][3]["app"] = change
            self.rejects(item)

    def test_missing_app_and_duplicate_app_rejected(self):
        item = self.receipt()
        item["tests"].pop()
        self.rejects(item)
        item = self.receipt()
        item["tests"].append(dict(item["tests"][0]))
        self.rejects(item)

    def test_forged_counts_and_boolean_numbers_rejected(self):
        for key, invalid in (("passed", 11), ("required", 0),
                             ("passed", True), ("required", True),
                             ("passed", "12")):
            item = self.receipt()
            item[key] = invalid
            self.rejects(item)

    def test_forged_release_flag_or_evidence_rejected(self):
        for key, invalid in (("release_authorized", True),
                             ("release_authorized", 0),
                             ("evidence", "WINDOWS_RELEASE"),
                             ("schema", "fvs-source-smoke-r408-v2")):
            item = self.receipt()
            item[key] = invalid
            self.rejects(item)

    def test_sha256_lowercase_64_hex_required(self):
        for invalid in ("", "a" * 63, "Z" * 64, "g" * 64, 0):
            item = self.receipt()
            item["source_sha256"] = invalid
            self.rejects(item)

    def test_extra_or_missing_fields_and_nested_fields_rejected(self):
        item = self.receipt()
        item["private_path"] = "SENSITIVE.csv"
        self.rejects(item)
        item = self.receipt()
        del item["tests"][0]["normal"]
        self.rejects(item)
        item = self.receipt()
        item["tests"][0]["private_path"] = "SENSITIVE.csv"
        self.rejects(item)

    def test_non_dict_nested_structures_rejected(self):
        item = self.receipt()
        item["tests"][0] = "ledger"
        self.rejects(item)
        item = self.receipt()
        item["tests"] = "pass" * 6
        self.rejects(item)

    def test_trailing_child_logs_and_invalid_json_rejected(self):
        for raw in (b"", b"not json", b"{}{}", b"[1,2,3]", b"{\xff}",
                    self.encode(self.receipt()) + b"\nSECRET_LOG"):
            with self.subTest(raw=raw[:14]):
                with self.assertRaises(SourceSmokeReceiptError):
                    require_six_app_smokes(raw)

    def test_bounded_receipt_never_parses_unbounded_stdout(self):
        with self.assertRaises(SourceSmokeReceiptError):
            require_six_app_smokes(b"x" * (MAX_RECEIPT_BYTES + 1))

    def test_wrong_payload_type_rejected(self):
        for raw in ("test", bytearray(b"{}"), None, 0):
            with self.subTest(kind=type(raw).__name__):
                with self.assertRaises(SourceSmokeReceiptError):
                    require_six_app_smokes(raw)

    def test_parent_runs_actual_receipt_validation_before_success(self):
        raw = self.encode(self.receipt())
        def child(command, **kwargs):
            self.assertNotEqual(kwargs['stdout'], gate.subprocess.DEVNULL)
            self.assertEqual(kwargs['stderr'], gate.subprocess.DEVNULL)
            kwargs['stdout'].write(raw)
            return SimpleNamespace(returncode=0)
        with patch.object(gate.subprocess, 'run', side_effect=child):
            self.assertEqual(gate._run_smokes(Path('/synthetic')), 12)

    def test_parent_refuses_zero_exit_contradictory_receipt(self):
        item = self.receipt()
        item['tests'][5]['normal'] = 'fail'
        raw = self.encode(item)
        def child(command, **kwargs):
            kwargs['stdout'].write(raw)
            return SimpleNamespace(returncode=0)
        with patch.object(gate.subprocess, 'run', side_effect=child):
            with self.assertRaises(gate.LocalGateError):
                gate._run_smokes(Path('/synthetic'))

    def test_parent_refuses_zero_exit_missing_receipt(self):
        with patch.object(gate.subprocess, 'run', return_value=SimpleNamespace(returncode=0)):
            with self.assertRaises(gate.LocalGateError):
                gate._run_smokes(Path('/synthetic'))

    def test_parent_refuses_nonzero_exit_even_with_good_receipt(self):
        def child(command, **kwargs):
            kwargs['stdout'].write(self.encode(self.receipt()))
            return SimpleNamespace(returncode=1)
        with patch.object(gate.subprocess, 'run', side_effect=child):
            with self.assertRaises(gate.LocalGateError):
                gate._run_smokes(Path('/synthetic'))

    def test_fixed_private_safe_error_text(self):
        item = self.receipt()
        item["private_path"] = "CLIENT_PROTECTED_FILENAME_789.csv"
        with self.assertRaises(SourceSmokeReceiptError) as failure:
            require_six_app_smokes(self.encode(item))
        self.assertNotIn("CLIENT_PROTECTED", str(failure.exception))


if __name__ == "__main__":
    unittest.main()
