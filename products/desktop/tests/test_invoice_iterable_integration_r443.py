"""R443 real Invoice Twin candidate-path iterable failure tests; synthetic only."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
import traceback
import unittest
from unittest.mock import patch

from fvs_suite import invoice_match
from fvs_suite.invoice_match import candidate_pairs

PRIVATE = "PRIVATE_CUSTOMER_ACCOUNT_7731"


def row(n, invoice="A", amount=Decimal("10.00")):
    return {"row": str(n), "v": "ACME", "inv": invoice, "amt": amount,
            "dt": date(2026, 1, 1), "vendor": "ACME", "invoice_number": invoice}


class InvoiceIterableIntegrationR443(unittest.TestCase):
    def assert_closed_private_error(self, records):
        with self.assertRaisesRegex(ValueError, "Invoice source records could not be read") as caught:
            candidate_pairs(records)
        failure = caught.exception
        self.assertIsNone(failure.__cause__)
        self.assertIsNone(failure.__context__)
        self.assertNotIn(PRIVATE, str(failure))
        self.assertNotIn(PRIVATE, "".join(traceback.format_exception(failure)))

    def test_private_iterator_creation_fails_before_evidence(self):
        class Source:
            def __iter__(self):
                raise OSError(PRIVATE)
        self.assert_closed_private_error(Source())

    def test_private_late_iterator_failure_never_returns_partial_candidates(self):
        def source():
            yield row(2)
            yield row(3)
            raise RuntimeError(PRIVATE)
        self.assert_closed_private_error(source())

    def test_native_validation_errors_remain_specific(self):
        with self.assertRaisesRegex(ValueError, "finite exact Decimal"):
            candidate_pairs([row(2, amount=2.5)])

    def test_valid_generator_retains_canonical_exact_and_near_candidates(self):
        records = [row(4, "B"), row(3, "A"), row(2, "A")]
        result = candidate_pairs((record for record in records))
        self.assertEqual([(a["row"], b["row"], status) for a, b, status, _ in result],
                         [("2", "3", "exact_invoice_key"),
                          ("2", "4", "review_possible_duplicate"),
                          ("3", "4", "review_possible_duplicate")])

    def test_row_limit_preempts_later_private_iterator_fault(self):
        observed = []
        def source():
            for number in (2, 3, 4):
                observed.append(number)
                yield row(number, str(number))
            raise RuntimeError(PRIVATE)
        with patch.object(invoice_match, "MAX_RECORDS", 2):
            with self.assertRaisesRegex(ValueError, "Too many invoice source records") as caught:
                candidate_pairs(source())
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(observed, [2, 3, 4])


if __name__ == "__main__":
    unittest.main()
