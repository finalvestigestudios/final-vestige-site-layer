"""R362 aggregate cardinality protection for tiny/empty SpendMap source cells."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from fvs_suite import spend_source_budget_r361 as limits
from fvs_suite.spend_source_budget_r361 import SpendSourceBudget


def columns(n: int) -> dict[str, str]:
    return {str(i): '' for i in range(n)}


class SpendSourceFieldBudgetR362(unittest.TestCase):
    def test_exact_global_field_limit_allowed(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 5):
            budget = SpendSourceBudget()
            budget.attest(columns(3))
            budget.attest(columns(2))

    def test_one_above_global_limit_rejected(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 5):
            budget = SpendSourceBudget()
            budget.attest(columns(3))
            with self.assertRaisesRegex(ValueError, 'field-count limit'):
                budget.attest(columns(3))

    def test_single_row_can_violate_total_not_per_row_cap(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 2):
            with self.assertRaisesRegex(ValueError, 'field-count limit'):
                SpendSourceBudget().attest(columns(3))

    def test_empty_columns_still_count(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 1):
            budget = SpendSourceBudget()
            budget.attest({'': ''})
            with self.assertRaisesRegex(ValueError, 'field-count limit'):
                budget.attest({'a': ''})

    def test_many_tiny_columns_across_rows_cannot_evade(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 192):
            budget = SpendSourceBudget()
            for _ in range(3):
                budget.attest(columns(64))
            with self.assertRaisesRegex(ValueError, 'field-count limit'):
                budget.attest({'x': ''})

    def test_field_count_failures_do_not_mutate_counters(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 4):
            budget = SpendSourceBudget()
            budget.attest(columns(2))
            with self.assertRaises(ValueError):
                budget.attest(columns(3))
            budget.attest(columns(2))

    def test_invalid_utf8_does_not_consume_field_slots(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 1):
            budget = SpendSourceBudget()
            with self.assertRaisesRegex(ValueError, 'UTF-8'):
                budget.attest({'x': '\ud800'})
            budget.attest({'x': 'safe'})

    def test_oversized_cell_does_not_consume_field_slots(self):
        with (patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 1),
              patch.object(limits, 'MAX_SPEND_SOURCE_CELL_CHARS', 3)):
            budget = SpendSourceBudget()
            with self.assertRaisesRegex(ValueError, 'cell size'):
                budget.attest({'x': 'long'})
            budget.attest({'x': 'ok'})

    def test_utf8_budget_failure_does_not_consume_field_slots(self):
        with (patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 1),
              patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 5)):
            budget = SpendSourceBudget()
            with self.assertRaisesRegex(ValueError, 'text byte limit'):
                budget.attest({'x': 'large'})
            budget.attest({'x': 'a'})

    def test_field_limit_rejection_precedes_utf8_encoding(self):
        with (patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 0),
              patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 0)):
            with self.assertRaisesRegex(ValueError, 'field-count limit'):
                SpendSourceBudget().attest({'x': '\ud800'})

    def test_empty_record_has_zero_field_charge(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 0):
            budget = SpendSourceBudget()
            budget.attest({})
            budget.attest({})

    def test_normal_five_field_financial_evidence_preserved(self):
        row = {'row': '2', 'vendor': '\u00a0ACME', 'date': '2026-11-01',
               'amount': '100.00', 'category': 'Supplies'}
        copy = row.copy()
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 5):
            SpendSourceBudget().attest(row)
        self.assertEqual(row, copy)

    def test_report_budgets_do_not_share_field_slots(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 1):
            SpendSourceBudget().attest({'x': ''})
            SpendSourceBudget().attest({'x': ''})

    def test_error_does_not_reflect_customer_field_values(self):
        secret = 'CONFIDENTIAL-ACCOUNT-54321'
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 0):
            with self.assertRaises(ValueError) as e:
                SpendSourceBudget().attest({'PRIVATE': secret})
        self.assertNotIn(secret, str(e.exception))
        self.assertNotIn('PRIVATE', str(e.exception))

    def test_duplicate_key_is_one_native_field(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TOTAL_FIELDS', 1):
            SpendSourceBudget().attest({'a': 'one', 'a': 'two'})

    def test_native_dict_subclass_stays_rejected(self):
        class UnsafeDict(dict):
            def __len__(self):
                raise AssertionError('untrusted hook')
        with self.assertRaisesRegex(ValueError, 'column limit'):
            SpendSourceBudget().attest(UnsafeDict({'a': ''}))


if __name__ == '__main__':
    unittest.main()
