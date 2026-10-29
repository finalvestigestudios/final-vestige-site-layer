"""Read-only, offline verification of ProcureGuard evidence packages.

Checks current file bytes, not provenance/authenticity of an unpinned inventory.
An independently retained SHA-256 pin can anchor inventory bytes. Results
never authorize a payment, procurement decision, or regulatory compliance.
"""
from __future__ import annotations

import argparse
import re
import stat
from pathlib import Path
from typing import Sequence

from .csv_snapshot import read_csv_snapshot
from .grant_anchor import verify_inventory_pin
from .manifest_guard import inventory_text

MAX_INVENTORY_BYTES = 64 * 1024
MAX_POLICY_BYTES = 8 * 1024
_STAMP = r"[0-9]{8}-[0-9]{6}-[0-9]{6}"
_REPORT_NAME = re.compile(rf"procurement-three-way-{_STAMP}\.csv\Z")
_INVENTORY_NAME = re.compile(rf"evidence-manifest-{_STAMP}\.txt\Z")


def _folder_signature(folder: Path) -> tuple[int, int, int, int, int]:
    info = folder.lstat()  # Do not follow a symlink to someone else's bundle.
    if not stat.S_ISDIR(info.st_mode):
        raise ValueError("Procurement evidence must be a real directory")
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def verify_procurement_bundle(
    package: str | Path,
    purchase_orders: str | Path,
    invoices: str | Path,
    receipts: str | Path,
    *,
    price_policy: str | Path | None = None,
    expected_inventory_sha256: str | None = None,
) -> bool:
    """Check the exact R35 package, original inputs, and optional JSON policy.

    Files must be supplied in original purchase-order, invoice, receipt order,
    with original basenames. Specify the same policy JSON used for reconciliation
    (or omit it when the built-in policy was used). If the pin comes from inside
    the bundle, it gives no authenticity protection. No inputs are written.
    """
    folder = Path(package)
    try:
        before = _folder_signature(folder)
        members = list(folder.iterdir())
        if len(members) != 2:
            raise ValueError("Procurement evidence requires exactly two files")
        report_matches = [p for p in members if _REPORT_NAME.fullmatch(p.name)]
        inventory_matches = [p for p in members if _INVENTORY_NAME.fullmatch(p.name)]
        if len(report_matches) != 1 or len(inventory_matches) != 1:
            raise ValueError("Procurement evidence has an unexpected file layout")
        for member in members:
            if not stat.S_ISREG(member.lstat().st_mode):
                raise ValueError("Procurement evidence contains a link or non-file")
        report, inventory = report_matches[0], inventory_matches[0]
        inventory_bytes = read_csv_snapshot(inventory, MAX_INVENTORY_BYTES)
        if expected_inventory_sha256 is not None:
            verify_inventory_pin(inventory_bytes, expected_inventory_sha256)
        sources = [Path(purchase_orders), Path(invoices), Path(receipts)]
        if price_policy is not None and str(price_policy).strip():
            policy = Path(price_policy)
            if policy.suffix.lower() != ".json":
                raise ValueError("Procurement price policy must be a JSON file")
            # R35 parsed policies through an 8 KiB descriptor-verified snapshot;
            # reject verification of a policy that could not have been parsed.
            read_csv_snapshot(policy, MAX_POLICY_BYTES)
            sources.append(policy)
        expected = inventory_text(sources, [report]).encode("utf-8")
        if inventory_bytes != expected:
            raise ValueError("Procurement SHA-256 inventory does not match current files")
        if read_csv_snapshot(inventory, MAX_INVENTORY_BYTES) != inventory_bytes:
            raise ValueError("Procurement evidence inventory changed during verification")
        if _folder_signature(folder) != before or set(folder.iterdir()) != set(members):
            raise ValueError("Procurement evidence package changed during verification")
    except (OSError, ValueError, UnicodeError) as exc:
        # Deliberately never leak user-provided paths or financial contents.
        permitted = (
            "Procurement evidence must", "Procurement evidence requires",
            "Procurement evidence has", "Procurement evidence contains",
            "Procurement price policy must", "Procurement SHA-256 inventory",
            "Procurement evidence inventory changed", "Procurement evidence package changed",
            "Invalid trusted inventory SHA-256 pin", "Trusted inventory SHA-256 pin",
        )
        if isinstance(exc, ValueError) and str(exc).startswith(permitted):
            raise ValueError(str(exc)) from None
        raise ValueError("Unable to verify ProcureGuard evidence package") from None
    return True


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check current ProcureGuard evidence bytes; no payment approval."
    )
    parser.add_argument("--price-policy", metavar="JSON",
                        help="Original custom policy JSON (omit if built-in policy was used)")
    parser.add_argument("--expected-inventory-sha256", metavar="HEX",
                        help="64 lowercase hex characters retained outside the evidence package")
    parser.add_argument("package", help="R35 procurement evidence directory")
    parser.add_argument("purchase_orders", help="Original purchase-order CSV")
    parser.add_argument("invoices", help="Original invoice CSV")
    parser.add_argument("receipts", help="Original receipt CSV")
    options = parser.parse_args(argv)
    try:
        verify_procurement_bundle(
            options.package, options.purchase_orders, options.invoices, options.receipts,
            price_policy=options.price_policy,
            expected_inventory_sha256=options.expected_inventory_sha256,
        )
    except ValueError:
        print("INVALID: procurement evidence does not match selected files or trusted pin")
        return 1
    if options.expected_inventory_sha256 is None:
        print("CONSISTENT (UNPINNED): editable inventory only; no authenticity anchor; human review required")
    else:
        print("CONSISTENT (PINNED): independent SHA-256 inventory pin matches; human review required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
