"""R193: validate every frozen SpendMap source row before invoking callbacks.

All data synthetic. This proves shape/coordinate fail-close, not CSV authenticity.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, Inexact, Rounded, localcontext
import unittest

from fvs_suite.spend_input import validated_spend_rows

SECRET = "PRIVATE_ACCOUNT_991122\n=FORMULA"


def row(n="2", **changes):
    source = {"row": n, "vendor": "ACME", "date": "2026-02-01",
              "amount": "12.34", "category": "Parts"}
    source.update(changes)
    return source


def run(rows, tracker=None):
    hits = tracker if tracker is not None else []
    def vendor(value):
        hits.append(("vendor", value))
        return value.upper()
    def day(value):
        hits.append(("date", value))
        return date.fromisoformat(value)
    def money(value):
        hits.append(("money", value))
        return Decimal(value)
    return validated_spend_rows(rows, normalize_vendor=vendor,
                                parse_date=day, parse_money=money)


class HostileDict(dict):
    def get(self, *args):
        raise AssertionError("untrusted get")
    def __iter__(self):
        raise AssertionError("untrusted iter")
    def items(self):
        raise AssertionError("untrusted items")
    def keys(self):
        raise AssertionError("untrusted keys")
    def __getitem__(self, *args):
        raise AssertionError("untrusted lookup")


class SpendCollectionPreflightR193(unittest.TestCase):
    def assert_fail_closed(self, second, expected):
        hits = []
        iterator = run([row(), second], hits)
        with self.assertRaises(ValueError) as caught:
            next(iterator)
        self.assertIn(expected, str(caught.exception))
        self.assertEqual(hits, [], "no parser callback before whole-source shape validation")
        self.assertNotIn(SECRET, str(caught.exception))
        with self.assertRaises(StopIteration):
            next(iterator)

    def test_late_duplicate_source_coordinate(self):
        self.assert_fail_closed(row("2"), "Duplicate spend physical CSV row")

    def test_late_noncanonical_leading_zero_coordinate(self):
        self.assert_fail_closed(row("03"), "canonical physical CSV row")

    def test_late_noncanonical_secret_coordinate(self):
        self.assert_fail_closed(row("3" + SECRET), "canonical physical CSV row")

    def test_late_missing_vendor(self):
        item = row("3")
        del item["vendor"]
        self.assert_fail_closed(item, "Spend vendor must be imported text")

    def test_late_missing_amount(self):
        item = row("3")
        del item["amount"]
        self.assert_fail_closed(item, "Spend amount must be imported text")

    def test_late_missing_date(self):
        item = row("3")
        del item["date"]
        self.assert_fail_closed(item, "Spend date must be imported text")

    def test_late_boolean_amount(self):
        self.assert_fail_closed(row("3", amount=True), "Spend amount must be imported text")

    def test_late_subclass_vendor(self):
        class StringSubclass(str):
            def __str__(self):
                raise AssertionError("unsafe str")
        self.assert_fail_closed(row("3", vendor=StringSubclass(SECRET)),
                                "Spend vendor must be imported text")

    def test_late_nontext_category(self):
        self.assert_fail_closed(row("3", category=Decimal("2")),
                                "Spend category must be imported text")

    def test_late_nontext_date(self):
        self.assert_fail_closed(row("3", date=None), "Spend date must be imported text")

    def test_late_empty_record(self):
        self.assert_fail_closed({}, "canonical physical CSV row")

    def test_late_bad_mapping_blocks_callbacks(self):
        self.assert_fail_closed(SECRET, "record must be a mapping")

    def test_late_nonplain_key_blocks_callbacks(self):
        item = row("3")
        item[Decimal("7")] = SECRET
        self.assert_fail_closed(item, "field names must be plain text")

    def test_late_str_subclass_key_blocks_callbacks(self):
        item = row("3")
        class Key(str):
            pass
        item[Key("private")] = SECRET
        self.assert_fail_closed(item, "field names must be plain text")

    def test_early_duplicate_has_no_callbacks(self):
        self.assert_fail_closed(row("2", amount=SECRET), "Duplicate spend physical")

    def test_late_third_row_invalid_blocks_all_callbacks(self):
        hits = []
        iterator = run([row(), row("3"), row("2")], hits)
        with self.assertRaisesRegex(ValueError, "Duplicate spend physical"):
            list(iterator)
        self.assertEqual(hits, [])

    def test_valid_three_rows_preserve_unordered_physical_citations(self):
        hits = []
        result = list(run([row("9"), row("2"), row("20")], hits))
        self.assertEqual([r[0]["row"] for r in result], ["9", "2", "20"])
        self.assertEqual([x[0] for x in hits], ["vendor", "date", "money"] * 3)
        self.assertEqual(result[1][-1], Decimal("12.34"))

    def test_all_valid_records_callback_once_each(self):
        hits = []
        result = list(run([row("2"), row("4")], hits))
        self.assertEqual(len(result), 2)
        self.assertEqual(len(hits), 6)

    def test_no_category_still_uncategorized(self):
        item = row()
        del item["category"]
        self.assertEqual(list(run([item]))[0][3], "Uncategorized")

    def test_dict_subclass_storage_cannot_run_overridden_methods(self):
        result = list(run([HostileDict(row()), HostileDict(row("4"))]))
        self.assertEqual(result[1][0]["row"], "4")

    def test_precise_decimal_unchanged_under_trapping_context(self):
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.traps[Inexact] = ctx.traps[Rounded] = True
            result = list(run([row()]))
        self.assertEqual(result[0][-1], Decimal("12.34"))

    def test_source_list_remains_unchanged(self):
        original = [row(), row("3")]
        snapshot = [dict(v) for v in original]
        list(run(original))
        self.assertEqual(original, snapshot)

    def test_empty_source_keeps_no_callbacks(self):
        hits = []
        self.assertEqual(list(run([], hits)), [])
        self.assertEqual(hits, [])

    def test_bad_money_text_still_rejected_privately(self):
        hits = []
        iterator = run([row(), row("3", amount=SECRET)], hits)
        with self.assertRaisesRegex(ValueError, "Invalid spend amount at physical row 3") as err:
            list(iterator)
        self.assertNotIn(SECRET, str(err.exception))
        # A syntactically text-shaped amount still requires parser validation.
        self.assertEqual(len(hits), 6)


if __name__ == "__main__":
    unittest.main()
