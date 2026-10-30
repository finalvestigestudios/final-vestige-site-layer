"""Deterministic source provenance and collision review for SpendMap Lite.

The matching key is intentionally lossy; distinct original vendor spellings
must not be silently represented as a verified identity. A spike is a review
flag, not a finding of fraud, incorrect spending, or noncompliance.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
import re
from typing import Callable, Mapping

from .review import labels_for_report, normalized_collision, raw_values
from .spend_median import RunningDecimalMedian
from .spend_input import validated_spend_rows


def summarize_spend(
    records: list[dict[str, str]], *,
    normalize_vendor: Callable[[str], str],
    parse_date: Callable[[str], object],
    parse_money: Callable[[str], Decimal],
    format_money: Callable[[Decimal], str],
    source_sha256: str,
) -> list[dict[str, str]]:
    """Summarize already-validated CSV rows with reversible source references.

    Each bucket retains its physical CSV line numbers and local original
    vendor spellings. A vendor-wide normalization collision is flagged in
    *every* affected bucket, even if variants appear in different months.
    Baselines use prior observed months, not interpolated calendar months.
    Both the CSV reader and this reusable summarizer enforce row safety.
    The source SHA-256 must fingerprint bytes from the SAME imported snapshot.
    It is evidence of source identity, not a digital signature or approval.
    """
    if not isinstance(source_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", source_sha256) is None:
        raise ValueError("Source snapshot SHA-256 must be 64 lowercase hexadecimal characters")

    totals: dict[tuple[str, str, str], Decimal] = defaultdict(lambda: Decimal(0))
    members: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    vendor_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    monthly: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: defaultdict(lambda: Decimal(0)))

    for record, vendor, month, category, amount in validated_spend_rows(
            records, normalize_vendor=normalize_vendor,
            parse_date=parse_date, parse_money=parse_money):
        bucket = (vendor, month, category)
        totals[bucket] += amount
        monthly[vendor][month] += amount
        members[bucket].append(record)
        vendor_rows[vendor].append(record)

    collision = {vendor: normalized_collision(rows, "vendor")
                 for vendor, rows in vendor_rows.items()}
    variant_counts = {
        vendor: len({name.casefold() for name in raw_values(rows, "vendor")})
        for vendor, rows in vendor_rows.items()
    }
    history: dict[tuple[str, str], tuple[int, Decimal | None, bool]] = {}
    for vendor, months in monthly.items():
        prior = RunningDecimalMedian()
        for month, total in sorted(months.items()):
            # Compare against previous observed months only; the current
            # month must not influence its own review threshold.
            baseline = prior.median() if len(prior) >= 3 else None
            spike = baseline is not None and baseline > 0 and total >= 2 * baseline
            history[(vendor, month)] = (len(prior), baseline, spike)
            prior.add(total)

    report = []
    for bucket in sorted(totals):
        vendor, month, category = bucket
        rows = members[bucket]
        count, baseline, spike = history[(vendor, month)]
        flags = []
        if spike:
            flags.append("review_spike")
        if collision[vendor]:
            flags.append("normalized_vendor_collision_review")
        report.append({
            "vendor_key": vendor,
            "month": month,
            "category": category,
            "amount": format_money(totals[bucket]),
            "flag": ";".join(flags),
            "vendor_month_total": format_money(monthly[vendor][month]),
            # An even-sized median may be half a cent; do not round evidence.
            "baseline_median": "" if baseline is None else format(baseline, "f"),
            "history_months": str(count),
            "source_rows": ";".join(row["row"] for row in rows),
            "source_vendor_labels": labels_for_report(rows, "vendor"),
            "vendor_label_variants": str(variant_counts[vendor]),
            "source_sha256": source_sha256,
        })
    return report
