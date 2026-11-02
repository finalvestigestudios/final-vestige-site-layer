"""Fail-closed, local-only replay of four free desktop reports against their sources.

Re-running the current trusted engine can detect report edits and incorrect
source/settings selections. This is NOT a signature, source authenticity proof,
compliance conclusion, or a replacement for human review. In particular, a
header-only financial CSV has no row-bound source fingerprint: HOLD rather
than certify it from coincidentally identical header bytes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .manifest_guard import _hash_regular, MAX_INPUT_BYTES, MAX_REPORT_BYTES
from .csv_snapshot import read_csv_snapshot
from .policy_diff import MAX_POLICY_BYTES

_SOURCE_COUNTS = {
    "ledger-diff": 2,
    "invoice-twins": 1,
    "spend-map": 1,
    "policy-delta": 2,
}


@dataclass(frozen=True)
class ReplayReceipt:
    """Source-byte and report-byte SHA-256 values, not a signed attestation."""
    kind: str
    report_sha256: str
    source_sha256: tuple[str, ...]


def _require_financial_rows(generated: Path) -> None:
    """Do not call an empty, header-only CSV source-bound evidence."""
    with generated.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        if not next(reader, None):
            raise ValueError("Missing financial report header")
        for record in reader:
            if record:
                return
    raise ValueError("No source-bound review rows; verify the original sources manually")



def _snapshot_sources_for_replay(
    sources: tuple[Path, ...],
    custody_hashes: tuple[tuple[str, tuple[int, int, int, int, int]], ...],
    maximum: int,
    private_root: Path,
) -> tuple[Path, ...]:
    """Run engines only on private copies of the *already hashed* source bytes.

    Reopening original paths during replay allows a file to change between
    the custody hash and engine parsing. A later path recheck still detects
    ordinary mutations, but the engine should never depend on those mutable
    paths. The copy must match the original pre-replay SHA-256, or HOLD.
    Subdirectories preserve original basenames (Policy Delta reports them)
    without colliding when two sources have the same filename.
    """
    copies: list[Path] = []
    for index, (source, observed) in enumerate(zip(sources, custody_hashes)):
        raw = read_csv_snapshot(source, maximum)
        if hashlib.sha256(raw).hexdigest() != observed[0]:
            raise ValueError("Selected evidence changed before replay snapshot")
        private_slot = private_root / f"source-{index}"
        private_slot.mkdir()
        snapshot = private_slot / source.name
        snapshot.write_bytes(raw)
        copied_hash, _ = _hash_regular(snapshot, maximum)
        if copied_hash != observed[0]:
            raise ValueError("Private replay source does not match the custody hash")
        copies.append(snapshot)
    return tuple(copies)


def verify_report(
    kind: str, report: str | os.PathLike[str],
    sources: Sequence[str | os.PathLike[str]], *,
    window_days: int = 7,
    left_match_column: str | None = None,
    right_match_column: str | None = None,
    left_amount_column: str | None = None,
    right_amount_column: str | None = None,
) -> ReplayReceipt:
    """Rebuild one free-product report and compare exact bytes, never modifying inputs.

    A verified match only establishes reproducibility under THIS engine version,
    input selection, and option set. It is not a guarantee that the data is
    accurate, the algorithm correct, or a decision legally/commercially valid.

    Sources and report are checked by descriptor before/after the private
    replay. All failures HOLD; no customer bytes are printed or transmitted.
    """
    if type(kind) is not str or kind not in _SOURCE_COUNTS:
        raise ValueError("Unsupported free report type; premium verification is not available")
    if not isinstance(sources, (tuple, list)) or len(sources) != _SOURCE_COUNTS[kind]:
        raise ValueError("Incorrect number of original source files")
    if type(window_days) is not int or not 0 <= window_days <= 365:
        raise ValueError("Invoice window must be an integer from 0 to 365")
    if kind != "invoice-twins" and window_days != 7:
        raise ValueError("Invoice window is not applicable to this report")
    mapping = (left_match_column, right_match_column,
               left_amount_column, right_amount_column)
    if kind != "ledger-diff" and any(value is not None for value in mapping):
        raise ValueError("Ledger column options are not applicable to this report")
    if any(value is not None and type(value) is not str for value in mapping):
        raise ValueError("Ledger columns must be strings")

    try:
        original = Path(report)
        inputs = tuple(Path(source) for source in sources)
    except (TypeError, ValueError):
        raise ValueError("Report and sources must be local filesystem paths") from None
    required_suffix = ".txt" if kind == "policy-delta" else ".csv"
    if original.suffix.lower() != required_suffix:
        raise ValueError("Report extension does not match the selected product")

    source_cap = MAX_POLICY_BYTES if kind == "policy-delta" else MAX_INPUT_BYTES
    source_before = tuple(_hash_regular(source, source_cap) for source in inputs)
    original_before = _hash_regular(original, MAX_REPORT_BYTES)

    # Import locally only. There is no telemetry, network call, or premium engine.
    from . import engine

    with tempfile.TemporaryDirectory(prefix="fvs-local-replay-") as private:
        # Bind engine reads to descriptor-verified bytes, not mutable originals.
        # Source/report pathname custody is independently rechecked below.
        replay_inputs = _snapshot_sources_for_replay(
            inputs, source_before, source_cap, Path(private))
        if kind == "ledger-diff":
            generated = engine.ledger_diff(
                replay_inputs[0], replay_inputs[1], private,
                left_match_column=left_match_column,
                right_match_column=right_match_column,
                left_amount_column=left_amount_column,
                right_amount_column=right_amount_column)
        elif kind == "invoice-twins":
            generated = engine.invoice_twins(replay_inputs[0], private, window_days=window_days)
        elif kind == "spend-map":
            generated = engine.spend_map(replay_inputs[0], private)
        else:
            generated = engine.policy_delta(replay_inputs[0], replay_inputs[1], private)
        if len(generated) != 1:
            raise ValueError("Unexpected report count; replay cannot be certified")
        comparison = Path(generated[0])
        if comparison.suffix.lower() != required_suffix:
            raise ValueError("Generated report type differs from the selected product")
        if kind != "policy-delta":
            _require_financial_rows(comparison)
        generated_digest, _ = _hash_regular(comparison, MAX_REPORT_BYTES)

    # Every input and the observed original report must remain the same file
    # with the same bytes/metadata throughout regeneration. A changed path,
    # symlink, or changed metadata is a HOLD even if bytes happen to match.
    source_after = tuple(_hash_regular(source, source_cap) for source in inputs)
    original_after = _hash_regular(original, MAX_REPORT_BYTES)
    if source_after != source_before or original_after != original_before:
        raise ValueError("Evidence changed during replay; no verified result")
    if generated_digest != original_before[0]:
        raise ValueError("Report differs from a fresh local source replay")
    return ReplayReceipt(
        kind=kind, report_sha256=original_before[0],
        source_sha256=tuple(result[0] for result in source_before))


class _PrivateArgumentParser(argparse.ArgumentParser):
    """Turn argparse diagnostics into a caller-safe error.

    Standard argparse embeds the rejected value or option in stderr. An invalid
    invoice window, unknown flag or product identifier can be an actual client
    filename, financial cell or secret passed by mistake. Do not echo it.
    --help retains its standard, static usage output and successful exit.
    """

    def error(self, message: str) -> None:
        raise ValueError("Private replay command arguments rejected") from None


def main(argv: Sequence[str] | None = None) -> int:
    """Privacy-preserving CLI; never echo paths, financial cells or exceptions."""
    parser = _PrivateArgumentParser(
        description="Offline exact-byte replay for four free Final Vestige Labs reports; not compliance approval.")
    parser.add_argument("--kind", required=True, choices=tuple(_SOURCE_COUNTS))
    parser.add_argument("--report", required=True)
    parser.add_argument("--source", required=True, action="append")
    parser.add_argument("--window-days", type=int, default=7)
    parser.add_argument("--left-match-column")
    parser.add_argument("--right-match-column")
    parser.add_argument("--left-amount-column")
    parser.add_argument("--right-amount-column")
    try:
        # Parse inside the privacy boundary: otherwise argparse exposes
        # rejected customer-supplied values and exits before generic HOLD.
        args = parser.parse_args(argv)
        receipt = verify_report(
            args.kind, args.report, args.source,
            window_days=args.window_days,
            left_match_column=args.left_match_column,
            right_match_column=args.right_match_column,
            left_amount_column=args.left_amount_column,
            right_amount_column=args.right_amount_column)
    except (ValueError, OSError, TypeError, csv.Error, UnicodeError):
        print("REPLAY HOLD: selected report and sources cannot be verified under the current local engine.", file=sys.stderr)
        return 1
    print("LOCAL REPLAY VERIFIED (not a signature or compliance determination): "
          f"kind={receipt.kind} report_sha256={receipt.report_sha256} "
          f"source_count={len(receipt.source_sha256)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
