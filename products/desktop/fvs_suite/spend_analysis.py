"""Deterministic source provenance and collision review for SpendMap Lite.

The matching key is intentionally lossy; distinct original vendor spellings
must not be silently represented as a verified identity. A spike is a review
flag, not a finding of fraud, incorrect spending, or noncompliance.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from decimal import Context, Decimal, localcontext
from functools import wraps
import re
from typing import Callable, Mapping

from .review import ascii_case_identity, labels_for_report, normalized_collision, raw_values
from .spend_median import RunningDecimalMedian
from .spend_input import validated_spend_rows

VENDOR_MONTH_EVIDENCE_LIMIT = 32  # Bounded preview; full evidence is in SHA-bound source.


def _vendor_month_line_digest(source_sha256: str, vendor: str, month: str,
                              ordered_lines: list[int]) -> str:
    """Domain-separated full-membership fingerprint; not a signature or source proof.

    Inputs are ASCII from the strict source-digest, normalized-vendor, month,
    and canonical physical-row validators. Include the source SHA and group key
    so equal line positions from different files/groups cannot masquerade as
    equal evidence. A bounded report preview NEVER replaces this full digest.
    """
    digest = sha256(b"FVS-SPEND-VENDOR-MONTH-LINES-v1\\n")
    for element in (source_sha256, vendor, month, str(len(ordered_lines))):
        digest.update(element.encode("ascii") + b"\\n")
    for line in ordered_lines:
        digest.update(str(line).encode("ascii") + b"\\n")
    return digest.hexdigest()


def _exact_spend_context(operation):
    """Make capped 200k-row fixed-point aggregation independent of caller context."""
    @wraps(operation)
    def guarded(*args, **kwargs):
        # A fresh private context also isolates caller-specific traps and Emax.
        # Per amount <= 1e12, cents; 200k rows, < 22 significant aggregate digits.
        with localcontext(Context(prec=64)):
            return operation(*args, **kwargs)
    return guarded


@_exact_spend_context
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
    # A net total can hide large purchases offset by credits or refunds.
    # Keep charges and credit magnitudes separately, in exact Decimal cents.
    # Do not treat either a matched sign or a refund as a compliance finding.
    gross_charges: dict[tuple[str, str, str], Decimal] = defaultdict(lambda: Decimal(0))
    gross_credits: dict[tuple[str, str, str], Decimal] = defaultdict(lambda: Decimal(0))
    # Per-vendor/month gross figures reveal cross-category credits obscuring charges.
    vendor_month_charges: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: defaultdict(lambda: Decimal(0)))
    vendor_month_credits: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: defaultdict(lambda: Decimal(0)))
    vendor_month_lines: dict[tuple[str, str], list[int]] = defaultdict(list)
    members: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    vendor_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    monthly: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: defaultdict(lambda: Decimal(0)))
    # Category baselines are independent of the vendor-wide spike signal.
    # Never normalize categories or manufacture missing calendar months.
    category_monthly: dict[tuple[str, str], dict[str, Decimal]] = defaultdict(
        lambda: defaultdict(lambda: Decimal(0)))

    for record, vendor, month, category, amount in validated_spend_rows(
            records, normalize_vendor=normalize_vendor,
            parse_date=parse_date, parse_money=parse_money):
        bucket = (vendor, month, category)
        vendor_month_lines[(vendor, month)].append(int(record["row"]))
        totals[bucket] += amount
        if amount > 0:
            gross_charges[bucket] += amount
            vendor_month_charges[vendor][month] += amount
        elif amount < 0:
            # copy_negate never rounds the original Decimal under hostile
            # caller contexts; this magnitude is not a new source amount.
            credit = amount.copy_negate()
            gross_credits[bucket] += credit
            vendor_month_credits[vendor][month] += credit
        monthly[vendor][month] += amount
        category_monthly[(vendor, category)][month] += amount
        members[bucket].append(record)
        vendor_rows[vendor].append(record)

    # The existing category-only source_rows cannot attest to cross-category
    # vendor/month gross totals. Preview numeric physical lines across all
    # categories; count omitted rows instead of silently claiming full coverage.
    # Sorted once per group, bounded by the global 200,000-record import cap.
    # The export still previews ONLY the earliest 32 physical start lines;
    # hash every contributing line in numeric order, including omitted lines.
    month_evidence = {}
    for (vendor, month), lines in vendor_month_lines.items():
        ordered = sorted(lines)
        month_evidence[(vendor, month)] = (
            ";".join(str(line) for line in ordered[:VENDOR_MONTH_EVIDENCE_LIMIT]),
            str(len(ordered)),
            str(max(0, len(ordered) - VENDOR_MONTH_EVIDENCE_LIMIT)),
            _vendor_month_line_digest(source_sha256, vendor, month, ordered),
        )

    collision = {vendor: normalized_collision(rows, "vendor")
                 for vendor, rows in vendor_rows.items()}
    variant_counts = {
        vendor: len({ascii_case_identity(name) for name in raw_values(rows, "vendor")})
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

    # A category spike can be hidden by a fall in another category even when
    # vendor-wide month totals do not change. Separate transparent evidence
    # lets a human reviewer identify that pattern without changing legacy flags.
    category_history: dict[tuple[str, str, str], tuple[int, Decimal | None, bool]] = {}
    for (vendor, category), months in category_monthly.items():
        prior = RunningDecimalMedian()
        for month, total in sorted(months.items()):
            baseline = prior.median() if len(prior) >= 3 else None
            spike = baseline is not None and baseline > 0 and total >= 2 * baseline
            category_history[(vendor, month, category)] = (len(prior), baseline, spike)
            prior.add(total)

    report = []
    for bucket in sorted(totals):
        vendor, month, category = bucket
        rows = members[bucket]
        count, baseline, spike = history[(vendor, month)]
        category_count, category_baseline, category_spike = category_history[bucket]
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
            "gross_charges": format_money(gross_charges[bucket]),
            "gross_credits": format_money(gross_credits[bucket]),
            "credit_offset_review": (
                "review_mixed_sign_offset"
                if gross_charges[bucket] > 0 and gross_credits[bucket] > 0 else ""),
            "vendor_month_evidence_rows": month_evidence[(vendor, month)][0],
            "vendor_month_evidence_count": month_evidence[(vendor, month)][1],
            "vendor_month_evidence_omitted": month_evidence[(vendor, month)][2],
            "vendor_month_evidence_sha256": month_evidence[(vendor, month)][3],
            "vendor_month_gross_charges": format_money(vendor_month_charges[vendor][month]),
            "vendor_month_gross_credits": format_money(vendor_month_credits[vendor][month]),
            "vendor_month_offset_review": (
                "review_vendor_month_mixed_sign_offset"
                if vendor_month_charges[vendor][month] > 0
                and vendor_month_credits[vendor][month] > 0 else ""),
            "flag": ";".join(flags),
            "vendor_month_total": format_money(monthly[vendor][month]),
            # An even-sized median may be half a cent; do not round evidence.
            "baseline_median": "" if baseline is None else format(baseline, "f"),
            "history_months": str(count),
            "category_history_months": str(category_count),
            "category_baseline_median": (
                "" if category_baseline is None else format(category_baseline, "f")),
            "category_review_flag": "review_category_spike" if category_spike else "",
            "source_rows": ";".join(row["row"] for row in rows),
            "source_vendor_labels": labels_for_report(rows, "vendor"),
            "vendor_label_variants": str(variant_counts[vendor]),
            "source_sha256": source_sha256,
        })
    return report
