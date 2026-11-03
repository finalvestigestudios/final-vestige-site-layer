"""R92 public API candidate-count and audit-pair custody regression tests.

Synthetic inputs only; no customer data, telemetry, cloud service or approval.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal, Context, Inexact, Rounded, localcontext
import hashlib
import unittest

from fvs_suite.invoice_match import MAX_CANDIDATES, candidate_pairs
from fvs_suite.invoice_provenance import attach_invoice_provenance

SOURCE = hashlib.sha256(b"synthetic local source\n").hexdigest()


def invoice(row: int, key: str = "A", day: int = 0, amount: str = "1.00"):
    return {
        "row": str(row), "v": "ACME", "inv": key,
        "amt": Decimal(amount), "dt": date(2026, 1, 1) + timedelta(days=day),
        "vendor": "Acme", "invoice_number": key,
    }


def report(a="2", b="3", status="exact_invoice_key", **extra):
    return {"row_a": a, "row_b": b, "status": status, **extra}


class InvoiceCandidateEnvelopeR92(unittest.TestCase):
    def attach(self, rows):
        return attach_invoice_provenance(rows, source_sha256=SOURCE)

    def test_exact_default_limit_is_declared_safety_cap(self):
        self.assertEqual(MAX_CANDIDATES, 100_000)
        self.assertEqual(candidate_pairs([]), [])
        self.assertEqual(candidate_pairs([], max_candidates=MAX_CANDIDATES), [])

    def test_over_cap_direct_request_is_rejected_before_reading_input(self):
        def should_not_read():
            raise AssertionError("public engine consumed a rejected request")
            yield invoice(2)
        with self.assertRaisesRegex(ValueError, "safety maximum"):
            candidate_pairs(should_not_read(), max_candidates=MAX_CANDIDATES + 1)

    def test_absurd_requested_cap_fails_without_allocating_candidate_results(self):
        with self.assertRaisesRegex(ValueError, "safety maximum"):
            candidate_pairs([], max_candidates=10**100)

    def test_bad_cap_types_rejected_before_consuming_generator(self):
        for cap in (0, -1, True, 0.5, "100000", None, Decimal("2")):
            with self.subTest(cap=repr(cap)), self.assertRaisesRegex(ValueError, "positive integer"):
                candidate_pairs([], max_candidates=cap)

    def test_lower_positive_limit_still_fails_closed_on_dense_pairs(self):
        rows = [invoice(2, "A"), invoice(3, "B"), invoice(4, "C")]
        with self.assertRaisesRegex(ValueError, "no incomplete report was saved"):
            candidate_pairs(rows, max_candidates=2)

    def test_one_pair_at_exact_cap_remains_supported(self):
        pairs = candidate_pairs([invoice(2, "A"), invoice(3, "A")], max_candidates=MAX_CANDIDATES)
        self.assertEqual([(p[0]["row"], p[1]["row"], p[2]) for p in pairs],
                         [("2", "3", "exact_invoice_key")])

    def test_direct_provenance_rejects_more_than_safety_cap_before_iterating_records(self):
        # len-check prevents 100k SHA256 computations and copied outputs.
        huge = [None] * (MAX_CANDIDATES + 1)
        with self.assertRaisesRegex(ValueError, "Too many invoice review candidates"):
            self.attach(huge)

    def test_unordered_duplicate_pair_same_status_fails_closed(self):
        rows = [report("2", "99"), report("99", "2")]
        with self.assertRaisesRegex(ValueError, "Duplicate invoice candidate"):
            self.attach(rows)

    def test_unordered_near_duplicate_same_status_fails_closed(self):
        kind = "review_possible_duplicate"
        with self.assertRaisesRegex(ValueError, "Duplicate invoice candidate"):
            self.attach([report("99", "2", kind), report("2", "99", kind)])

    def test_same_direction_repeated_pair_remains_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate invoice candidate"):
            self.attach([report(), deepcopy(report())])

    def test_single_pair_orientation_remains_auditable(self):
        forward = self.attach([report("2", "3")])[0]
        reverse = self.attach([report("3", "2")])[0]
        self.assertNotEqual(forward["candidate_ref"], reverse["candidate_ref"])

    def test_different_review_classifications_cannot_share_source_pair(self):
        # R170: the same physical source pair has one review classification.
        rows = [report("2", "3"), report("3", "2", "review_possible_duplicate")]
        with self.assertRaisesRegex(ValueError, "Duplicate invoice candidate"):
            self.attach(rows)

    def test_fails_closed_on_11_digit_csv_line_reference(self):
        for name in ("row_a", "row_b"):
            with self.subTest(field=name), self.assertRaisesRegex(ValueError, "physical CSV rows"):
                r = report()
                r[name] = "10000000000"
                self.attach([r])

    def test_5000_digit_physical_line_is_rejected_without_unsafe_int_conversion(self):
        with self.assertRaisesRegex(ValueError, "physical CSV rows"):
            self.attach([report("2", "9" * 5000)])

    def test_ten_digit_canonical_row_still_supported(self):
        self.assertRegex(self.attach([report("2", "9999999999")])[0]["candidate_ref"], r"\A[0-9a-f]{64}\Z")

    def test_untrusted_report_type_is_private_and_deterministic(self):
        with self.assertRaisesRegex(ValueError, "report must be a list"):
            self.attach("SECRET client-A /tmp/path.csv")

    def test_copy_and_stable_source_digest_do_not_mutate_original(self):
        rows = [report("5", "3", "review_possible_duplicate", vendor="PRIVATE-ID-ABC")]
        before = deepcopy(rows)
        one = self.attach(rows)
        two = self.attach(rows)
        self.assertEqual(rows, before)
        self.assertEqual(one, two)
        self.assertEqual(one[0]["source_sha256"], SOURCE)
        self.assertNotIn("PRIVATE", one[0]["candidate_ref"])

    def test_cross_status_and_vendor_sensitive_fields_are_not_in_error(self):
        rows = [report("2", "3", vendor="SECRET_VENDOR"),
                report("3", "2", vendor="SECRET_OTHER")]
        with self.assertRaises(ValueError) as result:
            self.attach(rows)
        self.assertNotIn("SECRET", str(result.exception))

    def test_hostile_decimal_context_has_no_effect_on_duplicate_identity(self):
        pair = [invoice(2, "A", amount="0.00000001"), invoice(3, "B", amount="0.00000001")]
        expected = candidate_pairs(pair)
        with localcontext(Context(prec=2, Emax=4, Emin=-4)) as ctx:
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            observed = candidate_pairs(pair)
        self.assertEqual([(a["row"], b["row"], s) for a,b,s,_ in expected],
                         [(a["row"], b["row"], s) for a,b,s,_ in observed])


if __name__ == "__main__":
    unittest.main()
