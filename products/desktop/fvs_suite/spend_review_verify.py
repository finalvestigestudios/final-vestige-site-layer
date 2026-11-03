"""R157 independent SpendMap historical review-evidence verification.

No imports from the SpendMap report summarizer, its streaming median, or its
review-flag helpers. These are reproducibility checks, NOT fraud findings.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Context, Decimal, localcontext
from heapq import heappop, heappush
from typing import Iterable


FIELDS = frozenset((
    "flag", "baseline_median", "history_months",
    "category_history_months", "category_baseline_median",
    "category_review_flag", "vendor_label_variants",
))
_ASCII_LOWER = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"
)
_ZERO = Decimal("0.00")
_TWO = Decimal("2")


class _IndependentMedian:
    """Independent two-heap exact-Decimal median, O(log n) insertion.

    Negated lower heap supplies max-heap behavior. It deliberately does not
    import SpendMap's production RunningDecimalMedian implementation.
    """

    def __init__(self) -> None:
        self.low: list[Decimal] = []
        self.high: list[Decimal] = []

    def __len__(self) -> int:
        return len(self.low) + len(self.high)

    def add(self, value: Decimal) -> None:
        if not self.low or value <= -self.low[0]:
            heappush(self.low, -value)
        else:
            heappush(self.high, value)
        if len(self.low) > len(self.high) + 1:
            heappush(self.high, -heappop(self.low))
        elif len(self.high) > len(self.low):
            heappush(self.low, -heappop(self.high))

    def median(self) -> Decimal:
        if not self.low:
            raise ValueError("Empty history has no median")
        if len(self.low) == len(self.high):
            return (-self.low[0] + self.high[0]) / _TWO
        return -self.low[0]


def _history(months: dict[str, Decimal]) -> dict[str, tuple[str, str, bool]]:
    result = {}
    seen = _IndependentMedian()
    for month in sorted(months):
        baseline = seen.median() if len(seen) >= 3 else None
        spike = (baseline is not None and baseline > _ZERO
                 and months[month] >= _TWO * baseline)
        result[month] = (
            str(len(seen)),
            "" if baseline is None else format(baseline, "f"),
            spike,
        )
        seen.add(months[month])
    return result


def compute_expected_review_fields(
    observations: Iterable[tuple[str, str, str, Decimal, str]],
) -> dict[tuple[str, str, str], dict[str, str]]:
    """Recompute historic spike and vendor-collision review metadata.

    Each input is (normalized vendor, observed YYYY-MM, export-safe category,
    validated exact cents, original source vendor label). Caller pins the
    original file bytes and validates every record before calling.

    Historical baselines use previous *observed* months only (no interpolation).
    Exact half-cent medians are preserved rather than rounded for display.
    An independent private Decimal context prevents a hostile ambient precision
    or trap configuration from silently suppressing review thresholds.
    """
    with localcontext(Context(prec=64)):
        month_net: dict[tuple[str, str], Decimal] = defaultdict(lambda: _ZERO)
        category_net: dict[tuple[str, str, str], Decimal] = defaultdict(lambda: _ZERO)
        variants: dict[str, set[str]] = defaultdict(set)
        for vendor, month, category, amount, source_label in observations:
            month_net[(vendor, month)] += amount
            category_net[(vendor, month, category)] += amount
            if source_label.strip():
                # ASCII case alone is a safe identity equivalence. Unicode
                # casefold could conceal visually meaningful label changes.
                variants[vendor].add(source_label.strip().translate(_ASCII_LOWER))

        by_vendor: dict[str, dict[str, Decimal]] = defaultdict(dict)
        for (vendor, month), total in month_net.items():
            by_vendor[vendor][month] = total
        vendor_history = {
            (vendor, month): metrics
            for vendor, months in by_vendor.items()
            for month, metrics in _history(months).items()
        }

        by_category: dict[tuple[str, str], dict[str, Decimal]] = defaultdict(dict)
        for (vendor, month, category), total in category_net.items():
            by_category[(vendor, category)][month] = total
        category_history = {
            (vendor, month, category): metrics
            for (vendor, category), months in by_category.items()
            for month, metrics in _history(months).items()
        }

        expectations = {}
        for bucket in category_net:
            vendor, month, _ = bucket
            h_count, baseline, spike = vendor_history[(vendor, month)]
            c_count, c_baseline, c_spike = category_history[bucket]
            collision = len(variants[vendor]) > 1
            flags = []
            if spike:
                flags.append("review_spike")
            if collision:
                flags.append("normalized_vendor_collision_review")
            expectations[bucket] = {
                "flag": ";".join(flags),
                "baseline_median": baseline,
                "history_months": h_count,
                "category_history_months": c_count,
                "category_baseline_median": c_baseline,
                "category_review_flag": "review_category_spike" if c_spike else "",
                "vendor_label_variants": str(len(variants[vendor])),
            }
        return expectations
