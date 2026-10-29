"""Offline, read-only consistency check for published GrantAudit evidence bundles.

This compares the *current bytes* of three operator-selected source CSV files
and the two reports against the published SHA-256 inventory. It cannot prove
who created the inventory, prevent edits after verification, or approve a claim.
"""
from __future__ import annotations

import argparse
import re
import stat
from pathlib import Path
from typing import Sequence

from .csv_snapshot import read_csv_snapshot
from .manifest_guard import inventory_text

MAX_INVENTORY_BYTES = 64 * 1024
_STAMP = r"[0-9]{8}-[0-9]{6}-[0-9]{6}"
_PATTERNS = (
    re.compile(rf"grant-audit-exceptions-{_STAMP}\.csv\Z"),
    re.compile(rf"grant-budget-check-{_STAMP}\.csv\Z"),
    re.compile(rf"evidence-manifest-{_STAMP}\.txt\Z"),
)


def _directory_signature(path: Path) -> tuple[int, int, int, int, int]:
    """Reject linked/replaced folders and ordinary concurrent folder edits."""
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode):
        raise ValueError("Evidence package must be a real directory")
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def verify_grant_bundle(
    package: str | Path, claims: str | Path, ledger: str | Path,
    budgets: str | Path,
) -> bool:
    """Check exact R32 bundle structure and all five SHA-256 inventory entries.

    Inputs must be supplied in claims, ledger, budgets order, and must have
    their original basenames. Returns True only when the inventory exactly
    describes their *present* bytes and both published report files.

    Error messages intentionally omit source paths and financial content.
    Read-only, bounded, symlink-rejecting, and fail-closed on ambiguity.
    """
    folder = Path(package)
    try:
        before = _directory_signature(folder)
        members = list(folder.iterdir())
        if len(members) != 3:
            raise ValueError("Evidence package must contain exactly three files")
        # Generated names are unique by stem. No glob partial matches and no
        # sorting by unrelated timestamps: each of the three must match once.
        matched: list[Path] = []
        for pattern in _PATTERNS:
            found = [path for path in members if pattern.fullmatch(path.name)]
            if len(found) != 1:
                raise ValueError("Evidence package has an unexpected file layout")
            matched.append(found[0])
        for path in members:
            if not stat.S_ISREG(path.lstat().st_mode):
                raise ValueError("Evidence package contains a link or non-file")
        exceptions, budget_review, inventory = matched
        first_inventory = read_csv_snapshot(inventory, MAX_INVENTORY_BYTES)
        actual_inventory = inventory_text(
            [Path(claims), Path(ledger), Path(budgets)],
            [exceptions, budget_review],
        ).encode("utf-8")
        if first_inventory != actual_inventory:
            raise ValueError("SHA-256 evidence inventory does not match current files")
        # Reject an inventory rewritten while the other files were rehashed.
        if read_csv_snapshot(inventory, MAX_INVENTORY_BYTES) != first_inventory:
            raise ValueError("Evidence inventory changed during verification")
        if _directory_signature(folder) != before or set(folder.iterdir()) != set(members):
            raise ValueError("Evidence package changed during verification")
    except (OSError, ValueError, UnicodeError) as exc:
        # Never include private original paths or raw source values in errors.
        if isinstance(exc, ValueError) and exc.args and str(exc).startswith((
            "Evidence package must", "Evidence package has", "Evidence package contains",
            "SHA-256 evidence", "Evidence inventory changed", "Evidence package changed"
        )):
            raise ValueError(str(exc)) from None
        raise ValueError("Unable to verify GrantAudit evidence package") from None
    return True


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify the current contents of a GrantAudit evidence package (not an approval)."
    )
    parser.add_argument("package", help="GrantAudit evidence directory")
    parser.add_argument("claims", help="Original claims CSV")
    parser.add_argument("ledger", help="Original ledger CSV")
    parser.add_argument("budgets", help="Original budgets CSV")
    options = parser.parse_args(argv)
    try:
        verify_grant_bundle(options.package, options.claims, options.ledger, options.budgets)
    except ValueError:
        print("INVALID: evidence package does not match selected source and report files")
        return 1
    print("CONSISTENT: current evidence bytes match the inventory; human review still required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
