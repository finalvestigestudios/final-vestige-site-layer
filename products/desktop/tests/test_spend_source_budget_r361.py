"""R361 direct SpendMap resource budget and native evidence tests; synthetic only."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from fvs_suite import spend_source_budget_r361 as limits
from fvs_suite.spend_source_budget_r361 import SpendSourceBudget


def row(vendor='ACME', category='Supplies'):
    return {'row': '2', 'vendor': vendor, 'date': '2026-11-01',
            'amount': '100.00', 'category': category}


class SpendSourceBudgetR361(unittest.TestCase):
    def test_small_financial_row_passes(self):
        SpendSourceBudget().attest(row())

    def test_two_rows_within_budget(self):
        budget = SpendSourceBudget()
        budget.attest(row('ACME'))
        budget.attest(row('BETA'))

    def test_zero_column_dict_is_allowed_for_later_required_field_validation(self):
        SpendSourceBudget().attest({})

    def test_exact_column_cap_passes(self):
        SpendSourceBudget().attest({str(n): '' for n in range(64)})

    def test_one_column_above_cap_rejected(self):
        with self.assertRaisesRegex(ValueError, 'column limit'):
            SpendSourceBudget().attest({str(n): '' for n in range(65)})

    def test_single_overlarge_vendor_rejected(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_CELL_CHARS', 10):
            with self.assertRaisesRegex(ValueError, 'cell size limit'):
                SpendSourceBudget().attest(row('A' * 11))

    def test_single_exact_limit_vendor_allowed(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_CELL_CHARS', 10):
            SpendSourceBudget().attest(row('A' * 10))

    def test_overlarge_category_rejected(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_CELL_CHARS', 10):
            with self.assertRaisesRegex(ValueError, 'cell size limit'):
                SpendSourceBudget().attest(row(category='X' * 11))

    def test_overlarge_unused_extra_column_rejected(self):
        source = row()
        source['unused'] = 'X' * 11
        with patch.object(limits, 'MAX_SPEND_SOURCE_CELL_CHARS', 10):
            with self.assertRaisesRegex(ValueError, 'cell size limit'):
                SpendSourceBudget().attest(source)

    def test_overlarge_column_name_rejected(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_CELL_CHARS', 10):
            with self.assertRaisesRegex(ValueError, 'cell size limit'):
                SpendSourceBudget().attest({'X' * 11: 'value'})

    def test_budget_counts_utf8_encoded_bytes_not_codepoints(self):
        source = {'v': '€'}  # 1 + 3 + 2 framing = 6 bytes
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 5):
            with self.assertRaisesRegex(ValueError, 'text byte limit'):
                SpendSourceBudget().attest(source)
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 6):
            SpendSourceBudget().attest(source)

    def test_four_byte_utf8_expansion_is_counted(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 6):
            with self.assertRaisesRegex(ValueError, 'text byte limit'):
                SpendSourceBudget().attest({'v': '😀'})

    def test_budget_counts_unused_extra_field(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 8):
            with self.assertRaisesRegex(ValueError, 'text byte limit'):
                SpendSourceBudget().attest({'a': '1', 'extra': ''})

    def test_report_budget_accumulates_across_rows(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 7):
            budget = SpendSourceBudget()
            budget.attest({'a': '1'})  # 4 bytes
            with self.assertRaisesRegex(ValueError, 'text byte limit'):
                budget.attest({'b': '2'})

    def test_exact_total_limit_is_accepted(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 8):
            budget = SpendSourceBudget()
            budget.attest({'a': '1'})
            budget.attest({'b': '2'})

    def test_failed_row_does_not_consume_budget(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 8):
            budget = SpendSourceBudget()
            with self.assertRaises(ValueError):
                budget.attest({'a': '1', 'too-long': 'value'})
            budget.attest({'a': '1'})
            budget.attest({'b': '2'})

    def test_reject_non_native_dict(self):
        class HostileDict(dict):
            def items(self):
                raise AssertionError('untrusted items invoked')
        with self.assertRaises(ValueError):
            SpendSourceBudget().attest(HostileDict(row()))

    def test_reject_non_native_text_value(self):
        class HostileStr(str):
            def encode(self, *a, **k):
                raise AssertionError('unsafe encode hook')
        with self.assertRaises(ValueError):
            SpendSourceBudget().attest({'v': HostileStr('X')})

    def test_reject_non_native_key(self):
        class HostileStr(str):
            def encode(self, *a, **k):
                raise AssertionError('unsafe encode hook')
        with self.assertRaises(ValueError):
            SpendSourceBudget().attest({HostileStr('v'): 'X'})

    def test_reject_lone_surrogate(self):
        with self.assertRaisesRegex(ValueError, 'UTF-8') as caught:
            SpendSourceBudget().attest({'v': '\ud800'})
        self.assertIsNone(caught.exception.__context__)

    def test_reject_surrogate_in_key(self):
        with self.assertRaisesRegex(ValueError, 'UTF-8'):
            SpendSourceBudget().attest({'\udfff': 'X'})

    def test_does_not_echo_secret_in_oversize_error(self):
        secret = 'PRIVATE-CLIENT-SSN-99999'
        with patch.object(limits, 'MAX_SPEND_SOURCE_CELL_CHARS', 10):
            with self.assertRaises(ValueError) as e:
                SpendSourceBudget().attest({'v': secret})
        self.assertNotIn(secret, str(e.exception))

    def test_budget_is_report_scoped(self):
        with patch.object(limits, 'MAX_SPEND_SOURCE_TEXT_BYTES', 4):
            SpendSourceBudget().attest({'a': '1'})
            SpendSourceBudget().attest({'a': '1'})

    def test_valid_unicode_nbsp_source_allowed(self):
        SpendSourceBudget().attest(row('\u00a0ACME'))

    def test_does_not_modify_original_record(self):
        source = row()
        original = dict(source)
        SpendSourceBudget().attest(source)
        self.assertEqual(source, original)


if __name__ == '__main__':
    unittest.main()
