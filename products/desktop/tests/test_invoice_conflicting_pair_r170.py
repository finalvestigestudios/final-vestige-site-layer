"""R170: one source-pair cannot receive two contradictory invoice findings.

All values are synthetic. A candidate ID is a locator for human review, not
authorization, a signature, fraud proof, or evidence of genuine invoices.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from fvs_suite.invoice_provenance import attach_invoice_provenance

SHA = "a" * 64
SECOND_SHA = "b" * 64
EXACT = "exact_invoice_key"
NEAR = "review_possible_duplicate"


def row(a="2", b="3", status=EXACT):
    return {"row_a": a, "row_b": b, "status": status,
            "vendor": "SYNTHETIC PRIVATE VENDOR",
            "amount_a": "12.00", "amount_b": "12.00",
            "review_flags": "requires_human_review"}


def refs(rows, sha=SHA):
    return attach_invoice_provenance(rows, source_sha256=sha)


class ForgedGet(dict):
    def get(self, key, default=None):
        if key == "status":
            return EXACT
        return super().get(key, default)

    def keys(self):
        raise AssertionError("untrusted keys() invoked")

    def items(self):
        raise AssertionError("untrusted items() invoked")


class InvoiceConflictingPairR170(unittest.TestCase):
    def reject(self, records):
        with self.assertRaisesRegex(ValueError, "Duplicate invoice candidate pair"):
            refs(records)

    def test_conflicting_same_orientation_exact_first(self):
        self.reject([row(status=EXACT), row(status=NEAR)])

    def test_conflicting_same_orientation_near_first(self):
        self.reject([row(status=NEAR), row(status=EXACT)])

    def test_conflicting_reverse_orientation_exact_first(self):
        self.reject([row(status=EXACT), row("3", "2", NEAR)])

    def test_conflicting_reverse_orientation_near_first(self):
        self.reject([row(status=NEAR), row("3", "2", EXACT)])

    def test_identical_status_same_direction_still_rejected(self):
        self.reject([row(), row()])

    def test_identical_status_reverse_still_rejected(self):
        self.reject([row(), row("3", "2")])

    def test_near_only_duplicate_still_rejected(self):
        self.reject([row(status=NEAR), row(status=NEAR)])

    def test_conflict_after_other_distinct_pairs(self):
        self.reject([row(), row("4", "5", NEAR),
                     row("6", "7", EXACT), row("3", "2", NEAR)])

    def test_conflict_separated_by_other_status(self):
        self.reject([row(status=NEAR), row("4", "5", EXACT),
                     row("2", "3", EXACT)])

    def test_distinct_pairs_with_different_statuses_permitted(self):
        output = refs([row(), row("4", "5", NEAR)])
        self.assertEqual(len(output), 2)
        self.assertEqual([r["status"] for r in output], [EXACT, NEAR])

    def test_distinct_pairs_with_shared_one_source_row_permitted(self):
        output = refs([row("2", "3", EXACT), row("2", "4", NEAR),
                       row("3", "4", EXACT)])
        self.assertEqual(len(output), 3)

    def test_distinct_pairs_with_same_status_permitted(self):
        output = refs([row("2", "3", EXACT), row("5", "7", EXACT)])
        self.assertEqual(len(output), 2)
        self.assertNotEqual(output[0]["candidate_ref"], output[1]["candidate_ref"])

    def test_no_input_mutation_when_conflict_rejected(self):
        original = [row(), row("3", "2", NEAR)]
        before = deepcopy(original)
        self.reject(original)
        self.assertEqual(before, original)
        self.assertNotIn("candidate_ref", original[0])

    def test_no_input_mutation_on_valid_return(self):
        original = [row()]
        before = deepcopy(original)
        output = refs(original)
        self.assertEqual(original, before)
        self.assertNotEqual(id(original[0]), id(output[0]))

    def test_standalone_status_ref_remains_deterministic(self):
        self.assertEqual(refs([row()]), refs([deepcopy(row())]))
        self.assertEqual(refs([row(status=NEAR)]),
                         refs([deepcopy(row(status=NEAR))]))

    def test_standalone_statuses_have_distinct_refs(self):
        exact = refs([row()])[0]["candidate_ref"]
        near = refs([row(status=NEAR)])[0]["candidate_ref"]
        self.assertNotEqual(exact, near)

    def test_pair_order_does_not_change_locator_for_same_row(self):
        first = refs([row("2", "3"), row("5", "6", NEAR)])
        second = refs([row("5", "6", NEAR), row("2", "3")])
        self.assertEqual({r["candidate_ref"] for r in first},
                         {r["candidate_ref"] for r in second})

    def test_source_digest_still_binds_reference(self):
        self.assertNotEqual(refs([row()])[0]["candidate_ref"],
                            refs([row()], sha=SECOND_SHA)[0]["candidate_ref"])

    def test_supplied_fake_refs_are_overwritten(self):
        fake = row()
        fake.update({"candidate_ref": "forged", "source_sha256": SECOND_SHA})
        out = refs([fake])[0]
        self.assertEqual(out["source_sha256"], SHA)
        self.assertNotEqual(out["candidate_ref"], "forged")

    def test_underlying_storage_drives_conflict_not_forged_getter(self):
        deceptive = ForgedGet(row(status=NEAR))
        self.reject([row(status=EXACT), deceptive])

    def test_private_values_are_not_echoed_on_conflict(self):
        private = "ACCOUNT_NUMBER_CUSTOMER_X_809714"
        secret = row(status=NEAR)
        secret["vendor"] = private
        try:
            refs([row(), secret])
            self.fail("expected closed report")
        except ValueError as exc:
            self.assertNotIn(private, str(exc))
            self.assertNotIn("809714", str(exc))

    def test_input_order_variation_always_rejects(self):
        a, b = row(), row("3", "2", NEAR)
        for sequence in ([a, b], [b, a]):
            with self.subTest(first=sequence[0]["status"]):
                self.reject(sequence)


if __name__ == "__main__":
    unittest.main()
