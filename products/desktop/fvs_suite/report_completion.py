"""Local-only verification of desktop report outputs before announcing success.

This verifies only the GUI's immediately observable output contract, not the
content integrity, provenance or durability of engine reports. It never reads
financial data or writes, deletes, uploads, or retries a destination.
"""
from __future__ import annotations

import os
import re
import stat
from pathlib import Path


_MAX_REPORTS = 16
_NATIVE_PATH_TYPE = type(Path())
# Free engines publish one file immediately under the chosen directory.
# Premium engines publish a complete, ordered manifest-bound evidence bundle.
_FREE_REPORTS = {
    "ledger": ("ledger-diff", ".csv"),
    "invoices": ("invoice-twins", ".csv"),
    "spend": ("spend-map", ".csv"),
    "policy": ("policy-delta", ".txt"),
}
_PREMIUM_REPORTS = {
    "grants": (("grant-audit-exceptions", ".csv"),
               ("grant-budget-check", ".csv"),
               ("evidence-manifest", ".txt")),
    "procurement": (("procurement-three-way", ".csv"),
                    ("evidence-manifest", ".txt")),
}
_REPORT_TIMESTAMP = re.compile(r"[0-9]{8}-[0-9]{6}-[0-9]{6}\Z", re.ASCII)
_BUNDLE_TIMESTAMP = re.compile(r"[0-9]{8}T[0-9]{6}Z-[0-9a-f]{32}\Z", re.ASCII)


def _confirm_output_placement(paths: tuple[Path, ...], folder: str | Path,
                              app_id: str) -> None:
    """Require exactly the app's expected files within the selected destination.

    Match lexical *native* paths, never resolve a forged/linked report into an
    unrelated customer's tree. The report files are also lstat-checked by the
    caller. No data is read and no existing output is modified.
    """
    if type(app_id) is not str:
        raise ValueError("Invalid report product identity")
    if type(folder) is str:
        if not folder.strip():
            raise ValueError("An output directory is required")
        directory = Path(folder)
    elif type(folder) is _NATIVE_PATH_TYPE:
        directory = folder
    else:
        raise ValueError("Invalid output directory")
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError("Output destination must be an existing directory, not a link")

    if app_id in _FREE_REPORTS:
        if len(paths) != 1 or paths[0].parent != directory:
            raise ValueError("Unexpected free report location or inventory")
        expected = (_FREE_REPORTS[app_id],)
    elif app_id in _PREMIUM_REPORTS:
        expected = _PREMIUM_REPORTS[app_id]
        if len(paths) != len(expected):
            raise ValueError("Incomplete premium evidence package")
        bundle = paths[0].parent
        prefix = "grant-evidence-" if app_id == "grants" else "procurement-evidence-"
        if (bundle.parent != directory or not bundle.name.startswith(prefix)
                or _BUNDLE_TIMESTAMP.fullmatch(bundle.name[len(prefix):]) is None
                or not bundle.is_dir() or bundle.is_symlink()
                or any(path.parent != bundle for path in paths)):
            raise ValueError("Unexpected premium evidence package location")
    else:
        raise ValueError("Unknown report product identity")

    for path, (stem, suffix) in zip(paths, expected):
        if not path.name.startswith(stem + "-") or path.suffix != suffix:
            raise ValueError("Unexpected report file name or type")
        timestamp = path.name[len(stem) + 1:-len(suffix)]
        if _REPORT_TIMESTAMP.fullmatch(timestamp) is None:
            raise ValueError("Unexpected report file identity")


def confirm_report_files(outputs: object, *, folder: str | Path | None = None,
                         app_id: str | None = None) -> tuple[Path, ...]:
    """Reject empty/malformed report inventories and missing/nonregular reports.

    Exact native Path objects avoid invoking user-defined path hooks. A single
    non-following ``stat`` checks each report leaf (rejecting links, directories
    and empty files). When *both* destination/product are supplied, require the
    six engines' actual output layouts before any success or premium review
    selection. Existing standalone callers may omit both keywords; the real
    GUI must always supply both. Snapshots are not a durable filesystem lease.
    """
    if (folder is None) != (app_id is None):
        raise ValueError("Report output location and product must be paired")
    if type(outputs) not in (list, tuple) or not 1 <= len(outputs) <= _MAX_REPORTS:
        raise ValueError("Invalid generated report inventory")
    checked: list[Path] = []
    seen: set[Path] = set()
    identities: set[tuple[int, int]] = set()
    for path in outputs:
        if type(path) is not _NATIVE_PATH_TYPE or not path.name or path in seen:
            raise ValueError("Invalid generated report path")
        info = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode) or info.st_size <= 0:
            raise ValueError("Generated report is not a nonempty regular file")
        # Distinct names referring to one hard-linked file are not two pieces
        # of independent review evidence. Some Windows filesystems expose
        # st_ino=0; do not manufacture identity proof in that case.
        identity = (info.st_dev, info.st_ino)
        if info.st_ino and identity in identities:
            raise ValueError("Report inventory contains an aliased file")
        identities.add(identity)
        seen.add(path)
        checked.append(path)
    confirmed = tuple(checked)
    if folder is not None:
        _confirm_output_placement(confirmed, folder, app_id)
        if app_id in _PREMIUM_REPORTS:
            # Bind the returned report bytes to their published SHA inventory.
            # A valid filename/bundle alone is not sufficient review evidence.
            from .premium_manifest_completion import verify_premium_inventory
            verify_premium_inventory(confirmed, app_id)
    return confirmed
