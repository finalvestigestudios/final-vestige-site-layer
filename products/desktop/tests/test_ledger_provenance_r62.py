"""R62 LedgerDiff input-snapshot identity checks: offline synthetic records."""
from __future__ import annotations

import unittest
from copy import deepcopy

from fvs_suite.ledger_provenance import (
    IDENTICAL_INPUT_REVIEW, attach_ledger_provenance,
)

A = "a" * 64
B = "b" * 64


def base_rows():
    return [
        {"id": "T1", "status": "matched", "left_amount": "0.30", "right_amount": "0.30",
         "difference": "0.00", "left_rows": "2;4", "right_rows": "3", "left_ids": "T1", "right_ids": "t1"},
        {"id": "T2", "status": "variance", "left_amount": "1.01", "right_amount": "1.00",
         "difference": "0.01", "left_rows": "5", "right_rows": "6", "left_ids": "T2", "right_ids": "T2"},
    ]


class LedgerSourceProvenanceR62(unittest.TestCase):
    def test_two_independent_snapshot_digests_propagate_to_every_row(self):
        rows = attach_ledger_provenance(base_rows(), left_sha256=A, right_sha256=B)
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["left_source_sha256"] for r in rows}, {A})
        self.assertEqual({r["right_source_sha256"] for r in rows}, {B})
        self.assertTrue(all(r["input_identity_review"] == "" for r in rows))

    def test_identical_bytes_trigger_explicit_review_even_when_matched(self):
        rows = attach_ledger_provenance(base_rows(), left_sha256=A, right_sha256=A)
        self.assertTrue(all(r["input_identity_review"] == IDENTICAL_INPUT_REVIEW
                            for r in rows))
        self.assertEqual(rows[0]["status"], "matched")

    def test_identical_bytes_still_preserve_independent_variance(self):
        rows = attach_ledger_provenance(base_rows(), left_sha256=B, right_sha256=B)
        self.assertEqual(rows[1]["status"], "variance")
        self.assertEqual(rows[1]["difference"], "0.01")
        self.assertEqual(rows[1]["input_identity_review"], IDENTICAL_INPUT_REVIEW)

    def test_report_rows_never_mutated(self):
        initial = base_rows()
        saved = deepcopy(initial)
        report = attach_ledger_provenance(initial, left_sha256=A, right_sha256=B)
        self.assertEqual(initial, saved)
        self.assertIsNot(report, initial)
        self.assertTrue(all(new is not old for new, old in zip(report, initial)))

    def test_normalized_matching_and_money_are_not_recomputed(self):
        before = base_rows()
        after = attach_ledger_provenance(before, left_sha256=A, right_sha256=B)
        for original, new in zip(before, after):
            self.assertEqual({k: new[k] for k in original}, original)

    def test_swapping_input_order_swaps_digests(self):
        first = attach_ledger_provenance(base_rows(), left_sha256=A, right_sha256=B)
        second = attach_ledger_provenance(base_rows(), left_sha256=B, right_sha256=A)
        self.assertEqual(first[0]["left_source_sha256"], second[0]["right_source_sha256"])
        self.assertEqual(first[0]["right_source_sha256"], second[0]["left_source_sha256"])

    def test_different_digests_with_equal_parsed_totals_not_flagged(self):
        self.assertEqual(attach_ledger_provenance(
            base_rows(), left_sha256=A, right_sha256=B)[0]["input_identity_review"], "")

    def test_empty_report_still_validates_digests(self):
        self.assertEqual(attach_ledger_provenance([], left_sha256=A, right_sha256=B), [])
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            attach_ledger_provenance([], left_sha256="bad", right_sha256=B)

    def test_empty_report_same_hash_does_not_fabricate_rows(self):
        self.assertEqual(attach_ledger_provenance([], left_sha256=A, right_sha256=A), [])

    def test_invalid_left_digest_fails_closed(self):
        for candidate in (None, False, 1, b"a" * 64, [], {}, object(),
                          "", "a" * 63, "a" * 65, "A" * 64, "g" * 64,
                          "a" * 64 + "\n", " " + "a" * 64, "a" * 63 + "é"):
            with self.subTest(candidate=repr(candidate)), self.assertRaisesRegex(ValueError, "SHA-256"):
                attach_ledger_provenance(base_rows(), left_sha256=candidate, right_sha256=B)

    def test_invalid_right_digest_fails_closed(self):
        for candidate in (None, b"b" * 64, "B" * 64, "b" * 63, "b" * 65,
                          "b" * 63 + "0\x00", " " + "b" * 63):
            with self.subTest(candidate=repr(candidate)), self.assertRaisesRegex(ValueError, "SHA-256"):
                attach_ledger_provenance(base_rows(), left_sha256=A, right_sha256=candidate)

    def test_required_hash_cannot_be_omitted(self):
        with self.assertRaises(TypeError):
            attach_ledger_provenance(base_rows(), left_sha256=A)

    def test_determinism_with_repeated_calls(self):
        self.assertEqual(attach_ledger_provenance(base_rows(), left_sha256=A, right_sha256=B),
                         attach_ledger_provenance(base_rows(), left_sha256=A, right_sha256=B))

    def test_non_hex_sensitive_values_never_enter_digests(self):
        row = {"id": "private-client-123", "status": "variance", "difference": "17.42"}
        result = attach_ledger_provenance([row], left_sha256=A, right_sha256=B)[0]
        self.assertNotIn("client", result["left_source_sha256"] + result["right_source_sha256"])
        self.assertEqual(result["id"], row["id"])

    def test_prior_provenance_keys_are_replaced_not_trusted(self):
        rows = [{"id": "X", "left_source_sha256": B,
                 "right_source_sha256": A, "input_identity_review": "forged"}]
        fixed = attach_ledger_provenance(rows, left_sha256=A, right_sha256=A)[0]
        self.assertEqual(fixed["left_source_sha256"], A)
        self.assertEqual(fixed["right_source_sha256"], A)
        self.assertEqual(fixed["input_identity_review"], IDENTICAL_INPUT_REVIEW)


if __name__ == "__main__":
    unittest.main()
