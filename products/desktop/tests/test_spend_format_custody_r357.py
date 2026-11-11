"""R357 SpendMap exact monetary display tests with synthetic values."""
from __future__ import annotations

from decimal import Context, Decimal, Inexact, localcontext
import unittest

from fvs_suite.spend_format_custody_r357 import verified_spend_money_display as verify


class SpendFormatCustodyR357(unittest.TestCase):
    def test_fixed_cents(self):
        self.assertEqual(verify(Decimal('12.50'), '12.50'), '12.50')

    def test_plain_integer_display(self):
        self.assertEqual(verify(Decimal('12.00'), '12'), '12')

    def test_single_fractional_digit(self):
        self.assertEqual(verify(Decimal('12.50'), '12.5'), '12.5')

    def test_dollars_currency(self):
        self.assertEqual(verify(Decimal('1234.50'), '$1,234.50'), '$1,234.50')

    def test_negative_prefix_currency(self):
        self.assertEqual(verify(Decimal('-1234.50'), '-$1,234.50'), '-$1,234.50')

    def test_negative_currency_prefix(self):
        self.assertEqual(verify(Decimal('-1234.50'), '$-1,234.50'), '$-1,234.50')

    def test_accounting_parentheses(self):
        self.assertEqual(verify(Decimal('-1234.50'), '($1,234.50)'), '($1,234.50)')

    def test_positive_sign(self):
        self.assertEqual(verify(Decimal('1234.50'), '+1234.50'), '+1234.50')

    def test_zero_sign_preserved(self):
        self.assertEqual(verify(Decimal('-0.00'), '-0.00'), '-0.00')
        self.assertEqual(verify(Decimal('0.00'), '0'), '0')

    def test_zero_sign_laundering_rejected(self):
        for n, s in (('-0.00', '0.00'), ('0.00', '-0.00'),
                     ('-0.00', '$0.00'), ('0.00', '($0.00)')):
            with self.subTest(n=n, s=s), self.assertRaises(ValueError):
                verify(Decimal(n), s)

    def test_inflated_amount_rejected(self):
        with self.assertRaises(ValueError):
            verify(Decimal('100.00'), '1000.00')

    def test_reduced_amount_rejected(self):
        with self.assertRaises(ValueError):
            verify(Decimal('100.00'), '10.00')

    def test_subcent_display_not_rounded(self):
        for s in ('1.004', '1.005', '1.009', '1.000'):
            with self.subTest(s=s), self.assertRaises(ValueError):
                verify(Decimal('1.00'), s)

    def test_rejects_spreadsheet_formula_and_injection(self):
        for s in ('=100.00', '+=100', '@SUM(A1:A2)', '\t100.00', '\r100.00',
                  '100.00\n=1+1', "'100.00", '１００.００'):
            with self.subTest(s=s), self.assertRaises(ValueError):
                verify(Decimal('100.00'), s)

    def test_rejects_nonfixed_and_malformed(self):
        for s in ('1e2', '1_00', '1,00.00', '1,0000.00', '100.', '.25',
                  'Infinity', 'NaN', '--100', '100CR', ' (100) ', '(+100)',
                  '(-100)', '($-100)', '($100', '$100)'):
            with self.subTest(s=s), self.assertRaises(ValueError):
                verify(Decimal('100.00'), s)

    def test_rejects_str_subclass_without_invoking_methods(self):
        class PrivateStr(str):
            def __len__(self):
                raise AssertionError('should not execute')
        with self.assertRaises(ValueError):
            verify(Decimal('10.00'), PrivateStr('10.00'))

    def test_rejects_nontext(self):
        for item in (None, 100, 100.0, Decimal('100.00'), b'100.00'):
            with self.subTest(type=type(item).__name__), self.assertRaises(ValueError):
                verify(Decimal('100.00'), item)

    def test_rejects_non_decimal(self):
        with self.assertRaises(ValueError):
            verify(100.0, '100.00')

    def test_rejects_nonfinite_amount(self):
        for amount in (Decimal('NaN'), Decimal('Infinity'), Decimal('-Infinity')):
            with self.subTest(amount=str(amount)), self.assertRaises(ValueError):
                verify(amount, '100.00')

    def test_rejects_oversized_output(self):
        with self.assertRaises(ValueError):
            verify(Decimal('0.00'), '0' * 81)

    def test_no_sensitive_value_in_errors(self):
        for value in ('PRIVATE-CELL 100.00', '\nPRIVATE-CELL'):
            with self.assertRaises(ValueError) as ctx:
                verify(Decimal('100.00'), value)
            self.assertNotIn('PRIVATE-CELL', str(ctx.exception))

    def test_exact_large_aggregate(self):
        self.assertEqual(verify(Decimal('1999999999999.98'), '1999999999999.98'),
                         '1999999999999.98')

    def test_caller_decimal_context_untouched(self):
        with localcontext(Context(prec=2)) as context:
            context.traps[Inexact] = True
            self.assertEqual(verify(Decimal('999999999999.99'), '999999999999.99'),
                             '999999999999.99')
            self.assertEqual(context.prec, 2)

    def test_valid_match_never_changes_display(self):
        self.assertEqual(verify(Decimal('1.00'), '$1.00'), '$1.00')


if __name__ == '__main__':
    unittest.main()
