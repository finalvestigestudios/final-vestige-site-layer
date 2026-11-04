"""R175: synthetic LedgerDiff direct-report primitive / source-identity custody."""
from __future__ import annotations

from decimal import Decimal
import unittest

from fvs_suite.ledger_provenance import (
    IDENTICAL_INPUT_REVIEW, attach_ledger_provenance,
)

A = "a" * 64
B = "b" * 64
PRIVATE = "private-client-abc-123"


def row():
    return {"id": "T1", "status": "variance", "left_amount": "1.01",
            "right_amount": "1.00", "difference": "0.01",
            "left_rows": "2", "right_rows": "3"}


def bind(records=None, left=A, right=B):
    return attach_ledger_provenance([row()] if records is None else records,
                                    left_sha256=left, right_sha256=right)


class LyingString(str):
    def __str__(self):
        raise AssertionError("unsafe string conversion invoked")

    def __eq__(self, other):
        raise AssertionError("unsafe string comparison invoked")

    def __hash__(self):
        raise AssertionError("unsafe string hashing invoked")


class LyingDict(dict):
    def get(self, key, default=None):
        return "FORGED"

    def keys(self):
        raise AssertionError("untrusted keys invoked")

    def items(self):
        raise AssertionError("untrusted items invoked")

    def __iter__(self):
        raise AssertionError("untrusted row iteration invoked")

    def __getitem__(self, name):
        raise AssertionError("untrusted row indexing invoked")


class LyingList(list):
    def __len__(self):
        raise AssertionError("untrusted list length invoked")

    def __iter__(self):
        raise AssertionError("untrusted list iteration invoked")


class InsertableLyingKey(str):
    __hash__ = str.__hash__

    def __eq__(self, other):
        raise AssertionError("untrusted key comparison invoked")


class LedgerReportCustodyR175(unittest.TestCase):
    def reject(self, records, fragment, left=A, right=B):
        with self.assertRaises(ValueError) as caught:
            bind(records, left, right)
        self.assertIn(fragment, str(caught.exception))
        self.assertNotIn(PRIVATE, str(caught.exception))

    def test_original_cents_and_row_refs_preserved(self):
        result = bind()[0]
        self.assertEqual(result["left_amount"], "1.01")
        self.assertEqual(result["right_amount"], "1.00")
        self.assertEqual(result["difference"], "0.01")
        self.assertEqual(result["left_rows"], "2")
        self.assertEqual(result["right_rows"], "3")

    def test_distinct_digest_values_bound_to_report(self):
        result = bind()[0]
        self.assertEqual((result["left_source_sha256"], result["right_source_sha256"]), (A, B))
        self.assertEqual(result["input_identity_review"], "")

    def test_identical_digest_requires_human_review(self):
        self.assertEqual(bind(left=A, right=A)[0]["input_identity_review"],
                         IDENTICAL_INPUT_REVIEW)

    def test_empty_report_stays_empty(self):
        self.assertEqual(bind([]), [])

    def test_empty_report_still_rejects_bad_digest(self):
        self.reject([], "SHA-256", left="bad")

    def test_preexisting_digest_columns_are_overwritten(self):
        candidate = {**row(), "left_source_sha256": B,
                     "right_source_sha256": A, "input_identity_review": "forged"}
        result = bind([candidate], left=A, right=A)[0]
        self.assertEqual(result["left_source_sha256"], A)
        self.assertEqual(result["right_source_sha256"], A)
        self.assertEqual(result["input_identity_review"], IDENTICAL_INPUT_REVIEW)

    def test_original_row_not_mutated(self):
        original = row()
        result = bind([original])[0]
        self.assertEqual(original, row())
        self.assertIsNot(result, original)

    def test_output_row_not_alias_to_input(self):
        original = row()
        result = bind([original])[0]
        original["difference"] = "9999.99"
        self.assertEqual(result["difference"], "0.01")

    def test_two_distinct_rows_preserve_order(self):
        records = [row(), {**row(), "id": "T2", "difference": "0.02"}]
        self.assertEqual([x["id"] for x in bind(records)], ["T1", "T2"])

    def test_repeat_call_is_deterministic(self):
        self.assertEqual(bind(), bind())

    def test_digest_subclass_left_rejected_before_equality(self):
        self.reject([], "SHA-256", left=LyingString(A))

    def test_digest_subclass_right_rejected_before_equality(self):
        self.reject([], "SHA-256", right=LyingString(A))

    def test_digest_uppercase_rejected(self):
        self.reject([], "SHA-256", left="A" * 64)

    def test_digest_newline_rejected(self):
        self.reject([], "SHA-256", right=B + "\n")

    def test_digest_non_string_rejected(self):
        self.reject([], "SHA-256", right=object())

    def test_row_collection_subclass_rejected_before_iteration(self):
        self.reject(LyingList([row()]), "plain list")

    def test_tuple_collection_rejected(self):
        self.reject((row(),), "plain list")

    def test_non_dict_row_rejected(self):
        self.reject([PRIVATE], "record")

    def test_forged_dict_methods_cannot_replace_amount(self):
        result = bind([LyingDict(row())])[0]
        self.assertEqual(result["difference"], "0.01")

    def test_forged_dict_methods_cannot_replace_rows(self):
        result = bind([LyingDict(row())])[0]
        self.assertEqual((result["left_rows"], result["right_rows"]), ("2", "3"))

    def test_subclass_key_rejected_before_hashing(self):
        forged = dict(row())
        # str subclasses are hashable via the base constructor, but must
        # never be admitted as report field identities.
        dict.__setitem__(forged, InsertableLyingKey("extra"), "x")
        self.reject([forged], "field names")

    def test_hostile_non_string_key_rejected_before_rehash(self):
        forged = dict(row())
        # Invalid numeric column keys must be rejected without coercion.
        forged[1] = "sensitive"
        self.reject([forged], "field names")

    def test_string_subclass_amount_rejected_before_str_hook(self):
        forged = row()
        forged["left_amount"] = LyingString(PRIVATE)
        self.reject([forged], "field values")

    def test_string_subclass_status_rejected(self):
        forged = row()
        forged["status"] = LyingString("matched")
        self.reject([forged], "field values")

    def test_nested_mutable_report_value_rejected(self):
        forged = row()
        forged["difference"] = [PRIVATE]
        self.reject([forged], "field values")

    def test_decimal_report_value_rejected_without_coercion(self):
        forged = row()
        forged["difference"] = Decimal("0.01")
        self.reject([forged], "field values")

    def test_integer_report_value_rejected(self):
        forged = row()
        forged["left_rows"] = 2
        self.reject([forged], "field values")

    def test_bool_report_value_rejected(self):
        forged = row()
        forged["left_rows"] = True
        self.reject([forged], "field values")

    def test_untrusted_prior_digest_value_rejected_not_stringified(self):
        forged = row()
        forged["left_source_sha256"] = {"key": PRIVATE}
        self.reject([forged], "field values")

    def test_private_text_not_leaked_in_validation_errors(self):
        forged = row()
        forged["id"] = [PRIVATE]
        self.reject([forged], "field values")

    def test_no_compliance_determination_added(self):
        result = bind()[0]
        self.assertEqual(result["status"], "variance")
        self.assertNotIn("approved", result)

    def test_unicode_plain_text_preserved(self):
        forged = row()
        forged["id"] = "Référence-α"
        self.assertEqual(bind([forged])[0]["id"], "Référence-α")


if __name__ == "__main__":
    unittest.main()
