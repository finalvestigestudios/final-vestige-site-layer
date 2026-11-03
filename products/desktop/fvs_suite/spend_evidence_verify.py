"""R155 offline verification of SpendMap vendor/month evidence membership.

Unlike exact report replay, checks source-line membership independently of
financial totals or the report-generator's digest helper. This is NOT an audit,
a validation of reported monetary values, a signature, or payment approval.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .csv_snapshot import read_csv_snapshot
from .manifest_guard import _hash_regular, MAX_INPUT_BYTES, MAX_REPORT_BYTES
from .spend_input import validated_spend_rows

LIMIT = 32
DOMAIN = b"FVS-SPEND-VENDOR-MONTH-LINES-v1\n"
REQUIRED = frozenset((
    "vendor_key", "month", "category", "source_rows", "source_sha256",
    "vendor_month_evidence_rows", "vendor_month_evidence_count",
    "vendor_month_evidence_omitted", "vendor_month_evidence_sha256",
))


@dataclass(frozen=True)
class MembershipReceipt:
    source_sha256: str
    report_sha256: str
    groups_verified: int
    buckets_verified: int


def _digest(source_sha: str, vendor: str, month: str, lines: list[int]) -> str:
    """Independently recompute the documented R154 ASCII wire format."""
    parts = [DOMAIN, source_sha.encode("ascii") + b"\n",
             vendor.encode("ascii") + b"\n", month.encode("ascii") + b"\n",
             str(len(lines)).encode("ascii") + b"\n"]
    hasher = hashlib.sha256()
    for part in parts:
        hasher.update(part)
    for row in lines:
        hasher.update(str(row).encode("ascii") + b"\n")
    return hasher.hexdigest()


def verify_membership(source: str | Path, report: str | Path) -> MembershipReceipt:
    """Check all source groups, each category bucket, and report evidence fields.

    Hash/metadata pin originals, process a private copy of pinned source bytes,
    and recheck both selected original paths afterward. Fail closed on empty
    sources: a header-only report contains no embedded source digest.
    """
    from . import engine
    source_path, report_path = Path(source), Path(report)
    if source_path.suffix.lower() != ".csv" or report_path.suffix.lower() != ".csv":
        raise ValueError("Expected two local CSV files")
    before_source = _hash_regular(source_path, MAX_INPUT_BYTES)
    before_report = _hash_regular(report_path, MAX_REPORT_BYTES)
    source_bytes = read_csv_snapshot(source_path, MAX_INPUT_BYTES)
    report_bytes = read_csv_snapshot(report_path, MAX_REPORT_BYTES)
    if (hashlib.sha256(source_bytes).hexdigest() != before_source[0]
            or hashlib.sha256(report_bytes).hexdigest() != before_report[0]):
        raise ValueError("Selected source or report changed before verification")

    with tempfile.TemporaryDirectory(prefix="fvs-spend-membership-") as folder:
        copy = Path(folder) / "spend.csv"
        copy.write_bytes(source_bytes)
        records, parsed_sha = engine.table(
            copy, ("vendor", "amount", "date"), ("category",),
            include_digest=True)
        if parsed_sha != before_source[0]:
            raise ValueError("Private source snapshot mismatch")

        groups: dict[tuple[str, str], list[int]] = defaultdict(list)
        buckets: dict[tuple[str, str, str], list[str]] = defaultdict(list)
        for record, vendor, month, category, _amount in validated_spend_rows(
                records, normalize_vendor=engine.key, parse_date=engine.parse_date,
                parse_money=engine.money):
            groups[(vendor, month)].append(int(record["row"]))
            # The CSV exporter protects leading spreadsheet formulas.
            buckets[(vendor, month, engine.safe_cell(category))].append(record["row"])

    if not groups:
        raise ValueError("Header-only report cannot establish source custody")
    expected = {}
    for key, lines in groups.items():
        ordered = sorted(lines)
        expected[key] = (
            ";".join(str(n) for n in ordered[:LIMIT]),
            str(len(ordered)),
            str(max(0, len(ordered) - LIMIT)),
            _digest(before_source[0], key[0], key[1], ordered),
        )
    try:
        decoded = report_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded, newline=""), strict=True)
        headers = reader.fieldnames
        if (headers is None or len(headers) != len(set(headers))
                or not REQUIRED.issubset(headers)):
            raise ValueError("Missing or ambiguous SpendMap evidence columns")
        seen = set()
        for entry in reader:
            if None in entry or any(value is None for value in entry.values()):
                raise ValueError("Malformed SpendMap evidence row")
            bucket = (entry["vendor_key"], entry["month"], entry["category"])
            if bucket in seen or bucket not in buckets:
                raise ValueError("Duplicate or unexpected category evidence")
            seen.add(bucket)
            month_key = bucket[:2]
            preview, count, omitted, digest = expected[month_key]
            if (entry["source_sha256"] != before_source[0]
                    or entry["source_rows"] != ";".join(buckets[bucket])
                    or entry["vendor_month_evidence_rows"] != preview
                    or entry["vendor_month_evidence_count"] != count
                    or entry["vendor_month_evidence_omitted"] != omitted
                    or entry["vendor_month_evidence_sha256"] != digest):
                raise ValueError("SpendMap group evidence does not match source")
    except (UnicodeError, csv.Error, OverflowError) as exc:
        raise ValueError("Malformed local SpendMap evidence") from None
    if seen != set(buckets):
        raise ValueError("SpendMap source category evidence is incomplete")
    if (_hash_regular(source_path, MAX_INPUT_BYTES) != before_source
            or _hash_regular(report_path, MAX_REPORT_BYTES) != before_report):
        raise ValueError("Selected evidence changed during verification")
    return MembershipReceipt(before_source[0], before_report[0],
                             len(groups), len(buckets))


class _PrivateParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, allow_abbrev=False, **kwargs)

    def error(self, message: str) -> None:
        raise ValueError("Invalid private verification arguments")

    def parse_args(self, args: Sequence[str] | None = None, namespace=None):
        tokens = list(sys.argv[1:] if args is None else args)
        if len(tokens) == 1 and tokens[0] in ("--help", "-h"):
            return super().parse_args(tokens, namespace)
        options = [t.partition("=")[0] for t in tokens]
        if (any(type(t) is not str for t in tokens)
                or any(options.count(flag) != 1 for flag in ("--source", "--report"))
                or "--" in tokens
                or ("--help" in tokens or "-h" in tokens) and len(tokens) != 1):
            raise ValueError("Invalid private verification arguments")
        return super().parse_args(tokens, namespace)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _PrivateParser(
        description="Offline SpendMap source-line evidence membership check; not a compliance audit.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--report", required=True)
    try:
        args = parser.parse_args(argv)
        receipt = verify_membership(args.source, args.report)
    except Exception:
        print("SPEND MEMBERSHIP HOLD: selected local evidence cannot be verified.",
              file=sys.stderr)
        return 1
    print(f"SPEND MEMBERSHIP VERIFIED (not financial audit or signature): "
          f"groups={receipt.groups_verified} buckets={receipt.buckets_verified} "
          f"source_sha256={receipt.source_sha256} report_sha256={receipt.report_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
