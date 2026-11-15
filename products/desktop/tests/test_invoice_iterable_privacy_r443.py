"""R443: fail-closed private iterator faults in Invoice Twin Scout (synthetic)."""
from __future__ import annotations

import traceback
import unittest

from fvs_suite.invoice_match import _private_source_records

PRIVATE = "CUSTOMER_ACCOUNT_7731_PRIVATE"


class IterationFailure:
    def __iter__(self):
        raise OSError(PRIVATE)


class NextFailure:
    def __init__(self, entries=(), *, error=ValueError):
        self.entries = iter(entries)
        self.error = error
        self.calls = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.calls += 1
        try:
            return next(self.entries)
        except StopIteration:
            raise self.error(PRIVATE)


class InvoiceIterablePrivacyR443(unittest.TestCase):
    def assert_private_refusal(self, records):
        with self.assertRaisesRegex(ValueError, "Invoice source records could not be read") as caught:
            list(_private_source_records(records))
        error = caught.exception
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)
        self.assertNotIn(PRIVATE, str(error))
        self.assertNotIn(PRIVATE, repr(error))
        self.assertNotIn(PRIVATE, "".join(traceback.format_exception(error)))

    def test_iterator_creation_fault_is_sanitized(self):
        self.assert_private_refusal(IterationFailure())

    def test_next_fault_before_first_record_is_sanitized(self):
        self.assert_private_refusal(NextFailure())

    def test_next_fault_after_valid_records_is_not_partial_success(self):
        self.assert_private_refusal(NextFailure([{"row": "2"}, {"row": "3"}]))

    def test_invalid_iterable_is_sanitized(self):
        self.assert_private_refusal(None)

    def test_iterator_returning_noniterator_is_sanitized(self):
        class NonIterator:
            def __iter__(self):
                return 5
        self.assert_private_refusal(NonIterator())

    def test_fault_with_private_attributes_not_retained(self):
        class RichFault(OSError):
            def __init__(self, message):
                super().__init__(message)
                self.private_account = PRIVATE
        self.assert_private_refusal(NextFailure(error=RichFault))

    def test_internal_generator_stop_iteration_failure_is_sanitized(self):
        def bad_source():
            yield {"row": "2"}
            raise StopIteration(PRIVATE)
        self.assert_private_refusal(bad_source())

    def test_real_stop_iteration_and_empty_are_supported(self):
        self.assertEqual(list(_private_source_records(iter(()))), [])
        self.assertEqual(list(_private_source_records([])), [])

    def test_valid_generator_preserves_input_objects_and_order(self):
        items = [{"row": "3"}, {"row": "2"}]
        actual = list(_private_source_records((x for x in items)))
        self.assertEqual(actual, items)
        self.assertIs(actual[0], items[0])

    def test_process_interruptions_are_not_masked(self):
        class Interrupt:
            def __iter__(self):
                return self
            def __next__(self):
                raise KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            list(_private_source_records(Interrupt()))


if __name__ == "__main__":
    unittest.main()
