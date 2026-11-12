"""Synthetic six-engine source verification; never a Windows binary release gate.

The report proves only that the inventoried checkout stayed byte-stable during
six synthetic source smokes. It is not signing, security scanning or QD approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from pathlib import Path

from report_evidence import prepare_report_path, publish_report
from scripts.smoke_result_custody_r386 import checked_smoke_outputs

APPS = (
    ("LedgerDiffLite", "ledger"),
    ("InvoiceTwinScout", "invoices"),
    ("SpendMapLite", "spend"),
    ("PolicyDeltaDesk", "policy"),
    ("GrantAuditStudioPro", "grants"),
    ("ProcureGuardStudioPro", "procurement"),
)
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_SOURCE_FILES = 512
_READ_SIZE = 64 * 1024


def _identity(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _same_path_descriptor_identity(path_info: os.stat_result,
                                   descriptor_info: os.stat_result,
                                   *, windows: bool | None = None) -> bool:
    """Compare two OS views without discarding per-view custody checks.

    Windows 3.12 path lstat and fd fstat can report *different creation-time*
    (st_ctime_ns) values for the same dev+inode (R101 hosted proof: three
    files initially, then eleven). That timestamp is NOT portable as a
    cross-API identity field. Keep all six structural fields in the
    cross-view comparison. Preserve creation-time checks for each view
    separately before/after the complete read in _fingerprint.
    Linux keeps the original full seven-field comparison.
    """
    if windows is None:
        windows = os.name == "nt"
    path_identity = _identity(path_info)
    descriptor_identity = _identity(descriptor_info)
    if windows:
        return path_identity[:-1] == descriptor_identity[:-1]
    return path_identity == descriptor_identity


def _fingerprint(path: Path, root: Path) -> str:
    """Hash a single bounded regular checkout file without following symlinks.

    Compare path and descriptor identities before and after reading so observed
    replacements, in-flight writes and hardlink aliases cannot be certified.
    """
    fd = None
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or before.st_size > MAX_SOURCE_BYTES
                or not path.resolve(strict=True).is_relative_to(root)):
            raise ValueError("unsafe or oversized desktop source file")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
        fd = os.open(path, flags)
        start = os.fstat(fd)
        if not _same_path_descriptor_identity(before, start):
            raise ValueError("Desktop source changed before fingerprinting")
        digest = hashlib.sha256()
        consumed = 0
        while True:
            block = os.read(fd, _READ_SIZE)
            if not block:
                break
            consumed += len(block)
            if consumed > MAX_SOURCE_BYTES:
                raise ValueError("Desktop source exceeds safety bound")
            digest.update(block)
        # Compare *each* view to itself so Windows creation-time mismatches
        # across lstat/fstat never weaken same-view change detection. An
        # in-flight rewrite/inode swap remains a hard failure.
        if (consumed != before.st_size or _identity(os.fstat(fd)) != _identity(start)
                or _identity(path.lstat()) != _identity(before)):
            raise ValueError("Desktop source changed while fingerprinting")
        return digest.hexdigest()
    except (OSError, RuntimeError):
        raise ValueError("Unsafe or changing desktop source file") from None
    finally:
        if fd is not None:
            os.close(fd)


def _checked_directory(path: Path, root: Path) -> None:
    """Reject symlinked ancestors, not merely symlinks at the final directory."""
    try:
        current = root
        for component in path.relative_to(root).parts:
            current = current / component
            if not stat.S_ISDIR(current.lstat().st_mode):
                raise ValueError("Incomplete or unsafe desktop source tree")
    except (OSError, RuntimeError, ValueError):
        raise ValueError("Incomplete or unsafe desktop source tree") from None


def _package_python_sources(package: Path) -> list[Path]:
    """Traverse nested Python packages without following directory symlinks."""
    discovered = []
    pending = [package]
    visited = 0
    try:
        while pending:
            directory = pending.pop()
            visited += 1
            if visited > MAX_SOURCE_FILES:
                raise ValueError("Incomplete or unsafe desktop source tree")
            with os.scandir(directory) as iterator:
                for entry in iterator:
                    item = Path(entry.path)
                    mode = item.lstat().st_mode
                    if stat.S_ISLNK(mode):
                        raise ValueError("Incomplete or unsafe desktop source tree")
                    if stat.S_ISDIR(mode):
                        pending.append(item)
                    elif item.suffix == ".py":
                        if not stat.S_ISREG(mode):
                            raise ValueError("Incomplete or unsafe desktop source tree")
                        discovered.append(item)
                    if len(discovered) + len(pending) > MAX_SOURCE_FILES:
                        raise ValueError("Incomplete or unsafe desktop source tree")
    except (OSError, RuntimeError, ValueError):
        raise ValueError("Incomplete or unsafe desktop source tree") from None
    return discovered


def source_inventory(repo_root: Path) -> list[dict[str, str]]:
    """Inventory all desktop Python runtime sources and exactly six launchers.

    Include nested engine modules, top-level imported helpers and operator
    scripts, rather than certifying only the top level of fvs_suite. Test and
    cache files remain out of scope. A second inventory is taken after smokes.
    """
    root = Path(repo_root).resolve(strict=True)
    desktop = root / "products" / "desktop"
    package = desktop / "fvs_suite"
    launchers = desktop / "launchers"
    scripts = desktop / "scripts"
    for directory in (desktop, package, launchers):
        _checked_directory(directory, root)
    if os.path.lexists(scripts):
        _checked_directory(scripts, root)

    files = _package_python_sources(package)
    required_launchers = [launchers / (name + ".py") for name, _ in APPS]
    # An unapproved seventh launcher must not be silently omitted from evidence.
    if {p.name for p in launchers.iterdir() if p.suffix == ".py"} != {
            path.name for path in required_launchers}:
        raise ValueError("Incomplete or unsafe desktop source tree")
    script_files = _package_python_sources(scripts) if scripts.is_dir() else []
    selected = sorted(set([*files, *desktop.glob("*.py"),
                           *script_files, *required_launchers]))
    if (not files or len(selected) > MAX_SOURCE_FILES
            or any(not p.is_file() or p.is_symlink() for p in selected)):
        raise ValueError("Incomplete or unsafe desktop source tree")
    inventory = []
    for path in selected:
        digest = _fingerprint(path, root)
        inventory.append({"path": path.relative_to(root).as_posix(), "sha256": digest})
    return inventory


def verify_smokes(run_smoke) -> list[dict[str, object]]:
    """Execute each actual engine's synthetic contract, never customer inputs."""
    results = []
    for name, app_id in APPS:
        outputs = run_smoke(app_id)
        paths = checked_smoke_outputs(outputs)
        results.append({"app": name, "engine": app_id,
                        "result": "PASS", "synthetic_output_count": len(paths)})
    return results


def _source_metadata(repo_root: Path, inventory: list[dict[str, str]]) -> list[tuple[int, ...]]:
    """Private stat snapshot, detecting same-byte rewrites and inode swaps."""
    root = Path(repo_root).resolve(strict=True)
    try:
        return [_identity((root / item["path"]).lstat()) for item in inventory]
    except (OSError, RuntimeError, ValueError):
        raise ValueError("Desktop source metadata unavailable") from None


def report_data(repo_root: Path, run_smoke, *, commit: str = "") -> dict:
    """Fail closed when inventoried source files change during six app smokes."""
    inventory = source_inventory(repo_root)
    metadata = _source_metadata(repo_root, inventory)
    results = verify_smokes(run_smoke)
    final_inventory = source_inventory(repo_root)
    if (final_inventory != inventory
            or _source_metadata(repo_root, final_inventory) != metadata):
        raise RuntimeError("Desktop sources changed during synthetic smoke; evidence withheld")
    return {
        "schema": "fvs-source-smoke-v1",
        "scope": "PYTHON_SOURCE_ONLY_NOT_WINDOWS_BINARY_VERIFICATION",
        "released": False,
        "qd_approved": False,
        "commit": commit,
        "source_inventory": inventory,
        "application_results": results,
        "all_six_passed": len(results) == len(APPS),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path,
                        help="Atomically create a new external source-only evidence JSON")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[3]
    destination = prepare_report_path(args.report, root) if args.report else None
    from fvs_suite.smoke import run_smoke
    data = report_data(root, run_smoke, commit=os.environ.get("GITHUB_SHA", ""))
    if destination is not None:
        publish_report(destination, data)
    print(f"PASS: {len(data['application_results'])}/6 synthetic source engine smokes; "
          "NOT Windows binary verification or release approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
