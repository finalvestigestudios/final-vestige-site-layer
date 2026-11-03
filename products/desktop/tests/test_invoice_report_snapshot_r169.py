"""R169: report-level Invoice Twin candidate IDs must use real owned evidence.

Synthetic direct API adversaries only. No files, license state, customers,
fraud/compliance decisions, telemetry or production outputs are involved.
"""
from __future__ import annotations

from copy import deepcopy
import re
import unittest

from fvs_suite.invoice_provenance import attach_invoice_provenance

SHA = "a" * 64
OTHER_SHA = "b" * 64


def record(a="2", b="3", status="exact_invoice_key"):
    return {"row_a": a, "row_b": b, "status": status,
            "vendor": "private synthetic vendor", "amount_a": "12.00",
            "review_flags": "human_review_only"}


class StringSubclass(str):
    pass


class IdentityAlias(str):
    def __new__(cls, text, claimed):
        obj = super().__new__(cls, text)
        obj.claimed = claimed
        return obj

    def __hash__(self):
        return hash(self.claimed)

    def __eq__(self, other):
        return str(other) == self.claimed


class ForgedMapping(dict):
    def get(self, field, default=None):
        return {"row_a": "2", "row_b": "3",
                "status": "exact_invoice_key"}.get(field, default)

    def keys(self):
        raise AssertionError("Untrusted keys hook executed")

    def items(self):
        raise AssertionError("Untrusted items hook executed")

    def __iter__(self):
        raise AssertionError("Untrusted iteration hook executed")

    def __getitem__(self, field):
        raise AssertionError("Untrusted getitem hook executed")


class DeceptiveList(list):
    def __iter__(self):
        raise AssertionError("Untrusted list iterator executed")

    def __len__(self):
        raise AssertionError("Untrusted list length executed")


class InvoiceReportSnapshotCustodyR169(unittest.TestCase):
    def attach(self, rows=None, *, sha=SHA):
        return attach_invoice_provenance([record()] if rows is None else rows,
                                         source_sha256=sha)

    def reject(self, rows, message):
        with self.assertRaisesRegex(ValueError, message):
            self.attach(rows)

    def test_exact_candidate_id_stable(self):
        self.assertEqual(self.attach(), self.attach())
        self.assertRegex(self.attach()[0]["candidate_ref"], r"\\A[0-9a-f]{64}\\Z")

    def test_near_candidate_id_stable(self):
        row = record(status="review_possible_duplicate")
        self.assertEqual(self.attach([row]), self.attach([deepcopy(row)]))

    def test_pair_orientation_changes_reference(self):
        first = self.attach()[0]["candidate_ref"]
        reverse = self.attach([record("3", "2")])[0]["candidate_ref"]
        self.assertNotEqual(first, reverse)

    def test_digest_changes_reference(self):
        self.assertNotEqual(self.attach()[0]["candidate_ref"],
                            self.attach(sha=OTHER_SHA)[0]["candidate_ref"])

    def test_reject_digest_str_subclass(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.attach(sha=StringSubclass(SHA))

    def test_reject_digest_equality_alias(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.attach(sha=IdentityAlias(SHA, OTHER_SHA))

    def test_reject_list_subclass_hooks(self):
        self.reject(DeceptiveList([record()]), "report must be a list")

    def test_reject_row_a_subclass(self):
        self.reject([record(a=StringSubclass("2"))], "physical CSV rows")

    def test_reject_row_b_subclass(self):
        self.reject([record(b=StringSubclass("3"))], "physical CSV rows")

    def test_reject_row_a_equality_alias(self):
        self.reject([record(a=IdentityAlias("2", "3"))], "physical CSV rows")

    def test_reject_row_b_equality_alias(self):
        self.reject([record(b=IdentityAlias("3", "2"))], "physical CSV rows")

    def test_reject_status_subclass(self):
        self.reject([record(status=StringSubclass("exact_invoice_key"))],
                    "classification")

    def test_reject_status_equality_alias(self):
        self.reject([record(status=IdentityAlias("notapproved", "exact_invoice_key"))],
                    "classification")

    def test_reject_extra_subclass_field_name(self):
        row = record()
        row[StringSubclass("extra")] = "private"
        self.reject([row], "field names must be plain text")

    def test_reject_row_a_field_name_alias(self):
        row = record()
        del row["row_a"]
        row[IdentityAlias("hidden", "row_a")] = "2"
        self.reject([row], "field names must be plain text")

    def test_native_storage_ignores_forged_getter(self):
        row = ForgedMapping(record("2", "4"))
        result = self.attach([row])[0]
        self.assertEqual((result["row_a"], result["row_b"]), ("2", "4"))
        self.assertEqual(result["candidate_ref"],
                         self.attach([record("2", "4")])[0]["candidate_ref"])

    def test_native_storage_ignores_forged_items_and_iteration(self):
        row = ForgedMapping(record())
        result = self.attach([row])[0]
        self.assertEqual(result["status"], "exact_invoice_key")
        self.assertEqual(result["candidate_ref"], self.attach()[0]["candidate_ref"])

    def test_reject_invalid_stored_row_despite_forged_getter(self):
        self.reject([ForgedMapping(record(a="1"))], "physical CSV rows")

    def test_reject_invalid_stored_status_despite_forged_getter(self):
        self.reject([ForgedMapping(record(status="approved"))], "classification")

    def test_reject_same_stored_row_despite_forged_getter(self):
        self.reject([ForgedMapping(record(a="3", b="3"))], "distinct")

    def test_reject_reverse_duplicate_without_returning_partial(self):
        self.reject([record(), record("3", "2")], "Duplicate invoice candidate")

    def test_reject_late_invalid_without_returning_partial(self):
        self.reject([record(), record("4", "5"), record("1", "9")],
                    "physical CSV rows")

    def test_input_rows_are_not_mutated(self):
        source = [record()]
        before = deepcopy(source)
        self.attach(source)
        self.assertEqual(source, before)
        self.assertNotIn("candidate_ref", source[0])

    def test_return_values_are_snapshot_owned(self):
        source = [record()]
        out = self.attach(source)[0]
        source[0]["row_a"] = "999"
        source[0]["vendor"] = "changed after call"
        self.assertEqual((out["row_a"], out["vendor"]),
                         ("2", "private synthetic vendor"))

    def test_existing_untrusted_reference_fields_overwritten(self):
        row = record()
        row.update({"source_sha256": OTHER_SHA, "candidate_ref": "FORGED"})
        out = self.attach([row])[0]
        self.assertEqual(out["source_sha256"], SHA)
        self.assertNotEqual(out["candidate_ref"], "FORGED")

    def test_private_field_name_never_echoed_in_error(self):
        secret = "PRIVATE_CUSTOMER_ACCOUNT_9075"
        row = record()
        row[StringSubclass(secret)] = "internal"
        with self.assertRaises(ValueError) as caught:
            self.attach([row])
        self.assertNotIn(secret, str(caught.exception))

    def test_empty_report_still_checks_digest(self):
        self.assertEqual(self.attach([]), [])
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.attach([], sha="not-a-sha")

    def test_opaque_review_columns_preserved(self):
        row = record()
        row["review_flags"] = "manual_review"
        row["amount_a"] = "0.005"
        out = self.attach([row])[0]
        self.assertEqual((out["review_flags"], out["amount_a"]),
                         ("manual_review", "0.005"))
        self.assertEqual(row["amount_a"], "0.005")


if __name__ == "__main__":
    unittest.main()
