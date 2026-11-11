"""R363 real SpendMap engine regression tests (requires complete repository)."""
from __future__ import annotations

from decimal import Inexact, Rounded, localcontext
import unittest

from fvs_suite.engine import dollars, key, money, parse_date
from fvs_suite.spend_analysis import summarize_spend

DIGEST = "a" * 64


def row(number: int, vendor: str = "ACME", category: str = "Supplies",
        date: str = "2026-11-01", amount: str = "1.00") -> dict[str, str]:
    return {"row": str(number), "vendor": vendor, "date": date,
            "amount": amount, "category": category}


def report(records: list[dict[str, str]]) -> list[dict[str, str]]:
    return summarize_spend(records, normalize_vendor=key, parse_date=parse_date,
                           parse_money=money, format_money=dollars,
                           source_sha256=DIGEST)


class SourceRowOrderEngineR363(unittest.TestCase):
    def test_one_bucket_orders_physical_rows_numerically(self):
        result = report([row(10), row(2), row(9)])
        self.assertEqual(result[0]["source_rows"], "2;9;10")
        self.assertEqual(result[0]["amount"], "3.00")

    def test_permuting_direct_input_does_not_change_report(self):
        rows = [row(10, amount="3.00"), row(2, amount="2.00"), row(9, amount="-1.00")]
        self.assertEqual(report(rows), report(list(reversed(rows))))

    def test_cross_vendor_buckets_are_independent(self):
        result = report([row(10), row(7, vendor="BETA"), row(2), row(3, vendor="BETA")])
        self.assertEqual({r["vendor_key"]: r["source_rows"] for r in result},
                         {"ACME": "2;10", "BETA": "3;7"})

    def test_category_bucket_citations_are_independent(self):
        result = report([row(11, category="Travel"), row(9),
                         row(2, category="Travel"), row(3)])
        self.assertEqual({r["category"]: r["source_rows"] for r in result},
                         {"Travel": "2;11", "Supplies": "3;9"})

    def test_month_bucket_citations_are_independent(self):
        result = report([row(10, date="2026-12-01"), row(9),
                         row(2, date="2026-12-03"), row(3)])
        self.assertEqual({r["month"]: r["source_rows"] for r in result},
                         {"2026-11": "3;9", "2026-12": "2;10"})

    def test_input_records_remain_unchanged(self):
        rows = [row(9), row(2)]
        snapshot = [item.copy() for item in rows]
        report(rows)
        self.assertEqual(rows, snapshot)

    def test_duplicate_source_row_remains_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate spend physical CSV row"):
            report([row(2), row(2)])

    def test_hostile_decimal_context_cannot_change_order(self):
        with localcontext() as context:
            context.prec = 2
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            result = report([row(10), row(2), row(9)])
        self.assertEqual(result[0]["source_rows"], "2;9;10")
        self.assertEqual(result[0]["amount"], "3.00")


if __name__ == "__main__":
    unittest.main()
