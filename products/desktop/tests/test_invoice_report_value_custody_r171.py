"""R171: Invoice Twin report provenance owns only immutable plain-text display evidence.

Synthetic direct-API inputs; no customer content, network activity, telemetry
or automated payment/compliance decisions.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal
import unittest

from fvs_suite.invoice_provenance import attach_invoice_provenance

SHA = "a" * 64
OTHER_SHA = "b" * 64
MESSAGE = "Invoice candidate display values must be plain text"


def row():
    return {
        "row_a": "2", "row_b": "3", "status": "exact_invoice_key",
        "vendor": "SYNTHETIC VENDOR", "amount_a": "12.00",
        "amount_b": "12.00", "review_flags": "human_review_only",
    }


def attach(rows, sha=SHA):
    return attach_invoice_provenance(rows, source_sha256=sha)


class DangerousValue:
    def __str__(self):
        raise AssertionError("untrusted __str__ must not execute")

    def __repr__(self):
        raise AssertionError("untrusted __repr__ must not execute")

    def __bool__(self):
        raise AssertionError("untrusted __bool__ must not execute")


class HostileString(str):
    def __str__(self):
        raise AssertionError("untrusted string subclass __str__ executed")

    def __eq__(self, other):
        raise AssertionError("untrusted string subclass __eq__ executed")


class FakeReportDict(dict):
    def get(self, key, default=None):
        return "SAFE"
    
    def items(self):
        raise AssertionError("untrusted dict subclass items() executed")


class InvoiceReportValueCustodyR171(unittest.TestCase):
    def reject(self, field, value):
        candidate = row()
        candidate[field] = value
        with self.assertRaisesRegex(ValueError, MESSAGE):
            attach([candidate])

    def test_reject_integer_display(self):
        self.reject("amount_a", 1200)

    def test_reject_decimal_display(self):
        self.reject("amount_b", Decimal("12.00"))

    def test_reject_float_display(self):
        self.reject("amount_a", 12.0)

    def test_reject_boolean_display(self):
        self.reject("review_flags", True)

    def test_reject_none_display(self):
        self.reject("vendor", None)

    def test_reject_bytes_display(self):
        self.reject("vendor", b"private")

    def test_reject_list_display(self):
        self.reject("vendor", ["private"])

    def test_reject_dict_display(self):
        self.reject("review_flags", {"private": "yes"})

    def test_reject_tuple_display(self):
        self.reject("review_flags", ("private",))

    def test_reject_set_display(self):
        self.reject("vendor", {"private"})

    def test_reject_object_display(self):
        self.reject("vendor", object())

    def test_reject_str_subclass_display(self):
        self.reject("vendor", HostileString("private"))

    def test_hostile_value_string_hooks_are_not_called(self):
        self.reject("vendor", DangerousValue())

    def test_hostile_string_equality_is_not_called(self):
        self.reject("amount_a", HostileString("12.00"))

    def test_mutable_nested_value_cannot_be_returned(self):
        mutable = ["private"]
        self.reject("notes", mutable)
        self.assertEqual(mutable, ["private"])

    def test_late_invalid_candidate_aborts_whole_report(self):
        valid = row()
        invalid = {**row(), "row_a": "4", "row_b": "5",
                   "review_flags": ["secret"]}
        with self.assertRaisesRegex(ValueError, MESSAGE):
            attach([valid, invalid])
        self.assertNotIn("candidate_ref", valid)

    def test_late_invalid_after_multiple_valid_candidates(self):
        candidates = [row(), {**row(), "row_a": "4", "row_b": "5"},
                      {**row(), "row_a": "6", "row_b": "7", "vendor": {}}]
        with self.assertRaisesRegex(ValueError, MESSAGE):
            attach(candidates)
        self.assertTrue(all("candidate_ref" not in r for r in candidates))

    def test_private_value_not_in_rejection_message(self):
        private = "CUSTOMER_PRIVATE_ACCT_51679"
        try:
            self.reject("notes", [private])
        except AssertionError:
            raise
        candidate = {**row(), "notes": [private]}
        with self.assertRaises(ValueError) as caught:
            attach([candidate])
        self.assertNotIn(private, str(caught.exception))
        self.assertNotIn("51679", str(caught.exception))

    def test_valid_display_text_preserved(self):
        original = row()
        self.assertEqual(attach([original])[0]["vendor"], original["vendor"])

    def test_custom_plain_text_column_preserved(self):
        original = {**row(), "review_notes": "manual follow-up required"}
        self.assertEqual(attach([original])[0]["review_notes"],
                         "manual follow-up required")

    def test_unicode_text_unchanged(self):
        original = {**row(), "vendor": "SYNTHÉTIQUE 合法 review",
                    "review_flags": "évidence\nline two"}
        out = attach([original])[0]
        self.assertEqual(out["vendor"], original["vendor"])
        self.assertEqual(out["review_flags"], original["review_flags"])

    def test_untrusted_reference_placeholders_are_overwritten(self):
        original = {**row(), "source_sha256": ["forged"], "candidate_ref": {"x": "y"}}
        out = attach([original])[0]
        self.assertEqual(out["source_sha256"], SHA)
        self.assertRegex(out["candidate_ref"], r"\A[0-9a-f]{64}\Z")
        self.assertNotEqual(out["candidate_ref"], original["candidate_ref"])

    def test_source_digest_still_binds_reference(self):
        self.assertNotEqual(attach([row()])[0]["candidate_ref"],
                            attach([row()], OTHER_SHA)[0]["candidate_ref"])

    def test_physical_row_error_contract_unchanged(self):
        original = {**row(), "row_a": 2}
        with self.assertRaisesRegex(ValueError, "physical CSV rows"):
            attach([original])

    def test_status_error_contract_unchanged(self):
        original = {**row(), "status": "approved"}
        with self.assertRaisesRegex(ValueError, "classification"):
            attach([original])

    def test_source_rows_not_mutated_by_valid_report(self):
        original = [row()]
        prior = deepcopy(original)
        result = attach(original)
        self.assertEqual(original, prior)
        self.assertIsNot(original[0], result[0])

    def test_malicious_dict_subclass_cannot_hide_bad_display_value(self):
        forged = FakeReportDict({**row(), "notes": DangerousValue()})
        with self.assertRaisesRegex(ValueError, MESSAGE):
            attach([forged])

    def test_normalized_result_uses_only_plain_strings(self):
        original = {**row(), "extra": "opaque review"}
        result = attach([original])[0]
        self.assertTrue(all(type(k) is str and type(v) is str
                            for k, v in result.items()))

    def test_text_columns_do_not_affect_stable_locator(self):
        one = attach([row()])[0]["candidate_ref"]
        changed = {**row(), "vendor": "DIFFERENT SYNTHETIC VENDOR",
                   "amount_a": "0.005", "review_flags": "different"}
        two = attach([changed])[0]["candidate_ref"]
        self.assertEqual(one, two)


if __name__ == "__main__":
    unittest.main()
