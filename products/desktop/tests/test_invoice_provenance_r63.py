"""R63 deterministic Invoice Twin Scout input/candidate audit references."""
from __future__ import annotations

from copy import deepcopy
import re
import unittest

from fvs_suite.invoice_provenance import attach_invoice_provenance

A = "a" * 64
B = "b" * 64


def example_rows():
    return [
        {"row_a": "2", "row_b": "5", "status": "exact_invoice_key",
         "vendor": "Local-A", "amount_a": "0.30", "amount_b": "0.30",
         "review_flags": "normalized_vendor_key_review"},
        {"row_a": "5", "row_b": "7", "status": "review_possible_duplicate",
         "vendor": "Local-B", "amount_a": "1234.50", "amount_b": "1234.50",
         "review_flags": ""},
    ]


class InvoiceProvenanceR63(unittest.TestCase):
    def attach(self, rows=None, sha=A):
        return attach_invoice_provenance(example_rows() if rows is None else rows,
                                         source_sha256=sha)

    def test_digest_and_ids_are_present_for_every_candidate(self):
        rows = self.attach()
        self.assertEqual([r["source_sha256"] for r in rows], [A, A])
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{64}", r["candidate_ref"]) for r in rows))
        self.assertNotEqual(rows[0]["candidate_ref"], rows[1]["candidate_ref"])

    def test_same_source_and_rows_are_deterministic(self):
        self.assertEqual(self.attach(), self.attach())

    def test_raw_source_change_changes_candidate_identity(self):
        original, changed = self.attach(), self.attach(sha=B)
        self.assertNotEqual(original[0]["candidate_ref"], changed[0]["candidate_ref"])

    def test_source_row_change_changes_candidate_identity(self):
        changed = example_rows()
        changed[0]["row_b"] = "6"
        self.assertNotEqual(self.attach()[0]["candidate_ref"],
                            self.attach(changed)[0]["candidate_ref"])

    def test_pair_order_change_changes_reference(self):
        changed = example_rows()
        changed[0]["row_a"], changed[0]["row_b"] = "5", "2"
        self.assertNotEqual(self.attach()[0]["candidate_ref"],
                            self.attach(changed)[0]["candidate_ref"])

    def test_review_classification_changes_reference(self):
        changed = example_rows()
        changed[0]["status"] = "review_possible_duplicate"
        self.assertNotEqual(self.attach()[0]["candidate_ref"],
                            self.attach(changed)[0]["candidate_ref"])

    def test_copy_not_mutation(self):
        rows = example_rows()
        before = deepcopy(rows)
        result = self.attach(rows)
        self.assertEqual(rows, before)
        self.assertIsNot(result, rows)
        for a, b in zip(rows, result):
            self.assertIsNot(a, b)
            self.assertEqual({k: b[k] for k in a}, a)

    def test_existing_money_and_review_labels_unchanged(self):
        rows = self.attach()
        self.assertEqual(rows[0]["amount_a"], "0.30")
        self.assertEqual(rows[0]["review_flags"], "normalized_vendor_key_review")
        self.assertEqual(rows[1]["amount_b"], "1234.50")

    def test_original_untrusted_evidence_columns_are_replaced(self):
        rows = example_rows()
        rows[0]["source_sha256"] = B
        rows[0]["candidate_ref"] = "FAKE"
        fixed = self.attach(rows)[0]
        self.assertEqual(fixed["source_sha256"], A)
        self.assertNotEqual(fixed["candidate_ref"], "FAKE")

    def test_no_customer_identifier_embedded_in_candidate_reference(self):
        row = {"row_a": "2", "row_b": "3", "status": "exact_invoice_key",
               "vendor": "private-client-789", "invoice_a": "invoice-secret"}
        out = self.attach([row])[0]
        self.assertNotIn("client", out["candidate_ref"])
        self.assertNotIn("invoice", out["candidate_ref"])

    def test_empty_report_validates_input_but_creates_no_fake_candidate(self):
        self.assertEqual(self.attach([]), [])
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.attach([], sha="invalid")

    def test_invalid_fingerprints_fail_closed(self):
        for bad in (None, False, 0, [], {}, b"a" * 64, "", "a" * 63,
                    "a" * 65, "A" * 64, "g" * 64, A + "\n", " " + A,
                    "a" * 63 + "é", "a" * 63 + "\x00"):
            with self.subTest(bad=repr(bad)), self.assertRaisesRegex(ValueError, "SHA-256"):
                self.attach(sha=bad)

    def test_missing_digest_keyword_argument_is_error(self):
        with self.assertRaises(TypeError):
            attach_invoice_provenance(example_rows())

    def test_invalid_physical_row_rejected(self):
        for bad in (None, False, 0, 2, "", "0", "1", "-2", "+2", "02", " 2",
                    "2\n", "2.5", "２", "²", [], {}, "42\x00"):
            for name in ("row_a", "row_b"):
                with self.subTest(bad=repr(bad), field=name):
                    rows = example_rows()
                    rows[0][name] = bad
                    with self.assertRaisesRegex(ValueError, "physical CSV rows"):
                        self.attach(rows)

    def test_same_row_not_a_pair(self):
        rows = example_rows()
        rows[0]["row_b"] = "2"
        with self.assertRaisesRegex(ValueError, "distinct"):
            self.attach(rows)

    def test_unknown_status_cannot_be_evidence(self):
        for tag in ("approved", "fraud_detected", "matched", "", None, 1, [], {}):
            rows = example_rows()
            rows[0]["status"] = tag
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, "classification"):
                self.attach(rows)

    def test_missing_fields_rejected(self):
        for missing in ("row_a", "row_b", "status"):
            rows = example_rows()
            del rows[0][missing]
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                self.attach(rows)

    def test_bad_report_type_rejected(self):
        with self.assertRaisesRegex(ValueError, "report record"):
            self.attach(["not a report row"])

    def test_duplicate_pair_rejected_without_partial_return(self):
        rows = example_rows()
        rows.append(deepcopy(rows[0]))
        with self.assertRaisesRegex(ValueError, "Duplicate invoice candidate"):
            self.attach(rows)

    def test_distinct_status_same_row_pair_is_rejected(self):
        # R170: competing classifications of the identical pair fail closed.
        rows = example_rows()
        rows[1]["row_a"], rows[1]["row_b"] = "2", "5"
        with self.assertRaisesRegex(ValueError, "Duplicate invoice candidate"):
            self.attach(rows)

    def test_identifier_changes_only_for_auditable_tuple_not_display_text(self):
        rows = example_rows()
        rows[0]["vendor"] = "very-different-vendor-label"
        rows[0]["amount_a"] = "9.99"
        self.assertEqual(self.attach()[0]["candidate_ref"],
                         self.attach(rows)[0]["candidate_ref"])
        # The source digest *must* change when source bytes change in engine.


if __name__ == "__main__":
    unittest.main()
