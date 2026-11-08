"""R276 receipt-contract regressions; synthetic data, never native EXE QA."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "source_smoke_receipt_r276.py"
spec = importlib.util.spec_from_file_location("source_smoke_receipt_r276", MODULE)
receipt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receipt)


def fixture():
    return [{"app": name, "engine": engine, "result": "PASS",
             "synthetic_output_count": index + 1}
            for index, (name, engine) in enumerate(receipt.EXPECTED)]


class SmokeReceiptContractTests(unittest.TestCase):
    def setUp(self):
        self.records = fixture()

    def rejected(self):
        self.assertFalse(receipt.valid_source_smoke_records(self.records))

    def test_all_six_canonical_records_pass(self):
        self.assertTrue(receipt.valid_source_smoke_records(self.records))

    def test_max_count_is_valid(self):
        self.records[0]["synthetic_output_count"] = receipt.MAX_SYNTHETIC_OUTPUTS
        self.assertTrue(receipt.valid_source_smoke_records(self.records))

    def test_missing_engine_rejected(self):
        self.records[0].pop("engine")
        self.rejected()

    def test_incorrect_engine_rejected(self):
        self.records[0]["engine"] = "procurement"
        self.rejected()

    def test_wrong_engine_each_app_rejected(self):
        for n in range(6):
            with self.subTest(n=n):
                records = fixture()
                records[n]["engine"] = records[(n + 1) % 6]["engine"]
                self.assertFalse(receipt.valid_source_smoke_records(records))

    def test_wrong_app_each_record_rejected(self):
        for n in range(6):
            with self.subTest(n=n):
                records = fixture()
                records[n]["app"] = records[(n + 1) % 6]["app"]
                self.assertFalse(receipt.valid_source_smoke_records(records))

    def test_duplicate_app_rejected(self):
        self.records[1] = copy.deepcopy(self.records[0])
        self.rejected()

    def test_out_of_order_rejected(self):
        self.records.reverse()
        self.rejected()

    def test_missing_record_rejected(self):
        self.records.pop()
        self.rejected()

    def test_extra_record_rejected(self):
        self.records.append(copy.deepcopy(self.records[0]))
        self.rejected()

    def test_missing_result_rejected(self):
        self.records[0].pop("result")
        self.rejected()

    def test_false_success_rejected(self):
        self.records[0]["result"] = True
        self.rejected()

    def test_failed_result_rejected(self):
        self.records[0]["result"] = "FAIL"
        self.rejected()

    def test_extra_private_field_rejected(self):
        self.records[0]["path"] = "C:/private/payroll.csv"
        self.rejected()

    def test_count_boolean_rejected(self):
        self.records[0]["synthetic_output_count"] = True
        self.rejected()

    def test_count_zero_rejected(self):
        self.records[0]["synthetic_output_count"] = 0
        self.rejected()

    def test_count_negative_rejected(self):
        self.records[0]["synthetic_output_count"] = -1
        self.rejected()

    def test_count_above_limit_rejected(self):
        self.records[0]["synthetic_output_count"] = receipt.MAX_SYNTHETIC_OUTPUTS + 1
        self.rejected()

    def test_count_fractional_rejected(self):
        self.records[0]["synthetic_output_count"] = 1.0
        self.rejected()

    def test_count_string_rejected(self):
        self.records[0]["synthetic_output_count"] = "1"
        self.rejected()

    def test_record_subclass_rejected(self):
        class Forged(dict):
            pass
        self.records[0] = Forged(self.records[0])
        self.rejected()

    def test_list_subclass_rejected(self):
        class Forged(list):
            pass
        self.records = Forged(self.records)
        self.rejected()

    def test_wrong_container_rejected(self):
        self.records = None
        self.rejected()

    def test_nested_private_object_count_rejected(self):
        self.records[0]["synthetic_output_count"] = {"private": "C:/private/payroll.csv"}
        self.rejected()

    def test_no_exception_message_reflects_private_fields(self):
        self.records[0]["path"] = "C:/private/payroll.csv"
        self.assertFalse(receipt.valid_source_smoke_records(self.records))


if __name__ == "__main__":
    unittest.main()
