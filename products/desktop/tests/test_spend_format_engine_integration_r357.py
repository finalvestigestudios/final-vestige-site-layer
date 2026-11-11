"""R357 exact SpendMap report display integration: requires genuine suite modules.

Synthetic rows only. Financial reports are evidence for human review, not a
payment-authorization or compliance decision.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
import unittest

from fvs_suite.spend_analysis import summarize_spend

_SOURCE_SHA = '7' * 64


def source(row, amount='100.00', month=1):
    return {'row': str(row), 'vendor': 'ACME', 'amount': amount,
            'date': f'2026-{month:02d}-01', 'category': 'Supplies'}


def render(records, formatter=None):
    return summarize_spend(
        records, normalize_vendor=lambda s: s,
        parse_date=date.fromisoformat, parse_money=Decimal,
        format_money=formatter or (lambda amount: format(amount, '.2f')),
        source_sha256=_SOURCE_SHA,
    )


class SpendFormatEngineIntegrationR357(unittest.TestCase):
    def test_real_exact_amount_and_gross_survive(self):
        out = render([source(2), source(3, '25.50')])[0]
        self.assertEqual(out['amount'], '125.50')
        self.assertEqual(out['gross_charges'], '125.50')
        self.assertEqual(out['source_rows'], '2;3')
        self.assertEqual(out['source_sha256'], _SOURCE_SHA)

    def test_malicious_formatter_inflation_rejected(self):
        def lying(value):
            return '9000.00'
        with self.assertRaisesRegex(ValueError, 'monetary display'):
            render([source(2)], formatter=lying)

    def test_malicious_formatter_reduction_rejected(self):
        with self.assertRaisesRegex(ValueError, 'monetary display'):
            render([source(2)], formatter=lambda _: '0.00')

    def test_malicious_formatter_late_call_rejected(self):
        calls = []
        def formatter(value):
            calls.append(value)
            return '12345.00' if len(calls) == 4 else format(value, '.2f')
        with self.assertRaisesRegex(ValueError, 'monetary display'):
            render([source(2)], formatter=formatter)
        self.assertEqual(len(calls), 4)

    def test_private_exception_never_echoed(self):
        def formatter(_):
            raise RuntimeError('PRIVATE-CELL: client information')
        with self.assertRaises(ValueError) as caught:
            render([source(2)], formatter=formatter)
        self.assertNotIn('PRIVATE-CELL', str(caught.exception))

    def test_nontext_formatter_rejected(self):
        with self.assertRaisesRegex(ValueError, 'monetary display'):
            render([source(2)], formatter=lambda amount: amount)

    def test_csv_formula_in_display_rejected(self):
        with self.assertRaisesRegex(ValueError, 'monetary display'):
            render([source(2)], formatter=lambda _: '=SUM(A1:A2)')

    def test_invalid_subcent_format_rejected(self):
        with self.assertRaisesRegex(ValueError, 'monetary display'):
            render([source(2)], formatter=lambda _: '100.001')

    def test_standard_negative_credits_remain_exact(self):
        out = render([source(2, '100.00'), source(3, '-25.50')])[0]
        self.assertEqual(out['amount'], '74.50')
        self.assertEqual(out['gross_credits'], '25.50')
        self.assertEqual(out['credit_offset_review'], 'review_mixed_sign_offset')

    def test_allow_legacy_alternate_accounting_formatter(self):
        def format_accounting(value):
            return f'(${format(value.copy_abs(), ".2f")})' if value < 0 else f'${format(value, ".2f")}'
        out = render([source(2, '-25.50')], formatter=format_accounting)[0]
        self.assertEqual(out['amount'], '($25.50)')
        self.assertEqual(out['gross_credits'], '$25.50')

    def test_aggregate_exceeds_single_line_max_exactly(self):
        out = render([source(2, '999999999999.99'),
                      source(3, '999999999999.99')])[0]
        self.assertEqual(out['amount'], '1999999999999.98')
        self.assertEqual(out['vendor_month_total'], '1999999999999.98')

    def test_original_rows_not_modified_on_bad_format(self):
        original = [source(2)]
        saved = [dict(row) for row in original]
        with self.assertRaises(ValueError):
            render(original, formatter=lambda _: '1000.00')
        self.assertEqual(original, saved)


if __name__ == '__main__':
    unittest.main()
