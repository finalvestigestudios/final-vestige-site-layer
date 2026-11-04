"""R192: reject cross-record provenance mutation through direct API callbacks.

Synthetic records only; no filesystem, uploads, telemetry, or external services.
Existing unsorted physical row labels are preserved by design; snapshotting is
NOT an independent authenticity proof for a supplied source SHA-256.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, Inexact, Rounded, localcontext
import unittest

from fvs_suite.spend_input import MAX_SPEND_ROWS, validated_spend_rows

PRIVATE = 'PRIVATE ACCOUNT 999999!'


def row(index='2', vendor='ACME', amount='10.25', category='Parts'):
    return {'row': index, 'vendor': vendor, 'amount': amount,
            'date': '2026-01-02', 'category': category}


def parse(rows, *, vendor=lambda s: s.upper(), day=date.fromisoformat, money=Decimal):
    return list(validated_spend_rows(rows, normalize_vendor=vendor,
                                    parse_date=day, parse_money=money))


class HostileDict(dict):
    def get(self, *args):
        raise AssertionError('untrusted get() executed')

    def keys(self):
        raise AssertionError('untrusted keys() executed')

    def items(self):
        raise AssertionError('untrusted items() executed')

    def __getitem__(self, key):
        raise AssertionError('untrusted __getitem__ executed')

    def __iter__(self):
        raise AssertionError('untrusted __iter__ executed')


class SpendCollectionSnapshotR192(unittest.TestCase):
    def fixtures(self):
        return [row('2'), row('4', vendor='BETA', amount='25.50')]

    def assert_original_second(self, result):
        self.assertEqual(len(result), 2)
        saved, vendor, month, category, amount = result[1]
        self.assertEqual((saved['row'], saved['vendor'], saved['amount'],
                          vendor, month, category, amount),
                         ('4', 'BETA', '25.50', 'BETA', '2026-01', 'Parts', Decimal('25.50')))

    def test_normalizer_cannot_forge_future_row_number(self):
        records = self.fixtures()
        def transform(s):
            records[1]['row'] = '99'
            return s
        self.assert_original_second(parse(records, vendor=transform))

    def test_normalizer_cannot_forge_future_amount(self):
        records = self.fixtures()
        def transform(s):
            records[1]['amount'] = '999999999999.99'
            return s
        self.assert_original_second(parse(records, vendor=transform))

    def test_normalizer_cannot_replace_future_record(self):
        records = self.fixtures()
        def transform(s):
            records[1] = row('111', vendor='EVIL', amount='777.77')
            return s
        self.assert_original_second(parse(records, vendor=transform))

    def test_normalizer_cannot_delete_future_record(self):
        records = self.fixtures()
        def transform(s):
            records.pop()
            return s
        self.assert_original_second(parse(records, vendor=transform))

    def test_normalizer_cannot_append_fake_record(self):
        records = self.fixtures()
        def transform(s):
            records.append(row('99', vendor='EVIL'))
            return s
        self.assert_original_second(parse(records, vendor=transform))

    def test_normalizer_cannot_reverse_original_rows(self):
        records = self.fixtures()
        def transform(s):
            records.reverse()
            return s
        result = parse(records, vendor=transform)
        self.assertEqual([r[0]['row'] for r in result], ['2', '4'])

    def test_date_parser_cannot_change_future_category(self):
        records = self.fixtures()
        def transform(s):
            records[1]['category'] = 'Secretly changed'
            return date.fromisoformat(s)
        self.assert_original_second(parse(records, day=transform))

    def test_money_parser_cannot_change_future_date(self):
        records = self.fixtures()
        def transform(s):
            records[1]['date'] = '2050-12-31'
            return Decimal(s)
        self.assert_original_second(parse(records, money=transform))

    def test_money_parser_cannot_remove_future_amount(self):
        records = self.fixtures()
        def transform(s):
            records[1].pop('amount', None)
            return Decimal(s)
        self.assert_original_second(parse(records, money=transform))

    def test_mutations_to_same_original_record_do_not_change_snapshot(self):
        records = self.fixtures()
        def transform(s):
            records[0]['amount'] = '0.00'
            records[0]['row'] = '999'
            return s
        result = parse(records, vendor=transform)
        self.assertEqual(result[0][0]['row'], '2')
        self.assertEqual(result[0][-1], Decimal('10.25'))

    def test_different_vendor_keys_and_source_rows_remain_independent(self):
        records = [row('9', 'A'), row('2', 'B'), row('20', 'C')]
        result = parse(records)
        self.assertEqual([r[0]['row'] for r in result], ['9', '2', '20'])
        self.assertEqual([r[1] for r in result], ['A', 'B', 'C'])

    def test_native_dict_subclass_storage_used_for_all_rows(self):
        result = parse([HostileDict(row()), HostileDict(row('4', 'BETA', '25.50'))])
        self.assert_original_second(result)

    def test_native_dict_subclass_mutated_between_callback_and_visit_is_frozen(self):
        records = [HostileDict(row()), HostileDict(row('4', 'BETA', '25.50'))]
        def transform(s):
            dict.__setitem__(records[1], 'vendor', PRIVATE)
            return s
        self.assert_original_second(parse(records, vendor=transform))

    def test_frozen_row_is_independent_copy_not_original_dict(self):
        records = self.fixtures()
        result = parse(records)
        self.assertIsNot(result[0][0], records[0])
        self.assertIsNot(result[1][0], records[1])
        self.assertEqual(records, self.fixtures())

    def test_late_invalid_mapping_blocks_all_callbacks(self):
        records = [row(), None]
        calls = []
        with self.assertRaisesRegex(ValueError, 'record must be a mapping'):
            parse(records, vendor=lambda s: calls.append(s) or s)
        self.assertEqual(calls, [])

    def test_late_non_native_key_blocks_all_callbacks(self):
        records = [row(), row('3')]
        records[1][13] = PRIVATE
        calls = []
        with self.assertRaisesRegex(ValueError, 'field names must be plain text') as caught:
            parse(records, vendor=lambda s: calls.append(s) or s)
        self.assertEqual(calls, [])
        self.assertNotIn(PRIVATE, str(caught.exception))

    def test_duplicate_physical_line_still_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate spend physical'):
            parse([row('2'), row('2')])

    def test_late_invalid_row_uses_privacy_safe_error(self):
        with self.assertRaises(ValueError) as caught:
            parse([row('2'), row('4', amount=PRIVATE)])
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertIn('physical row 4', str(caught.exception))

    def test_row_count_limit_before_any_callback(self):
        self.assertEqual(MAX_SPEND_ROWS, 200000)
        calls = []
        with self.assertRaisesRegex(ValueError, 'Too many spend source'):
            parse([row()] * (MAX_SPEND_ROWS + 1), vendor=lambda s: calls.append(s))
        self.assertEqual(calls, [])

    def test_callback_failure_is_private_and_fails_closed(self):
        records = self.fixtures()
        def bad(s):
            records[1]['vendor'] = PRIVATE
            raise RuntimeError(PRIVATE)
        with self.assertRaises(ValueError) as caught:
            parse(records, vendor=bad)
        self.assertIn('Invalid vendor at physical row 2', str(caught.exception))
        self.assertNotIn(PRIVATE, str(caught.exception))

    def test_low_precision_context_does_not_alter_snapshots(self):
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            result = parse(self.fixtures())
            self.assertEqual(ctx.prec, 3)
        self.assert_original_second(result)

    def test_callback_called_once_per_frozen_record(self):
        seen = []
        result = parse(self.fixtures(), vendor=lambda s: seen.append(s) or s)
        self.assertEqual(seen, ['ACME', 'BETA'])
        self.assert_original_second(result)

    def test_empty_source_preserved(self):
        self.assertEqual(parse([]), [])


if __name__ == '__main__':
    unittest.main()
