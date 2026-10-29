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

APPS = (
    ("LedgerDiffLite", "ledger"),
    ("InvoiceTwinScout", "invoices"),
    ("SpendMapLite", "spend"),
    ("PolicyDeltaDesk", "policy"),
    ("GrantAuditStudioPro", "grants"),
    ("ProcureGuardStudioPro", "procurement"),
)
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_SOURCE_FILES = 256
_READ_SIZE = 64 * 1024


def _identity(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


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
        if _identity(start) != _identity(before):
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
        if (consumed != before.st_size or _identity(os.fstat(fd)) != _identity(before)
                or _identity(path.lstat()) != _identity(before)):
            raise ValueError("Desktop source changed while fingerprinting")
        return digest.hexdigest()
    except (OSError, RuntimeError):
        raise ValueError("Unsafe or changing desktop source file") from None
    finally:
        if fd is not None:
            os.close(fd)


def source_inventory(repo_root: Path) -> list[dict[str, str]]:
    """Inventory exactly the current Python engines and six launchers."""
    root = Path(repo_root).resolve(strict=True)
    package = root / "products" / "desktop" / "fvs_suite"
    launchers = root / "products" / "desktop" / "launchers"
    if (package.is_symlink() or launchers.is_symlink()
            or not package.is_dir() or not launchers.is_dir()):
        raise ValueError("Incomplete or unsafe desktop source tree")
    files = sorted(package.glob("*.py"))
    required_launchers = [launchers / (name + ".py") for name, _ in APPS]
    selected = sorted(set([*files, *required_launchers]))
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
        if not outputs:
            raise RuntimeError(f"{name} returned no source-smoke outputs")
        paths = [Path(p) for p in outputs]
        if any(p.is_absolute() or p.name in ("", ".", "..") or len(p.parts) != 1 for p in paths):
            raise RuntimeError(f"{name} returned an unsafe source-smoke output reference")
        results.append({"app": name, "engine": app_id,
                        "result": "PASS", "synthetic_output_count": len(paths)})
    return results


def report_data(repo_root: Path, run_smoke, *, commit: str = "") -> dict:
    """Fail closed when any inventoried source is edited during six app smokes."""
    inventory = source_inventory(repo_root)
    results = verify_smokes(run_smoke)
    if source_inventory(repo_root) != inventory:
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
