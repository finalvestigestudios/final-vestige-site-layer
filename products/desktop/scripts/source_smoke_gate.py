"""Internal, cross-platform source smoke gate for the six Final Vestige Labs engines.

This is NOT an executable/installer test or a release authorization. Only synthetic
inputs are used by fvs_suite.smoke; the report contains source hashes, not data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

APPS = (
    ("LedgerDiffLite", "ledger"),
    ("InvoiceTwinScout", "invoices"),
    ("SpendMapLite", "spend"),
    ("PolicyDeltaDesk", "policy"),
    ("GrantAuditStudioPro", "grants"),
    ("ProcureGuardStudioPro", "procurement"),
)


def source_inventory(repo_root: Path) -> list[dict[str, str]]:
    """Hash the exact Python engine/launcher files used by the source smoke."""
    root = Path(repo_root).resolve()
    package = root / "products" / "desktop" / "fvs_suite"
    launchers = root / "products" / "desktop" / "launchers"
    files = sorted(package.glob("*.py")) if package.is_dir() else []
    required_launchers = [launchers / (name + ".py") for name, _ in APPS]
    if not files or any(not f.is_file() or f.is_symlink() for f in [*files, *required_launchers]):
        raise ValueError("Incomplete or unsafe desktop source tree; source smoke cannot pass")
    inventory = []
    for path in sorted(set([*files, *required_launchers])):
        # No symlinks permitted. Never follow source paths outside the checkout.
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Source inventory contains a symlink or external path")
        inventory.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    return inventory


def verify_smokes(run_smoke) -> list[dict[str, object]]:
    """Execute every engine in its actual import context. Fail on first error."""
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
    inventory = source_inventory(repo_root)
    results = verify_smokes(run_smoke)
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
    parser.add_argument("--report", type=Path, help="Write internal JSON evidence (never download binaries)")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[3]
    # Import at execution time so isolated tests can validate the gate itself.
    from fvs_suite.smoke import run_smoke
    data = report_data(root, run_smoke, commit=os.environ.get("GITHUB_SHA", ""))
    payload = json.dumps(data, sort_keys=True, indent=2) + "\n"
    if args.report:
        if not args.report.parent.is_dir() or args.report.is_symlink():
            raise ValueError("Report destination must be an existing safe folder")
        with args.report.open("x", encoding="utf-8") as out:
            out.write(payload)
    print(f"PASS: {len(data['application_results'])}/6 synthetic source engine smokes; "
          "NOT Windows binary verification or release approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
