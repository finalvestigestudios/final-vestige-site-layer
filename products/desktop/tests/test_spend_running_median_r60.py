"""R60 SpendMap exact incremental median regression cases (synthetic only)."""
from __future__ import annotations

import re
import unittest
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from statistics import median

from fvs_suite.spend_median import RunningDecimalMedian
from fvs_suite.spend_analysis import summarize_spend


def _normalize(label: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", label.upper())


def _money(raw: str) -> Decimal:
    return Decimal(raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _format(total: Decimal) -> str:
    return format(total.quantize(Decimal("0.01")), ".2f")


def _summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return summarize_spend(rows, normalize_vendor=_normalize,
                           parse_date=date.fromisoformat,
                           parse_money=_money, format_money=_format)


class SpendRunningMedianR60(unittest.TestCase):
    def test_empty_median_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty history"):
            RunningDecimalMedian().median()

    def test_one_two_three_four_month_medians(self):
        history = RunningDecimalMedian()
        for raw, expected in (("10.01", "10.01"), ("10.00", "10.005"),
                              ("9.99", "10.00"), ("20.00", "10.005")):
            history.add(Decimal(raw))
            self.assertEqual(history.median(), Decimal(expected))

    def test_exact_half_cent_large_values(self):
        history = RunningDecimalMedian()
        history.add(Decimal("1000000000000.01"))
        history.add(Decimal("1000000000000.02"))
        self.assertEqual(history.median(), Decimal("1000000000000.015"))

    def test_negative_refunds_zero_and_positive_spend(self):
        history = RunningDecimalMedian()
        for raw in ("-20.00", "0.00", "-1.01", "100.00", "-1.00"):
            history.add(Decimal(raw))
        self.assertEqual(history.median(), Decimal("-1.00"))

    def test_ties_and_rebalancing(self):
        history = RunningDecimalMedian()
        for raw in ("1", "10", "1", "10", "1", "10", "1", "10"):
            history.add(Decimal(raw))
        self.assertEqual(history.median(), Decimal("5.5"))
        self.assertEqual(len(history), 8)

    def test_nondecimal_nonfinite_values_rejected_unchanged(self):
        history = RunningDecimalMedian()
        history.add(Decimal("10"))
        for bad in (10, 1.5, "10", Decimal("NaN"), Decimal("Infinity"),
                    Decimal("-Infinity")):
            with self.subTest(value=repr(bad)), self.assertRaises(ValueError):
                history.add(bad)
        self.assertEqual((len(history), history.median()), (1, Decimal("10")))

    def test_large_bounded_history_matches_reference(self):
        # Tests the release-sized history algorithm without relying on timing.
        history = RunningDecimalMedian()
        observed = []
        for n in range(50000):
            value = Decimal((n * 7919) % 10007 - 5000) / Decimal(100)
            history.add(value)
            observed.append(value)
        self.assertEqual(len(history), 50000)
        self.assertEqual(history.median(), median(observed))

    def test_sequential_medians_match_decimal_reference(self):
        history = RunningDecimalMedian()
        observed = []
        for n in range(75):
            value = Decimal((n * 17) % 23 - 11) / Decimal(100)
            history.add(value)
            observed.append(value)
            self.assertEqual(history.median(), median(observed), f"month {n}")

    def test_independent_vendor_medians(self):
        left, right = RunningDecimalMedian(), RunningDecimalMedian()
        for n in ("1", "2", "3", "4"):
            left.add(Decimal(n))
        for n in ("10", "11", "12"):
            right.add(Decimal(n))
        self.assertEqual(left.median(), Decimal("2.5"))
        self.assertEqual(right.median(), Decimal("11"))

    def test_spendmap_history_excludes_current_month(self):
        rows = [{"row": str(n + 2), "vendor": "ACME", "amount": amount,
                 "date": f"2026-{n+1:02d}-01", "category": "Parts"}
                for n, amount in enumerate(("10", "10", "10", "20", "1"))]
        report = _summary(rows)
        self.assertEqual([r["history_months"] for r in report],
                         ["0", "1", "2", "3", "4"])
        self.assertEqual([r["baseline_median"] for r in report],
                         ["", "", "", "10.00", "10.00"])
        self.assertEqual([r["flag"] for r in report],
                         ["", "", "", "review_spike", ""])

    def test_spendmap_spike_exact_median_and_collision_unchanged(self):
        rows = [{"row": str(n + 2), "vendor": vendor, "amount": amount,
                 "date": f"2026-{n+1:02d}-01", "category": "Parts"}
                for n, (vendor, amount) in enumerate((
                    ("ACME", "10.00"), ("ACME", "10.01"), ("ACME", "10.00"),
                    ("ACME", "10.02"), ("A-CME", "20.01")))]
        report = _summary(rows)
        self.assertEqual(report[-1]["baseline_median"], "10.005")
        self.assertEqual(report[-1]["flag"],
                         "review_spike;normalized_vendor_collision_review")
        self.assertTrue(all("normalized_vendor_collision_review" in r["flag"]
                            for r in report))

    def test_spendmap_many_distinct_observed_months(self):
        rows = []
        for n in range(4800):
            year, month = 1800 + n // 12, n % 12 + 1
            rows.append({"row": str(n + 2), "vendor": "ACME", "amount": "1.00",
                         "date": f"{year:04d}-{month:02d}-01", "category": "Parts"})
        result = _summary(rows)
        self.assertEqual(len(result), 4800)
        self.assertEqual(result[-1]["history_months"], "4799")
        self.assertEqual(result[-1]["baseline_median"], "1.00")
        self.assertEqual(result[-1]["flag"], "")

    def test_repeated_execution_deterministic(self):
        rows = [{"row": "2", "vendor": "A-CME", "amount": "10.00",
                 "date": "2026-01-01", "category": "Parts"},
                {"row": "3", "vendor": "ACME", "amount": "30.00",
                 "date": "2026-02-01", "category": "Other"}]
        self.assertEqual(_summary(rows), _summary(rows))


if __name__ == "__main__":
    unittest.main()
